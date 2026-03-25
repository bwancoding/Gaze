'use client';

import React, { useState, useEffect } from 'react';
import { useRouter, useParams } from 'next/navigation';
import Header from '../../../components/Header';
import { API_BASE_URL } from '../../../lib/config';


interface TrendingArticle {
  id: number;
  title: string;
  summary?: string;
  url: string;
  published_at?: string;
  heat_score: number;
  source_name?: string;
}

interface TrendingEventDetail {
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
  articles: TrendingArticle[];
}

function formatDate(dateStr?: string): string {
  if (!dateStr) return '';
  const date = new Date(dateStr);
  if (isNaN(date.getTime())) return '';
  return date.toLocaleDateString('en-US', {
    month: 'short', day: 'numeric', year: 'numeric', hour: '2-digit', minute: '2-digit'
  });
}

export default function TrendingEventPage() {
  const router = useRouter();
  const params = useParams();
  const eventId = params.id as string;

  const [event, setEvent] = useState<TrendingEventDetail | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!eventId) return;

    const fetchEvent = async () => {
      try {
        setIsLoading(true);
        const response = await fetch(`${API_BASE_URL}/api/trending/${eventId}`);
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        const data = await response.json();
        setEvent(data);
      } catch (err) {
        console.error('Failed to fetch trending event:', err);
        setError('Unable to load event details.');
      } finally {
        setIsLoading(false);
      }
    };

    fetchEvent();
  }, [eventId]);

  return (
    <div className="min-h-screen bg-stone-50">
      <Header />

      <main className="container mx-auto px-6 py-8 max-w-4xl">
        {/* Back Link */}
        <button
          onClick={() => router.push('/trending')}
          className="flex items-center gap-2 text-sm text-stone-500 hover:text-stone-700 mb-6 transition-colors"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
          </svg>
          Back to Trending
        </button>

        {isLoading ? (
          <div className="animate-pulse space-y-4">
            <div className="h-8 bg-stone-200 rounded w-3/4"></div>
            <div className="h-4 bg-stone-100 rounded w-1/2"></div>
            <div className="h-40 bg-stone-200 rounded-xl mt-6"></div>
          </div>
        ) : error || !event ? (
          <div className="bg-red-50 border border-red-200 rounded-lg p-6 text-red-700">
            <p>{error || 'Event not found'}</p>
          </div>
        ) : (
          <>
            {/* Event Header */}
            <div className="mb-8">
              <div className="flex items-center gap-3 mb-4 flex-wrap">
                <span className="text-sm font-medium text-orange-600 bg-orange-50 px-3 py-1 rounded-full">
                  🔥 {event.heat_score.toFixed(1)} heat
                </span>
                {event.category && (
                  <span className="text-sm font-medium text-stone-600 bg-stone-100 px-3 py-1 rounded-full">
                    {event.category}
                  </span>
                )}
                <span className="text-sm text-stone-400">
                  {event.article_count} articles from {event.sources?.length || event.media_count} sources
                </span>
              </div>

              <h1 className="text-3xl font-bold text-stone-900 mb-3">
                {event.title}
              </h1>

              {event.summary && (
                <p className="text-lg text-stone-600 leading-relaxed">
                  {event.summary}
                </p>
              )}

              <div className="flex items-center gap-4 mt-4 text-sm text-stone-400">
                <span>First reported: {formatDate(event.created_at)}</span>
                <span>Updated: {formatDate(event.last_updated)}</span>
              </div>

              {/* Keywords */}
              {event.keywords?.length > 0 && (
                <div className="flex flex-wrap gap-2 mt-4">
                  {event.keywords.map(kw => (
                    <span key={kw} className="text-xs bg-stone-100 text-stone-500 px-2 py-1 rounded">
                      {kw}
                    </span>
                  ))}
                </div>
              )}

              {/* Sources */}
              {event.sources?.length > 0 && (
                <div className="flex flex-wrap gap-2 mt-4">
                  <span className="text-sm text-stone-500">Sources:</span>
                  {event.sources.map(src => (
                    <span key={src} className="text-sm font-medium text-stone-700 bg-white border border-stone-200 px-2 py-0.5 rounded">
                      {src}
                    </span>
                  ))}
                </div>
              )}
            </div>

            {/* Articles */}
            <div>
              <h2 className="text-xl font-semibold text-stone-900 mb-4">
                Related Articles ({event.articles?.length || 0})
              </h2>

              <div className="space-y-3">
                {event.articles?.map(article => (
                  <a
                    key={article.id}
                    href={article.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="block bg-white rounded-lg border border-stone-200 p-4 hover:border-stone-300 hover:shadow-md transition-all"
                  >
                    <div className="flex items-start justify-between gap-4">
                      <div className="flex-1 min-w-0">
                        <h3 className="font-medium text-stone-900 group-hover:text-stone-700 line-clamp-2">
                          {article.title}
                        </h3>
                        {article.summary && (
                          <p className="text-sm text-stone-500 mt-1 line-clamp-2">
                            {article.summary}
                          </p>
                        )}
                        <div className="flex items-center gap-3 mt-2 text-xs text-stone-400">
                          {article.source_name && (
                            <span className="font-medium text-stone-600">
                              {article.source_name}
                            </span>
                          )}
                          <span>{formatDate(article.published_at)}</span>
                        </div>
                      </div>
                      <div className="shrink-0 text-stone-400">
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                        </svg>
                      </div>
                    </div>
                  </a>
                ))}
              </div>
            </div>
          </>
        )}
      </main>
    </div>
  );
}
