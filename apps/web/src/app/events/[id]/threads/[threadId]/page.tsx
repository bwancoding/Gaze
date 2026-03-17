'use client';

import React, { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Header from '../../../../../components/Header';
import CommentSection from '../../../../../components/CommentSection';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface ThreadDetail {
  id: string;
  event_id: string;
  title: string;
  content: string;
  persona_name: string;
  avatar_color: string;
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

export default function ThreadDetailPage() {
  const params = useParams();
  const router = useRouter();
  const eventId = params.id as string;
  const threadId = params.threadId as string;

  const [thread, setThread] = useState<ThreadDetail | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [userVote, setUserVote] = useState<VoteType>(null);

  useEffect(() => {
    if (threadId) {
      fetch(`${API_BASE_URL}/api/threads/${threadId}`)
        .then(r => r.ok ? r.json() : Promise.reject('Not found'))
        .then(data => { setThread(data); setIsLoading(false); })
        .catch(() => setIsLoading(false));
    }
  }, [threadId]);

  const handleVote = async (action: 'like' | 'dislike') => {
    const token = localStorage.getItem('access_token');
    if (!token) {
      router.push('/login');
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

  if (isLoading) {
    return (
      <div className="min-h-screen bg-stone-50">
        <Header />
        <div className="container mx-auto px-6 py-12">
          <div className="animate-pulse space-y-4">
            <div className="h-8 bg-stone-200 rounded w-1/3"></div>
            <div className="h-32 bg-stone-200 rounded-2xl"></div>
          </div>
        </div>
      </div>
    );
  }

  if (!thread) {
    return (
      <div className="min-h-screen bg-stone-50">
        <Header />
        <div className="container mx-auto px-6 py-12 text-center">
          <h2 className="text-xl font-bold text-stone-900 mb-4">Thread not found</h2>
          <button onClick={() => router.push(`/events/${eventId}`)} className="bg-stone-900 text-white px-6 py-2 rounded-full">
            Back to Event
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-stone-50">
      <Header />
      <main className="container mx-auto px-6 py-8">
        <div className="max-w-3xl mx-auto">
          {/* Back to Event */}
          <button
            onClick={() => {
              const targetId = eventId || thread.event_id;
              if (targetId) router.push(`/events/${targetId}`);
              else router.back();
            }}
            className="inline-flex items-center space-x-2 text-stone-600 hover:text-stone-900 mb-6 group"
          >
            <svg className="w-5 h-5 group-hover:-translate-x-0.5 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
            </svg>
            <span className="font-medium">Back to Event</span>
          </button>

          {/* Thread */}
          <div className="bg-white rounded-2xl border border-stone-200 p-8 mb-8">
            <h1 className="text-2xl font-bold text-stone-900 mb-4">{thread.title}</h1>

            <div className="flex items-center space-x-4 text-sm text-stone-500 mb-6">
              <span className="flex items-center space-x-1">
                <span className={`w-2 h-2 rounded-full bg-${thread.avatar_color}-400`}></span>
                <span className="font-medium text-stone-700">{thread.persona_name}</span>
              </span>
              <span>{new Date(thread.created_at).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}</span>
              <span>{thread.view_count} views</span>
            </div>

            <div className="prose prose-stone max-w-none mb-6">
              <p className="text-stone-800 leading-relaxed whitespace-pre-wrap">{thread.content}</p>
            </div>

            {thread.tags?.length > 0 && (
              <div className="flex flex-wrap gap-2 mb-4">
                {thread.tags.map((tag, i) => (
                  <span key={i} className="text-xs bg-stone-100 text-stone-600 px-3 py-1 rounded-full">{tag}</span>
                ))}
              </div>
            )}

            <div className="flex items-center space-x-4 pt-4 border-t border-stone-200">
              {/* Like button */}
              <button
                onClick={() => handleVote('like')}
                className={`flex items-center space-x-1 px-3 py-1.5 rounded-lg text-sm transition-colors ${
                  userVote === 'like'
                    ? 'bg-blue-100 text-blue-700 font-semibold'
                    : 'text-stone-600 hover:bg-stone-100'
                }`}
              >
                <svg className="w-4 h-4" fill={userVote === 'like' ? 'currentColor' : 'none'} stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14 10h4.764a2 2 0 011.789 2.894l-3.5 7A2 2 0 0115.263 21h-4.017c-.163 0-.326-.02-.485-.06L7 20m7-10V5a2 2 0 00-2-2h-.095c-.5 0-.905.405-.905.905 0 .714-.211 1.412-.608 2.006L7 11v9m7-10h-2M7 20H5a2 2 0 01-2-2v-6a2 2 0 012-2h2.5" />
                </svg>
                <span>{thread.like_count}</span>
              </button>

              {/* Dislike button */}
              <button
                onClick={() => handleVote('dislike')}
                className={`flex items-center space-x-1 px-3 py-1.5 rounded-lg text-sm transition-colors ${
                  userVote === 'dislike'
                    ? 'bg-red-100 text-red-700 font-semibold'
                    : 'text-stone-600 hover:bg-stone-100'
                }`}
              >
                <svg className="w-4 h-4 transform rotate-180" fill={userVote === 'dislike' ? 'currentColor' : 'none'} stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14 10h4.764a2 2 0 011.789 2.894l-3.5 7A2 2 0 0115.263 21h-4.017c-.163 0-.326-.02-.485-.06L7 20m7-10V5a2 2 0 00-2-2h-.095c-.5 0-.905.405-.905.905 0 .714-.211 1.412-.608 2.006L7 11v9m7-10h-2M7 20H5a2 2 0 01-2-2v-6a2 2 0 012-2h2.5" />
                </svg>
                <span>{thread.dislike_count || 0}</span>
              </button>

              <span className="text-sm text-stone-500">{thread.reply_count} replies</span>
              {thread.is_locked && <span className="text-xs bg-red-100 text-red-600 px-2 py-0.5 rounded">Locked</span>}
            </div>
          </div>

          {/* Comments / Replies */}
          <div className="bg-white rounded-2xl border border-stone-200 p-8">
            <h3 className="text-lg font-bold text-stone-900 mb-4">Replies</h3>
            <CommentSection eventId={eventId} threadId={threadId} />
          </div>
        </div>
      </main>
    </div>
  );
}
