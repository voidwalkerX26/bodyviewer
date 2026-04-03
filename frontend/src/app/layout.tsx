import './globals.css';
import type { Metadata } from 'next';
import Link from 'next/link';

export const metadata: Metadata = {
  title: 'VoxelFit',
  description: 'Personal 3D body scanning and measurement app',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="antialiased">
        <nav className="bg-white border-b shadow-sm">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between h-16">
              <div className="flex">
                <Link href="/" className="flex items-center space-x-3">
                  <span className="text-xl font-bold text-gray-800">VoxelFit</span>
                </Link>
              </div>
              <div className="hidden md:flex">
                <div className="flex space-x-4">
                  <Link href="/" className="px-3 py-2 rounded-md text-sm font-medium text-gray-500 hover:text-gray-700 hover:bg-gray-50">
                    Dashboard
                  </Link>
                  <Link href="/scan" className="px-3 py-2 rounded-md text-sm font-medium text-gray-500 hover:text-gray-700 hover:bg-gray-50">
                    Scan
                  </Link>
                </div>
              </div>
            </div>
          </div>
        </nav>

        <div className="min-h-screen bg-gray-50">{children}</div>
      </body>
    </html>
  );
}