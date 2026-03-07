'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Header from '../components/Header';
import EventCard from '../components/EventCard';

// API 配置
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080';

// 类型定义
interface Event {
  id: string;
  title: string;
  summary?: string;
  category?: string;
  sourceCount: number;
  viewCount?: number;
  hotScore?: number;
  occurredAt?: string;
  storyAngle?: string;
  storyTeaser?: string;
}

// 自定义图标
const Icons = {
  Globe: () => (
    <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3.055 11H5a2 2 0 012 2v1a2 2 0 002 2 2 2 0 012 2v2.945M8 3.935V5.5A2.5 2.5 0 0010.5 8h.5a2 2 0 012 2 2 2 0 104 0 2 2 0 012-2h1.064M15 20.488V18a2 2 0 012-2h3.064M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
    </svg>
  ),
  BookOpen: () => (
    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
    </svg>
  ),
  Compass: () => (
    <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z" />
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
  Quote: () => (
    <svg className="w-8 h-8" fill="currentColor" viewBox="0 0 24 24">
      <path d="M14.017 21v-7.391c0-5.704 3.731-9.57 8.983-10.609l.995 2.151c-2.432.917-3.995 3.638-3.995 5.849h4v10h-9.983zm-14.017 0v-7.391c0-5.704 3.748-9.57 9-10.609l.996 2.151c-2.433.917-3.996 3.638-3.996 5.849h3.983v10h-9.983z" />
    </svg>
  ),
  Refresh: () => (
    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
    </svg>
  ),
};

// Category styles
const categoryStyles = {
  'Environment': {
    gradient: 'from-emerald-500 to-teal-600',
    bg: 'bg-emerald-50',
    text: 'text-emerald-700',
    border: 'border-emerald-200',
  },
  'Economy': {
    gradient: 'from-blue-500 to-indigo-600',
    bg: 'bg-blue-50',
    text: 'text-blue-700',
    border: 'border-blue-200',
  },
  'Technology': {
    gradient: 'from-violet-500 to-purple-600',
    bg: 'bg-violet-50',
    text: 'text-violet-700',
    border: 'border-violet-200',
  },
  'Politics': {
    gradient: 'from-amber-500 to-orange-600',
    bg: 'bg-amber-50',
    text: 'text-amber-700',
    border: 'border-amber-200',
  },
} as const;

// Default style for unknown categories
const defaultCategoryStyle = {
  gradient: 'from-stone-500 to-gray-600',
  bg: 'bg-stone-50',
  text: 'text-stone-700',
  border: 'border-stone-200',
};

// Helper function to get category style safely
const getCategoryStyle = (category: string | undefined) => {
  if (!category || !(category in categoryStyles)) {
    return defaultCategoryStyle;
  }
  return categoryStyles[category as keyof typeof categoryStyles];
};

// Default stories (fallback when API fails)
const defaultStories: Event[] = [
  {
    id: 'e62c83ae-94e9-41b8-8322-0a675f057a5a',
    title: 'Global Climate Summit Reaches New Agreement, Nations Commit to Carbon Reduction',
    summary: 'Two-week climate summit concludes in Dubai with nearly 200 countries agreeing to phase out fossil fuels.',
    category: 'Environment',
    sourceCount: 8,
    viewCount: 12453,
    hotScore: 95.8,
    occurredAt: new Date().toISOString(),
    storyAngle: 'The Beginning of Change',
    storyTeaser: 'When representatives from small island nations shed tears at the negotiating table, the world finally heard their cry.',
  },
  {
    id: '5724c881-6dd5-44ae-a37e-6bbb854bdcb0',
    title: 'Fed Announces Interest Rate Hold, Inflation Pressures Remain',
    summary: 'Federal Reserve Committee decides to maintain benchmark rate at 5.25%-5.50% range.',
    category: 'Economy',
    sourceCount: 5,
    viewCount: 8234,
    hotScore: 88.5,
    occurredAt: new Date().toISOString(),
    storyAngle: 'The Invisible Battlefield',
    storyTeaser: 'Behind every number lies the livelihood of millions.',
  },
  {
    id: '0eeafff2-5e27-45a2-9b18-034105eff7f9',
    title: 'AI Regulation Bill Passes European Parliament',
    summary: 'European Parliament passes AI Act with overwhelming majority, implementing strict oversight on high-risk AI systems.',
    category: 'Technology',
    sourceCount: 6,
    viewCount: 9876,
    hotScore: 92.3,
    occurredAt: new Date().toISOString(),
    storyAngle: 'Key to the Future',
    storyTeaser: 'In the corners of laboratories, the future is being written.',
  },
];

export default function Home() {
  const router = useRouter();
  const [events, setEvents] = useState<Event[]>([]);
  const [sortBy, setSortBy] = useState('hot_score');
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [hoveredStory, setHoveredStory] = useState<string | null>(null);

  // 从 API 获取数据
  const fetchEvents = async () => {
    try {
      setIsLoading(true);
      setError(null);
      
      const params = new URLSearchParams({
        page: '1',
        page_size: '20',
        sort_by: sortBy,
      });
      
      if (selectedCategory) {
        params.append('category', selectedCategory);
      }
      
      const response = await fetch(`${API_BASE_URL}/api/events?${params}`);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      
      // 为每个事件添加故事化字段（如果后端没有返回）
      const enrichedEvents = data.items.map((event: Event) => ({
        ...event,
        storyAngle: event.storyAngle || getCategoryStoryAngle(event.category),
        storyTeaser: event.storyTeaser || getCategoryStoryTeaser(event.category, event.title),
      }));
      
      setEvents(enrichedEvents);
    } catch (err) {
      console.error('Failed to fetch events:', err);
      setError('Unable to connect to server, using default data');
      setEvents(defaultStories);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchEvents();
  }, [sortBy, selectedCategory]);

  // Helper: Get story angle by category
  const getCategoryStoryAngle = (category?: string): string => {
    const angles: Record<string, string> = {
      'Environment': 'The Beginning of Change',
      'Economy': 'The Invisible Battlefield',
      'Technology': 'Key to the Future',
      'Politics': 'The Shift of Power',
    };
    return angles[category || ''] || 'Unfolding Now';
  };

  // Helper: Get story teaser by category
  const getCategoryStoryTeaser = (category?: string, title?: string): string => {
    const teasers: Record<string, string> = {
      'Environment': 'When nature sounds the alarm, humanity finally listens.',
      'Economy': 'Behind every number lies the livelihood of millions.',
      'Technology': 'In the corners of laboratories, the future is being written.',
      'Politics': 'The game of power, the fate of ordinary people.',
    };
    return teasers[category || ''] || 'Where the story begins.';
  };

  const featuredStory = events[0];
  const regularStories = events.slice(1);

  return (
    <div className="min-h-screen bg-stone-50">
      <Header />
      
      <main>
        {/* 故事化 Hero */}
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
                  <p className="text-sm text-slate-400">What's Really Happening In The World</p>
                </div>
              </div>
              
              <h2 className="text-5xl md:text-7xl font-bold mb-6 leading-tight">
                Every News Story,<br/>
                <span className="text-transparent bg-clip-text bg-gradient-to-r from-amber-200 via-orange-200 to-amber-200">
                  Is the Beginning of a Story
                </span>
              </h2>
              
              <p className="text-xl md:text-2xl text-slate-300 mb-12 leading-relaxed max-w-2xl">
                In this age of information overload, we help you slow down,<br/>
                See multiple perspectives, hear different voices.
              </p>
              
              <div className="flex flex-wrap gap-6">
                <div className="flex items-center space-x-3 bg-white/10 px-5 py-3 rounded-full backdrop-blur-sm border border-white/20">
                  <div className="w-2.5 h-2.5 bg-gradient-to-r from-red-400 to-rose-500 rounded-full"></div>
                  <span className="text-sm font-medium">Left · Progressive View</span>
                </div>
                <div className="flex items-center space-x-3 bg-white/10 px-5 py-3 rounded-full backdrop-blur-sm border border-white/20">
                  <div className="w-2.5 h-2.5 bg-gradient-to-r from-emerald-400 to-teal-500 rounded-full"></div>
                  <span className="text-sm font-medium">Center · Objective View</span>
                </div>
                <div className="flex items-center space-x-3 bg-white/10 px-5 py-3 rounded-full backdrop-blur-sm border border-white/20">
                  <div className="w-2.5 h-2.5 bg-gradient-to-r from-blue-400 to-cyan-500 rounded-full"></div>
                  <span className="text-sm font-medium">Right · Conservative View</span>
                </div>
              </div>
            </div>
          </div>
          
          <div className="absolute bottom-0 left-0 right-0 h-32 bg-gradient-to-t from-stone-50 to-transparent"></div>
        </section>

        {/* Category Navigation */}
        <section className="sticky top-0 z-20 bg-stone-50/95 backdrop-blur-sm border-b border-stone-200">
          <div className="container mx-auto px-6 py-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2 text-sm text-stone-500">
                <Icons.Compass />
                <span>Explore Stories</span>
              </div>
              
              <div className="flex flex-wrap gap-2">
                <button
                  onClick={() => setSelectedCategory(null)}
                  className={`px-4 py-2 rounded-full text-sm font-medium transition-all duration-300 ${
                    selectedCategory === null
                      ? 'bg-stone-900 text-white shadow-lg'
                      : 'bg-white text-stone-600 hover:bg-stone-100 border border-stone-200'
                  }`}
                >
                  All Stories
                </button>
                {['Environment', 'Economy', 'Technology', 'Politics'].map(cat => (
                  <button
                    key={cat}
                    onClick={() => setSelectedCategory(cat)}
                    className={`px-4 py-2 rounded-full text-sm font-medium transition-all duration-300 ${
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
                <button
                  onClick={fetchEvents}
                  className="p-2 text-stone-500 hover:text-stone-700 hover:bg-stone-100 rounded-lg transition-all"
                  title="Refresh Data"
                >
                  <Icons.Refresh />
                </button>
                <span className="text-sm text-stone-500">Sort by</span>
                <select
                  value={sortBy}
                  onChange={(e) => setSortBy(e.target.value)}
                  className="border border-stone-300 rounded-lg px-3 py-2 bg-white text-stone-700 text-sm focus:ring-2 focus:ring-stone-500 focus:border-transparent"
                >
                  <option value="hot_score">🔥 Hot</option>
                  <option value="view_count">👁 Views</option>
                  <option value="created_at">🕐 Time</option>
                </select>
              </div>
            </div>
          </div>
        </section>

        {/* Error Message */}
        {error && (
          <div className="container mx-auto px-6 py-4">
            <div className="bg-amber-50 border border-amber-200 rounded-lg p-4 text-amber-800">
              <p>⚠️ {error}</p>
              <p className="text-sm mt-1">Tip: Make sure the backend is running at {API_BASE_URL}</p>
            </div>
          </div>
        )}

      {/* Loading State */}
      {isLoading ? (
        <section className="container mx-auto px-6 py-12">
          <div className="animate-pulse bg-stone-200 rounded-3xl h-96"></div>
        </section>
      ) : featuredStory ? (
          <section className="container mx-auto px-6 py-12">
            <div className="mb-8">
              <span className="text-sm font-medium text-stone-500 uppercase tracking-wider">Featured Story</span>
            </div>
            
            <article 
              onClick={() => router.push(`/events/${featuredStory.id}`)}
              className={`group relative overflow-hidden rounded-3xl bg-gradient-to-br ${getCategoryStyle(featuredStory.category).gradient} p-8 md:p-12 text-white shadow-2xl transition-all duration-500 hover:shadow-3xl cursor-pointer`}
              onMouseEnter={() => setHoveredStory(featuredStory.id)}
              onMouseLeave={() => setHoveredStory(null)}
            >
              <div className="absolute top-0 right-0 w-96 h-96 bg-white/10 rounded-full -translate-y-1/2 translate-x-1/2 blur-3xl"></div>
              <div className="absolute bottom-0 left-0 w-64 h-64 bg-white/10 rounded-full translate-y-1/2 -translate-x-1/2 blur-2xl"></div>
              
              <div className="relative z-10 grid md:grid-cols-2 gap-8 items-center">
                <div>
                  <div className="flex items-center space-x-3 mb-6">
                    <span className="inline-block bg-white/20 backdrop-blur-sm px-4 py-1.5 rounded-full text-sm font-medium">
                      {featuredStory.category}
                    </span>
                    <span className="text-white/70">·</span>
                    <span className="text-sm text-white/80">{featuredStory.storyAngle}</span>
                  </div>
                  
                  <h3 className="text-3xl md:text-4xl font-bold mb-6 leading-tight">
                    {featuredStory.title}
                  </h3>
                  
                  <div className="mb-6">
                    <div className="flex items-start space-x-3">
                      <div className="text-white/60 mt-1">
                        <Icons.Quote />
                      </div>
                      <p className="text-lg md:text-xl text-white/90 leading-relaxed italic">
                        {featuredStory.storyTeaser}
                      </p>
                    </div>
                  </div>
                  
                  <p className="text-white/80 leading-relaxed mb-8">
                    {featuredStory.summary}
                  </p>
                  
                  <div className="flex items-center space-x-4 mb-8">
                    <span className="text-sm text-white/70">Multi-perspective Analysis</span>
                    <div className="flex space-x-2">
                      <div className="w-8 h-8 rounded-full bg-gradient-to-r from-red-400 to-rose-500 flex items-center justify-center text-xs font-bold">L</div>
                      <div className="w-8 h-8 rounded-full bg-gradient-to-r from-emerald-400 to-teal-500 flex items-center justify-center text-xs font-bold">C</div>
                      <div className="w-8 h-8 rounded-full bg-gradient-to-r from-blue-400 to-cyan-500 flex items-center justify-center text-xs font-bold">R</div>
                    </div>
                  </div>
                  
                  <div className="flex items-center space-x-4">
                    <div className="group/btn inline-flex items-center space-x-2 bg-white text-stone-900 px-6 py-3 rounded-full font-semibold hover:bg-stone-100 transition-all duration-300 shadow-lg hover:shadow-xl">
                      <span>Read Full Story</span>
                      <span className="group-hover/btn:translate-x-1 transition-transform duration-300">
                        <Icons.ArrowRight />
                      </span>
                    </div>
                    <div className="flex items-center space-x-4 text-sm text-white/70">
                      <span>{featuredStory.sourceCount} Sources</span>
                      <span>·</span>
                      <span>{featuredStory.viewCount?.toLocaleString() || 0} Reads</span>
                    </div>
                  </div>
                </div>
                
                <div className="hidden md:flex items-center justify-center">
                  <div className="relative">
                    <div className="w-64 h-64 rounded-full border-2 border-white/20 absolute animate-spin-slow" style={{ animationDuration: '20s' }}></div>
                    <div className="w-56 h-56 rounded-full border-2 border-white/30 absolute animate-spin-slow" style={{ animationDuration: '15s', animationDirection: 'reverse' }}></div>
                    <div className="w-48 h-48 rounded-full bg-white/10 backdrop-blur-sm flex items-center justify-center">
                      <div className="text-6xl">
                        {featuredStory.category === 'Environment' && '🌍'}
                        {featuredStory.category === 'Economy' && '💰'}
                        {featuredStory.category === 'Technology' && '🚀'}
                        {featuredStory.category === 'Politics' && '🏛️'}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </article>
          </section>
        ) : (
          <section className="container mx-auto px-6 py-12">
            <div className="text-center py-20">
              <p className="text-stone-500 text-lg">No Stories Yet</p>
              <p className="text-stone-400 text-sm mt-2">Backend API may not have data</p>
            </div>
          </section>
        )}

        {/* More Stories */}
        {!isLoading && regularStories.length > 0 && (
          <section className="container mx-auto px-6 py-12">
            <div className="mb-8">
              <span className="text-sm font-medium text-stone-500 uppercase tracking-wider">More Stories</span>
            </div>
            
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
              {regularStories.map((event, index) => (
                <article
                  key={event.id}
                  onClick={() => router.push(`/events/${event.id}`)}
                  className="group bg-white rounded-2xl border border-stone-200 overflow-hidden hover:shadow-xl hover:border-stone-300 transition-all duration-300 cursor-pointer"
                  style={{ animationDelay: `${index * 100}ms` }}
                >
                  <div className={`h-1.5 bg-gradient-to-r ${getCategoryStyle(event.category).gradient}`}></div>
                  
                  <div className="p-6">
                    <div className="flex items-center justify-between mb-4">
                      <span className={`inline-block px-3 py-1 rounded-full text-xs font-medium ${getCategoryStyle(event.category).bg} ${getCategoryStyle(event.category).text}`}>
                        {event.category}
                      </span>
                      <span className="text-xs text-stone-500">{event.storyAngle}</span>
                    </div>
                    
                    <h4 className="text-xl font-bold text-stone-900 mb-3 line-clamp-2 group-hover:text-stone-700 transition-colors duration-200">
                      {event.title}
                    </h4>
                    
                    <p className="text-stone-600 text-sm leading-relaxed mb-4 line-clamp-2 italic">
                      {event.storyTeaser}
                    </p>
                    
                    <p className="text-stone-500 text-sm leading-relaxed mb-6 line-clamp-2">
                      {event.summary}
                    </p>
                    
                    <div className="flex items-center justify-between pt-4 border-t border-stone-100">
                      <div className="flex items-center space-x-3 text-xs text-stone-500">
                        <span className="flex items-center">
                          <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
                          </svg>
                          {event.sourceCount}
                        </span>
                        <span>·</span>
                        <span>{event.hotScore?.toFixed(1) || 0}° Hot</span>
                      </div>
                      
                      <div className="flex space-x-1">
                        <div className="w-2 h-2 rounded-full bg-gradient-to-r from-red-400 to-rose-500"></div>
                        <div className="w-2 h-2 rounded-full bg-gradient-to-r from-emerald-400 to-teal-500"></div>
                        <div className="w-2 h-2 rounded-full bg-gradient-to-r from-blue-400 to-cyan-500"></div>
                      </div>
                    </div>
                  </div>
                </article>
              ))}
            </div>
          </section>
        )}

        {/* Why Multi-perspective */}
        <section className="bg-stone-900 text-stone-100 py-20 mt-20">
          <div className="container mx-auto px-6">
            <div className="max-w-3xl mx-auto text-center">
              <div className="w-16 h-16 bg-gradient-to-br from-amber-400 to-orange-500 rounded-2xl flex items-center justify-center mx-auto mb-8 shadow-lg">
                <Icons.Sparkles />
              </div>
              
              <h3 className="text-3xl md:text-4xl font-bold mb-6">
                Why Do We Need Multi-perspective?
              </h3>
              
              <p className="text-lg text-stone-300 leading-relaxed mb-8">
                Every news story is the result of editorial choices.<br/>
                What did they choose? What did they ignore?<br/>
                We believe truth is not in a single voice,<br/>
                But in the dialogue between different perspectives.
              </p>
              
              <div className="grid md:grid-cols-3 gap-8 mt-12">
                <div className="text-center">
                  <div className="text-4xl mb-4">📰</div>
                  <h4 className="font-semibold mb-2">Multi-source Aggregation</h4>
                  <p className="text-sm text-stone-400">Hundreds of media, one event</p>
                </div>
                <div className="text-center">
                  <div className="text-4xl mb-4">🤖</div>
                  <h4 className="font-semibold mb-2">AI Summary</h4>
                  <p className="text-sm text-stone-400">Left, Center, Right - Three Views</p>
                </div>
                <div className="text-center">
                  <div className="text-4xl mb-4">🔍</div>
                  <h4 className="font-semibold mb-2">Bias Analysis</h4>
                  <p className="text-sm text-stone-400">Identify Stance, Think Independently</p>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* 页脚 */}
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
                <a href="#" className="hover:text-stone-900 transition-colors">About Us</a>
                <a href="#" className="hover:text-stone-900 transition-colors">Editorial</a>
                <a href="#" className="hover:text-stone-900 transition-colors">Privacy</a>
                <a href="#" className="hover:text-stone-900 transition-colors">Contact</a>
              </div>
            </div>
            
            <div className="mt-8 pt-8 border-t border-stone-200 text-center text-sm text-stone-500">
              <p>© 2026 WRHITW · See the World Through Stories</p>
            </div>
          </div>
        </footer>
      </main>
    </div>
  );
}
