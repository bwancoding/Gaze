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

const categoryStyles: Record<string, { gradient: string; bg: string; text: string; border: string; icon: string }> = {
  'Environment': { gradient: 'from-emerald-500 to-teal-600', bg: 'bg-emerald-50', text: 'text-emerald-700', border: 'border-emerald-200', icon: '🌍' },
  'Economy': { gradient: 'from-blue-500 to-indigo-600', bg: 'bg-blue-50', text: 'text-blue-700', border: 'border-blue-200', icon: '📊' },
  'Technology': { gradient: 'from-violet-500 to-purple-600', bg: 'bg-violet-50', text: 'text-violet-700', border: 'border-violet-200', icon: '💻' },
  'Politics': { gradient: 'from-amber-500 to-orange-600', bg: 'bg-amber-50', text: 'text-amber-700', border: 'border-amber-200', icon: '🏛️' },
  'Geopolitics': { gradient: 'from-red-500 to-orange-600', bg: 'bg-red-50', text: 'text-red-700', border: 'border-red-200', icon: '🌐' },
  'Society': { gradient: 'from-teal-500 to-cyan-600', bg: 'bg-teal-50', text: 'text-teal-700', border: 'border-teal-200', icon: '👥' },
  'Health': { gradient: 'from-rose-500 to-pink-600', bg: 'bg-rose-50', text: 'text-rose-700', border: 'border-rose-200', icon: '🏥' },
  'Science': { gradient: 'from-cyan-500 to-sky-600', bg: 'bg-cyan-50', text: 'text-cyan-700', border: 'border-cyan-200', icon: '🔬' },
};

const defaultStyle = { gradient: 'from-stone-500 to-gray-600', bg: 'bg-stone-50', text: 'text-stone-700', border: 'border-stone-200', icon: '📰' };

