'use client';

import { useState } from 'react';

export default function ScanPage() {
  const [frontImage, setFrontImage] = useState<File | null>(null);
  const [sideImage, setSideImage] = useState<File | null>(null);
  const [height, setHeight] = useState<string>('');
  const [isUploading, setIsUploading] = useState(false);
  const [scanId, setScanId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleFrontChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0] || null;
    setFrontImage(file);
    setError(null);
  };

  const handleSideChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0] || null;
    setSideImage(file);
    setError(null);
  };

  const handleHeightChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setHeight(e.target.value);
    setError(null);
  };

  const handleUpload = async () => {
    if (!frontImage || !sideImage) {
      setError('Please select both front and side images');
      return;
    }

    if (!height || isNaN(parseFloat(height)) || parseFloat(height) <= 0) {
      setError('Please enter a valid height in centimeters');
      return;
    }

    setIsUploading(true);
    setError(null);

    try {
      const formData = new FormData();
      formData.append('front', frontImage);
      formData.append('side', sideImage);
      formData.append('height', height);

      const response = await fetch('http://localhost:8000/api/scan/upload', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`Upload failed: ${response.status}`);
      }

      const result = await response.json();
      setScanId(result.scan_id);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error occurred');
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-2xl mx-auto">
        <h1 className="text-3xl font-bold mb-6 text-center">VoxelFit Body Scanner</h1>

        {scanId && (
          <div className="bg-green-50 border-l-4 border-green-500 p-4 mb-6">
            <h2 className="text-lg font-semibold">Scan Uploaded Successfully!</h2>
            <p className="mt-2">Scan ID: <code className="bg-gray-200 px-2 py-1 rounded">{scanId}</code></p>
            <p className="mt-2">Checking processing status...</p>
          </div>
        )}

        <form className="space-y-6" onSubmit={(e) => e.preventDefault()}>
          <div>
            <label htmlFor="front" className="block text-sm font-medium mb-2">
              Front View Image
            </label>
            <input
              id="front"
              type="file"
              accept="image/*"
              onChange={handleFrontChange}
              className={`block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4
                file:rounded-full file:border-0 file:text-sm file:font-semibold
                file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100
                ${!frontImage ? 'file:cursor-pointer' : 'cursor-not-allowed'}`}
              disabled={!!frontImage}
            />
            {frontImage && (
              <p className="mt-2 text-sm text-gray-600">
                Selected: {frontImage.name}
              </p>
            )}
          </div>

          <div>
            <label htmlFor="side" className="block text-sm font-medium mb-2">
              Side View Image
            </label>
            <input
              id="side"
              type="file"
              accept="image/*"
              onChange={handleSideChange}
              className={`block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4
                file:rounded-full file:border-0 file:text-sm file:font-semibold
                file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100
                ${!sideImage ? 'file:cursor-pointer' : 'cursor-not-allowed'}`}
              disabled={!!sideImage}
            />
            {sideImage && (
              <p className="mt-2 text-sm text-gray-600">
                Selected: {sideImage.name}
              </p>
            )}
          </div>

          <div>
            <label htmlFor="height" className="block text-sm font-medium mb-2">
              Your Height (cm)
            </label>
            <input
              id="height"
              type="number"
              min="50"
              max="250"
              step="0.1"
              value={height}
              onChange={handleHeightChange}
              className={`block w-full text-sm text-gray-500
                ${height ? '' : 'placeholder:text-gray-400'}
                focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500
                border border-gray-300 rounded-md px-3 py-2
                placeholder:text-gray-400 focus:text-gray-700 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500`}
              placeholder="e.g., 175.5"
            />
          </div>

          <button
            type="submit"
            disabled={isUploading || !frontImage || !sideImage || !height}
            className={`w-full flex items-center justify-center px-6 py-3 text-sm font-medium
              transition-colors duration-200
              ${isUploading || !frontImage || !sideImage || !height
                ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                : 'bg-blue-600 text-white hover:bg-blue-700'}`}
          >
            {isUploading ? (
              <>
                <svg className="mr-2 h-4 w-4 animate-spin" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z"></path>
                </svg>
                Uploading...
              </>
            ) : (
              'Upload and Process Scan'
            )}
          </button>
        </form>

        {error && (
          <div className="bg-red-50 border-l-4 border-red-500 p-4 mt-6">
            <h2 className="text-lg font-semibold">Error</h2>
            <p className="mt-2">{error}</p>
          </div>
        )}
      </div>
    </div>
  );
}