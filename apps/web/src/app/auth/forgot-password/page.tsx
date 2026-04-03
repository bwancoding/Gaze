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
    <div className="min-h-screen" style={{ background: 'var(--color-paper)' }}>
      <Header />

      <main className="container mx-auto px-6 py-12">
        <div className="max-w-md mx-auto">
          <div className="border rounded-md p-8" style={{ borderColor: 'var(--color-rule)' }}>
            <div className="text-center mb-8">
              <h1 className="font-serif font-bold mb-2" style={{ color: 'var(--color-ink)', fontSize: '1.75rem' }}>
                Forgot Password
              </h1>
              <p className="text-sm" style={{ color: 'var(--color-ink-light)' }}>
                Enter your email to receive a password reset link
              </p>
            </div>

            {!sent ? (
              <form onSubmit={handleSubmit} className="space-y-6">
                <div>
                  <label htmlFor="email" className="block text-sm font-medium mb-2" style={{ color: 'var(--color-ink)' }}>
                    Email Address
                  </label>
                  <input
                    id="email"
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="you@example.com"
                    required
                    className="w-full px-4 py-3 border rounded-md text-sm focus:outline-none transition-colors"
                    style={{ background: 'var(--color-paper)', borderColor: 'var(--color-rule)', color: 'var(--color-ink)' }}
                  />
                </div>

                {error && (
                  <div className="p-4 border rounded-md text-sm" style={{ borderColor: 'var(--color-accent)', background: 'rgba(194,65,12,0.05)', color: 'var(--color-ink)' }}>
                    {error}
                  </div>
                )}

                <button
                  type="submit"
                  disabled={isLoading}
                  className="w-full py-3 rounded-md font-medium text-sm text-white transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                  style={{ background: 'var(--color-accent)' }}
                >
                  {isLoading ? 'Sending...' : 'Send Reset Link'}
                </button>
              </form>
            ) : (
              <div className="space-y-6">
                <div className="p-4 border rounded-md text-sm" style={{ borderColor: 'var(--color-rule)', background: 'rgba(194,65,12,0.04)', color: 'var(--color-ink)' }}>
                  <p className="font-medium mb-1">Check your email</p>
                  <p style={{ color: 'var(--color-ink-light)' }}>If an account exists for <strong>{email}</strong>, you will receive a password reset link.</p>
                </div>

                {resetToken && process.env.NODE_ENV === 'development' && (
                  <div className="p-4 border rounded-md text-sm" style={{ borderColor: 'var(--color-accent)', background: 'rgba(194,65,12,0.05)' }}>
                    <p className="font-medium mb-2" style={{ color: 'var(--color-ink)' }}>Development: Direct Reset Link</p>
                    <a
                      href={`/auth/reset-password?token=${encodeURIComponent(resetToken)}`}
                      className="inline-block px-4 py-2 rounded-md text-sm font-medium text-white transition-colors"
                      style={{ background: 'var(--color-accent)' }}
                    >
                      Reset Password Now
                    </a>
                  </div>
                )}
              </div>
            )}

            <div className="mt-6 text-center space-y-2">
              <p className="text-sm" style={{ color: 'var(--color-ink-light)' }}>
                Remember your password?{' '}
                <a href="/auth/login" className="font-medium" style={{ color: 'var(--color-accent)' }}>
                  Sign In
                </a>
              </p>
              <p className="text-sm" style={{ color: 'var(--color-ink-light)' }}>
                Don&apos;t have an account?{' '}
                <a href="/auth/register" className="font-medium" style={{ color: 'var(--color-accent)' }}>
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
