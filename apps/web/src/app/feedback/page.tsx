'use client';

import React, { useState } from 'react';
import Header from '../../components/Header';
import { API_BASE_URL } from '../../lib/config';


type FeedbackType = 'bug' | 'feature' | 'content' | 'general';

const feedbackTypes: { value: FeedbackType; label: string; icon: string }[] = [
  { value: 'bug', label: 'Bug Report', icon: '🐛' },
  { value: 'feature', label: 'Feature Request', icon: '💡' },
  { value: 'content', label: 'Content Issue', icon: '📰' },
  { value: 'general', label: 'General Feedback', icon: '💬' },
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
    <div className="min-h-screen bg-stone-900">
      <Header />

      <main className="container mx-auto px-6 py-16 max-w-2xl">
        <div className="text-center mb-12">
          <h1 className="text-3xl md:text-4xl font-bold text-stone-100 mb-4">
            Share Your Thoughts
          </h1>
          <p className="text-stone-400">
            Help us make Gaze better. Your feedback shapes what we build next.
          </p>
        </div>

        {status === 'sent' ? (
          <div className="bg-emerald-900/30 border border-emerald-700 rounded-2xl p-8 text-center">
            <div className="text-4xl mb-4">🙏</div>
            <h2 className="text-xl font-semibold text-emerald-300 mb-2">Thank you!</h2>
            <p className="text-stone-400 mb-6">Your feedback has been received. We truly appreciate it.</p>
            <button
              onClick={() => setStatus('idle')}
              className="text-sm text-emerald-400 hover:text-emerald-300 underline"
            >
              Send more feedback
            </button>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Feedback Type */}
            <div>
              <label className="block text-sm font-medium text-stone-300 mb-3">What kind of feedback?</label>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                {feedbackTypes.map((ft) => (
                  <button
                    key={ft.value}
                    type="button"
                    onClick={() => setType(ft.value)}
                    className={`flex flex-col items-center p-4 rounded-xl border transition-all ${
                      type === ft.value
                        ? 'border-amber-500 bg-amber-500/10 text-amber-300'
                        : 'border-stone-700 bg-stone-800/50 text-stone-400 hover:border-stone-600'
                    }`}
                  >
                    <span className="text-2xl mb-1">{ft.icon}</span>
                    <span className="text-xs font-medium">{ft.label}</span>
                  </button>
                ))}
              </div>
            </div>

            {/* Message */}
            <div>
              <label htmlFor="message" className="block text-sm font-medium text-stone-300 mb-2">
                Your message
              </label>
              <textarea
                id="message"
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                rows={6}
                required
                placeholder="Tell us what's on your mind..."
                className="w-full bg-stone-800 border border-stone-700 rounded-xl px-4 py-3 text-stone-100 placeholder-stone-500 focus:outline-none focus:ring-2 focus:ring-amber-500/50 focus:border-amber-500 resize-none"
              />
            </div>

            {/* Email (optional) */}
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-stone-300 mb-2">
                Email <span className="text-stone-500">(optional, if you&apos;d like a response)</span>
              </label>
              <input
                id="email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="you@example.com"
                className="w-full bg-stone-800 border border-stone-700 rounded-xl px-4 py-3 text-stone-100 placeholder-stone-500 focus:outline-none focus:ring-2 focus:ring-amber-500/50 focus:border-amber-500"
              />
            </div>

            {status === 'error' && (
              <div className="bg-red-900/30 border border-red-700 rounded-xl p-4 text-sm text-red-300">
                Something went wrong. Please try again or email us directly at{' '}
                <a href="mailto:support@wrhitw.com" className="underline">support@wrhitw.com</a>
              </div>
            )}

            <button
              type="submit"
              disabled={!message.trim() || status === 'sending'}
              className="w-full bg-amber-500 text-stone-900 py-3.5 rounded-xl font-semibold hover:bg-amber-400 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {status === 'sending' ? 'Sending...' : 'Submit Feedback'}
            </button>

            <p className="text-center text-xs text-stone-500">
              Or reach us directly at{' '}
              <a href="mailto:support@wrhitw.com" className="text-amber-500 hover:text-amber-400">
                support@wrhitw.com
              </a>
            </p>
          </form>
        )}
      </main>
    </div>
  );
}
