'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import Header from '../../components/Header';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface TrendingEvent {
  rank: number;
  id: number;
  title: string;
  summary?: string;
  keywords: string[];
  category?: string;
  heat_score: number;
  article_count: number;
  media_count: number;
  sources: string[];
  created_at?: string;
  last_updated?: string;
}

const CATEGORIES = ['All', 'Politics', 'Economy', 'Technology', 'War & Conflict', 'Environment'];

const categoryColors: Record<string, string> = {
  politics: 'bg-amber-100 text-amber-800',
  economy: 'bg-blue-100 text-blue-800',
  technology: 'bg-violet-100 text-violet-800',
  environment: 'bg-emerald-100 text-emerald-800',
  'war & conflict': 'bg-red-100 text-red-800',
};

function getCategoryColor(category?: string): string {
  if (!category) return 'bg-stone-100 text-stone-600';
  return categoryColors[category.toLowerCase()] || 'bg-stone-100 text-stone-600';
}

function getHeatColor(score: number): string {
  if (score >= 80) return 'bg-red-500';
  if (score >= 50) return 'bg-orange-500';
  if (score >= 20) return 'bg-amber-500';
  return 'bg-stone-400';
}

function formatTimeAgo(dateStr?: string): string {
  if (!dateStr) return '';
  const date = new Date(dateStr);
  if (isNaN(date.getTime())) return '';
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffMins = Math.floor(diffMs / 60000);
  if (diffMins < 60) return `${diffMins}m ago`;
  const diffHours = Math.floor(diffMins / 60);
  if (diffHours < 24) return `${diffHours}h ago`;
  const diffDays = Math.floor(diffHours / 24);
  return `${diffDays}d ago`;
}

