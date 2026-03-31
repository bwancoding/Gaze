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
        {/* Fade overlay */}
        <div className="absolute inset-0 bg-gradient-to-b from-transparent to-neutral-50 pointer-events-none"></div>

        {/* Login prompt */}
        <div className="relative bg-white border border-neutral-200 rounded-lg p-8 text-center">
          <h3 className="font-serif text-lg font-semibold text-neutral-900 mb-2">
            Join the Discussion
          </h3>

          <p className="text-neutral-600 text-sm mb-1">
            {remaining} more comments waiting for you
          </p>
          <p className="text-xs text-neutral-400 mb-6">
            Sign in to read all comments, share your perspective, and engage with others
          </p>

          <button
            onClick={handleLogin}
            className="bg-neutral-900 text-white px-6 py-2.5 rounded-md text-sm font-medium hover:bg-neutral-800 transition-colors"
          >
            Sign In to Continue
          </button>

          <p className="text-xs text-neutral-400 mt-4">
            Already have an account? Sign in now
          </p>
        </div>
      </div>
    </div>
  );
}
