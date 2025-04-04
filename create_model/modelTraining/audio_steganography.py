import os
import torch
import torch.nn as nn
import torch.optim as optim
import librosa
import numpy as np
import pandas as pd
from torch.utils.data import Dataset, DataLoader
from tqdm import tqdm
import torch.nn.functional as F
from torchvision import models
import warnings

# Device Configuration
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

warnings.filterwarnings("ignore", category=UserWarning, module='librosa')

# Paths
dataset_path = "dataset_prep/dataset/split_data/split_audio"
train_path = os.path.join(dataset_path, "train")
val_path = os.path.join(dataset_path, "val")
save_model_path = os.path.join(os.getcwd(), "backend/models/best_audio_model.pth")

# Function to convert waveform to spectrogram
def waveform_to_spectrogram(waveform, sr=22050, n_mels=128, target_shape=(128, 300)):
    waveform, _ = librosa.effects.trim(waveform)  # Trim silence
    n_fft = min(2048, len(waveform))
    spectrogram = librosa.feature.melspectrogram(y=waveform, sr=sr, n_mels=n_mels, n_fft=n_fft)
    spectrogram = librosa.power_to_db(spectrogram, ref=np.max)
    spectrogram = (spectrogram - spectrogram.min()) / (spectrogram.max() - spectrogram.min())  # Normalize
    spectrogram = torch.tensor(spectrogram, dtype=torch.float32).unsqueeze(0)
    return pad_spectrogram(spectrogram, target_shape)

# Function to pad spectrogram
def pad_spectrogram(spectrogram, target_shape=(128, 300)):
    _, height, width = spectrogram.shape
    if width < target_shape[1]:
        pad_width = target_shape[1] - width
        spectrogram = F.pad(spectrogram, (0, pad_width), mode='constant', value=0)
    elif width > target_shape[1]:
        spectrogram = spectrogram[:, :, :target_shape[1]]
    return spectrogram

# SpecAugment for spectrograms
def spec_augment(spec, time_mask_param=30, freq_mask_param=13):
    _, freq, time = spec.shape
    if time > time_mask_param:
        t = np.random.randint(0, time - time_mask_param)
        spec[:, :, t:t + time_mask_param] = 0
    if freq > freq_mask_param:
        f = np.random.randint(0, freq - freq_mask_param)
        spec[:, f:f + freq_mask_param, :] = 0
    return spec

# Augmentation Function
def augment_waveform(waveform, sr):
    if np.random.rand() < 0.3:
        waveform += 0.005 * np.random.randn(len(waveform))
    if np.random.rand() < 0.3:
        rate = np.random.uniform(0.8, 1.2)
        waveform = librosa.effects.time_stretch(y=waveform, rate=rate)
    if np.random.rand() < 0.3:
        steps = np.random.uniform(-1, 1)
        waveform = librosa.effects.pitch_shift(waveform, sr=sr, n_steps=steps)
    return waveform

# Audio Dataset Class
class AudioDataset(Dataset):
    def __init__(self, data_dir, sr=22050, n_mels=128):
        self.data_dir = data_dir
        self.sr = sr
        self.n_mels = n_mels
        self.file_paths = []
        self.labels = []

        for label, subdir in enumerate(["clean", "stego"]):
            full_path = os.path.join(data_dir, subdir)
            for file in os.listdir(full_path):
                self.file_paths.append(os.path.join(full_path, file))
                self.labels.append(label)

    def __len__(self):
        return len(self.file_paths)

    def __getitem__(self, idx):
        file_path = self.file_paths[idx]
        label = self.labels[idx]
        waveform, _ = librosa.load(file_path, sr=self.sr)
        waveform = augment_waveform(waveform, self.sr)
        spectrogram = waveform_to_spectrogram(waveform, sr=self.sr, n_mels=self.n_mels)
        spectrogram = spec_augment(spectrogram)  # Apply SpecAugment
        return spectrogram, torch.tensor(label, dtype=torch.long)

# ResNet34 Model for Audio Spectrograms
class ResNet34Audio(nn.Module):
    def __init__(self, num_classes):
        super(ResNet34Audio, self).__init__()
        self.resnet34 = models.resnet34(weights=models.ResNet34_Weights.DEFAULT)
        self.resnet34.conv1 = nn.Conv2d(1, 64, kernel_size=7, stride=2, padding=3, bias=False)  # For 1-channel input

        # Freeze fewer layers for more learning capacity
        for name, param in self.resnet34.named_parameters():
            if "layer2" not in name and "layer3" not in name and "layer4" not in name and "fc" not in name:
                param.requires_grad = False

        num_ftrs = self.resnet34.fc.in_features
        self.resnet34.fc = nn.Linear(num_ftrs, num_classes)

    def forward(self, x):
        return self.resnet34(x)

# Train Function with Model Accuracy Calculation
def train(model, train_loader, val_loader, epochs=50, lr=0.0003, weight_decay=1e-4):
    model.to(device)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.AdamW(filter(lambda p: p.requires_grad, model.parameters()), lr=lr, weight_decay=weight_decay)
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode='min', patience=2, factor=0.5)

    best_acc = 0
    patience = 10
    counter = 0

    for epoch in range(epochs):
        model.train()
        total_train_loss = 0

        print(f"\n🔄 Epoch {epoch+1}/{epochs} Training...")
        for inputs, labels in tqdm(train_loader, desc="🛠️ Training", leave=False):
            inputs, labels = inputs.to(device), labels.to(device)
            optimizer.zero_grad()
            outputs = model(inputs)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
            total_train_loss += loss.item()

        avg_train_loss = total_train_loss / len(train_loader)

        # 🔍 Validation
        model.eval()
        correct, total = 0, 0
        with torch.no_grad():
            for inputs, labels in tqdm(val_loader, desc="🔍 Validating", leave=False):
                inputs, labels = inputs.to(device), labels.to(device)
                outputs = model(inputs)
                _, predicted = torch.max(outputs, 1)
                correct += (predicted == labels).sum().item()
                total += labels.size(0)

        accuracy = 100 * correct / total
        scheduler.step(avg_train_loss)

        print(f"📘 Epoch {epoch+1}/{epochs} - Train Loss: {avg_train_loss:.4f}, Val Accuracy: {accuracy:.2f}%")

        if accuracy > best_acc:
            best_acc = accuracy
            torch.save(model.state_dict(), save_model_path)
            print(f"💾 Best model saved (Acc: {accuracy:.2f}%) ✅")
            counter = 0
        else:
            counter += 1

        if counter >= patience:
            print("⏹️ Early stopping triggered! Best Val Accuracy:", best_acc)
            break

    print(f"\n🏁 Training complete. Best model saved at: {save_model_path}")

# Load Dataset & Create Dataloaders
if __name__ == "__main__":
    train_dataset = AudioDataset(train_path)
    val_dataset = AudioDataset(val_path)

    train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=32, shuffle=False)

    print(f"Training samples: {len(train_dataset)}, Validation samples: {len(val_dataset)}")

    num_classes = 2
    model = ResNet34Audio(num_classes)
    train(model, train_loader, val_loader)
