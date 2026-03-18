'use client';

import React from 'react';
import { useRouter } from 'next/navigation';

interface LoginPromptProps {
  total: number;
  shown: number;
  onLogin?: () => void;
}

export default function LoginPrompt({ total, shown, onLogin }: LoginPromptProps) {
  const router = useRouter();
  const remaining = total - shown;

  const handleLogin = () => {
    if (onLogin) {
      onLogin();
    } else {
      router.push('/auth/login');
    }
  };

  return (
    <div className="my-8">
      <div className="relative">
        {/* Gradient overlay effect */}
        <div className="absolute inset-0 bg-gradient-to-b from-transparent via-stone-50 to-stone-50 pointer-events-none"></div>
        
        {/* Login prompt card */}
        <div className="relative bg-gradient-to-br from-blue-50 to-indigo-50 rounded-2xl border border-blue-200 p-8 text-center shadow-lg">
          {/* Icon */}
          <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <svg className="w-8 h-8 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
            </svg>
          </div>

          {/* Title */}
          <h3 className="text-xl font-bold text-blue-900 mb-2">
            Join the Discussion
          </h3>

          {/* Description */}
          <p className="text-blue-800 mb-1">
            {remaining} more comments waiting for you
          </p>
          <p className="text-sm text-blue-600 mb-6">
            Sign in to read all comments, share your perspective, and engage with others
          </p>

          {/* Feature list */}
          <div className="grid grid-cols-3 gap-4 mb-6 text-sm">
            <div className="text-blue-700">
              <div className="font-semibold mb-1">📖</div>
              <div>Read All</div>
            </div>
            <div className="text-blue-700">
              <div className="font-semibold mb-1">💬</div>
              <div>Comment</div>
            </div>
            <div className="text-blue-700">
              <div className="font-semibold mb-1">👍</div>
              <div>Interact</div>
            </div>
          </div>

          {/* Buttons */}
          <div className="flex items-center justify-center space-x-3">
            <button
              onClick={handleLogin}
              className="bg-blue-600 text-white px-8 py-3 rounded-full font-medium hover:bg-blue-700 transition-colors shadow-lg hover:shadow-xl"
            >
              Sign In to Continue
            </button>
          </div>

          {/* Existing account prompt */}
          <p className="text-xs text-blue-600 mt-4">
            Already have an account? Sign in now
          </p>
        </div>
      </div>
    </div>
  );
}