const getStyle = (cat?: string) => (cat && categoryStyles[cat]) || defaultStyle;

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

  const allCategories = Object.keys(categoryStyles);
  const featuredStory = events[0];
  const regularStories = events.slice(1);

  return (
    <div className="min-h-screen bg-stone-50">
      <Header />

      {/* Page Header with Search */}
      <section className="bg-white border-b border-stone-200">
        <div className="container mx-auto px-6 py-8">
          <div className="flex flex-col md:flex-row md:items-end md:justify-between gap-4">
            <div>
              <h1 className="text-3xl font-bold text-stone-900 mb-2">Published Stories</h1>
              <p className="text-stone-500">
                {totalCount > 0 ? `${totalCount} events analyzed with AI-powered stakeholder perspectives` : 'Events analyzed and published with AI-powered stakeholder perspectives'}
              </p>
            </div>
            {/* Search Bar */}
            <div className="relative w-full md:w-80">
              <svg className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-stone-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
              <input
                type="text"
                placeholder="Search events..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-10 pr-4 py-2.5 border border-stone-300 rounded-xl bg-stone-50 text-sm focus:ring-2 focus:ring-stone-500 focus:border-transparent focus:bg-white transition-all"
              />
              {searchQuery && (
                <button
                  onClick={() => setSearchQuery('')}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-stone-400 hover:text-stone-600"
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              )}
            </div>
          </div>
        </div>
      </section>

      {/* Filters Bar */}
      <section className="sticky top-[73px] z-20 bg-white/95 backdrop-blur-sm border-b border-stone-200 shadow-sm">
        <div className="container mx-auto px-6 py-3">
          <div className="flex items-center justify-between gap-4">
            {/* Category Pills */}
            <div className="flex flex-wrap gap-2 flex-1">
              <button
                onClick={() => { setSelectedCategory(null); setPage(1); }}
                className={`px-4 py-2 rounded-full text-sm font-medium transition-all flex items-center gap-1.5 ${
                  selectedCategory === null
                    ? 'bg-stone-900 text-white shadow-lg'
                    : 'bg-white text-stone-600 hover:bg-stone-100 border border-stone-200'
                }`}
              >
                All
                {Object.values(categoryCounts).reduce((a, b) => a + b, 0) > 0 && (
                  <span className={`text-xs px-1.5 py-0.5 rounded-full ${selectedCategory === null ? 'bg-white/20' : 'bg-stone-100'}`}>
                    {Object.values(categoryCounts).reduce((a, b) => a + b, 0)}
                  </span>
                )}
              </button>
              {allCategories.map(cat => {
                const count = categoryCounts[cat] || 0;
                const style = categoryStyles[cat];
                return (
                  <button
                    key={cat}
                    onClick={() => { setSelectedCategory(selectedCategory === cat ? null : cat); setPage(1); }}
                    className={`px-4 py-2 rounded-full text-sm font-medium transition-all flex items-center gap-1.5 ${
                      selectedCategory === cat
                        ? 'bg-stone-900 text-white shadow-lg'
                        : `bg-white ${style.text} hover:${style.bg} border ${style.border}`
                    }`}
                  >
                    <span>{style.icon}</span>
                    {cat}
                    {count > 0 && (
                      <span className={`text-xs px-1.5 py-0.5 rounded-full ${
                        selectedCategory === cat ? 'bg-white/20' : style.bg
                      }`}>
                        {count}
                      </span>
                    )}
                  </button>
                );
              })}
            </div>

            {/* Sort */}
            <div className="flex items-center space-x-2 flex-shrink-0">
              <select
                value={sortBy}
                onChange={(e) => { setSortBy(e.target.value); setPage(1); }}
                className="border border-stone-300 rounded-lg px-3 py-2 bg-white text-stone-700 text-sm focus:ring-2 focus:ring-stone-500 focus:border-transparent"
              >
                <option value="hot_score">🔥 Hottest</option>
                <option value="last_activity">⚡ Most Active</option>
                <option value="view_count">👁 Most Viewed</option>
                <option value="created_at">🕐 Latest</option>
              </select>
            </div>
          </div>
        </div>
      </section>

      {/* Active Filters Display */}
      {(debouncedSearch || selectedCategory) && (
        <section className="container mx-auto px-6 pt-4">
          <div className="flex items-center gap-2 text-sm">
            <span className="text-stone-400">Showing:</span>
            {selectedCategory && (
              <span className={`inline-flex items-center gap-1 px-3 py-1 rounded-full ${getStyle(selectedCategory).bg} ${getStyle(selectedCategory).text} text-xs font-medium`}>
                {getStyle(selectedCategory).icon} {selectedCategory}
                <button onClick={() => setSelectedCategory(null)} className="ml-1 hover:opacity-70">×</button>
              </span>
            )}
            {debouncedSearch && (
              <span className="inline-flex items-center gap-1 px-3 py-1 rounded-full bg-stone-100 text-stone-600 text-xs font-medium">
                &ldquo;{debouncedSearch}&rdquo;
                <button onClick={() => setSearchQuery('')} className="ml-1 hover:opacity-70">×</button>
              </span>
            )}
            <button
              onClick={() => { setSelectedCategory(null); setSearchQuery(''); }}
              className="text-xs text-stone-400 hover:text-stone-600 underline"
            >
              Clear all
            </button>
          </div>
        </section>
      )}

      {/* Error */}
      {error && (
        <div className="container mx-auto px-6 py-4">
          <div className="bg-amber-50 border border-amber-200 rounded-lg p-4 text-amber-800">{error}</div>
        </div>
      )}

      {/* Content */}
      {isLoading ? (
        <section className="container mx-auto px-6 py-12">
          <div className="animate-pulse space-y-6">
            <div className="bg-stone-200 rounded-3xl h-64"></div>
            <div className="grid md:grid-cols-3 gap-6">
              {[1, 2, 3].map(i => <div key={i} className="bg-stone-200 rounded-2xl h-48"></div>)}
            </div>
          </div>
        </section>
      ) : events.length === 0 ? (
        <section className="container mx-auto px-6 py-20 text-center">
          <div className="text-5xl mb-4">🔍</div>
          <p className="text-stone-600 text-lg mb-2">No stories found</p>
          <p className="text-stone-400 text-sm">
            {debouncedSearch
              ? `No results for "${debouncedSearch}"${selectedCategory ? ` in ${selectedCategory}` : ''}`
              : selectedCategory
                ? `No stories in ${selectedCategory} yet`
                : 'No published stories yet'}
          </p>
          {(debouncedSearch || selectedCategory) && (
            <button
              onClick={() => { setSelectedCategory(null); setSearchQuery(''); }}
              className="mt-4 px-6 py-2 bg-stone-900 text-white rounded-full text-sm font-medium hover:bg-stone-800 transition-colors"
            >
              Clear Filters
            </button>
          )}
        </section>
      ) : (
        <>
          {/* Featured */}
          {featuredStory && (
            <section className="container mx-auto px-6 py-8">
              <article
                onClick={() => router.push(`/events/${featuredStory.id}`)}
                className={`group relative overflow-hidden rounded-3xl bg-gradient-to-br ${getStyle(featuredStory.category).gradient} p-8 md:p-12 text-white shadow-2xl hover:shadow-3xl transition-all duration-500 cursor-pointer`}
              >
                <div className="absolute top-0 right-0 w-96 h-96 bg-white/10 rounded-full -translate-y-1/2 translate-x-1/2 blur-3xl"></div>
                <div className="relative z-10 max-w-2xl">
                  <span className="inline-block bg-white/20 backdrop-blur-sm px-4 py-1.5 rounded-full text-sm font-medium mb-6">
                    {featuredStory.category}
                  </span>
                  <h2 className="text-3xl md:text-4xl font-bold mb-4 leading-tight">
                    {featuredStory.title}
                  </h2>
                  <p className="text-white/80 leading-relaxed mb-6 line-clamp-3">
                    {featuredStory.summary}
                  </p>
                  <div className="flex items-center space-x-4 text-sm text-white/70">
                    <span>{featuredStory.source_count} Sources</span>
                    <span>{(featuredStory.view_count || 0).toLocaleString()} Views</span>
                    <span>🔥 {featuredStory.hot_score?.toFixed(1) || 0}</span>
                  </div>
                </div>
              </article>
            </section>
          )}

          {/* Grid */}
          {regularStories.length > 0 && (
            <section className="container mx-auto px-6 pb-12">
              <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
                {regularStories.map(event => {
                  const style = getStyle(event.category);
                  return (
                    <article
                      key={event.id}
                      onClick={() => router.push(`/events/${event.id}`)}
                      className="group bg-white rounded-2xl border border-stone-200 overflow-hidden hover:shadow-xl hover:border-stone-300 transition-all duration-300 cursor-pointer"
                    >
                      <div className={`h-1.5 bg-gradient-to-r ${style.gradient}`}></div>
                      <div className="p-6">
                        <div className="flex items-center justify-between mb-3">
                          <span className={`text-xs px-3 py-1 rounded-full font-medium ${style.bg} ${style.text}`}>
                            {style.icon} {event.category}
                          </span>
                        </div>
                        <h3 className="text-lg font-bold text-stone-900 mb-2 line-clamp-2 group-hover:text-stone-700 transition-colors">
                          {event.title}
                        </h3>
                        <p className="text-stone-500 text-sm leading-relaxed mb-4 line-clamp-3">
                          {event.summary}
                        </p>
                        <div className="flex items-center justify-between pt-3 border-t border-stone-100 text-xs text-stone-400">
                          <span>{event.source_count} sources</span>
                          <span>🔥 {event.hot_score?.toFixed(1) || 0}</span>
                        </div>
                      </div>
                    </article>
                  );
                })}
              </div>

              {/* Pagination */}
              {totalPages > 1 && (
                <div className="flex items-center justify-center space-x-4 mt-12">
                  <button
                    onClick={() => setPage(p => Math.max(1, p - 1))}
                    disabled={page <= 1}
                    className="px-5 py-2.5 bg-white border border-stone-200 rounded-full text-sm font-medium text-stone-700 hover:bg-stone-50 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
                  >
                    ← Previous
                  </button>
                  <span className="text-sm text-stone-500">
                    Page {page} of {totalPages}
                  </span>
                  <button
                    onClick={() => setPage(p => Math.min(totalPages, p + 1))}
                    disabled={page >= totalPages}
                    className="px-5 py-2.5 bg-white border border-stone-200 rounded-full text-sm font-medium text-stone-700 hover:bg-stone-50 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
                  >
                    Next →
                  </button>
                </div>
              )}
            </section>
          )}
        </>
      )}
    </div>
  );
}
