'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import Header from '../../../components/Header';
import { login } from '../../../lib/auth';

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setIsLoading(true);

    try {
      await login(email, password);
      router.push('/stories');
    } catch (err: any) {
      setError(err.message || 'Login failed. Please check your credentials.');
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
                Welcome Back
              </h1>
              <p className="text-sm" style={{ color: 'var(--color-ink-light)' }}>
                Sign in to share your perspective
              </p>
            </div>

            <form onSubmit={handleLogin} className="space-y-5">
              <div>
                <label htmlFor="email" className="block text-sm font-medium mb-2" style={{ color: 'var(--color-ink)' }}>
                  Email
                </label>
                <input
                  id="email"
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="test@example.com"
                  required
                  className="w-full px-4 py-3 border rounded-md text-sm focus:outline-none transition-colors"
                  style={{ background: 'var(--color-paper)', borderColor: 'var(--color-rule)', color: 'var(--color-ink)' }}
                />
              </div>

              <div>
                <div className="flex items-center justify-between mb-2">
                  <label htmlFor="password" className="block text-sm font-medium" style={{ color: 'var(--color-ink)' }}>
                    Password
                  </label>
                  <a href="/auth/forgot-password" className="text-xs" style={{ color: 'var(--color-accent)' }}>
                    Forgot password?
                  </a>
                </div>
                <input
                  id="password"
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
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
                {isLoading ? 'Signing in...' : 'Sign In'}
              </button>
            </form>

            <div className="mt-6 text-center">
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
