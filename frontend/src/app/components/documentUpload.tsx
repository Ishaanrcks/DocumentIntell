"use client"
import { useState } from 'react';
import axios from 'axios';
import { CloudArrowUpIcon, DocumentTextIcon, CheckCircleIcon } from '@heroicons/react/24/outline';

export default function DocumentUpload() {
    const [file, setFile] = useState<File | null>(null);
    const [uploading, setUploading] = useState(false);
    const [dragActive, setDragActive] = useState(false);

    const handleUpload = async () => {
        if (!file) return;

        setUploading(true);
        const formData = new FormData();
        formData.append('file', file);

        try {
            await axios.post('http://localhost:8000/api/documents/upload/', formData);
            alert('Document uploaded successfully!');
            setFile(null);
        } catch (error) {
            alert('Upload failed');
        }
        setUploading(false);
    };

    const handleDrag = (e: React.DragEvent) => {
        e.preventDefault();
        e.stopPropagation();
        if (e.type === "dragenter" || e.type === "dragover") {
            setDragActive(true);
        } else if (e.type === "dragleave") {
            setDragActive(false);
        }
    };

    const handleDrop = (e: React.DragEvent) => {
        e.preventDefault();
        e.stopPropagation();
        setDragActive(false);

        if (e.dataTransfer.files && e.dataTransfer.files[0]) {
            setFile(e.dataTransfer.files[0]);
        }
    };

    return (
        <div className="p-8 max-w-md mx-auto bg-gradient-to-br from-gray-900 to-gray-800 rounded-2xl shadow-2xl border border-gray-700">
            <div className="text-center mb-6">
                <CloudArrowUpIcon className="h-12 w-12 text-blue-400 mx-auto mb-3" />
                <h2 className="text-2xl font-bold text-white mb-2">Upload Document</h2>
                <p className="text-gray-400 text-sm">Upload your text documents for AI analysis</p>
            </div>

            {/* Drag and Drop Area */}
            <div
                className={`relative border-2 border-dashed rounded-xl p-8 text-center transition-all duration-300 ${dragActive
                        ? 'border-blue-400 bg-blue-400/10'
                        : file
                            ? 'border-green-400 bg-green-400/10'
                            : 'border-gray-600 hover:border-gray-500'
                    }`}
                onDragEnter={handleDrag}
                onDragLeave={handleDrag}
                onDragOver={handleDrag}
                onDrop={handleDrop}
            >
                <input
                    type="file"
                    accept=".txt"
                    onChange={(e) => setFile(e.target.files?.[0] || null)}
                    className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                />

                {file ? (
                    <div className="space-y-3">
                        <CheckCircleIcon className="h-10 w-10 text-green-400 mx-auto" />
                        <div>
                            <p className="text-green-400 font-medium">{file.name}</p>
                            <p className="text-gray-400 text-sm">{(file.size / 1024).toFixed(1)} KB</p>
                        </div>
                    </div>
                ) : (
                    <div className="space-y-3">
                        <DocumentTextIcon className="h-10 w-10 text-gray-400 mx-auto" />
                        <div>
                            <p className="text-white font-medium">Drop your file here</p>
                            <p className="text-gray-400 text-sm">or click to browse</p>
                            <p className="text-gray-500 text-xs mt-2">Supports: .txt files</p>
                        </div>
                    </div>
                )}
            </div>

            {/* Upload Button */}
            <button
                onClick={handleUpload}
                disabled={!file || uploading}
                className={`w-full mt-6 py-3 px-6 rounded-xl font-semibold text-white transition-all duration-300 transform ${!file || uploading
                        ? 'bg-gray-600 cursor-not-allowed opacity-50'
                        : 'bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 hover:scale-105 shadow-lg hover:shadow-xl'
                    }`}
            >
                {uploading ? (
                    <div className="flex items-center justify-center space-x-2">
                        <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                        <span>Uploading...</span>
                    </div>
                ) : (
                    <div className="flex items-center justify-center space-x-2">
                        <CloudArrowUpIcon className="h-5 w-5" />
                        <span>Upload Document</span>
                    </div>
                )}
            </button>
        </div>
    );
}
