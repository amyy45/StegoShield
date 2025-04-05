
import React from "react";
import { ShieldCheck, Image, Mic, Video } from "lucide-react";

const features = [
  {
    title: "Image Steganalysis",
    description: "Detect hidden payloads in PNG, JPEG, and BMP files using advanced CNN models.",
    icon: <Image className="w-8 h-8 text-indigo-600" />,
  },
  {
    title: "Audio Steganalysis",
    description: "Analyze spectrograms to identify steganography in MP3 and WAV audio formats.",
    icon: <Mic className="w-8 h-8 text-indigo-600" />,
  },
  {
    title: "Video Steganalysis",
    description: "Detect encoded information in MP4 and AVI files with hybrid CNN-LSTM models.",
    icon: <Video className="w-8 h-8 text-indigo-600" />,
  },
  {
    title: "Real-time Detection",
    description: "Get instant analysis reports and payload suspicion score with every upload.",
    icon: <ShieldCheck className="w-8 h-8 text-indigo-600" />,
  },
];

const Feature = () => {
  return (
    <section className="py-20 bg-white" id="features">
      <div className="max-w-screen-xl mx-auto px-4 text-center">
        <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-6">
          Powerful Features to Keep Your Files Safe
        </h2>
        <p className="text-gray-600 mb-12 max-w-2xl mx-auto">
          StegoShield provides multi-model steganalysis using deep learning to uncover hidden data in your images, audio, and video files.
        </p>

        <div className="grid gap-10 sm:grid-cols-2 lg:grid-cols-4">
          {features.map((feature, index) => (
            <div
              key={index}
              className="bg-gray-50 p-6 rounded-2xl shadow hover:shadow-md transition-all"
            >
              <div className="flex justify-center mb-4">{feature.icon}</div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">{feature.title}</h3>
              <p className="text-sm text-gray-600">{feature.description}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default Feature;
