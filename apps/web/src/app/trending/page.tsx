'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import Header from '../../components/Header';
import { API_BASE_URL } from '../../lib/config';


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
  event_id?: string;
  published_event_id?: string;
}

const CATEGORIES = ['All', 'Politics', 'Economy', 'Technology', 'War & Conflict', 'Environment'];

const getCatClass = (cat?: string): string => {
  const map: Record<string, string> = {
    'Environment': 'cat-environment',
    'Economy': 'cat-economy',
    'Technology': 'cat-technology',
    'Politics': 'cat-politics',
    'War & Conflict': 'cat-conflict',
    'Entertainment': 'cat-entertainment',
    'Geopolitics': 'cat-geopolitics',
    'Health': 'cat-health',
    'Science': 'cat-science',
    'Society': 'cat-society',
  };
  return (cat && map[cat]) || 'bg-neutral-100 text-neutral-700';
};

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
  const [lastRefresh, setLastRefresh] = useState<Date | null>(null);
  const [mounted, setMounted] = useState(false);

  useEffect(() => { setMounted(true); }, []);

  const fetchTrending = useCallback(async () => {
    try {
      setIsLoading(true);
      setError(null);

      const params = new URLSearchParams({ limit: '10', published_only: 'true' });
      if (selectedCategory !== 'All') {
        params.append('category', selectedCategory.toLowerCase());
      }

      const response = await fetch(`${API_BASE_URL}/api/trending?${params}`);
      if (!response.ok) throw new Error(`HTTP ${response.status}`);

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

  useEffect(() => { fetchTrending(); }, [fetchTrending]);

  // Auto-refresh every 5 minutes
  useEffect(() => {
    const interval = setInterval(fetchTrending, 5 * 60 * 1000);
    return () => clearInterval(interval);
  }, [fetchTrending]);

  const getEventLink = (t: TrendingEvent) => t.published_event_id || t.event_id;

  return (
    <div className="min-h-screen bg-neutral-50">
      <Header />

      <main className="container mx-auto px-6 py-8">
        {/* Page Header */}
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="font-serif text-headline text-neutral-900">Trending</h1>
            <p className="text-sm text-neutral-500 mt-1">
              Top stories people are following worldwide
            </p>
          </div>
          <div className="flex items-center gap-3">
            <span className="text-xs text-neutral-400" suppressHydrationWarning>
              {mounted && lastRefresh ? `Updated ${lastRefresh.toLocaleTimeString()}` : ''}
            </span>
            <button
              onClick={fetchTrending}
              disabled={isLoading}
              className="flex items-center gap-1.5 px-3 py-1.5 border border-neutral-300 rounded-md text-sm text-neutral-600 hover:bg-neutral-100 transition-colors disabled:opacity-50"
            >
              <svg className={`w-3.5 h-3.5 ${isLoading ? 'animate-spin' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
              Refresh
            </button>
          </div>
        </div>

        <hr className="rule-thick mb-6" />

        {/* Category Tabs */}
        <div className="flex gap-1 mb-8 overflow-x-auto pb-2">
          {CATEGORIES.map(cat => (
            <button
              key={cat}
              onClick={() => setSelectedCategory(cat)}
              className={`px-3 py-1.5 rounded-md text-sm whitespace-nowrap transition-colors ${
                selectedCategory === cat
                  ? 'bg-neutral-900 text-white'
                  : 'text-neutral-500 hover:bg-neutral-200'
              }`}
            >
              {cat}
            </button>
          ))}
        </div>

        {/* Error State */}
        {error && (
          <div className="border border-amber-300 bg-amber-50 rounded-lg p-4 mb-6 text-sm text-amber-800">
            <p>{error}</p>
          </div>
        )}

        {/* Loading State */}
        {isLoading ? (
          <div className="space-y-4">
            {[1,2,3].map(i => (
              <div key={i} className="animate-pulse h-24 bg-neutral-200 rounded-lg" />
            ))}
          </div>
        ) : events.length === 0 ? (
          <div className="text-center py-20 border border-neutral-200 rounded-lg bg-white">
            <h3 className="text-lg font-serif text-neutral-900 mb-2">No trending stories right now</h3>
            <p className="text-sm text-neutral-500 mb-6">Check back later for breaking stories</p>
            <button
              onClick={fetchTrending}
              className="px-4 py-2 bg-neutral-900 text-white rounded-md text-sm hover:bg-neutral-800 transition-colors"
            >
              Check Again
            </button>
          </div>
        ) : (
          <div className="space-y-0 divide-y divide-neutral-200">
            {/* #1 — Featured lead story */}
            {events[0] && (() => {
              const t = events[0];
              const link = getEventLink(t);
              return (
                <article
                  onClick={() => link ? router.push(`/events/${link}`) : router.push(`/trending/${t.id}`)}
                  className="group pb-8 cursor-pointer"
                >
                  <div className="flex items-start gap-6">
                    <span className="text-4xl font-serif font-bold text-accent-light flex-shrink-0 leading-none pt-1">1</span>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-3 mb-2">
                        <span className={`text-xs px-2 py-0.5 rounded-md font-medium ${getCatClass(t.category)}`}>
                          {t.category}
                        </span>
                        {mounted && t.last_updated && (
                          <span className="text-xs text-neutral-400" suppressHydrationWarning>{formatTimeAgo(t.last_updated)}</span>
                        )}
                      </div>
                      <h2 className="font-serif text-2xl md:text-3xl font-bold text-neutral-900 mb-3 leading-tight group-hover:text-accent transition-colors">
                        {t.title}
                      </h2>
                      {t.summary && (
                        <p className="text-neutral-600 leading-relaxed mb-4 line-clamp-2">
                          {t.summary}
                        </p>
                      )}
                      <div className="flex items-center gap-4 text-xs text-neutral-400">
                        <span>{t.article_count} articles</span>
                        <span>{t.heat_score.toFixed(0)} heat</span>
                        <span>{t.sources?.length || t.media_count} sources</span>
                      </div>
                    </div>
                  </div>
                </article>
              );
            })()}

            {/* Remaining stories — clean list */}
            {events.slice(1).map((t) => {
              const link = getEventLink(t);
              return (
                <article
                  key={t.id}
                  onClick={() => link ? router.push(`/events/${link}`) : router.push(`/trending/${t.id}`)}
                  className="group flex items-start gap-4 py-5 cursor-pointer"
                >
                  <span className={`text-xl font-serif font-bold flex-shrink-0 w-8 text-right leading-none pt-0.5 ${
                    t.rank <= 3 ? 'text-accent-light' : 'text-neutral-300'
                  }`}>
                    {t.rank}
                  </span>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <span className={`text-xs px-2 py-0.5 rounded-md font-medium ${getCatClass(t.category)}`}>
                        {t.category}
                      </span>
                      {mounted && t.last_updated && (
                        <span className="text-xs text-neutral-400" suppressHydrationWarning>{formatTimeAgo(t.last_updated)}</span>
                      )}
                    </div>
                    <h3 className="font-semibold text-neutral-900 group-hover:text-accent transition-colors leading-snug mb-1">
                      {t.title}
                    </h3>
                    <div className="flex items-center gap-3 text-xs text-neutral-400">
                      <span>{t.article_count} articles</span>
                      <span>{t.heat_score.toFixed(0)} heat</span>
                    </div>
                  </div>
                </article>
              );
            })}
          </div>
        )}
      </main>
    </div>
  );
}
