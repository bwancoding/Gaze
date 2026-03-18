'use client';

import React, { useState } from 'react';
import Header from '../../../components/Header';
import { forgotPassword } from '../../../lib/auth';

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [sent, setSent] = useState(false);
  const [resetToken, setResetToken] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setIsLoading(true);

    try {
      const result = await forgotPassword(email);
      setSent(true);
      // MVP: show the reset token directly (in production, sent via email)
      if (result.reset_token) {
        setResetToken(result.reset_token);
      }
    } catch (err: any) {
      setError(err.message || 'Request failed');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-stone-50">
      <Header />

      <main className="container mx-auto px-6 py-12">
        <div className="max-w-md mx-auto">
          <div className="bg-white rounded-2xl border border-stone-200 p-8 shadow-lg">
            <div className="text-center mb-8">
              <div className="text-4xl mb-4">🔑</div>
              <h1 className="text-3xl font-bold text-stone-900 mb-2">
                Forgot Password
              </h1>
              <p className="text-stone-600">
                Enter your email to receive a password reset link
              </p>
            </div>

            {!sent ? (
              <form onSubmit={handleSubmit} className="space-y-6">
                <div>
                  <label htmlFor="email" className="block text-sm font-medium text-stone-700 mb-2">
                    Email Address
                  </label>
                  <input
                    id="email"
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="you@example.com"
                    required
                    className="w-full px-4 py-3 border border-stone-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                  />
                </div>

                {error && (
                  <div className="p-4 bg-red-50 border border-red-200 rounded-xl text-red-700 text-sm">
                    {error}
                  </div>
                )}

                <button
                  type="submit"
                  disabled={isLoading}
                  className="w-full py-3.5 bg-stone-900 text-white rounded-xl font-medium hover:bg-stone-800 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                  {isLoading ? 'Sending...' : 'Send Reset Link'}
                </button>
              </form>
            ) : (
              <div className="space-y-6">
                <div className="p-4 bg-emerald-50 border border-emerald-200 rounded-xl text-emerald-700 text-sm">
                  <p className="font-medium mb-1">Check your email</p>
                  <p>If an account exists for <strong>{email}</strong>, you will receive a password reset link.</p>
                </div>

                {resetToken && (
                  <div className="p-4 bg-amber-50 border border-amber-200 rounded-xl text-amber-800 text-sm">
                    <p className="font-medium mb-2">MVP Mode: Direct Reset Link</p>
                    <p className="mb-3 text-xs">In production, this link would be sent via email.</p>
                    <a
                      href={`/auth/reset-password?token=${encodeURIComponent(resetToken)}`}
                      className="inline-block px-4 py-2 bg-amber-600 text-white rounded-lg text-sm font-medium hover:bg-amber-700 transition-colors"
                    >
                      Reset Password Now
                    </a>
                  </div>
                )}
              </div>
            )}

            <div className="mt-6 text-center space-y-2">
              <p className="text-sm text-stone-600">
                Remember your password?{' '}
                <a href="/auth/login" className="text-blue-600 hover:text-blue-700 font-medium">
                  Sign In
                </a>
              </p>
              <p className="text-sm text-stone-600">
                Don&apos;t have an account?{' '}
                <a href="/auth/register" className="text-blue-600 hover:text-blue-700 font-medium">
                  Create Account
                </a>
              </p>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
