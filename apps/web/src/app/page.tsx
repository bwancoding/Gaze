'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Header from '../components/Header';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface TrendingEvent {
  rank: number;
  id: string;
  title: string;
  summary: string;
  keywords: string[];
  category: string;
  heat_score: number;
  status: string;
  article_count: number;
  media_count: number;
  sources: string[];
  created_at: string;
  last_updated: string;
  event_id?: string;
  published_event_id?: string;
}

// Icons
const Icons = {
  BookOpen: () => (
    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
    </svg>
  ),
  Sparkles: () => (
    <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
      <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
    </svg>
  ),
  ArrowRight: () => (
    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 8l4 4m0 0l-4 4m4-4H3" />
    </svg>
  ),
};

// Category styles
const categoryStyles: Record<string, { gradient: string; bg: string; text: string }> = {
  'Environment': { gradient: 'from-emerald-500 to-teal-600', bg: 'bg-emerald-50', text: 'text-emerald-700' },
  'Economy': { gradient: 'from-blue-500 to-indigo-600', bg: 'bg-blue-50', text: 'text-blue-700' },
  'Technology': { gradient: 'from-violet-500 to-purple-600', bg: 'bg-violet-50', text: 'text-violet-700' },
  'Politics': { gradient: 'from-amber-500 to-orange-600', bg: 'bg-amber-50', text: 'text-amber-700' },
};
const defaultStyle = { gradient: 'from-stone-500 to-gray-600', bg: 'bg-stone-50', text: 'text-stone-700' };
const getStyle = (cat?: string) => (cat && categoryStyles[cat]) || defaultStyle;

