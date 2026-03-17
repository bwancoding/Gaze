'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { isAuthenticated, logout, getCurrentUser, fetchWithAuth } from '../lib/auth';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface HeaderProps {
  title?: string;
  subtitle?: string;
}

export default function Header({ title = 'WRHITW', subtitle = "What's Really Happening In The World" }: HeaderProps) {
  const router = useRouter();
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [userEmail, setUserEmail] = useState<string | null>(null);
  const [unreadCount, setUnreadCount] = useState(0);

  useEffect(() => {
    checkAuth();
  }, []);

  const checkAuth = async () => {
    const authenticated = isAuthenticated();
    setIsLoggedIn(authenticated);

    if (authenticated) {
      const user = await getCurrentUser();
      if (user) {
        setUserEmail(user.email);
      }
      // Fetch unread notification count
      try {
        const res = await fetchWithAuth(`${API_BASE_URL}/api/notifications/unread-count`);
        if (res.ok) {
          const data = await res.json();
          setUnreadCount(data.count);
        }
      } catch {}
    }
  };

  const handleSignIn = () => {
    router.push('/auth/login');
  };

  const handleSignOut = async () => {
    await logout();
    setIsLoggedIn(false);
    setUserEmail(null);
    router.push('/');
  };

  return (
    <header className="bg-white border-b border-neutral-200 sticky top-0 z-50">
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          {/* Logo */}
          <a href="/" className="flex items-center space-x-3 hover:opacity-80 transition-opacity">
            <div className="w-10 h-10 bg-primary-600 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-xl">W</span>
            </div>
            <div>
              <h1 className="text-xl font-bold text-neutral-900">{title}</h1>
              <p className="text-xs text-neutral-500 hidden sm:block">{subtitle}</p>
            </div>
          </a>

          {/* Navigation */}
          <nav className="flex items-center space-x-4">
            <a href="/" className="text-neutral-600 hover:text-primary-600 transition-colors text-sm">
              Home
            </a>
            <a href="/stories" className="text-neutral-600 hover:text-primary-600 transition-colors text-sm font-medium">
              Stories
            </a>
            <a href="/about" className="text-neutral-600 hover:text-primary-600 transition-colors text-sm">
              About
            </a>

            {isLoggedIn ? (
              <div className="flex items-center space-x-2">
                {/* Notification Bell */}
                <button
                  onClick={() => router.push('/notifications')}
                  className="relative p-2 text-neutral-600 hover:text-primary-600 transition-colors"
                  title="Notifications"
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                      d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
                  </svg>
                  {unreadCount > 0 && (
                    <span className="absolute -top-0.5 -right-0.5 w-4 h-4 bg-red-500 text-white text-[10px] font-bold rounded-full flex items-center justify-center">
                      {unreadCount > 9 ? '9+' : unreadCount}
                    </span>
                  )}
                </button>

                {/* Profile Icon */}
                <button
                  onClick={() => router.push('/profile')}
                  className="p-2 text-neutral-600 hover:text-primary-600 transition-colors"
                  title="Profile"
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                      d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                  </svg>
                </button>

                <span className="text-sm text-neutral-600 hidden md:inline">
                  {userEmail}
                </span>
                <button
                  onClick={handleSignOut}
                  className="bg-neutral-100 text-neutral-700 px-3 py-1.5 rounded-md text-sm hover:bg-neutral-200 transition-colors"
                >
                  Sign Out
                </button>
              </div>
            ) : (
              <button
                onClick={handleSignIn}
                className="bg-primary-600 text-white px-4 py-2 rounded-md hover:bg-primary-700 transition-colors"
              >
                Sign In
              </button>
            )}
          </nav>
        </div>
      </div>
    </header>
  );
}