export default function TrendingPage() {
  const router = useRouter();
  const [events, setEvents] = useState<TrendingEvent[]>([]);
  const [selectedCategory, setSelectedCategory] = useState('All');
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastRefresh, setLastRefresh] = useState<Date>(new Date());

  const fetchTrending = useCallback(async () => {
    try {
      setIsLoading(true);
      setError(null);

      const params = new URLSearchParams({ limit: '20' });
      if (selectedCategory !== 'All') {
        params.append('category', selectedCategory.toLowerCase());
      }

      const response = await fetch(`${API_BASE_URL}/api/trending?${params}`);
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const data = await response.json();
      setEvents(data.events || []);
      setLastRefresh(new Date());
    } catch (err) {
      console.error('Failed to fetch trending:', err);
      setError('Unable to load trending data. Make sure the backend is running.');
      setEvents([]);
    } finally {
      setIsLoading(false);
    }
  }, [selectedCategory]);

  useEffect(() => {
    fetchTrending();
  }, [fetchTrending]);

  // Auto-refresh every 5 minutes
  useEffect(() => {
    const interval = setInterval(fetchTrending, 5 * 60 * 1000);
    return () => clearInterval(interval);
  }, [fetchTrending]);

  const maxHeatScore = events.length > 0 ? Math.max(...events.map(e => e.heat_score)) : 100;

  return (
    <div className="min-h-screen bg-stone-50">
      <Header />

      <main className="container mx-auto px-6 py-8">
        {/* Page Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold text-stone-900 flex items-center gap-3">
              <span className="text-3xl">🔥</span>
              Trending Now
            </h1>
            <p className="text-stone-500 mt-1">
              Top stories from {events.length > 0 ? events[0].sources?.length || 0 : 0}+ sources, updated in real-time
            </p>
          </div>
          <div className="flex items-center gap-3">
            <span className="text-xs text-stone-400">
              Last updated: {lastRefresh.toLocaleTimeString()}
            </span>
            <button
              onClick={fetchTrending}
              disabled={isLoading}
              className="flex items-center gap-2 px-4 py-2 bg-white border border-stone-200 rounded-lg text-sm text-stone-700 hover:bg-stone-50 transition-colors disabled:opacity-50"
            >
              <svg className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
              Refresh
            </button>
          </div>
        </div>

        {/* Category Tabs */}
        <div className="flex gap-2 mb-8 overflow-x-auto pb-2">
          {CATEGORIES.map(cat => (
            <button
              key={cat}
              onClick={() => setSelectedCategory(cat)}
              className={`px-4 py-2 rounded-full text-sm font-medium whitespace-nowrap transition-all ${
                selectedCategory === cat
                  ? 'bg-stone-900 text-white shadow-lg'
                  : 'bg-white text-stone-600 hover:bg-stone-100 border border-stone-200'
              }`}
            >
              {cat}
            </button>
          ))}
        </div>

        {/* Error State */}
        {error && (
          <div className="bg-amber-50 border border-amber-200 rounded-lg p-4 mb-6 text-amber-800">
            <p>{error}</p>
            <p className="text-sm mt-1">Backend URL: {API_BASE_URL}</p>
          </div>
        )}

        {/* Loading State */}
        {isLoading ? (
          <div className="space-y-4">
            {[...Array(5)].map((_, i) => (
              <div key={i} className="animate-pulse bg-white rounded-xl p-6 border border-stone-200">
                <div className="flex items-center gap-4">
                  <div className="w-10 h-10 bg-stone-200 rounded-lg"></div>
                  <div className="flex-1">
                    <div className="h-5 bg-stone-200 rounded w-3/4 mb-2"></div>
                    <div className="h-3 bg-stone-100 rounded w-1/2"></div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : events.length === 0 ? (
          /* Empty State */
          <div className="text-center py-20">
            <div className="text-6xl mb-4">📭</div>
            <h3 className="text-xl font-semibold text-stone-700 mb-2">No trending events yet</h3>
            <p className="text-stone-500 mb-6">
              The system is still collecting data from news sources.
            </p>
            <button
              onClick={fetchTrending}
              className="px-6 py-3 bg-stone-900 text-white rounded-lg hover:bg-stone-800 transition-colors"
            >
              Check Again
            </button>
          </div>
        ) : (
          /* Trending List */
          <div className="space-y-3">
            {events.map((event) => (
              <article
                key={event.id}
                onClick={() => router.push(`/trending/${event.id}`)}
                className="group bg-white rounded-xl border border-stone-200 hover:border-stone-300 hover:shadow-lg transition-all duration-200 cursor-pointer overflow-hidden"
              >
                <div className="flex items-stretch">
                  {/* Rank */}
                  <div className="flex items-center justify-center w-16 shrink-0 bg-stone-50 border-r border-stone-100">
                    <span className={`text-2xl font-bold ${
                      event.rank <= 3 ? 'text-orange-500' : 'text-stone-400'
                    }`}>
                      {event.rank}
                    </span>
                  </div>

                  {/* Content */}
                  <div className="flex-1 p-5">
                    <div className="flex items-start justify-between gap-4">
                      <div className="flex-1 min-w-0">
                        <h3 className="text-lg font-semibold text-stone-900 group-hover:text-stone-700 transition-colors line-clamp-2">
                          {event.title}
                        </h3>

                        {event.summary && (
                          <p className="text-sm text-stone-500 mt-1 line-clamp-1">
                            {event.summary}
                          </p>
                        )}

                        <div className="flex items-center gap-3 mt-3 flex-wrap">
                          {event.category && (
                            <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${getCategoryColor(event.category)}`}>
                              {event.category}
                            </span>
                          )}

                          <span className="text-xs text-stone-400">
                            {event.article_count} articles
                          </span>
                          <span className="text-xs text-stone-400">
                            {event.sources?.length || event.media_count} sources
                          </span>

                          {event.keywords?.slice(0, 3).map(kw => (
                            <span key={kw} className="text-xs text-stone-400 bg-stone-50 px-2 py-0.5 rounded">
                              {kw}
                            </span>
                          ))}

                          <span className="text-xs text-stone-400">
                            {formatTimeAgo(event.created_at)}
                          </span>
                        </div>
                      </div>

                      {/* Heat Score Bar */}
                      <div className="flex flex-col items-end gap-1 shrink-0">
                        <span className="text-sm font-bold text-stone-700">
                          {event.heat_score.toFixed(1)}
                        </span>
                        <div className="w-24 h-2 bg-stone-100 rounded-full overflow-hidden">
                          <div
                            className={`h-full rounded-full transition-all duration-500 ${getHeatColor(
                              (event.heat_score / maxHeatScore) * 100
                            )}`}
                            style={{ width: `${Math.min((event.heat_score / maxHeatScore) * 100, 100)}%` }}
                          />
                        </div>
                        <span className="text-[10px] text-stone-400">heat</span>
                      </div>
                    </div>
                  </div>
                </div>
              </article>
            ))}
          </div>
        )}
      </main>
    </div>
  );
}
