'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import Header from '../../components/Header';
import { API_BASE_URL } from '../../lib/config';


interface Event {
  id: string;
  title: string;
  summary?: string;
  category?: string;
  source_count: number;
  view_count?: number;
  hot_score?: number;
  occurred_at?: string;
  created_at?: string;
  last_activity_at?: string;
}

const CATEGORIES = ['Environment', 'Economy', 'Technology', 'Politics', 'Geopolitics', 'Society', 'Health', 'Science', 'Culture', 'Entertainment', 'Sports'];

const getCatClass = (cat?: string): string => {
  const map: Record<string, string> = {
    'Environment': 'cat-environment',
    'Economy': 'cat-economy',
    'Technology': 'cat-technology',
    'Politics': 'cat-politics',
    'Geopolitics': 'cat-geopolitics',
    'Society': 'cat-society',
    'Health': 'cat-health',
    'Science': 'cat-science',
    'Culture': 'cat-culture',
    'Entertainment': 'cat-entertainment',
    'Sports': 'cat-sports',
  };
  return (cat && map[cat]) || 'bg-neutral-100 text-neutral-700';
};

/* ── Time ago helper ───────────────────────────────── */
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

export default function StoriesPage() {
  const router = useRouter();
  const [events, setEvents] = useState<Event[]>([]);
  const [sortBy, setSortBy] = useState('last_activity');
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [debouncedSearch, setDebouncedSearch] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [totalCount, setTotalCount] = useState(0);
  const [categoryCounts, setCategoryCounts] = useState<Record<string, number>>({});
  const [mounted, setMounted] = useState(false);

  useEffect(() => { setMounted(true); }, []);

  // Debounce search
  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedSearch(searchQuery);
      setPage(1);
    }, 300);
    return () => clearTimeout(timer);
  }, [searchQuery]);

  // Hard cap: Stories page shows top 41 active events by heat.
  // Page 1 = 21 items (lead + 20 in grid). Page 2 = 20 items (grid only, no lead).
  const PAGE_SIZE_P1 = 21;
  const PAGE_SIZE_P2 = 20;
  const MAX_EVENTS = 41;

  const fetchEvents = useCallback(async () => {
    try {
      setIsLoading(true);
      setError(null);
      // Always fetch the full 41-event window in one request, then slice client-side.
      // This keeps pagination purely presentational and avoids double-counting when
      // the filter/sort changes heat ordering.
      const params = new URLSearchParams({
        page: '1',
        page_size: String(MAX_EVENTS),
        sort_by: sortBy,
      });
      if (selectedCategory) params.append('category', selectedCategory);
      if (debouncedSearch.trim()) params.append('search', debouncedSearch.trim());

      const response = await fetch(`${API_BASE_URL}/api/events?${params}`);
      if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
      const data = await response.json();
      const items: Event[] = (data.items || []).slice(0, MAX_EVENTS);
      setEvents(items);
      // Compute totalPages from the capped count
      const count = items.length;
      const pages = count <= PAGE_SIZE_P1 ? 1 : 2;
      setTotalPages(pages);
      setTotalCount(count);
      if (data.category_counts) setCategoryCounts(data.category_counts);
    } catch (err) {
      console.error('Failed to fetch events:', err);
      setError('Unable to connect to server.');
      setEvents([]);
    } finally {
      setIsLoading(false);
    }
  }, [sortBy, selectedCategory, debouncedSearch]);

  useEffect(() => {
    fetchEvents();
  }, [fetchEvents]);

  // Slice into page 1 (lead + 20) vs page 2 (next 20, no lead)
  const pageItems = page === 1
    ? events.slice(0, PAGE_SIZE_P1)
    : events.slice(PAGE_SIZE_P1, PAGE_SIZE_P1 + PAGE_SIZE_P2);
  const leadEvent = page === 1 ? pageItems[0] : undefined;
  const restEvents = page === 1 ? pageItems.slice(1) : pageItems;

  return (
    <div className="min-h-screen" style={{ background: 'var(--color-paper)' }}>
      <Header />

      {/* Page Header */}
      <section className="border-b" style={{ borderColor: 'var(--color-rule)' }}>
        <div className="container mx-auto px-6 py-8">
          <div className="flex flex-col md:flex-row md:items-end md:justify-between gap-4">
            <div>
              <h1 className="font-serif font-bold mb-1" style={{ color: 'var(--color-ink)', fontSize: 'clamp(1.5rem, 3vw, 2rem)' }}>Stories</h1>
              <p className="text-sm" style={{ color: 'var(--color-ink-light)' }}>
                {totalCount > 0 ? `${totalCount} events with stakeholder perspectives` : 'Events published with stakeholder perspectives'}
              </p>
            </div>
            {/* Search Bar */}
            <div className="relative w-full md:w-72">
              <svg className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4" style={{ color: 'var(--color-ink-light)' }} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
              <input
                type="text"
                placeholder="Search events..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border rounded-md text-sm transition-colors focus:outline-none"
                style={{
                  background: 'var(--color-paper)',
                  borderColor: 'var(--color-rule)',
                  color: 'var(--color-ink)',
                }}
              />
              {searchQuery && (
                <button
                  onClick={() => setSearchQuery('')}
                  className="absolute right-3 top-1/2 -translate-y-1/2"
                  style={{ color: 'var(--color-ink-light)' }}
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              )}
            </div>
          </div>
        </div>
      </section>

      {/* Filters Bar — editorial underline tabs */}
      <section className="sticky top-[57px] z-20 border-b" style={{ background: 'var(--color-paper)', borderColor: 'var(--color-rule)' }}>
        <div className="container mx-auto px-6">
          <div className="flex items-center justify-between gap-4">
            {/* Category tabs */}
            <div className="flex gap-0 flex-1 overflow-x-auto" style={{ scrollbarWidth: 'none' }}>
              <button
                onClick={() => { setSelectedCategory(null); setPage(1); }}
                className="relative px-3 py-2.5 text-sm transition-colors whitespace-nowrap"
                style={{ color: selectedCategory === null ? 'var(--color-ink)' : 'var(--color-ink-light)' }}
              >
                All
                {Object.values(categoryCounts).reduce((a, b) => a + b, 0) > 0 && (
                  <span className="ml-1 text-xs opacity-50">
                    {Object.values(categoryCounts).reduce((a, b) => a + b, 0)}
                  </span>
                )}
                {selectedCategory === null && (
                  <span className="absolute bottom-0 left-3 right-3 h-0.5" style={{ background: 'var(--color-accent)' }} />
                )}
              </button>
              {CATEGORIES.map(cat => {
                const count = categoryCounts[cat] || 0;
                return (
                  <button
                    key={cat}
                    onClick={() => { setSelectedCategory(selectedCategory === cat ? null : cat); setPage(1); }}
                    className="relative px-3 py-2.5 text-sm transition-colors whitespace-nowrap"
                    style={{ color: selectedCategory === cat ? 'var(--color-ink)' : 'var(--color-ink-light)' }}
                  >
                    {cat}
                    {count > 0 && <span className="ml-1 text-xs opacity-50">{count}</span>}
                    {selectedCategory === cat && (
                      <span className="absolute bottom-0 left-3 right-3 h-0.5" style={{ background: 'var(--color-accent)' }} />
                    )}
                  </button>
                );
              })}
            </div>

            {/* Sort */}
            <select
              value={sortBy}
              onChange={(e) => { setSortBy(e.target.value); setPage(1); }}
              className="border rounded-md px-3 py-1.5 text-sm focus:outline-none"
              style={{
                background: 'var(--color-paper)',
                borderColor: 'var(--color-rule)',
                color: 'var(--color-ink-light)',
              }}
            >
              <option value="hot_score">Hottest</option>
              <option value="last_activity">Most Active</option>
              <option value="view_count">Most Viewed</option>
              <option value="created_at">Latest</option>
            </select>
          </div>
        </div>
      </section>

      {/* Active Filters Display */}
      {(debouncedSearch || selectedCategory) && (
        <section className="container mx-auto px-6 pt-4">
          <div className="flex items-center gap-2 text-sm">
            <span style={{ color: 'var(--color-ink-light)' }}>Showing:</span>
            {selectedCategory && (
              <span className={`inline-flex items-center gap-1 px-2.5 py-0.5 rounded-sm ${getCatClass(selectedCategory)} text-xs font-medium`}>
                {selectedCategory}
                <button onClick={() => setSelectedCategory(null)} className="ml-1 hover:opacity-70">&times;</button>
              </span>
            )}
            {debouncedSearch && (
              <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-sm text-xs" style={{ background: 'var(--color-rule)', color: 'var(--color-ink-light)' }}>
                &ldquo;{debouncedSearch}&rdquo;
                <button onClick={() => setSearchQuery('')} className="ml-1 hover:opacity-70">&times;</button>
              </span>
            )}
            <button
              onClick={() => { setSelectedCategory(null); setSearchQuery(''); }}
              className="text-xs underline"
              style={{ color: 'var(--color-ink-light)' }}
            >
              Clear all
            </button>
          </div>
        </section>
      )}

      {/* Error */}
      {error && (
        <div className="container mx-auto px-6 py-4">
          <div className="border rounded-md p-4 text-sm" style={{ borderColor: 'var(--color-accent)', background: 'rgba(194,65,12,0.05)', color: 'var(--color-ink)' }}>{error}</div>
        </div>
      )}

      {/* Content */}
      {isLoading ? (
        <section className="container mx-auto px-6 py-8">
          <div className="space-y-4">
            {[1, 2, 3, 4].map(i => (
              <div key={i} className="animate-pulse h-20 rounded-md" style={{ background: 'var(--color-rule)' }} />
            ))}
          </div>
        </section>
      ) : pageItems.length === 0 ? (
        <section className="container mx-auto px-6 py-20 text-center">
          <h3 className="font-serif text-lg mb-2" style={{ color: 'var(--color-ink)' }}>No stories found</h3>
          <p className="text-sm mb-4" style={{ color: 'var(--color-ink-light)' }}>
            {debouncedSearch
              ? `No results for "${debouncedSearch}"${selectedCategory ? ` in ${selectedCategory}` : ''}`
              : selectedCategory
                ? `No stories in ${selectedCategory} yet`
                : 'No published stories yet'}
          </p>
          {(debouncedSearch || selectedCategory) && (
            <button
              onClick={() => { setSelectedCategory(null); setSearchQuery(''); }}
              className="px-4 py-2 rounded-md text-sm transition-colors text-white"
              style={{ background: 'var(--color-ink)' }}
            >
              Clear Filters
            </button>
          )}
        </section>
      ) : (
        <section className="container mx-auto px-6 py-8">
          {/* Lead story — editorial feature */}
          {leadEvent && (
            <article
              onClick={() => router.push(`/events/${leadEvent.id}`)}
              className="group cursor-pointer mb-8 pb-8 border-b flex gap-6"
              style={{ borderColor: 'var(--color-rule)' }}
            >
              <div className="w-1 flex-shrink-0 rounded-full" style={{ background: 'var(--color-accent)' }} />
              <div className="flex-1">
                <div className="flex items-center gap-3 mb-2">
                  {leadEvent.category && (
                    <span className={`text-xs px-2 py-0.5 rounded-sm font-medium ${getCatClass(leadEvent.category)}`}>
                      {leadEvent.category}
                    </span>
                  )}
                  {mounted && leadEvent.last_activity_at && (
                    <span className="text-xs" style={{ color: 'var(--color-ink-light)' }} suppressHydrationWarning>
                      {formatTimeAgo(leadEvent.last_activity_at)}
                    </span>
                  )}
                </div>
                <h3
                  className="font-serif font-bold leading-tight mb-2 group-hover:opacity-75 transition-opacity"
                  style={{ color: 'var(--color-ink)', fontSize: 'clamp(1.25rem, 3vw, 1.75rem)', letterSpacing: '-0.01em' }}
                >
                  {leadEvent.title}
                </h3>
                {leadEvent.summary && (
                  <p className="text-sm leading-relaxed max-w-2xl line-clamp-2 mb-3" style={{ color: 'var(--color-ink-light)' }}>
                    {leadEvent.summary}
                  </p>
                )}
                <div className="flex items-center gap-3 text-xs" style={{ color: 'var(--color-ink-light)' }}>
                  <span>{leadEvent.source_count} sources</span>
                  <span className="w-1 h-1 rounded-full" style={{ background: 'var(--color-rule)' }} />
                  <span>{(leadEvent.view_count || 0).toLocaleString()} views</span>
                </div>
              </div>
            </article>
          )}

          {/* Rest — two-column editorial list */}
          <div className="grid md:grid-cols-2 gap-x-8 gap-y-0">
            {restEvents.map(event => (
              <article
                key={event.id}
                onClick={() => router.push(`/events/${event.id}`)}
                className="group py-4 cursor-pointer border-b"
                style={{ borderColor: 'var(--color-rule)' }}
              >
                <div className="flex items-center gap-2 mb-1.5">
                  {event.category && (
                    <span className={`text-xs px-2 py-0.5 rounded-sm font-medium ${getCatClass(event.category)}`}>
                      {event.category}
                    </span>
                  )}
                  {mounted && event.last_activity_at && (
                    <span className="text-xs" style={{ color: 'var(--color-ink-light)' }} suppressHydrationWarning>
                      {formatTimeAgo(event.last_activity_at)}
                    </span>
                  )}
                </div>
                <h3
                  className="font-serif font-semibold leading-snug mb-1.5 group-hover:opacity-75 transition-opacity"
                  style={{ color: 'var(--color-ink)' }}
                >
                  {event.title}
                </h3>
                <div className="flex items-center gap-3 text-xs" style={{ color: 'var(--color-ink-light)' }}>
                  <span>{event.source_count} sources</span>
                  <span className="w-1 h-1 rounded-full" style={{ background: 'var(--color-rule)' }} />
                  <span>{(event.view_count || 0).toLocaleString()} views</span>
                </div>
              </article>
            ))}
          </div>

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="flex items-center justify-center gap-4 mt-10 pt-6 border-t" style={{ borderColor: 'var(--color-rule)' }}>
              <button
                onClick={() => setPage(p => Math.max(1, p - 1))}
                disabled={page <= 1}
                className="px-4 py-2 border rounded-md text-sm transition-colors disabled:opacity-30 disabled:cursor-not-allowed"
                style={{ borderColor: 'var(--color-rule)', color: 'var(--color-ink-light)' }}
              >
                &larr; Previous
              </button>
              <span className="text-sm font-serif" style={{ color: 'var(--color-ink-light)' }}>
                {page} / {totalPages}
              </span>
              <button
                onClick={() => setPage(p => Math.min(totalPages, p + 1))}
                disabled={page >= totalPages}
                className="px-4 py-2 border rounded-md text-sm transition-colors disabled:opacity-30 disabled:cursor-not-allowed"
                style={{ borderColor: 'var(--color-rule)', color: 'var(--color-ink-light)' }}
              >
                Next &rarr;
              </button>
            </div>
          )}
        </section>
      )}
    </div>
  );
}
