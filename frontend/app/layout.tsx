import type { Metadata } from 'next';
import './globals.css';
import { AuthProvider } from '@/components/AuthProvider';
import Header from '@/components/Header';
import { Providers } from './providers';

export const metadata: Metadata = {
  title: 'Todo App - Manage Your Tasks',
  description: 'A modern todo application built with Next.js and FastAPI',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-gray-50">
        <AuthProvider>
          <Header />
          <main><Providers>{children}</Providers></main>
        </AuthProvider>
      </body>
    </html>
  );
}
