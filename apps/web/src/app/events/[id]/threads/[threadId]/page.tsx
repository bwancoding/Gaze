'use client';

import React, { useState, useEffect, useRef } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Header from '../../../../../components/Header';
import CommentSection from '../../../../../components/CommentSection';
import { API_BASE_URL } from '../../../../../lib/config';


interface ThreadDetail {
  id: string;
  event_id: string;
  title: string;
  content: string;
  persona_name: string;
  avatar_color: string;
  is_verified?: boolean;
  reply_count: number;
  like_count: number;
  dislike_count: number;
  view_count: number;
  is_locked: boolean;
  tags: string[];
  created_at: string;
  updated_at: string;
}

type VoteType = 'like' | 'dislike' | null;

const avatarColors: Record<string, string> = {
  blue: 'bg-blue-500', red: 'bg-red-500', green: 'bg-green-500',
  yellow: 'bg-yellow-500', purple: 'bg-purple-500', pink: 'bg-pink-500',
  indigo: 'bg-indigo-500', teal: 'bg-teal-500', gray: 'bg-gray-500',
  orange: 'bg-orange-500',
};

export default function ThreadDetailPage() {
  const params = useParams();
  const router = useRouter();
  const eventId = params.id as string;
  const threadId = params.threadId as string;
  const commentSectionRef = useRef<HTMLDivElement>(null);

  const [thread, setThread] = useState<ThreadDetail | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [userVote, setUserVote] = useState<VoteType>(null);
  const [showBackToTop, setShowBackToTop] = useState(false);

  useEffect(() => {
    if (threadId) {
      fetch(`${API_BASE_URL}/api/threads/${threadId}`)
        .then(r => r.ok ? r.json() : Promise.reject('Not found'))
        .then(data => { setThread(data); setIsLoading(false); })
        .catch(() => setIsLoading(false));
    }
  }, [threadId]);

  // Show floating back-to-top when scrolled down
  useEffect(() => {
    const handleScroll = () => {
      setShowBackToTop(window.scrollY > 400);
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const handleVote = async (action: 'like' | 'dislike') => {
    const token = localStorage.getItem('access_token');
    if (!token) {
      router.push('/auth/login');
      return;
    }
    const r = await fetch(`${API_BASE_URL}/api/threads/${threadId}/vote?action=${action}`, {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${token}` },
    });
    if (r.ok) {
      const data = await r.json();
      setThread(prev => prev ? { ...prev, like_count: data.like_count, dislike_count: data.dislike_count } : prev);
      setUserVote(data.user_vote);
    }
  };

  const timeAgo = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const seconds = Math.floor((now.getTime() - date.getTime()) / 1000);
    if (seconds < 60) return 'Just now';
    if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`;
    if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ago`;
    if (seconds < 604800) return `${Math.floor(seconds / 86400)}d ago`;
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-stone-50">
        <Header />
        <div className="container mx-auto px-6 py-12 max-w-3xl">
          <div className="animate-pulse space-y-4">
            <div className="h-6 bg-stone-200 rounded w-24"></div>
            <div className="h-8 bg-stone-200 rounded w-2/3"></div>
            <div className="h-40 bg-stone-200 rounded-2xl"></div>
          </div>
        </div>
      </div>
    );
  }

  if (!thread) {
    return (
      <div className="min-h-screen bg-stone-50">
        <Header />
        <div className="container mx-auto px-6 py-16 text-center">
          <div className="text-5xl mb-4">🔍</div>
          <h2 className="text-xl font-bold text-stone-900 mb-2">Thread not found</h2>
          <p className="text-stone-500 mb-6">This thread may have been deleted or moved.</p>
          <button onClick={() => router.push(`/events/${eventId}`)} className="bg-stone-900 text-white px-6 py-2.5 rounded-full font-medium hover:bg-stone-800 transition-colors">
            ← Back to Event
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-stone-50">
      <Header />

      {/* Sticky top bar with back button */}
      <div className="sticky top-0 z-30 bg-white/80 backdrop-blur-md border-b border-stone-200">
        <div className="container mx-auto px-6 max-w-3xl">
          <div className="flex items-center justify-between py-3">
            <button
              onClick={() => {
                const targetId = eventId || thread.event_id;
                if (targetId) router.push(`/events/${targetId}`);
                else router.back();
              }}
              className="inline-flex items-center space-x-2 text-stone-600 hover:text-stone-900 group"
            >
              <svg className="w-4 h-4 group-hover:-translate-x-0.5 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
              <span className="font-medium text-sm">Back to Event</span>
            </button>
            <div className="flex items-center space-x-3 text-xs text-stone-500">
              <span className="flex items-center space-x-1">
                <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" /><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" /></svg>
                <span>{thread.view_count}</span>
              </span>
              <span className="flex items-center space-x-1">
                <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" /></svg>
                <span>{thread.reply_count} replies</span>
              </span>
            </div>
          </div>
        </div>
      </div>

      <main className="container mx-auto px-6 py-6">
        <div className="max-w-3xl mx-auto">

          {/* Thread Card */}
          <div className="bg-white rounded-2xl border border-stone-200 overflow-hidden mb-6">
            {/* Thread Header */}
            <div className="p-6 pb-0">
              <h1 className="text-xl font-bold text-stone-900 mb-4 leading-snug">{thread.title}</h1>

              {/* Author info */}
              <div className="flex items-center space-x-3 mb-4">
                <div className={`w-9 h-9 rounded-full ${avatarColors[thread.avatar_color] || 'bg-gray-500'} flex items-center justify-center text-white font-bold text-sm flex-shrink-0`}>
                  {thread.persona_name.charAt(0).toUpperCase()}
                </div>
                <div className="flex flex-col">
                  <div className="flex items-center space-x-2">
                    <span className="font-semibold text-stone-900 text-sm">{thread.persona_name}</span>
                    {thread.is_verified && (
                      <span className="inline-flex items-center px-1.5 py-0.5 rounded-full text-[10px] font-medium bg-blue-100 text-blue-700">
                        ✓ Verified
                      </span>
                    )}
                    {thread.is_locked && (
                      <span className="inline-flex items-center px-1.5 py-0.5 rounded-full text-[10px] font-medium bg-red-100 text-red-600">
                        🔒 Locked
                      </span>
                    )}
                  </div>
                  <span className="text-xs text-stone-500">{timeAgo(thread.created_at)}</span>
                </div>
              </div>
            </div>

            {/* Thread Content */}
            <div className="px-6 pb-4">
              <div className="text-stone-800 leading-relaxed whitespace-pre-wrap text-[15px]">
                {thread.content}
              </div>
            </div>

            {/* Tags */}
            {thread.tags?.length > 0 && (
              <div className="px-6 pb-4 flex flex-wrap gap-2">
                {thread.tags.map((tag, i) => (
                  <span key={i} className="text-xs bg-stone-100 text-stone-600 px-2.5 py-1 rounded-full">#{tag}</span>
                ))}
              </div>
            )}

            {/* Action bar */}
            <div className="flex items-center space-x-1 px-6 py-3 border-t border-stone-100 bg-stone-50/50">
              <button
                onClick={() => handleVote('like')}
                className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-full text-sm transition-all ${
                  userVote === 'like'
                    ? 'bg-blue-100 text-blue-700 font-semibold'
                    : 'text-stone-600 hover:bg-stone-100'
                }`}
              >
                <svg className="w-4 h-4" fill={userVote === 'like' ? 'currentColor' : 'none'} stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 15l7-7 7 7" />
                </svg>
                <span>{thread.like_count}</span>
              </button>

              <button
                onClick={() => handleVote('dislike')}
                className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-full text-sm transition-all ${
                  userVote === 'dislike'
                    ? 'bg-red-100 text-red-700 font-semibold'
                    : 'text-stone-600 hover:bg-stone-100'
                }`}
              >
                <svg className="w-4 h-4" fill={userVote === 'dislike' ? 'currentColor' : 'none'} stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                </svg>
                <span>{thread.dislike_count || 0}</span>
              </button>

              <div className="flex-1"></div>

              <button
                onClick={() => commentSectionRef.current?.scrollIntoView({ behavior: 'smooth' })}
                className="flex items-center space-x-1.5 px-3 py-1.5 rounded-full text-sm text-stone-600 hover:bg-stone-100 transition-all"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                </svg>
                <span>{thread.reply_count} Replies</span>
              </button>
            </div>
          </div>

          {/* Comments Section */}
          <div ref={commentSectionRef}>
            <CommentSection eventId={eventId} threadId={threadId} />
          </div>
        </div>
      </main>

      {/* Floating back-to-top + back-to-event buttons */}
      {showBackToTop && (
        <div className="fixed bottom-6 right-6 flex flex-col space-y-2 z-40">
          <button
            onClick={() => {
              const targetId = eventId || thread.event_id;
              if (targetId) router.push(`/events/${targetId}`);
            }}
            className="w-12 h-12 bg-stone-900 text-white rounded-full shadow-lg hover:bg-stone-800 transition-all flex items-center justify-center"
            title="Back to Event"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
          </button>
          <button
            onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })}
            className="w-12 h-12 bg-white text-stone-700 rounded-full shadow-lg border border-stone-200 hover:bg-stone-50 transition-all flex items-center justify-center"
            title="Back to Top"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 15l7-7 7 7" />
            </svg>
          </button>
        </div>
      )}
    </div>
  );
}
