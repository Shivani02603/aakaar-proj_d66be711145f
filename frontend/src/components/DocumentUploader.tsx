import React, { useState } from 'react';
import { ingestFile } from '../api/aiApi';
import toast from 'react-hot-toast';

interface DocumentUploaderProps {
  sessionId: string;
}

const DocumentUploader: React.FC<DocumentUploaderProps> = ({ sessionId }) => {
  const [isDragging, setIsDragging] = useState(false);
  const [uploadProgress, setUploadProgress] = useState<number | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  const handleDragOver = (event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDrop = async (event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    setIsDragging(false);

    const files = event.dataTransfer.files;
    if (files.length === 0) return;

    const file = files[0];
    await uploadFile(file);
  };

  const handleFileSelect = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files;
    if (files && files.length > 0) {
      const file = files[0];
      await uploadFile(file);
    }
  };

  const uploadFile = async (file: File) => {
    if (!['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'application/vnd.ms-excel', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'].includes(file.type)) {
      toast.error('Unsupported file type. Please upload a PDF, DOCX, XLS, or XLSX file.');
      return;
    }

    setUploadProgress(0);
    setSuccessMessage(null);

    try {
      const response = await ingestFile(file, sessionId, (progressEvent) => {
        if (progressEvent.lengthComputable) {
          const progress = Math.round((progressEvent.loaded / progressEvent.total) * 100);
          setUploadProgress(progress);
        }
      });

      if (response.headers.get('Content-Type')?.includes('application/json')) {
        const responseBody = await response.json();
        setSuccessMessage(`✓ Indexed ${responseBody.chunks_indexed} chunks`);
      } else {
        throw new Error('Unexpected response format');
      }
    } catch (error: any) {
      const errorMessage = error.response?.data?.message || 'An error occurred while uploading the file.';
      toast.error(errorMessage);
    } finally {
      setUploadProgress(null);
    }
  };

  return (
    <div className="w-full max-w-lg mx-auto">
      <div
        className={`border-2 border-dashed rounded-lg p-6 text-center ${isDragging ? 'border-blue-500 bg-blue-50' : 'border-gray-300'}`}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
      >
        <p className="text-gray-600">Drag and drop your file here, or</p>
        <label className="text-blue-500 cursor-pointer underline">
          <input
            type="file"
            className="hidden"
            accept=".pdf,.docx,.xlsx,.xls"
            onChange={handleFileSelect}
          />
          browse files
        </label>
      </div>
      {uploadProgress !== null && (
        <div className="mt-4">
          <div className="relative w-full h-4 bg-gray-200 rounded">
            <div
              className="absolute top-0 left-0 h-4 bg-blue-500 rounded"
              style={{ width: `${uploadProgress}%` }}
            ></div>
          </div>
          <p className="text-sm text-gray-600 mt-2">{uploadProgress}%</p>
        </div>
      )}
      {successMessage && (
        <div className="mt-4 text-green-600 font-semibold">{successMessage}</div>
      )}
    </div>
  );
};

export default DocumentUploader;