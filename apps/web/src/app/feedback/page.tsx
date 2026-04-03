'use client';

import React, { useState } from 'react';
import Header from '../../components/Header';
import { API_BASE_URL } from '../../lib/config';


type FeedbackType = 'bug' | 'feature' | 'content' | 'general';

const feedbackTypes: { value: FeedbackType; label: string }[] = [
  { value: 'bug', label: 'Bug Report' },
  { value: 'feature', label: 'Feature Request' },
  { value: 'content', label: 'Content Issue' },
  { value: 'general', label: 'General Feedback' },
];

export default function FeedbackPage() {
  const [type, setType] = useState<FeedbackType>('general');
  const [message, setMessage] = useState('');
  const [email, setEmail] = useState('');
  const [status, setStatus] = useState<'idle' | 'sending' | 'sent' | 'error'>('idle');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!message.trim()) return;

    setStatus('sending');
    try {
      const res = await fetch(`${API_BASE_URL}/api/feedback`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ type, message: message.trim(), email: email.trim() || null }),
      });
      if (!res.ok) throw new Error('Failed');
      setStatus('sent');
      setMessage('');
      setEmail('');
    } catch {
      setStatus('error');
    }
  };

  return (
    <div className="min-h-screen" style={{ background: 'var(--color-paper)' }}>
      <Header />

      <main className="container mx-auto px-6 py-16 max-w-xl">
        <div className="mb-10">
          <h1 className="font-serif font-bold mb-3" style={{ color: 'var(--color-ink)', fontSize: 'clamp(1.5rem, 3vw, 2rem)' }}>
            Share Your Thoughts
          </h1>
          <p className="text-sm" style={{ color: 'var(--color-ink-light)' }}>
            Help us make Gaze better. Your feedback shapes what we build next.
          </p>
        </div>

        {status === 'sent' ? (
          <div className="border rounded-md p-8 text-center" style={{ borderColor: 'var(--color-rule)', background: 'rgba(194,65,12,0.04)' }}>
            <h2 className="font-serif text-lg font-semibold mb-2" style={{ color: 'var(--color-ink)' }}>Thank you!</h2>
            <p className="text-sm mb-6" style={{ color: 'var(--color-ink-light)' }}>Your feedback has been received. We truly appreciate it.</p>
            <button
              onClick={() => setStatus('idle')}
              className="text-sm underline" style={{ color: 'var(--color-accent)' }}
            >
              Send more feedback
            </button>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Feedback Type */}
            <div>
              <label className="block text-sm font-medium mb-2" style={{ color: 'var(--color-ink)' }}>What kind of feedback?</label>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
                {feedbackTypes.map((ft) => (
                  <button
                    key={ft.value}
                    type="button"
                    onClick={() => setType(ft.value)}
                    className="px-3 py-2 rounded-md border text-sm transition-colors"
                    style={{
                      borderColor: type === ft.value ? 'var(--color-ink)' : 'var(--color-rule)',
                      background: type === ft.value ? 'var(--color-ink)' : 'var(--color-paper)',
                      color: type === ft.value ? '#fff' : 'var(--color-ink-light)',
                    }}
                  >
                    {ft.label}
                  </button>
                ))}
              </div>
            </div>

            {/* Message */}
            <div>
              <label htmlFor="message" className="block text-sm font-medium mb-2" style={{ color: 'var(--color-ink)' }}>
                Your message
              </label>
              <textarea
                id="message"
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                rows={6}
                required
                placeholder="Tell us what's on your mind..."
                className="w-full border rounded-md px-4 py-3 text-sm resize-none focus:outline-none"
                style={{
                  background: 'var(--color-paper)',
                  borderColor: 'var(--color-rule)',
                  color: 'var(--color-ink)',
                }}
              />
            </div>

            {/* Email (optional) */}
            <div>
              <label htmlFor="email" className="block text-sm font-medium mb-2" style={{ color: 'var(--color-ink)' }}>
                Email <span style={{ color: 'var(--color-ink-light)' }}>(optional, if you&apos;d like a response)</span>
              </label>
              <input
                id="email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="you@example.com"
                className="w-full border rounded-md px-4 py-3 text-sm focus:outline-none"
                style={{
                  background: 'var(--color-paper)',
                  borderColor: 'var(--color-rule)',
                  color: 'var(--color-ink)',
                }}
              />
            </div>

            {status === 'error' && (
              <div className="border rounded-md p-4 text-sm" style={{ borderColor: 'var(--color-accent)', background: 'rgba(194,65,12,0.05)', color: 'var(--color-ink)' }}>
                Something went wrong. Please try again or email us directly at{' '}
                <a href="mailto:support@wrhitw.com" className="underline">support@wrhitw.com</a>
              </div>
            )}

            <button
              type="submit"
              disabled={!message.trim() || status === 'sending'}
              className="w-full py-3 rounded-md font-medium text-sm transition-colors disabled:opacity-50 disabled:cursor-not-allowed text-white"
              style={{ background: 'var(--color-accent)' }}
            >
              {status === 'sending' ? 'Sending...' : 'Submit Feedback'}
            </button>

            <p className="text-center text-xs" style={{ color: 'var(--color-ink-light)' }}>
              Or reach us directly at{' '}
              <a href="mailto:support@wrhitw.com" className="underline" style={{ color: 'var(--color-ink)' }}>
                support@wrhitw.com
              </a>
            </p>
          </form>
        )}
      </main>
    </div>
  );
}
