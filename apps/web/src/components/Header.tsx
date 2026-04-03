'use client';

import React, { useState, useEffect } from 'react';
import { useRouter, usePathname } from 'next/navigation';
import { isAuthenticated, logout, getCurrentUser, fetchWithAuth } from '../lib/auth';
import { API_BASE_URL } from '../lib/config';


interface HeaderProps {
  title?: string;
  subtitle?: string;
}

export default function Header({ title = 'Gaze', subtitle = "What's Really Happening In The World" }: HeaderProps) {
  const router = useRouter();
  const pathname = usePathname();
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [userEmail, setUserEmail] = useState<string | null>(null);
  const [unreadCount, setUnreadCount] = useState(0);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  useEffect(() => {
    checkAuth();
  }, []);

  // Close mobile menu on route change
  useEffect(() => {
    setMobileMenuOpen(false);
  }, [pathname]);

  const checkAuth = async () => {
    const authenticated = isAuthenticated();
    setIsLoggedIn(authenticated);

    if (authenticated) {
      const user = await getCurrentUser();
      if (user) {
        setUserEmail(user.email);
      }
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
    setUnreadCount(0);
    window.location.href = '/';
  };

  const isActive = (path: string) => {
    if (path === '/') return pathname === '/';
    return pathname.startsWith(path);
  };

  const navLinkClass = (path: string) =>
    `transition-colors text-sm ${
      isActive(path)
        ? 'text-neutral-900 font-semibold'
        : 'text-neutral-500 hover:text-neutral-900'
    }`;

  const mobileNavLinkClass = (path: string) =>
    `block py-2 px-3 rounded-lg transition-colors text-sm ${
      isActive(path)
        ? 'text-neutral-900 font-semibold bg-neutral-100'
        : 'text-neutral-700 hover:bg-neutral-100'
    }`;

  return (
    <header className="sticky top-0 z-50 border-b" style={{ background: 'var(--color-paper)', borderColor: 'var(--color-rule)' }}>
      <div className="container mx-auto px-4 py-3 sm:py-4">
        <div className="flex items-center justify-between">
          {/* Logo — typographic, no colored box */}
          <a href="/" className="flex items-center space-x-2.5 hover:opacity-80 transition-opacity">
            <span className="font-serif text-2xl font-bold tracking-tight text-neutral-900">{title}</span>
            <span className="hidden sm:block text-xs text-neutral-400 border-l border-neutral-200 pl-2.5 leading-tight max-w-[140px]">{subtitle}</span>
          </a>

          {/* Desktop Navigation */}
          <nav className="hidden md:flex items-center space-x-5">
            <a href="/" className={navLinkClass('/')}>Home</a>
            <a href="/stories" className={navLinkClass('/stories')}>Stories</a>
            <a href="/feedback" className={navLinkClass('/feedback')}>Feedback</a>

            <div className="w-px h-5 bg-neutral-200" />

            {isLoggedIn ? (
              <div className="flex items-center space-x-3">
                <button
                  onClick={() => router.push('/notifications')}
                  className="relative p-1.5 text-neutral-500 hover:text-neutral-900 transition-colors"
                  title="Notifications"
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
                      d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
                  </svg>
                  {unreadCount > 0 && (
                    <span className="absolute -top-0.5 -right-0.5 w-4 h-4 bg-accent text-white text-[10px] font-bold rounded-full flex items-center justify-center">
                      {unreadCount > 9 ? '9+' : unreadCount}
                    </span>
                  )}
                </button>
                <button
                  onClick={() => router.push('/profile')}
                  className="p-1.5 text-neutral-500 hover:text-neutral-900 transition-colors"
                  title="Profile"
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
                      d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                  </svg>
                </button>
                <span className="text-sm text-neutral-500 hidden lg:inline">
                  {userEmail}
                </span>
                <button
                  onClick={handleSignOut}
                  className="text-sm text-neutral-500 hover:text-neutral-900 transition-colors"
                >
                  Sign Out
                </button>
              </div>
            ) : (
              <div className="flex items-center space-x-3">
                <button
                  onClick={handleSignIn}
                  className="text-sm text-neutral-500 hover:text-neutral-900 transition-colors"
                >
                  Sign In
                </button>
                <button
                  onClick={() => router.push('/auth/register')}
                  className="bg-neutral-900 text-white px-4 py-1.5 rounded-md hover:bg-neutral-800 transition-colors text-sm"
                >
                  Sign Up
                </button>
              </div>
            )}
          </nav>

          {/* Mobile: icons + hamburger */}
          <div className="flex md:hidden items-center space-x-1">
            {isLoggedIn && (
              <button
                onClick={() => router.push('/notifications')}
                className="relative p-2 text-neutral-600"
                title="Notifications"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
                    d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
                </svg>
                {unreadCount > 0 && (
                  <span className="absolute -top-0.5 -right-0.5 w-4 h-4 bg-accent text-white text-[10px] font-bold rounded-full flex items-center justify-center">
                    {unreadCount > 9 ? '9+' : unreadCount}
                  </span>
                )}
              </button>
            )}
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="p-2 text-neutral-700 hover:text-neutral-900 transition-colors"
              aria-label="Toggle menu"
            >
              {mobileMenuOpen ? (
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M6 18L18 6M6 6l12 12" />
                </svg>
              ) : (
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M4 6h16M4 12h16M4 18h16" />
                </svg>
              )}
            </button>
          </div>
        </div>

        {/* Mobile Menu Dropdown */}
        {mobileMenuOpen && (
          <div className="md:hidden mt-3 pt-3 border-t border-neutral-200">
            <nav className="flex flex-col space-y-1 mb-3">
              <a href="/" className={mobileNavLinkClass('/')}>Home</a>
              <a href="/stories" className={mobileNavLinkClass('/stories')}>Stories</a>
              <a href="/feedback" className={mobileNavLinkClass('/feedback')}>Feedback</a>
            </nav>
            <div className="pt-3 border-t border-neutral-100">
              {isLoggedIn ? (
                <div className="flex flex-col space-y-2">
                  <a href="/profile" className="block py-2 px-3 rounded-lg text-sm text-neutral-700 hover:bg-neutral-100">
                    Profile {userEmail && <span className="text-neutral-400 ml-1">({userEmail})</span>}
                  </a>
                  <button
                    onClick={handleSignOut}
                    className="w-full text-left py-2 px-3 rounded-lg text-sm text-red-600 hover:bg-red-50 transition-colors"
                  >
                    Sign Out
                  </button>
                </div>
              ) : (
                <div className="flex space-x-2 px-3 pb-2">
                  <button
                    onClick={handleSignIn}
                    className="flex-1 text-center py-2.5 border border-neutral-300 rounded-lg text-sm font-medium text-neutral-700 hover:bg-neutral-50 transition-colors"
                  >
                    Sign In
                  </button>
                  <button
                    onClick={() => router.push('/auth/register')}
                    className="flex-1 text-center py-2.5 bg-neutral-900 text-white rounded-lg text-sm hover:bg-neutral-800 transition-colors"
                  >
                    Sign Up
                  </button>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </header>
  );
}
