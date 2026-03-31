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

const CATEGORIES = ['Environment', 'Economy', 'Technology', 'Politics', 'Geopolitics', 'Society', 'Health', 'Science'];

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
    'Entertainment': 'cat-entertainment',
  };
  return (cat && map[cat]) || 'bg-neutral-100 text-neutral-700';
};

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

  // Debounce search
  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedSearch(searchQuery);
      setPage(1);
    }, 300);
    return () => clearTimeout(timer);
  }, [searchQuery]);

  const fetchEvents = useCallback(async () => {
    try {
      setIsLoading(true);
      setError(null);
      const params = new URLSearchParams({
        page: String(page),
        page_size: '50',
        sort_by: sortBy,
      });
      if (selectedCategory) params.append('category', selectedCategory);
      if (debouncedSearch.trim()) params.append('search', debouncedSearch.trim());

      const response = await fetch(`${API_BASE_URL}/api/events?${params}`);
      if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
      const data = await response.json();
      setEvents(data.items || []);
      setTotalPages(data.total_pages || Math.ceil((data.total || 0) / 50) || 1);
      setTotalCount(data.total || 0);
      if (data.category_counts) setCategoryCounts(data.category_counts);
    } catch (err) {
      console.error('Failed to fetch events:', err);
      setError('Unable to connect to server.');
      setEvents([]);
    } finally {
      setIsLoading(false);
    }
  }, [sortBy, selectedCategory, debouncedSearch, page]);

  useEffect(() => {
    fetchEvents();
  }, [fetchEvents]);

  return (
    <div className="min-h-screen bg-neutral-50">
      <Header />

      {/* Page Header with Search */}
      <section className="bg-white border-b border-neutral-200">
        <div className="container mx-auto px-6 py-8">
          <div className="flex flex-col md:flex-row md:items-end md:justify-between gap-4">
            <div>
              <h1 className="font-serif text-headline text-neutral-900 mb-1">Stories</h1>
              <p className="text-sm text-neutral-500">
                {totalCount > 0 ? `${totalCount} events with stakeholder perspectives` : 'Events published with stakeholder perspectives'}
              </p>
            </div>
            {/* Search Bar */}
            <div className="relative w-full md:w-72">
              <svg className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-neutral-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
              <input
                type="text"
                placeholder="Search events..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-neutral-300 rounded-md bg-white text-sm focus:ring-1 focus:ring-neutral-900 focus:border-neutral-900 transition-colors"
              />
              {searchQuery && (
                <button
                  onClick={() => setSearchQuery('')}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-neutral-400 hover:text-neutral-600"
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

      {/* Filters Bar */}
      <section className="sticky top-[57px] z-20 bg-white border-b border-neutral-200">
        <div className="container mx-auto px-6 py-2.5">
          <div className="flex items-center justify-between gap-4">
            {/* Category pills */}
            <div className="flex flex-wrap gap-1 flex-1">
              <button
                onClick={() => { setSelectedCategory(null); setPage(1); }}
                className={`px-3 py-1 rounded-md text-sm transition-colors ${
                  selectedCategory === null
                    ? 'bg-neutral-900 text-white'
                    : 'text-neutral-600 hover:bg-neutral-100'
                }`}
              >
                All
                {Object.values(categoryCounts).reduce((a, b) => a + b, 0) > 0 && (
                  <span className="ml-1.5 text-xs opacity-60">
                    {Object.values(categoryCounts).reduce((a, b) => a + b, 0)}
                  </span>
                )}
              </button>
              {CATEGORIES.map(cat => {
                const count = categoryCounts[cat] || 0;
                return (
                  <button
                    key={cat}
                    onClick={() => { setSelectedCategory(selectedCategory === cat ? null : cat); setPage(1); }}
                    className={`px-3 py-1 rounded-md text-sm transition-colors ${
                      selectedCategory === cat
                        ? 'bg-neutral-900 text-white'
                        : 'text-neutral-600 hover:bg-neutral-100'
                    }`}
                  >
                    {cat}
                    {count > 0 && <span className="ml-1.5 text-xs opacity-60">{count}</span>}
                  </button>
                );
              })}
            </div>

            {/* Sort */}
            <select
              value={sortBy}
              onChange={(e) => { setSortBy(e.target.value); setPage(1); }}
              className="border border-neutral-300 rounded-md px-3 py-1.5 bg-white text-neutral-700 text-sm focus:ring-1 focus:ring-neutral-900 focus:border-neutral-900"
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
            <span className="text-neutral-400">Showing:</span>
            {selectedCategory && (
              <span className={`inline-flex items-center gap-1 px-2.5 py-0.5 rounded-md ${getCatClass(selectedCategory)} text-xs font-medium`}>
                {selectedCategory}
                <button onClick={() => setSelectedCategory(null)} className="ml-1 hover:opacity-70">&times;</button>
              </span>
            )}
            {debouncedSearch && (
              <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-md bg-neutral-100 text-neutral-600 text-xs">
                &ldquo;{debouncedSearch}&rdquo;
                <button onClick={() => setSearchQuery('')} className="ml-1 hover:opacity-70">&times;</button>
              </span>
            )}
            <button
              onClick={() => { setSelectedCategory(null); setSearchQuery(''); }}
              className="text-xs text-neutral-400 hover:text-neutral-600 underline"
            >
              Clear all
            </button>
          </div>
        </section>
      )}

      {/* Error */}
      {error && (
        <div className="container mx-auto px-6 py-4">
          <div className="border border-amber-300 bg-amber-50 rounded-lg p-4 text-sm text-amber-800">{error}</div>
        </div>
      )}

      {/* Content */}
      {isLoading ? (
        <section className="container mx-auto px-6 py-8">
          <div className="space-y-4">
            {[1, 2, 3, 4].map(i => (
              <div key={i} className="animate-pulse h-20 bg-neutral-200 rounded-lg" />
            ))}
          </div>
        </section>
      ) : events.length === 0 ? (
        <section className="container mx-auto px-6 py-20 text-center">
          <h3 className="font-serif text-lg text-neutral-900 mb-2">No stories found</h3>
          <p className="text-sm text-neutral-500 mb-4">
            {debouncedSearch
              ? `No results for "${debouncedSearch}"${selectedCategory ? ` in ${selectedCategory}` : ''}`
              : selectedCategory
                ? `No stories in ${selectedCategory} yet`
                : 'No published stories yet'}
          </p>
          {(debouncedSearch || selectedCategory) && (
            <button
              onClick={() => { setSelectedCategory(null); setSearchQuery(''); }}
              className="px-4 py-2 bg-neutral-900 text-white rounded-md text-sm hover:bg-neutral-800 transition-colors"
            >
              Clear Filters
            </button>
          )}
        </section>
      ) : (
        <section className="container mx-auto px-6 py-8">
          {/* Stories grid — clean cards */}
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-5">
            {events.map(event => (
              <article
                key={event.id}
                onClick={() => router.push(`/events/${event.id}`)}
                className="group bg-white border border-neutral-200 rounded-lg overflow-hidden hover:border-neutral-400 transition-colors cursor-pointer"
              >
                {/* Category bar — thin, flat color */}
                <div className={`h-0.5 ${getCatClass(event.category).split(' ')[0]}`} />
                <div className="p-5">
                  <div className="flex items-center justify-between mb-2.5">
                    <span className={`text-xs px-2 py-0.5 rounded-md font-medium ${getCatClass(event.category)}`}>
                      {event.category}
                    </span>
                    {event.hot_score && event.hot_score > 0 && (
                      <span className="text-xs text-neutral-400 font-medium">{event.hot_score.toFixed(1)}</span>
                    )}
                  </div>
                  <h3 className="font-serif font-semibold text-neutral-900 mb-2 line-clamp-2 group-hover:text-accent transition-colors leading-snug">
                    {event.title}
                  </h3>
                  {event.summary && (
                    <p className="text-sm text-neutral-500 leading-relaxed mb-4 line-clamp-3">
                      {event.summary}
                    </p>
                  )}
                  <div className="flex items-center justify-between pt-3 border-t border-neutral-100 text-xs text-neutral-400">
                    <span>{event.source_count} sources</span>
                    <span>{(event.view_count || 0).toLocaleString()} views</span>
                  </div>
                </div>
              </article>
            ))}
          </div>

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="flex items-center justify-center space-x-4 mt-10">
              <button
                onClick={() => setPage(p => Math.max(1, p - 1))}
                disabled={page <= 1}
                className="px-4 py-2 border border-neutral-300 rounded-md text-sm text-neutral-700 hover:bg-neutral-100 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
              >
                Previous
              </button>
              <span className="text-sm text-neutral-500">
                Page {page} of {totalPages}
              </span>
              <button
                onClick={() => setPage(p => Math.min(totalPages, p + 1))}
                disabled={page >= totalPages}
                className="px-4 py-2 border border-neutral-300 rounded-md text-sm text-neutral-700 hover:bg-neutral-100 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
              >
                Next
              </button>
            </div>
          )}
        </section>
      )}
    </div>
  );
}
