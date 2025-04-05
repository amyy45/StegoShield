import { useState } from "react";

const FileUploader = () => {
  const [file, setFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState("");
  const [fileType, setFileType] = useState("");
  const [result, setResult] = useState(null);

  const handleFileChange = (e) => {
    const uploadedFile = e.target.files[0];
    setFile(uploadedFile);
    setResult(null);

    if (uploadedFile) {
      const type = uploadedFile.type;

      setFileType(type.split("/")[0]); // image, audio, or video

      const reader = new FileReader();
      reader.onloadend = () => {
        setPreviewUrl(reader.result);
      };

      // Read for preview
      if (type.startsWith("image") || type.startsWith("audio") || type.startsWith("video")) {
        reader.readAsDataURL(uploadedFile);
      } else {
        setPreviewUrl("");
      }
    }
  };

  const handleAnalyze = async () => {
    if (!file) return alert("Upload a file first!");

    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await fetch("http://localhost:5000/api/predict", {
        method: "POST",
        body: formData,
      });

      const data = await res.json();
      setResult(data);
    } catch (error) {
      console.error("Prediction failed", error);
    }
  };

  const renderPreview = () => {
    if (!previewUrl) return null;

    if (fileType === "image") {
      return <img src={previewUrl} alt="Preview" className="mt-4 w-full rounded-lg border" />;
    } else if (fileType === "audio") {
      return <audio controls className="mt-4 w-full"><source src={previewUrl} /></audio>;
    } else if (fileType === "video") {
      return <video controls className="mt-4 w-full rounded-lg border"><source src={previewUrl} /></video>;
    }
    return null;
  };

  return (
    <div className="max-w-xl mx-auto my-10 p-6 bg-white shadow-lg rounded-xl space-y-4">
      <h2 className="text-xl font-semibold text-gray-800">Upload a File to Analyze</h2>

      <input
        type="file"
        accept="image/*,audio/*,video/*"
        onChange={handleFileChange}
        className="w-full"
      />

      {renderPreview()}

      <button
        onClick={handleAnalyze}
        className="mt-4 px-6 py-2 bg-indigo-600 text-white rounded-full hover:bg-indigo-500"
      >
        Analyze
      </button>

      {result && (
        <div className="mt-6 p-4 border rounded-lg text-center">
          <p className="text-lg font-semibold">
            Prediction:{" "}
            <span className={result.result === "Malicious" ? "text-red-600" : "text-green-600"}>
              {result.result}
            </span>
          </p>
          <p className="text-gray-600">Confidence: {(result.confidence * 100).toFixed(2)}%</p>
        </div>
      )}
    </div>
  );
};

export default FileUploader;
