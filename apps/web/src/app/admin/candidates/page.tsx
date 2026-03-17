'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface CandidateEvent {
  id: string;
  title: string;
  summary: string;
  category: string;
  status: string;
  source_count: number;
  trending_origin_id: number | null;
  background: string | null;
  created_at: string;
}

interface TrendingEvent {
  id: number;
  title: string;
  summary: string;
  category: string;
  article_count: number;
  hot_score: number;
  status: string;
  keywords: string[];
  created_at: string;
}

export default function CandidateReviewPage() {
  const router = useRouter();
  const [candidates, setCandidates] = useState<CandidateEvent[]>([]);
  const [trendingEvents, setTrendingEvents] = useState<TrendingEvent[]>([]);
  const [activeTab, setActiveTab] = useState<'candidates' | 'trending'>('candidates');
  const [isLoading, setIsLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState<string | null>(null);
  const [error, setError] = useState('');

  const getAuthHeaders = (): HeadersInit => {
    const headers: Record<string, string> = { 'Content-Type': 'application/json' };
    const storedAuth = localStorage.getItem('admin_auth');
    if (storedAuth) {
      const { username, password } = JSON.parse(storedAuth);
      headers['Authorization'] = 'Basic ' + btoa(`${username}:${password}`);
    }
    return headers;
  };

  useEffect(() => {
    const storedAuth = localStorage.getItem('admin_auth');
    if (!storedAuth) {
      router.push('/admin');
      return;
    }
    fetchData();
  }, []);

  const fetchData = async () => {
    setIsLoading(true);
    try {
      const [candidatesRes, trendingRes] = await Promise.all([
        fetch(`${API_BASE_URL}/api/admin/candidates`, { headers: getAuthHeaders() }),
        fetch(`${API_BASE_URL}/api/trending?page_size=50`, { headers: getAuthHeaders() }),
      ]);

      if (candidatesRes.ok) {
        const data = await candidatesRes.json();
        setCandidates(data.items || []);
      }
      if (trendingRes.ok) {
        const data = await trendingRes.json();
        // Only show raw (unprocessed) trending events
        const items = (data.items || data.events || []).filter((t: TrendingEvent) => t.status === 'raw');
        setTrendingEvents(items);
      }
    } catch (err) {
      setError('Failed to load data');
    } finally {
      setIsLoading(false);
    }
  };

  const handlePublish = async (eventId: string) => {
    if (!confirm('Publish this event? It will become visible to all users.')) return;
    setActionLoading(eventId);
    try {
      const res = await fetch(`${API_BASE_URL}/api/admin/events/${eventId}/publish`, {
        method: 'POST',
        headers: getAuthHeaders(),
      });
      if (res.ok) {
        setCandidates(prev => prev.filter(c => c.id !== eventId));
      } else {
        const data = await res.json();
        alert(data.detail || 'Failed to publish');
      }
    } catch {
      alert('Network error');
    } finally {
      setActionLoading(null);
    }
  };

  const handleReject = async (eventId: string) => {
    if (!confirm('Reject this candidate? It will be closed.')) return;
    setActionLoading(eventId);
    try {
      const res = await fetch(`${API_BASE_URL}/api/admin/events/${eventId}/reject`, {
        method: 'POST',
        headers: getAuthHeaders(),
      });
      if (res.ok) {
        setCandidates(prev => prev.filter(c => c.id !== eventId));
      } else {
        const data = await res.json();
        alert(data.detail || 'Failed to reject');
      }
    } catch {
      alert('Network error');
    } finally {
      setActionLoading(null);
    }
  };

  const handleGenerateAnalysis = async (eventId: string) => {
    setActionLoading(`analysis-${eventId}`);
    try {
      const res = await fetch(`${API_BASE_URL}/api/admin/events/${eventId}/generate-analysis`, {
        method: 'POST',
        headers: getAuthHeaders(),
      });
      if (res.ok) {
        const data = await res.json();
        alert(`Analysis generated! Quality: ${data.quality_score || 'N/A'}`);
        fetchData();
      } else {
        const data = await res.json();
        alert(data.detail || 'Failed to generate analysis');
      }
    } catch {
      alert('Network error');
    } finally {
      setActionLoading(null);
    }
  };

  const handlePromote = async (trendingId: number) => {
    if (!confirm('Promote this trending event to a candidate?')) return;
    setActionLoading(`promote-${trendingId}`);
    try {
      const res = await fetch(`${API_BASE_URL}/api/admin/trending/${trendingId}/promote`, {
        method: 'POST',
        headers: getAuthHeaders(),
      });
      if (res.ok) {
        setTrendingEvents(prev => prev.filter(t => t.id !== trendingId));
        fetchData();
        alert('Promoted to candidate!');
      } else {
        const data = await res.json();
        alert(data.detail || 'Failed to promote');
      }
    } catch {
      alert('Network error');
    } finally {
      setActionLoading(null);
    }
  };

  return (
    <div className="min-h-screen bg-stone-50">
      {/* Header */}
      <header className="bg-white border-b border-stone-200 sticky top-0 z-50">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-xl font-bold text-stone-900">Candidate Review</h1>
              <p className="text-xs text-stone-500">Review, publish, or reject candidate events</p>
            </div>
            <div className="flex items-center space-x-4">
              <button
                onClick={() => router.push('/admin')}
                className="text-stone-600 hover:text-stone-900 text-sm font-medium"
              >
                ← Dashboard
              </button>
            </div>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-6 py-8">
        {/* Tabs */}
        <div className="flex space-x-1 mb-8 bg-stone-200 rounded-lg p-1 max-w-md">
          <button
            onClick={() => setActiveTab('candidates')}
            className={`flex-1 px-4 py-2 rounded-md text-sm font-medium transition-colors ${
              activeTab === 'candidates'
                ? 'bg-white text-stone-900 shadow-sm'
                : 'text-stone-600 hover:text-stone-900'
            }`}
          >
            📋 Candidates ({candidates.length})
          </button>
          <button
            onClick={() => setActiveTab('trending')}
            className={`flex-1 px-4 py-2 rounded-md text-sm font-medium transition-colors ${
              activeTab === 'trending'
                ? 'bg-white text-stone-900 shadow-sm'
                : 'text-stone-600 hover:text-stone-900'
            }`}
          >
            🔥 Trending ({trendingEvents.length})
          </button>
        </div>

        {error && (
          <div className="bg-red-50 border border-red-200 text-red-800 px-4 py-3 rounded-lg mb-6">
            {error}
          </div>
        )}

        {isLoading ? (
          <div className="text-center py-20 text-stone-500">Loading...</div>
        ) : activeTab === 'candidates' ? (
          /* Candidates Tab */
          <div className="space-y-4">
            {candidates.length === 0 ? (
              <div className="text-center py-20 bg-white rounded-xl border border-stone-200">
                <p className="text-stone-500 text-lg mb-2">No candidates awaiting review</p>
                <p className="text-stone-400 text-sm">Promote trending events or create events manually</p>
              </div>
            ) : (
              candidates.map((event) => (
                <div key={event.id} className="bg-white rounded-xl border border-stone-200 p-6">
                  <div className="flex items-start justify-between">
                    <div className="flex-1 min-w-0 mr-6">
                      <div className="flex items-center space-x-3 mb-2">
                        <span className="inline-block px-2.5 py-1 rounded-full text-xs font-medium bg-amber-100 text-amber-700">
                          Candidate
                        </span>
                        {event.category && (
                          <span className="inline-block px-2.5 py-1 rounded-full text-xs font-medium bg-stone-100 text-stone-600">
                            {event.category}
                          </span>
                        )}
                        {event.trending_origin_id && (
                          <span className="inline-block px-2.5 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-700">
                            From Trending #{event.trending_origin_id}
                          </span>
                        )}
                      </div>

                      <h3 className="text-lg font-semibold text-stone-900 mb-2">{event.title}</h3>

                      {event.summary && (
                        <p className="text-stone-600 text-sm leading-relaxed mb-3 line-clamp-3">
                          {event.summary}
                        </p>
                      )}

                      {event.background && (
                        <div className="bg-stone-50 rounded-lg p-3 mb-3">
                          <p className="text-xs font-medium text-stone-500 mb-1">AI Background</p>
                          <p className="text-stone-600 text-sm line-clamp-2">{event.background}</p>
                        </div>
                      )}

                      <div className="flex items-center space-x-4 text-xs text-stone-500">
                        <span>{event.source_count || 0} sources</span>
                        <span>Created {new Date(event.created_at).toLocaleDateString()}</span>
                      </div>
                    </div>

                    <div className="flex flex-col space-y-2 flex-shrink-0">
                      <button
                        onClick={() => handlePublish(event.id)}
                        disabled={actionLoading === event.id}
                        className="px-4 py-2 bg-emerald-600 text-white rounded-lg text-sm font-medium hover:bg-emerald-700 transition-colors disabled:opacity-50"
                      >
                        ✅ Publish
                      </button>
                      <button
                        onClick={() => handleGenerateAnalysis(event.id)}
                        disabled={actionLoading === `analysis-${event.id}`}
                        className="px-4 py-2 bg-amber-500 text-white rounded-lg text-sm font-medium hover:bg-amber-600 transition-colors disabled:opacity-50"
                      >
                        🤖 Generate AI
                      </button>
                      <button
                        onClick={() => router.push(`/events/${event.id}`)}
                        className="px-4 py-2 bg-stone-100 text-stone-700 rounded-lg text-sm font-medium hover:bg-stone-200 transition-colors"
                      >
                        👁 Preview
                      </button>
                      <button
                        onClick={() => handleReject(event.id)}
                        disabled={actionLoading === event.id}
                        className="px-4 py-2 bg-red-50 text-red-600 rounded-lg text-sm font-medium hover:bg-red-100 transition-colors disabled:opacity-50"
                      >
                        ✕ Reject
                      </button>
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        ) : (
          /* Trending Tab */
          <div className="space-y-4">
            {trendingEvents.length === 0 ? (
              <div className="text-center py-20 bg-white rounded-xl border border-stone-200">
                <p className="text-stone-500 text-lg mb-2">No pending trending events</p>
                <p className="text-stone-400 text-sm">Run the trending pipeline to discover new events</p>
              </div>
            ) : (
              trendingEvents.map((trending) => (
                <div key={trending.id} className="bg-white rounded-xl border border-stone-200 p-6">
                  <div className="flex items-start justify-between">
                    <div className="flex-1 min-w-0 mr-6">
                      <div className="flex items-center space-x-3 mb-2">
                        <span className="inline-block px-2.5 py-1 rounded-full text-xs font-medium bg-orange-100 text-orange-700">
                          🔥 {trending.hot_score?.toFixed(1) || '0'}°
                        </span>
                        {trending.category && (
                          <span className="inline-block px-2.5 py-1 rounded-full text-xs font-medium bg-stone-100 text-stone-600">
                            {trending.category}
                          </span>
                        )}
                        <span className="text-xs text-stone-400">
                          {trending.article_count} articles
                        </span>
                      </div>

                      <h3 className="text-lg font-semibold text-stone-900 mb-2">{trending.title}</h3>

                      {trending.summary && (
                        <p className="text-stone-600 text-sm leading-relaxed mb-3 line-clamp-3">
                          {trending.summary}
                        </p>
                      )}

                      {trending.keywords && trending.keywords.length > 0 && (
                        <div className="flex flex-wrap gap-1.5 mb-3">
                          {trending.keywords.slice(0, 8).map((kw, i) => (
                            <span key={i} className="px-2 py-0.5 bg-stone-100 text-stone-600 rounded text-xs">
                              {kw}
                            </span>
                          ))}
                        </div>
                      )}

                      <div className="text-xs text-stone-500">
                        Discovered {new Date(trending.created_at).toLocaleDateString()}
                      </div>
                    </div>

                    <div className="flex flex-col space-y-2 flex-shrink-0">
                      <button
                        onClick={() => handlePromote(trending.id)}
                        disabled={actionLoading === `promote-${trending.id}`}
                        className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700 transition-colors disabled:opacity-50"
                      >
                        ⬆ Promote
                      </button>
                      <button
                        onClick={() => router.push(`/trending/${trending.id}`)}
                        className="px-4 py-2 bg-stone-100 text-stone-700 rounded-lg text-sm font-medium hover:bg-stone-200 transition-colors"
                      >
                        👁 View
                      </button>
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        )}
      </main>
    </div>
  );
}
