'use client';

import { useState } from 'react';
import Link from 'next/link';
import { useAuth } from './AuthProvider';
import { usePathname } from 'next/navigation';

export default function Header() {
  const { user, logout, loading } = useAuth();
  const pathname = usePathname();
  const [mobileOpen, setMobileOpen] = useState(false);

  const isActive = (path: string) =>
    path === '/' ? pathname === '/' : pathname.startsWith(path);

  const linkClass = (path: string) =>
    `px-3 py-2 rounded-md text-sm font-medium transition-colors ${
      isActive(path)
        ? 'bg-blue-50 text-blue-600'
        : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
    }`;

  return (
    <header className="bg-white shadow-sm">
      <nav className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Desktop + mobile top bar */}
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center">
            <Link href="/" className="text-xl font-bold text-blue-600">
              TodoApp
            </Link>
          </div>

          {/* Desktop nav */}
          <div className="hidden md:flex items-center space-x-4">
            <Link href="/" className={linkClass('/')}>
              Home
            </Link>

            {!loading && user && (
              <>
                <Link href="/dashboard" className={linkClass('/dashboard')}>
                  Dashboard
                </Link>
                <Link href="/chatbot" className={linkClass('/chatbot')}>
                  Chatbot
                </Link>
                <div className="flex items-center space-x-4 ml-4">
                  <span className="text-sm text-gray-500">
                    {user.email}
                  </span>
                  <button
                    onClick={logout}
                    className="text-gray-600 hover:text-gray-900 text-sm font-medium"
                  >
                    Logout
                  </button>
                </div>
              </>
            )}

            {!loading && !user && (
              <div className="flex items-center space-x-4 ml-4">
                <Link href="/chatbot" className={linkClass('/chatbot')}>
                  Chatbot
                </Link>
                <Link href="/login" className={linkClass('/login')}>
                  Login
                </Link>
                <Link
                  href="/signup"
                  className="bg-blue-600 text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-blue-700 transition-colors"
                >
                  Sign Up
                </Link>
              </div>
            )}
          </div>

          {/* Mobile hamburger */}
          <button
            className="md:hidden p-2 rounded-md text-gray-600 hover:text-gray-900 hover:bg-gray-100"
            onClick={() => setMobileOpen(!mobileOpen)}
            aria-label="Toggle menu"
          >
            <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              {mobileOpen ? (
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              ) : (
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
              )}
            </svg>
          </button>
        </div>

        {/* Mobile dropdown */}
        {mobileOpen && (
          <div className="md:hidden pb-3 space-y-1">
            <Link href="/" className={`block ${linkClass('/')}`} onClick={() => setMobileOpen(false)}>
              Home
            </Link>

            {!loading && user && (
              <>
                <Link href="/dashboard" className={`block ${linkClass('/dashboard')}`} onClick={() => setMobileOpen(false)}>
                  Dashboard
                </Link>
                <Link href="/chatbot" className={`block ${linkClass('/chatbot')}`} onClick={() => setMobileOpen(false)}>
                  Chatbot
                </Link>
                <div className="border-t border-gray-200 mt-2 pt-2 px-3">
                  <p className="text-sm text-gray-500">{user.email}</p>
                  <button
                    onClick={() => { setMobileOpen(false); logout(); }}
                    className="mt-1 text-sm font-medium text-gray-600 hover:text-gray-900"
                  >
                    Logout
                  </button>
                </div>
              </>
            )}

            {!loading && !user && (
              <>
                <Link href="/chatbot" className={`block ${linkClass('/chatbot')}`} onClick={() => setMobileOpen(false)}>
                  Chatbot
                </Link>
                <Link href="/login" className={`block ${linkClass('/login')}`} onClick={() => setMobileOpen(false)}>
                  Login
                </Link>
                <Link
                  href="/signup"
                  className="block mx-3 mt-1 text-center bg-blue-600 text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-blue-700 transition-colors"
                  onClick={() => setMobileOpen(false)}
                >
                  Sign Up
                </Link>
              </>
            )}
          </div>
        )}
      </nav>
    </header>
  );
}
