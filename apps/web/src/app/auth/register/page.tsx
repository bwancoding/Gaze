'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import Header from '../../../components/Header';
import { register } from '../../../lib/auth';

export default function RegisterPage() {
  const router = useRouter();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [displayName, setDisplayName] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (password.length < 6) {
      setError('Password must be at least 6 characters');
      return;
    }

    if (password !== confirmPassword) {
      setError('Passwords do not match');
      return;
    }

    setIsLoading(true);

    try {
      await register(email, password, displayName || undefined);
      router.push('/stories');
    } catch (err: any) {
      setError(err.message || 'Registration failed');
    } finally {
      setIsLoading(false);
    }
  };

  const inputStyle = {
    background: 'var(--color-paper)',
    borderColor: 'var(--color-rule)',
    color: 'var(--color-ink)',
  };

  return (
    <div className="min-h-screen" style={{ background: 'var(--color-paper)' }}>
      <Header />

      <main className="container mx-auto px-6 py-12">
        <div className="max-w-md mx-auto">
          <div className="border rounded-md p-8" style={{ borderColor: 'var(--color-rule)' }}>
            <div className="text-center mb-8">
              <h1 className="font-serif font-bold mb-2" style={{ color: 'var(--color-ink)', fontSize: '1.75rem' }}>
                Create Account
              </h1>
              <p className="text-sm" style={{ color: 'var(--color-ink-light)' }}>
                Join the conversation, see every perspective
              </p>
            </div>

            <form onSubmit={handleRegister} className="space-y-5">
              <div>
                <label htmlFor="displayName" className="block text-sm font-medium mb-2" style={{ color: 'var(--color-ink)' }}>
                  Display Name
                </label>
                <input
                  id="displayName"
                  type="text"
                  value={displayName}
                  onChange={(e) => setDisplayName(e.target.value)}
                  placeholder="How others will see you"
                  className="w-full px-4 py-3 border rounded-md text-sm focus:outline-none transition-colors"
                  style={inputStyle}
                />
                <p className="mt-1 text-xs" style={{ color: 'var(--color-ink-light)' }}>Optional. Defaults to your email username.</p>
              </div>

              <div>
                <label htmlFor="email" className="block text-sm font-medium mb-2" style={{ color: 'var(--color-ink)' }}>
                  Email <span style={{ color: 'var(--color-accent)' }}>*</span>
                </label>
                <input
                  id="email"
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="you@example.com"
                  required
                  className="w-full px-4 py-3 border rounded-md text-sm focus:outline-none transition-colors"
                  style={inputStyle}
                />
              </div>

              <div>
                <label htmlFor="password" className="block text-sm font-medium mb-2" style={{ color: 'var(--color-ink)' }}>
                  Password <span style={{ color: 'var(--color-accent)' }}>*</span>
                </label>
                <input
                  id="password"
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="At least 6 characters"
                  required
                  minLength={6}
                  className="w-full px-4 py-3 border rounded-md text-sm focus:outline-none transition-colors"
                  style={inputStyle}
                />
              </div>

              <div>
                <label htmlFor="confirmPassword" className="block text-sm font-medium mb-2" style={{ color: 'var(--color-ink)' }}>
                  Confirm Password <span style={{ color: 'var(--color-accent)' }}>*</span>
                </label>
                <input
                  id="confirmPassword"
                  type="password"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  placeholder="Re-enter your password"
                  required
                  minLength={6}
                  className="w-full px-4 py-3 border rounded-md text-sm focus:outline-none transition-colors"
                  style={inputStyle}
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
                {isLoading ? 'Creating Account...' : 'Create Account'}
              </button>
            </form>

            <div className="mt-6 text-center">
              <p className="text-sm" style={{ color: 'var(--color-ink-light)' }}>
                Already have an account?{' '}
                <a href="/auth/login" className="font-medium" style={{ color: 'var(--color-accent)' }}>
                  Sign In
                </a>
              </p>
            </div>

            <div className="mt-4 text-center">
              <p className="text-xs" style={{ color: 'var(--color-ink-light)' }}>
                By creating an account, you agree to participate respectfully and share genuine perspectives.
              </p>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
