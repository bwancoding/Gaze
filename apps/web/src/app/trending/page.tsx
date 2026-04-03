'use client';

import React, { useState, useEffect, useCallback, useRef } from 'react';
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

/* ── Scroll reveal hook — watches for dynamically added elements ── */
function useScrollReveal() {
  const initialized = useRef(false);
  useEffect(() => {
    if (initialized.current) return;
    initialized.current = true;
    const prefersReduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    const selectors = '.reveal:not(.is-visible), .reveal-left:not(.is-visible), .reveal-right:not(.is-visible), .reveal-scale:not(.is-visible)';

    if (prefersReduced) {
      const makeVisible = () => document.querySelectorAll(selectors).forEach(el => el.classList.add('is-visible'));
      makeVisible();
      const mo = new MutationObserver(makeVisible);
      mo.observe(document.body, { childList: true, subtree: true });
      return () => mo.disconnect();
    }

    const io = new IntersectionObserver(
      entries => entries.forEach(e => {
        if (e.isIntersecting) {
          e.target.classList.add('is-visible');
          io.unobserve(e.target);
        }
      }),
      { threshold: 0.12, rootMargin: '0px 0px -40px 0px' }
    );
    document.querySelectorAll(selectors).forEach(el => io.observe(el));
    const mo = new MutationObserver(() => {
      document.querySelectorAll(selectors).forEach(el => io.observe(el));
    });
    mo.observe(document.body, { childList: true, subtree: true });
    return () => { io.disconnect(); mo.disconnect(); };
  }, []);
}

