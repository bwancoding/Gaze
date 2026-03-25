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

// Category styles for gradient cards
const categoryStyles: Record<string, { gradient: string; bg: string; text: string }> = {
  'Environment': { gradient: 'from-emerald-500 to-teal-600', bg: 'bg-emerald-50', text: 'text-emerald-700' },
  'Economy': { gradient: 'from-blue-500 to-indigo-600', bg: 'bg-blue-50', text: 'text-blue-700' },
  'Technology': { gradient: 'from-violet-500 to-purple-600', bg: 'bg-violet-50', text: 'text-violet-700' },
  'Politics': { gradient: 'from-amber-500 to-orange-600', bg: 'bg-amber-50', text: 'text-amber-700' },
  'War & Conflict': { gradient: 'from-red-500 to-rose-600', bg: 'bg-red-50', text: 'text-red-700' },
  'Entertainment': { gradient: 'from-pink-500 to-fuchsia-600', bg: 'bg-pink-50', text: 'text-pink-700' },
};
const defaultStyle = { gradient: 'from-stone-500 to-gray-600', bg: 'bg-stone-50', text: 'text-stone-700' };
const getStyle = (cat?: string) => (cat && categoryStyles[cat]) || defaultStyle;

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

function getCategoryEmoji(cat?: string): string {
  if (!cat) return '📰';
  const map: Record<string, string> = {
    'Technology': '🤖', 'Environment': '🌍', 'Economy': '💰',
    'Politics': '🏛️', 'War & Conflict': '⚔️', 'Entertainment': '🎬',
    'Health': '🏥', 'Science': '🔬',
  };
  return map[cat] || '📰';
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
    <div className="min-h-screen bg-stone-900">
      <Header />

      <main className="container mx-auto px-6 py-8">
        {/* Page Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold text-stone-100 flex items-center gap-3">
              <span className="text-3xl">🔥</span>
              Trending Now
            </h1>
            <p className="text-stone-400 mt-1">
              Top stories people are following worldwide
            </p>
          </div>
          <div className="flex items-center gap-3">
            <span className="text-xs text-stone-500" suppressHydrationWarning>
              {mounted && lastRefresh ? `Updated ${lastRefresh.toLocaleTimeString()}` : ''}
            </span>
            <button
              onClick={fetchTrending}
              disabled={isLoading}
              className="flex items-center gap-2 px-4 py-2 bg-stone-800 border border-stone-700 rounded-lg text-sm text-stone-300 hover:bg-stone-700 transition-colors disabled:opacity-50"
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
                  ? 'bg-amber-500 text-stone-900 shadow-lg'
                  : 'bg-stone-800 text-stone-400 hover:bg-stone-700 border border-stone-700'
              }`}
            >
              {cat}
            </button>
          ))}
        </div>

        {/* Error State */}
        {error && (
          <div className="bg-amber-900/30 border border-amber-700 rounded-lg p-4 mb-6 text-amber-300">
            <p>{error}</p>
          </div>
        )}

        {/* Loading State */}
        {isLoading ? (
          <div className="animate-pulse space-y-6">
            <div className="bg-stone-800 rounded-3xl h-64"></div>
            <div className="grid md:grid-cols-2 gap-6">
              <div className="bg-stone-800 rounded-2xl h-48"></div>
              <div className="bg-stone-800 rounded-2xl h-48"></div>
            </div>
          </div>
        ) : events.length === 0 ? (
          <div className="text-center py-20 bg-stone-800/50 rounded-2xl border border-stone-700">
            <div className="text-6xl mb-4">📡</div>
            <h3 className="text-xl font-semibold text-stone-300 mb-2">No trending stories right now</h3>
            <p className="text-stone-500 mb-6">Check back later for breaking stories</p>
            <button
              onClick={fetchTrending}
              className="px-6 py-3 bg-amber-500 text-stone-900 rounded-lg hover:bg-amber-400 transition-colors font-medium"
            >
              Check Again
            </button>
          </div>
        ) : (
          <>
            {/* #1 — Full-width hero card with right-side image */}
            {events[0] && (() => {
              const t = events[0];
              const style = getStyle(t.category);
              const link = getEventLink(t);
              // Use picsum for reliable image loading
              const imageUrl = `https://picsum.photos/seed/${t.id}/800/600`;
              return (
                <article
                  onClick={() => link ? router.push(`/events/${link}`) : router.push(`/trending/${t.id}`)}
                  className="group relative overflow-hidden rounded-3xl text-white shadow-2xl hover:shadow-3xl transition-all duration-500 mb-6 cursor-pointer bg-stone-800"
                  style={{ minHeight: '340px' }}
                >
                  {/* Right-side image that fades out to the left into the dark background */}
                  <div className="absolute right-0 top-0 bottom-0 w-3/5 hidden md:block">
                    <img
                      src={imageUrl}
                      alt=""
                      className="w-full h-full object-cover"
                      style={{
                        maskImage: 'linear-gradient(to left, rgba(0,0,0,1) 30%, rgba(0,0,0,0.5) 60%, rgba(0,0,0,0) 100%)',
                        WebkitMaskImage: 'linear-gradient(to left, rgba(0,0,0,1) 30%, rgba(0,0,0,0.5) 60%, rgba(0,0,0,0) 100%)',
                      }}
                      onError={(e) => { (e.target as HTMLImageElement).style.display = 'none'; }}
                    />
                  </div>
                  {/* Content */}
                  <div className="relative z-10 p-8 md:p-12 md:w-2/3">
                    <div className="flex items-center space-x-3 mb-6">
                      <span className="bg-white/25 backdrop-blur-sm px-4 py-1.5 rounded-full text-sm font-bold shadow-lg">
                        #1 Trending
                      </span>
                      <span className="bg-white/15 px-3 py-1 rounded-full text-xs font-medium">{t.category}</span>
                      {mounted && t.last_updated && (
                        <span className="text-xs text-white/50" suppressHydrationWarning>{mounted ? formatTimeAgo(t.last_updated) : ''}</span>
                      )}
                    </div>
                    <h3 className="text-2xl md:text-4xl font-bold mb-4 leading-tight">
                      {t.title}
                    </h3>
                    {t.summary && (
                      <p className="text-base md:text-lg text-white/85 leading-relaxed mb-6 line-clamp-3">
                        {t.summary}
                      </p>
                    )}
                    <div className="flex flex-wrap gap-2 mb-6">
                      {t.keywords?.slice(0, 5).map((kw, i) => (
                        <span key={i} className="bg-white/15 text-white/90 text-sm px-3 py-1 rounded-full capitalize">
                          {kw}
                        </span>
                      ))}
                    </div>
                    <div className="flex items-center space-x-6 text-sm text-white/70">
                      <span className="flex items-center space-x-1.5">
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1m2 13a2 2 0 01-2-2V7m2 13a2 2 0 002-2V9a2 2 0 00-2-2h-2m-4-3H9M7 16h6M7 8h6v4H7V8z" /></svg>
                        <span>{t.article_count} articles</span>
                      </span>
                      <span className="flex items-center space-x-1.5">
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 18.657A8 8 0 016.343 7.343S7 9 9 10c0-2 .5-5 2.986-7C14 5 16.09 5.777 17.656 7.343A7.975 7.975 0 0120 13a7.975 7.975 0 01-2.343 5.657z" /></svg>
                        <span>{t.heat_score.toFixed(0)} heat</span>
                      </span>
                      <span>{t.sources?.length || t.media_count} media sources</span>
                    </div>
                  </div>
                </article>
              );
            })()}

            {/* #2 & #3 — Side-by-side medium cards */}
            {events.length >= 2 && (
              <div className="grid md:grid-cols-2 gap-6 mb-8">
                {events.slice(1, 3).map((t) => {
                  const style = getStyle(t.category);
                  const link = getEventLink(t);
                  return (
                    <article
                      key={t.id}
                      onClick={() => link ? router.push(`/events/${link}`) : router.push(`/trending/${t.id}`)}
                      className={`group relative overflow-hidden rounded-2xl bg-gradient-to-br ${style.gradient} text-white p-6 md:p-8 shadow-lg hover:shadow-2xl transition-all duration-300 cursor-pointer`}
                    >
                      <div className="absolute top-0 right-0 w-48 h-48 bg-white/10 rounded-full -translate-y-1/2 translate-x-1/2 blur-2xl"></div>
                      <div className="relative z-10">
                        <div className="flex items-center space-x-3 mb-4">
                          <span className="bg-white/25 backdrop-blur-sm px-3 py-1 rounded-full text-xs font-bold shadow">
                            #{t.rank}
                          </span>
                          <span className="bg-white/15 px-2.5 py-0.5 rounded-full text-xs">{t.category}</span>
                          <div className="flex-1"></div>
                          <span className="text-xs text-white/60">{t.heat_score.toFixed(0)} heat</span>
                        </div>
                        <h3 className="text-xl font-bold mb-3 line-clamp-2 leading-snug">
                          {t.title}
                        </h3>
                        {t.summary && (
                          <p className="text-sm text-white/80 line-clamp-2 mb-4">
                            {t.summary}
                          </p>
                        )}
                        <div className="flex items-center justify-between">
                          <div className="flex flex-wrap gap-1.5">
                            {t.keywords?.slice(0, 3).map((kw, i) => (
                              <span key={i} className="bg-white/15 text-white/90 text-xs px-2 py-0.5 rounded-full capitalize">
                                {kw}
                              </span>
                            ))}
                          </div>
                          <span className="text-xs text-white/60">{t.article_count} articles</span>
                        </div>
                      </div>
                    </article>
                  );
                })}
              </div>
            )}

            {/* Remaining as list */}
            {events.length > 3 && (
              <div className="bg-stone-800/50 rounded-2xl border border-stone-700 divide-y divide-stone-700/50 overflow-hidden">
                {events.slice(3).map((t) => {
                  const style = getStyle(t.category);
                  const link = getEventLink(t);
                  return (
                    <div
                      key={t.id}
                      onClick={() => link ? router.push(`/events/${link}`) : router.push(`/trending/${t.id}`)}
                      className="flex items-center px-6 py-4 hover:bg-stone-700/30 transition-colors cursor-pointer"
                    >
                      <span className={`text-lg font-bold w-10 flex-shrink-0 ${
                        t.rank <= 5 ? 'text-amber-500' : 'text-stone-500'
                      }`}>
                        {t.rank}
                      </span>
                      <div className="flex-1 min-w-0 mr-4">
                        <h4 className="font-semibold text-stone-100 truncate">
                          {t.title}
                        </h4>
                        <div className="flex items-center space-x-2 mt-1">
                          <span className={`text-xs px-2 py-0.5 rounded-full ${style.bg} ${style.text}`}>
                            {t.category}
                          </span>
                          {t.keywords?.slice(0, 2).map((kw, i) => (
                            <span key={i} className="text-xs text-stone-400 capitalize">
                              {kw}
                            </span>
                          ))}
                          {mounted && t.last_updated && (
                            <span className="text-xs text-stone-500" suppressHydrationWarning>{mounted ? formatTimeAgo(t.last_updated) : ''}</span>
                          )}
                        </div>
                      </div>
                      <div className="flex items-center space-x-4 text-xs text-stone-400 flex-shrink-0">
                        <span>{t.article_count} articles</span>
                        <span className="text-amber-500 font-medium">{t.heat_score.toFixed(0)}</span>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </>
        )}
      </main>
    </div>
  );
}
