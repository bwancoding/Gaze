'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { API_BASE_URL } from '../../../lib/config';


interface FeedbackItem {
  id: number;
  type: string;
  message: string;
  email: string | null;
  created_at: string;
}

const TYPE_COLORS: Record<string, { bg: string; text: string }> = {
  bug: { bg: '#FEE2E2', text: '#991B1B' },
  feature: { bg: '#DBEAFE', text: '#1E40AF' },
  content: { bg: '#FEF3C7', text: '#92400E' },
  general: { bg: '#F3F4F6', text: '#374151' },
};

export default function AdminFeedback() {
  const router = useRouter();
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [feedbacks, setFeedbacks] = useState<FeedbackItem[]>([]);
  const [typeFilter, setTypeFilter] = useState<string>('');
  const [currentPage, setCurrentPage] = useState(1);
  const [total, setTotal] = useState(0);
  const [isLoading, setIsLoading] = useState(false);
  const PAGE_SIZE = 20;

  useEffect(() => {
    const storedAuth = localStorage.getItem('admin_auth');
    if (storedAuth) {
      setIsAuthenticated(true);
    } else {
      router.push('/ctrl-be5abcba');
    }
  }, [router]);

  const fetchFeedback = async (page = currentPage) => {
    setIsLoading(true);
    try {
      const typeParam = typeFilter ? `&type=${typeFilter}` : '';
      const res = await fetch(
        `${API_BASE_URL}/api/feedback?page=${page}&page_size=${PAGE_SIZE}${typeParam}`
      );
      if (!res.ok) throw new Error('Failed to fetch');
      const data = await res.json();
      setFeedbacks(data.items);
      setTotal(data.total);
    } catch {
      // ignore
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (isAuthenticated) {
      setCurrentPage(1);
      fetchFeedback(1);
    }
  }, [isAuthenticated, typeFilter]);

  if (!isAuthenticated) return null;

  const totalPages = Math.ceil(total / PAGE_SIZE);

  return (
    <div className="min-h-screen" style={{ background: 'var(--color-paper)' }}>
      <div className="container mx-auto px-6 py-8 max-w-4xl">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <button
              onClick={() => router.push('/ctrl-be5abcba')}
              className="text-sm mb-2 inline-block"
              style={{ color: 'var(--color-accent)' }}
            >
              &larr; Back to Dashboard
            </button>
            <h1 className="font-serif text-2xl font-bold" style={{ color: 'var(--color-ink)' }}>
              User Feedback
            </h1>
            <p className="text-sm mt-1" style={{ color: 'var(--color-ink-light)' }}>
              {total} total submissions
            </p>
          </div>
        </div>

        {/* Type filter */}
        <div className="flex gap-2 mb-6">
          {['', 'bug', 'feature', 'content', 'general'].map((t) => (
            <button
              key={t}
              onClick={() => setTypeFilter(t)}
              className="px-3 py-1.5 rounded-md text-sm border transition-colors"
              style={{
                borderColor: typeFilter === t ? 'var(--color-ink)' : 'var(--color-rule)',
                background: typeFilter === t ? 'var(--color-ink)' : 'transparent',
                color: typeFilter === t ? '#fff' : 'var(--color-ink-light)',
              }}
            >
              {t || 'All'}
            </button>
          ))}
        </div>

        {/* Feedback list */}
        {isLoading ? (
          <div className="text-center py-12 text-neutral-500">Loading...</div>
        ) : feedbacks.length === 0 ? (
          <div className="text-center py-12 border rounded-lg" style={{ borderColor: 'var(--color-rule)' }}>
            <p className="text-neutral-500">No feedback yet</p>
          </div>
        ) : (
          <div className="space-y-3">
            {feedbacks.map((fb) => {
              const colors = TYPE_COLORS[fb.type] || TYPE_COLORS.general;
              return (
                <div
                  key={fb.id}
                  className="border rounded-lg p-5"
                  style={{ borderColor: 'var(--color-rule)', background: 'white' }}
                >
                  <div className="flex items-start justify-between mb-3">
                    <span
                      className="text-xs font-medium px-2 py-0.5 rounded"
                      style={{ background: colors.bg, color: colors.text }}
                    >
                      {fb.type}
                    </span>
                    <span className="text-xs" style={{ color: 'var(--color-ink-light)' }}>
                      {new Date(fb.created_at).toLocaleString()}
                    </span>
                  </div>
                  <p className="text-sm leading-relaxed whitespace-pre-wrap" style={{ color: 'var(--color-ink)' }}>
                    {fb.message}
                  </p>
                  {fb.email && (
                    <p className="mt-3 text-xs" style={{ color: 'var(--color-ink-light)' }}>
                      Contact: <a href={`mailto:${fb.email}`} className="underline">{fb.email}</a>
                    </p>
                  )}
                </div>
              );
            })}
          </div>
        )}

        {/* Pagination */}
        {totalPages > 1 && (
          <div className="flex items-center justify-center gap-4 mt-8">
            <button
              onClick={() => { setCurrentPage(p => p - 1); fetchFeedback(currentPage - 1); }}
              disabled={currentPage <= 1}
              className="px-3 py-1.5 text-sm border rounded disabled:opacity-30"
              style={{ borderColor: 'var(--color-rule)' }}
            >
              Previous
            </button>
            <span className="text-sm" style={{ color: 'var(--color-ink-light)' }}>
              Page {currentPage} of {totalPages}
            </span>
            <button
              onClick={() => { setCurrentPage(p => p + 1); fetchFeedback(currentPage + 1); }}
              disabled={currentPage >= totalPages}
              className="px-3 py-1.5 text-sm border rounded disabled:opacity-30"
              style={{ borderColor: 'var(--color-rule)' }}
            >
              Next
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
