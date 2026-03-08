'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';

interface HeaderProps {
  title?: string;
  subtitle?: string;
}

export default function Header({ title = 'WRHITW', subtitle = "What's Really Happening In The World" }: HeaderProps) {
  const router = useRouter();
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [userEmail, setUserEmail] = useState<string | null>(null);

  useEffect(() => {
    // 检查登录状态
    const email = localStorage.getItem('user_email');
    if (email) {
      setIsLoggedIn(true);
      setUserEmail(email);
    }
  }, []);

  const handleSignIn = () => {
    router.push('/auth/login');
  };

  const handleSignOut = () => {
    localStorage.removeItem('user_email');
    localStorage.removeItem('user_password');
    setIsLoggedIn(false);
    setUserEmail(null);
    router.push('/');
  };

  return (
    <header className="bg-white border-b border-neutral-200 sticky top-0 z-50">
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          {/* Logo */}
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-primary-600 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-xl">W</span>
            </div>
            <div>
              <h1 className="text-xl font-bold text-neutral-900">{title}</h1>
              <p className="text-xs text-neutral-500 hidden sm:block">{subtitle}</p>
            </div>
          </div>

          {/* Navigation */}
          <nav className="flex items-center space-x-4">
            <a href="/" className="text-neutral-600 hover:text-primary-600 transition-colors">
              Home
            </a>
            <a href="/categories" className="text-neutral-600 hover:text-primary-600 transition-colors">
              Categories
            </a>
            <a href="/about" className="text-neutral-600 hover:text-primary-600 transition-colors">
              About
            </a>
            
            {isLoggedIn ? (
              <div className="flex items-center space-x-3">
                <span className="text-sm text-neutral-600">
                  {userEmail}
                </span>
                <button
                  onClick={handleSignOut}
                  className="bg-neutral-100 text-neutral-700 px-4 py-2 rounded-md hover:bg-neutral-200 transition-colors"
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