export default function TrendingPage() {
  const router = useRouter();
  const [events, setEvents] = useState<TrendingEvent[]>([]);
  const [selectedCategory, setSelectedCategory] = useState('All');
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [mounted, setMounted] = useState(false);

  useEffect(() => { setMounted(true); }, []);
  useScrollReveal();

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
  const leadStory = events[0];
  const runnerUp = events.slice(1, 5);
  const remaining = events.slice(5);

  return (
    <div className="min-h-screen" style={{ background: 'var(--color-paper)' }}>
      <Header />

      <main className="container mx-auto px-6 py-8">
        {/* Page Header */}
        <div className="reveal mb-2">
          <p className="text-xs uppercase tracking-[0.25em] mb-3" style={{ color: 'var(--color-ink-light)' }}>
            What the world is watching
          </p>
          <h1 className="font-serif text-4xl md:text-5xl font-bold mb-1" style={{ color: 'var(--color-ink)', letterSpacing: '-0.02em' }}>
            Trending
          </h1>
        </div>

        <hr className="rule-thick mb-6" />

        {/* Category Tabs — editorial underline style */}
        <nav className="flex gap-6 mb-10 overflow-x-auto border-b" style={{ borderColor: 'var(--color-rule)' }}>
          {CATEGORIES.map(cat => (
            <button
              key={cat}
              onClick={() => setSelectedCategory(cat)}
              className="relative pb-3 text-sm whitespace-nowrap transition-colors"
              style={{
                color: selectedCategory === cat ? 'var(--color-ink)' : 'var(--color-ink-light)',
                fontWeight: selectedCategory === cat ? 600 : 400,
              }}
            >
              {cat}
              {selectedCategory === cat && (
                <span
                  className="absolute bottom-0 left-0 right-0 h-[3px]"
                  style={{ background: 'var(--color-accent)' }}
                />
              )}
            </button>
          ))}
        </nav>

        {/* Error State */}
        {error && (
          <div className="border rounded-lg p-4 mb-6 text-sm" style={{ borderColor: '#D97706', background: '#FFFBEB', color: '#92400E' }}>
            <p>{error}</p>
          </div>
        )}

        {/* Loading State */}
        {isLoading ? (
          <div className="space-y-4">
            {[1,2,3].map(i => (
              <div key={i} className="animate-pulse h-24 rounded-lg" style={{ background: 'var(--color-rule)' }} />
            ))}
          </div>
        ) : events.length === 0 ? (
          <div className="text-center py-20 border rounded-lg" style={{ borderColor: 'var(--color-rule)', background: 'white' }}>
            <h3 className="text-lg font-serif mb-2" style={{ color: 'var(--color-ink)' }}>No trending stories right now</h3>
            <p className="text-sm mb-6" style={{ color: 'var(--color-ink-light)' }}>Check back later for breaking stories</p>
            <button
              onClick={fetchTrending}
              className="px-4 py-2 text-white rounded-md text-sm transition-colors btn-press"
              style={{ background: 'var(--color-warm-dark)' }}
            >
              Check Again
            </button>
          </div>
        ) : (
          <div>
            {/* ═══ #1 Lead Story — dark editorial hero ═══ */}
            {leadStory && (() => {
              const link = getEventLink(leadStory);
              return (
                <article
                  onClick={() => link ? router.push(`/events/${link}`) : router.push(`/trending/${leadStory.id}`)}
                  className="reveal relative overflow-hidden grain rounded-lg mb-10 cursor-pointer group"
                  style={{ background: 'var(--color-warm-dark)' }}
                >
                  <div className="relative p-8 md:p-12">
                    <div className="flex items-center gap-3 mb-4">
                      <span className="text-xs font-bold uppercase tracking-widest" style={{ color: 'var(--color-accent)' }}>
                        No. 1
                      </span>
                      <span className="w-px h-3" style={{ background: 'rgba(255,255,255,0.2)' }} />
                      <span className={`text-xs px-2 py-0.5 rounded-sm font-medium ${getCatClass(leadStory.category)}`}>
                        {leadStory.category}
                      </span>
                      {mounted && leadStory.last_updated && (
                        <>
                          <span className="w-px h-3" style={{ background: 'rgba(255,255,255,0.2)' }} />
                          <span className="text-xs" style={{ color: 'rgba(255,255,255,0.4)' }} suppressHydrationWarning>
                            {formatTimeAgo(leadStory.last_updated)}
                          </span>
                        </>
                      )}
                    </div>
                    <h2
                      className="font-serif font-bold text-white mb-4 leading-tight group-hover:opacity-90 transition-opacity"
                      style={{ fontSize: 'clamp(1.75rem, 4vw, 2.75rem)', letterSpacing: '-0.02em' }}
                    >
                      {leadStory.title}
                    </h2>
                    {leadStory.summary && (
                      <p className="leading-relaxed mb-6 max-w-2xl line-clamp-2" style={{ color: 'rgba(255,255,255,0.6)' }}>
                        {leadStory.summary}
                      </p>
                    )}
                    <div className="flex items-center gap-4 text-xs" style={{ color: 'rgba(255,255,255,0.35)' }}>
                      <span>{leadStory.article_count} articles</span>
                      <span className="w-1 h-1 rounded-full" style={{ background: 'rgba(255,255,255,0.2)' }} />
                      <span>{leadStory.sources?.length || leadStory.media_count} sources</span>
                    </div>
                  </div>
                </article>
              );
            })()}

            {/* ═══ #2–#5 Runner-up stories — two-column grid ═══ */}
            {runnerUp.length > 0 && (
              <div className="grid md:grid-cols-2 gap-x-8 gap-y-0 mb-2">
                {runnerUp.map((t, i) => {
                  const link = getEventLink(t);
                  return (
                    <article
                      key={t.id}
                      onClick={() => link ? router.push(`/events/${link}`) : router.push(`/trending/${t.id}`)}
                      className={`reveal reveal-delay-${i + 1} group py-5 cursor-pointer border-b`}
                      style={{ borderColor: 'var(--color-rule)' }}
                    >
                      <div className="flex items-start gap-4">
                        <span
                          className="font-serif font-bold text-2xl flex-shrink-0 w-8 text-right leading-none pt-0.5"
                          style={{ color: 'var(--color-accent)', opacity: 0.5 }}
                        >
                          {t.rank}
                        </span>
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2 mb-1.5">
                            <span className={`text-xs px-2 py-0.5 rounded-sm font-medium ${getCatClass(t.category)}`}>
                              {t.category}
                            </span>
                            {mounted && t.last_updated && (
                              <span className="text-xs" style={{ color: 'var(--color-ink-light)' }} suppressHydrationWarning>
                                {formatTimeAgo(t.last_updated)}
                              </span>
                            )}
                          </div>
                          <h3
                            className="font-serif font-semibold leading-snug mb-1.5 group-hover:opacity-75 transition-opacity"
                            style={{ color: 'var(--color-ink)' }}
                          >
                            {t.title}
                          </h3>
                          <div className="flex items-center gap-3 text-xs" style={{ color: 'var(--color-ink-light)' }}>
                            <span>{t.article_count} articles</span>
                            <span className="w-1 h-1 rounded-full" style={{ background: 'var(--color-rule)' }} />
                            <span>{t.sources?.length || t.media_count} sources</span>
                          </div>
                        </div>
                      </div>
                    </article>
                  );
                })}
              </div>
            )}

            {/* ═══ Diamond ornament divider ═══ */}
            {remaining.length > 0 && (
              <div className="flex items-center gap-4 my-8">
                <div className="flex-1 h-px" style={{ background: 'var(--color-rule)' }} />
                <span className="text-xs" style={{ color: 'var(--color-rule)' }}>◆</span>
                <div className="flex-1 h-px" style={{ background: 'var(--color-rule)' }} />
              </div>
            )}

            {/* ═══ #6–#10 Remaining — compact list ═══ */}
            {remaining.length > 0 && (
              <div className="reveal">
                <p className="text-xs uppercase tracking-[0.2em] mb-4" style={{ color: 'var(--color-ink-light)' }}>
                  Also trending
                </p>
                <div className="space-y-0">
                  {remaining.map(t => {
                    const link = getEventLink(t);
                    return (
                      <article
                        key={t.id}
                        onClick={() => link ? router.push(`/events/${link}`) : router.push(`/trending/${t.id}`)}
                        className="group flex items-center gap-4 py-3 cursor-pointer border-b"
                        style={{ borderColor: 'var(--color-rule)' }}
                      >
                        <span
                          className="font-serif text-sm flex-shrink-0 w-6 text-right"
                          style={{ color: 'var(--color-ink-light)', opacity: 0.5 }}
                        >
                          {t.rank}
                        </span>
                        <span className={`text-xs px-1.5 py-0.5 rounded-sm font-medium flex-shrink-0 ${getCatClass(t.category)}`}>
                          {t.category}
                        </span>
                        <h3
                          className="font-serif text-sm flex-1 min-w-0 truncate group-hover:opacity-75 transition-opacity"
                          style={{ color: 'var(--color-ink)' }}
                        >
                          {t.title}
                        </h3>
                        {mounted && t.last_updated && (
                          <span className="text-xs flex-shrink-0" style={{ color: 'var(--color-ink-light)' }} suppressHydrationWarning>
                            {formatTimeAgo(t.last_updated)}
                          </span>
                        )}
                      </article>
                    );
                  })}
                </div>
              </div>
            )}
          </div>
        )}
      </main>
    </div>
  );
}
