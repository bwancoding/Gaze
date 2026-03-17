'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Header from '../../components/Header';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface Event {
  id: string;
  title: string;
  summary?: string;
  category?: string;
  sourceCount: number;
  viewCount?: number;
  hotScore?: number;
  occurredAt?: string;
}

const categoryStyles: Record<string, { gradient: string; bg: string; text: string; border: string }> = {
  'Environment': { gradient: 'from-emerald-500 to-teal-600', bg: 'bg-emerald-50', text: 'text-emerald-700', border: 'border-emerald-200' },
  'Economy': { gradient: 'from-blue-500 to-indigo-600', bg: 'bg-blue-50', text: 'text-blue-700', border: 'border-blue-200' },
  'Technology': { gradient: 'from-violet-500 to-purple-600', bg: 'bg-violet-50', text: 'text-violet-700', border: 'border-violet-200' },
  'Politics': { gradient: 'from-amber-500 to-orange-600', bg: 'bg-amber-50', text: 'text-amber-700', border: 'border-amber-200' },
};

const defaultStyle = { gradient: 'from-stone-500 to-gray-600', bg: 'bg-stone-50', text: 'text-stone-700', border: 'border-stone-200' };

const getStyle = (cat?: string) => (cat && categoryStyles[cat]) || defaultStyle;

export default function StoriesPage() {
  const router = useRouter();
  const [events, setEvents] = useState<Event[]>([]);
  const [sortBy, setSortBy] = useState('hot_score');
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);

  const fetchEvents = async () => {
    try {
      setIsLoading(true);
      setError(null);
      const params = new URLSearchParams({
        page: String(page),
        page_size: '21',
        sort_by: sortBy,
      });
      if (selectedCategory) params.append('category', selectedCategory);

      const response = await fetch(`${API_BASE_URL}/api/events?${params}`);
      if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
      const data = await response.json();
      setEvents(data.items || []);
      setTotalPages(data.total_pages || 1);
    } catch (err) {
      console.error('Failed to fetch events:', err);
      setError('Unable to connect to server.');
      setEvents([]);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchEvents();
  }, [sortBy, selectedCategory, page]);

  const featuredStory = events[0];
  const regularStories = events.slice(1);

  return (
    <div className="min-h-screen bg-stone-50">
      <Header />

      {/* Page Header */}
      <section className="bg-white border-b border-stone-200">
        <div className="container mx-auto px-6 py-8">
          <h1 className="text-3xl font-bold text-stone-900 mb-2">Published Stories</h1>
          <p className="text-stone-500">Events analyzed and published with AI-powered stakeholder perspectives</p>
        </div>
      </section>

      {/* Filters */}
      <section className="sticky top-0 z-20 bg-stone-50/95 backdrop-blur-sm border-b border-stone-200">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex flex-wrap gap-2">
              <button
                onClick={() => { setSelectedCategory(null); setPage(1); }}
                className={`px-4 py-2 rounded-full text-sm font-medium transition-all ${
                  selectedCategory === null
                    ? 'bg-stone-900 text-white shadow-lg'
                    : 'bg-white text-stone-600 hover:bg-stone-100 border border-stone-200'
                }`}
              >
                All
              </button>
              {['Environment', 'Economy', 'Technology', 'Politics'].map(cat => (
                <button
                  key={cat}
                  onClick={() => { setSelectedCategory(cat); setPage(1); }}
                  className={`px-4 py-2 rounded-full text-sm font-medium transition-all ${
                    selectedCategory === cat
                      ? 'bg-stone-900 text-white shadow-lg'
                      : 'bg-white text-stone-600 hover:bg-stone-100 border border-stone-200'
                  }`}
                >
                  {cat}
                </button>
              ))}
            </div>

            <div className="flex items-center space-x-2">
              <span className="text-sm text-stone-500">Sort by</span>
              <select
                value={sortBy}
                onChange={(e) => { setSortBy(e.target.value); setPage(1); }}
                className="border border-stone-300 rounded-lg px-3 py-2 bg-white text-stone-700 text-sm focus:ring-2 focus:ring-stone-500 focus:border-transparent"
              >
                <option value="hot_score">Hot</option>
                <option value="view_count">Views</option>
                <option value="created_at">Latest</option>
              </select>
            </div>
          </div>
        </div>
      </section>

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
          <p className="text-stone-500 text-lg">No stories found</p>
        </section>
      ) : (
        <>
          {/* Featured */}
          {featuredStory && (
            <section className="container mx-auto px-6 py-12">
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
                    <span>{featuredStory.sourceCount} Sources</span>
                    <span>{featuredStory.viewCount?.toLocaleString() || 0} Views</span>
                    <span>{featuredStory.hotScore?.toFixed(1) || 0} Hot</span>
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
                            {event.category}
                          </span>
                        </div>
                        <h3 className="text-lg font-bold text-stone-900 mb-2 line-clamp-2 group-hover:text-stone-700 transition-colors">
                          {event.title}
                        </h3>
                        <p className="text-stone-500 text-sm leading-relaxed mb-4 line-clamp-3">
                          {event.summary}
                        </p>
                        <div className="flex items-center justify-between pt-3 border-t border-stone-100 text-xs text-stone-400">
                          <span>{event.sourceCount} sources</span>
                          <span>{event.hotScore?.toFixed(1) || 0} hot</span>
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
                    Previous
                  </button>
                  <span className="text-sm text-stone-500">
                    Page {page} of {totalPages}
                  </span>
                  <button
                    onClick={() => setPage(p => Math.min(totalPages, p + 1))}
                    disabled={page >= totalPages}
                    className="px-5 py-2.5 bg-white border border-stone-200 rounded-full text-sm font-medium text-stone-700 hover:bg-stone-50 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
                  >
                    Next
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
