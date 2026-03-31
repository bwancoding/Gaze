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
    <div className="min-h-screen bg-neutral-50">
      <Header />

      <main className="container mx-auto px-6 py-16 max-w-xl">
        <div className="mb-10">
          <h1 className="font-serif text-headline text-neutral-900 mb-3">
            Share Your Thoughts
          </h1>
          <p className="text-neutral-500 text-sm">
            Help us make Gaze better. Your feedback shapes what we build next.
          </p>
        </div>

        {status === 'sent' ? (
          <div className="bg-emerald-50 border border-emerald-200 rounded-lg p-8 text-center">
            <h2 className="font-serif text-lg font-semibold text-emerald-800 mb-2">Thank you!</h2>
            <p className="text-neutral-600 text-sm mb-6">Your feedback has been received. We truly appreciate it.</p>
            <button
              onClick={() => setStatus('idle')}
              className="text-sm text-emerald-700 hover:underline"
            >
              Send more feedback
            </button>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Feedback Type */}
            <div>
              <label className="block text-sm font-medium text-neutral-700 mb-2">What kind of feedback?</label>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
                {feedbackTypes.map((ft) => (
                  <button
                    key={ft.value}
                    type="button"
                    onClick={() => setType(ft.value)}
                    className={`px-3 py-2 rounded-md border text-sm transition-colors ${
                      type === ft.value
                        ? 'border-neutral-900 bg-neutral-900 text-white'
                        : 'border-neutral-300 bg-white text-neutral-600 hover:border-neutral-400'
                    }`}
                  >
                    {ft.label}
                  </button>
                ))}
              </div>
            </div>

            {/* Message */}
            <div>
              <label htmlFor="message" className="block text-sm font-medium text-neutral-700 mb-2">
                Your message
              </label>
              <textarea
                id="message"
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                rows={6}
                required
                placeholder="Tell us what's on your mind..."
                className="w-full bg-white border border-neutral-300 rounded-lg px-4 py-3 text-neutral-900 placeholder-neutral-400 focus:outline-none focus:ring-1 focus:ring-neutral-900 focus:border-neutral-900 resize-none text-sm"
              />
            </div>

            {/* Email (optional) */}
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-neutral-700 mb-2">
                Email <span className="text-neutral-400">(optional, if you&apos;d like a response)</span>
              </label>
              <input
                id="email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="you@example.com"
                className="w-full bg-white border border-neutral-300 rounded-lg px-4 py-3 text-neutral-900 placeholder-neutral-400 focus:outline-none focus:ring-1 focus:ring-neutral-900 focus:border-neutral-900 text-sm"
              />
            </div>

            {status === 'error' && (
              <div className="border border-red-200 bg-red-50 rounded-lg p-4 text-sm text-red-700">
                Something went wrong. Please try again or email us directly at{' '}
                <a href="mailto:support@wrhitw.com" className="underline">support@wrhitw.com</a>
              </div>
            )}

            <button
              type="submit"
              disabled={!message.trim() || status === 'sending'}
              className="w-full bg-neutral-900 text-white py-3 rounded-md font-medium hover:bg-neutral-800 transition-colors disabled:opacity-50 disabled:cursor-not-allowed text-sm"
            >
              {status === 'sending' ? 'Sending...' : 'Submit Feedback'}
            </button>

            <p className="text-center text-xs text-neutral-400">
              Or reach us directly at{' '}
              <a href="mailto:support@wrhitw.com" className="text-neutral-600 hover:text-neutral-900">
                support@wrhitw.com
              </a>
            </p>
          </form>
        )}
      </main>
    </div>
  );
}
