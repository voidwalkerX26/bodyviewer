import Link from 'next/link';
import { useState, useEffect } from 'react';

export default function DashboardPage() {
  const [scans, setScans] = useState<Array<{id: string; timestamp: string; status: string}>>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadScans();
  }, []);

  const loadScans = async () => {
    setLoading(true);
    try {
      // Read local scans directory (for dev, we'll simulate this)
      // In a real app, this would be an API call to backend
      const response = await fetch('http://localhost:8000/api/scans');

      if (!response.ok) {
        // For now, let's try to read from local storage or return empty
        throw new Error('Failed to fetch scans');
      }

      const data = await response.json();
      setScans(data.scans || []);
    } catch (err) {
      // For development, show empty state with guidance
      setScans([]);
      setError('No scans yet. Upload your first scan using the Scan page.');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 p-8">
        <div className="flex items-center justify-center h-64">
          <div className="text-center">
            <svg className="mx-auto h-8 w-8 animate-spin text-blue-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z"></path>
            </svg>
            <p className="mt-2 text-sm text-gray-500">Loading scans...</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-4xl mx-auto">
        <div className="flex justify-between items-start mb-6">
          <h1 className="text-3xl font-bold">Scan History</h1>
          <Link href="/scan" className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700">
            New Scan
          </Link>
        </div>

        {error && (
          <div className="bg-red-50 border-l-4 border-red-500 p-4 mb-6">
            <h2 className="text-lg font-semibold">Notice</h2>
            <p className="mt-2">{error}</p>
          </div>
        )}

        {scans.length === 0 && !error && (
          <div className="bg-blue-50 border-l-4 border-blue-500 p-8 text-center">
            <h2 className="text-xl font-semibold mb-4">No scans yet</h2>
            <p className="text-gray-600 mb-4">
              Your scan history will appear here after you upload and process scans.
            </p>
            <Link href="/scan" className="inline-block px-6 py-3 bg-blue-600 text-white rounded-md hover:bg-blue-700">
              Upload First Scan
            </Link>
          </div>
        )}

        {scans.length > 0 && (
          <div className="space-y-4">
            <h2 className="text-xl font-semibold mb-4">Recent Scans</h2>
            <div className="divide-y divide-gray-200">
              {scans.map((scan) => (
                <div key={scan.id} className="py-4">
                  <div className="flex justify-between items-start">
                    <div>
                      <h3 className="font-medium">{scan.id}</h3>
                      <p className="text-sm text-gray-500">
                        {new Date(scan.timestamp).toLocaleString()}
                      </p>
                    </div>
                    <span className={`px-3 py-1 text-xs font-medium rounded-full
                      ${scan.status === 'completed'
                        ? 'bg-green-100 text-green-800'
                        : scan.status === 'processing'
                          ? 'bg-yellow-100 text-yellow-800'
                          : 'bg-gray-100 text-gray-800'}`}>
                      {scan.status}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}