export default function Home() {
  const router = useRouter();
  const [trendingEvents, setTrendingEvents] = useState<TrendingEvent[]>([]);
  const [isTrendingLoading, setIsTrendingLoading] = useState(true);

  useEffect(() => {
    (async () => {
      try {
        setIsTrendingLoading(true);
        const response = await fetch(`${API_BASE_URL}/api/trending?limit=10&published_only=true`);
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        const data = await response.json();
        setTrendingEvents(data.events || data.items || []);
      } catch (err) {
        console.error('Failed to fetch trending:', err);
        setTrendingEvents([]);
      } finally {
        setIsTrendingLoading(false);
      }
    })();
  }, []);

  return (
    <div className="min-h-screen bg-stone-50">
      <Header />

      <main>
        {/* Hero */}
        <section className="relative overflow-hidden bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 text-white">
          <div className="absolute inset-0 opacity-10">
            <div className="absolute inset-0" style={{
              backgroundImage: `url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.4'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")`,
            }}></div>
          </div>

          <div className="relative z-10 container mx-auto px-6 py-20 md:py-32">
            <div className="max-w-4xl">
              <div className="flex items-center space-x-4 mb-8">
                <div className="w-12 h-12 bg-gradient-to-br from-amber-400 to-orange-500 rounded-lg flex items-center justify-center shadow-lg">
                  <Icons.BookOpen />
                </div>
                <div>
                  <h1 className="text-2xl font-bold tracking-tight">WRHITW</h1>
                  <p className="text-sm text-slate-400">What&apos;s Really Happening In The World</p>
                </div>
              </div>

              <h2 className="text-5xl md:text-7xl font-bold mb-6 leading-tight">
                One World,<br/>
                <span className="text-transparent bg-clip-text bg-gradient-to-r from-amber-200 via-orange-200 to-amber-200">
                  Many Voices, One Conversation
                </span>
              </h2>

              <p className="text-xl md:text-2xl text-slate-300 mb-12 leading-relaxed max-w-2xl">
                We are all stewards of this world.<br/>
                Understand each other, engage in peaceful dialogue,<br/>
                and shape our shared future under the same sky.
              </p>

              <div className="flex flex-wrap gap-6">
                <div className="flex items-center space-x-3 bg-white/10 px-5 py-3 rounded-full backdrop-blur-sm border border-white/20">
                  <div className="w-2.5 h-2.5 bg-gradient-to-r from-blue-400 to-indigo-500 rounded-full"></div>
                  <span className="text-sm font-medium">AI Deep Analysis</span>
                </div>
                <div className="flex items-center space-x-3 bg-white/10 px-5 py-3 rounded-full backdrop-blur-sm border border-white/20">
                  <div className="w-2.5 h-2.5 bg-gradient-to-r from-amber-400 to-orange-500 rounded-full"></div>
                  <span className="text-sm font-medium">Stakeholder Perspectives</span>
                </div>
                <div className="flex items-center space-x-3 bg-white/10 px-5 py-3 rounded-full backdrop-blur-sm border border-white/20">
                  <div className="w-2.5 h-2.5 bg-gradient-to-r from-emerald-400 to-teal-500 rounded-full"></div>
                  <span className="text-sm font-medium">Community Discussion</span>
                </div>
              </div>
            </div>
          </div>

          <div className="absolute bottom-0 left-0 right-0 h-32 bg-gradient-to-t from-stone-50 to-transparent"></div>
        </section>

        {/* Trending Now */}
        <section className="container mx-auto px-6 py-12">
          <div className="mb-8 flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <span className="text-2xl">🔥</span>
              <div>
                <h2 className="text-2xl font-bold text-stone-900">Trending Now</h2>
                <p className="text-sm text-stone-500">Top stories people are following worldwide</p>
              </div>
            </div>
            {!isTrendingLoading && trendingEvents.length > 0 && (
              <span className="text-sm text-stone-400">{trendingEvents.length} trending</span>
            )}
          </div>

          {isTrendingLoading ? (
            <div className="animate-pulse space-y-6">
              <div className="grid md:grid-cols-3 gap-6">
                {[1, 2, 3].map(i => <div key={i} className="bg-stone-200 rounded-2xl h-48"></div>)}
              </div>
            </div>
          ) : trendingEvents.length === 0 ? (
            <div className="text-center py-16 bg-white rounded-2xl border border-stone-200">
              <div className="text-4xl mb-4">📡</div>
              <p className="text-stone-500">No trending stories right now</p>
              <p className="text-sm text-stone-400 mt-1">Check back later for breaking stories</p>
            </div>
          ) : (
            <>
              {/* #1 — Full-width hero card */}
              {trendingEvents[0] && (() => {
                const t = trendingEvents[0];
                const style = getStyle(t.category);
                const link = t.published_event_id || t.event_id;
                return (
                  <article
                    onClick={() => link && router.push(`/events/${link}`)}
                    className={`group relative overflow-hidden rounded-3xl bg-gradient-to-br ${style.gradient} text-white p-8 md:p-12 shadow-2xl hover:shadow-3xl transition-all duration-500 mb-6 ${link ? 'cursor-pointer' : 'cursor-default'}`}
                  >
                    <div className="absolute top-0 right-0 w-96 h-96 bg-white/10 rounded-full -translate-y-1/2 translate-x-1/2 blur-3xl"></div>
                    <div className="absolute bottom-0 left-0 w-64 h-64 bg-white/5 rounded-full translate-y-1/2 -translate-x-1/3 blur-2xl"></div>
                    <div className="relative z-10 grid md:grid-cols-3 gap-8">
                      <div className="md:col-span-2">
                        <div className="flex items-center space-x-3 mb-6">
                          <span className="bg-white/25 backdrop-blur-sm px-4 py-1.5 rounded-full text-sm font-bold shadow-lg">
                            🔥 #1 Trending
                          </span>
                          <span className="bg-white/15 px-3 py-1 rounded-full text-xs font-medium">{t.category}</span>
                        </div>
                        <h3 className="text-2xl md:text-4xl font-bold mb-4 leading-tight">
                          {t.title}
                        </h3>
                        <p className="text-base md:text-lg text-white/85 leading-relaxed mb-6 line-clamp-3">
                          {t.summary}
                        </p>
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
                            <span>{t.heat_score.toFixed(0)}° heat</span>
                          </span>
                          <span>{t.sources?.length || t.media_count} media sources</span>
                        </div>
                      </div>
                      <div className="hidden md:flex items-center justify-center">
                        <div className="w-40 h-40 rounded-full bg-white/10 backdrop-blur-sm flex items-center justify-center text-7xl">
                          {t.category === 'Technology' && '🤖'}
                          {t.category === 'Environment' && '🌍'}
                          {t.category === 'Economy' && '💰'}
                          {t.category === 'Politics' && '🏛️'}
                          {!['Technology', 'Environment', 'Economy', 'Politics'].includes(t.category) && '📰'}
                        </div>
                      </div>
                    </div>
                  </article>
                );
              })()}

              {/* #2 & #3 — Side-by-side medium cards */}
              {trendingEvents.length >= 2 && (
                <div className="grid md:grid-cols-2 gap-6 mb-8">
                  {trendingEvents.slice(1, 3).map((t) => {
                    const style = getStyle(t.category);
                    const link = t.published_event_id || t.event_id;
                    return (
                      <article
                        key={t.id}
                        onClick={() => link && router.push(`/events/${link}`)}
                        className={`group relative overflow-hidden rounded-2xl bg-gradient-to-br ${style.gradient} text-white p-6 md:p-8 shadow-lg hover:shadow-2xl transition-all duration-300 ${link ? 'cursor-pointer' : 'cursor-default'}`}
                      >
                        <div className="absolute top-0 right-0 w-48 h-48 bg-white/10 rounded-full -translate-y-1/2 translate-x-1/2 blur-2xl"></div>
                        <div className="relative z-10">
                          <div className="flex items-center space-x-3 mb-4">
                            <span className="bg-white/25 backdrop-blur-sm px-3 py-1 rounded-full text-xs font-bold shadow">
                              #{t.rank}
                            </span>
                            <span className="bg-white/15 px-2.5 py-0.5 rounded-full text-xs">{t.category}</span>
                            <div className="flex-1"></div>
                            <span className="text-xs text-white/60">{t.heat_score.toFixed(0)}° heat</span>
                          </div>
                          <h3 className="text-xl font-bold mb-3 line-clamp-2 leading-snug">
                            {t.title}
                          </h3>
                          <p className="text-sm text-white/80 line-clamp-2 mb-4">
                            {t.summary}
                          </p>
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
              {trendingEvents.length > 3 && (
                <div className="bg-white rounded-2xl border border-stone-200 divide-y divide-stone-100 overflow-hidden">
                  {trendingEvents.slice(3).map((t) => {
                    const style = getStyle(t.category);
                    return (
                      <div
                        key={t.id}
                        onClick={() => (t.published_event_id || t.event_id) && router.push(`/events/${t.published_event_id || t.event_id}`)}
                        className={`flex items-center px-6 py-4 hover:bg-stone-50 transition-colors ${(t.published_event_id || t.event_id) ? 'cursor-pointer' : ''}`}
                      >
                        <span className="text-lg font-bold text-stone-300 w-10 flex-shrink-0">
                          {t.rank}
                        </span>
                        <div className="flex-1 min-w-0 mr-4">
                          <h4 className="font-semibold text-stone-900 truncate">
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
                          </div>
                        </div>
                        <div className="flex items-center space-x-4 text-xs text-stone-400 flex-shrink-0">
                          <span>{t.article_count} articles</span>
                          <span className="text-amber-500 font-medium">{t.heat_score.toFixed(0)}°</span>
                        </div>
                      </div>
                    );
                  })}
                </div>
              )}
            </>
          )}

          {/* Browse all stories CTA */}
          <div className="mt-10 text-center">
            <button
              onClick={() => router.push('/stories')}
              className="inline-flex items-center space-x-2 bg-stone-900 text-white px-8 py-3.5 rounded-full font-semibold hover:bg-stone-800 transition-colors shadow-lg hover:shadow-xl"
            >
              <span>Browse All Published Stories</span>
              <Icons.ArrowRight />
            </button>
          </div>
        </section>

        {/* Why Stakeholder Perspectives */}
        <section className="bg-stone-900 text-stone-100 py-20 mt-8">
          <div className="container mx-auto px-6">
            <div className="max-w-3xl mx-auto text-center">
              <div className="w-16 h-16 bg-gradient-to-br from-amber-400 to-orange-500 rounded-2xl flex items-center justify-center mx-auto mb-8 shadow-lg">
                <Icons.Sparkles />
              </div>

              <h3 className="text-3xl md:text-4xl font-bold mb-6">
                We Share This World
              </h3>

              <p className="text-lg text-stone-300 leading-relaxed mb-4">
                Beneath the noise of headlines, there are real people — with real concerns,
                real hopes, and real stakes in every global event.
              </p>
              <p className="text-lg text-stone-300 leading-relaxed mb-8">
                WRHITW exists because we believe humanity thrives when we listen to each other.
                Not to win arguments, but to understand. Not to divide, but to find common ground
                as fellow travelers under the same vast sky.
              </p>

              <div className="grid md:grid-cols-3 gap-8 mt-12">
                <div className="text-center">
                  <div className="text-4xl mb-4">🌍</div>
                  <h4 className="font-semibold mb-2">See Every Perspective</h4>
                  <p className="text-sm text-stone-400">AI identifies who&apos;s affected and how they see it</p>
                </div>
                <div className="text-center">
                  <div className="text-4xl mb-4">🤝</div>
                  <h4 className="font-semibold mb-2">Dialogue, Not Debate</h4>
                  <p className="text-sm text-stone-400">Engage with empathy, seek understanding</p>
                </div>
                <div className="text-center">
                  <div className="text-4xl mb-4">✨</div>
                  <h4 className="font-semibold mb-2">Shape Our Future</h4>
                  <p className="text-sm text-stone-400">Together as stewards of one shared world</p>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Footer */}
        <footer className="bg-stone-100 border-t border-stone-200 py-12">
          <div className="container mx-auto px-6">
            <div className="flex flex-col md:flex-row justify-between items-center">
              <div className="flex items-center space-x-3 mb-4 md:mb-0">
                <div className="w-10 h-10 bg-gradient-to-br from-amber-400 to-orange-500 rounded-lg flex items-center justify-center text-white shadow">
                  <Icons.BookOpen />
                </div>
                <div>
                  <p className="font-semibold text-stone-900">WRHITW</p>
                  <p className="text-xs text-stone-500">See the Full Story</p>
                </div>
              </div>

              <div className="flex items-center space-x-6 text-sm text-stone-600">
                <a href="/stories" className="hover:text-stone-900 transition-colors">Stories</a>
                <a href="/about" className="hover:text-stone-900 transition-colors">About</a>
                <a href="/trending" className="hover:text-stone-900 transition-colors">Trending</a>
              </div>
            </div>

            <div className="mt-8 pt-8 border-t border-stone-200 text-center text-sm text-stone-500">
              <p>&copy; 2026 WRHITW &middot; One World, Many Voices, One Conversation</p>
            </div>
          </div>
        </footer>
      </main>
    </div>
  );
}
