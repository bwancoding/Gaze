'use client';

import React, { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Header from '../../../components/Header';
import BiasBadge from '../../../components/BiasBadge';
import EventCard from '../../../components/EventCard';
import CommentSection from '../../../components/CommentSection';

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
  createdAt?: string;
  updatedAt?: string;
}

interface Source {
  id: string;
  source: {
    id: string;
    name: string;
    bias_label: string;
    bias_score?: number;
  };
  article_title: string;
  article_url: string;
  published_at: string;
}

interface AiSummary {
  event_id: string;
  left_perspective: {
    summary: string;
    sources: string[];
  };
  center_perspective: {
    summary: string;
    sources: string[];
  };
  right_perspective: {
    summary: string;
    sources: string[];
  };
  generated_at: string;
}

interface TimelineEvent {
  time: string;
  title: string;
  description: string;
  sourceCount?: number;
}

// 自定义图标
const Icons = {
  ArrowLeft: () => (
    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
    </svg>
  ),
  Clock: () => (
    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
    </svg>
  ),
  ExternalLink: () => (
    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
    </svg>
  ),
  Eye: () => (
    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
    </svg>
  ),
  Fire: () => (
    <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
      <path fillRule="evenodd" d="M12.395 2.553a1 1 0 00-1.45-.385c-.345.23-.614.558-.822.88-.214.33-.403.713-.57 1.116-.334.804-.614 1.768-.84 2.734a31.365 31.365 0 00-.613 3.58 2.64 2.64 0 01-.945-1.067c-.328-.68-.398-1.534-.398-2.654A1 1 0 005.05 6.05 6.981 6.981 0 003 11a7 7 0 1011.95-4.95c-.592-.591-.98-.985-1.348-1.467-.363-.476-.724-1.063-1.207-2.03zM12.12 15.12A3 3 0 017 13s.879.5 2.5.5c0-1 .5-4 1.25-4.5.5 1 .786 1.293 1.371 1.879A2.99 2.99 0 0113 13a2.99 2.99 0 01-.879 2.121z" clipRule="evenodd" />
    </svg>
  ),
  Sparkles: () => (
    <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
      <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
    </svg>
  ),
  Newspaper: () => (
    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1m2 13a2 2 0 01-2-2V7m2 13a2 2 0 002-2V9a2 2 0 00-2-2h-2m-4-3H9M7 16h6M7 8h6v4H7V8z" />
    </svg>
  ),
  Bookmark: () => (
    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 5a2 2 0 012-2h10a2 2 0 012 2v16l-7-3.5L5 21V5z" />
    </svg>
  ),
  Share: () => (
    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.368 2.684 3 3 0 00-5.368-2.684z" />
    </svg>
  ),
  Robot: () => (
    <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
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
};

// Bias label colors
const biasColors = {
  left: {
    bg: 'bg-red-50',
    text: 'text-red-700',
    border: 'border-red-200',
    gradient: 'from-red-400 to-rose-500',
    label: 'Left',
  },
  center: {
    bg: 'bg-emerald-50',
    text: 'text-emerald-700',
    border: 'border-emerald-200',
    gradient: 'from-emerald-400 to-teal-500',
    label: 'Center',
  },
  right: {
    bg: 'bg-blue-50',
    text: 'text-blue-700',
    border: 'border-blue-200',
    gradient: 'from-blue-400 to-cyan-500',
    label: 'Right',
  },
};

export default function EventDetailPage() {
  const params = useParams();
  const router = useRouter();
  const eventId = params.id as string;

  const [event, setEvent] = useState<Event | null>(null);
  const [sources, setSources] = useState<Source[]>([]);
  const [summary, setSummary] = useState<AiSummary | null>(null);
  const [relatedEvents, setRelatedEvents] = useState<Event[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'sources' | 'summary' | 'timeline'>('summary');
  const fetchEvent = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/events/${eventId}`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      setEvent(data);
    } catch (err) {
      console.error('Failed to fetch event:', err);
      setError('无法加载事件详情');
    }
  };

  // 获取事件来源
  const fetchSources = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/events/${eventId}/sources`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      setSources(data);
    } catch (err) {
      console.error('Failed to fetch sources:', err);
    }
  };

  // 获取 AI 摘要
  const fetchSummary = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/events/${eventId}/summary`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      setSummary(data);
    } catch (err) {
      console.error('Failed to fetch summary:', err);
      // 摘要可能尚未生成，不显示错误
    }
  };

  // 获取相关事件
  const fetchRelatedEvents = async () => {
    try {
      const params = new URLSearchParams({
        page: '1',
        page_size: '3',
        sort_by: 'hot_score',
      });
      if (event?.category) {
        params.append('category', event.category);
      }
      
      const response = await fetch(`${API_BASE_URL}/api/events?${params}`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      // 排除当前事件
      const related = data.items.filter((e: Event) => e.id !== eventId);
      setRelatedEvents(related);
    } catch (err) {
      console.error('Failed to fetch related events:', err);
    }
  };

  useEffect(() => {
    if (eventId) {
      setIsLoading(true);
      setError(null);
      
      Promise.all([
        fetchEvent(),
        fetchSources(),
        fetchSummary(),
      ]).then(() => {
        setIsLoading(false);
      }).catch(() => {
        setIsLoading(false);
        setError('加载失败，请刷新重试');
      });
    }
  }, [eventId]);

  // 获取相关事件（在 event 加载完成后）
  useEffect(() => {
    if (event) {
      fetchRelatedEvents();
    }
  }, [event]);

  // 生成时间线（示例数据，实际应从后端获取）
  const generateTimeline = (): TimelineEvent[] => {
    if (!event) return [];
    
    // This is a sample implementation, timeline data should come from backend
    return [
      {
        time: event.occurredAt || event.createdAt || '',
        title: 'Event Occurred',
        description: event.summary || 'Event first reported',
        sourceCount: sources.length,
      },
      {
        time: new Date().toISOString(),
        title: 'Multi-source Coverage',
        description: `${sources.length} media outlets covered this event`,
        sourceCount: sources.length,
      },
    ];
  };

  const timeline = generateTimeline();

  if (isLoading) {
    return (
      <div className="min-h-screen bg-stone-50">
        <Header />
        <div className="container mx-auto px-6 py-12">
          <div className="animate-pulse space-y-8">
            <div className="h-8 bg-stone-200 rounded w-1/4"></div>
            <div className="h-32 bg-stone-200 rounded-2xl"></div>
            <div className="h-64 bg-stone-200 rounded-2xl"></div>
          </div>
        </div>
      </div>
    );
  }

  if (error || !event) {
    return (
      <div className="min-h-screen bg-stone-50">
        <Header />
        <div className="container mx-auto px-6 py-12">
          <div className="max-w-2xl mx-auto text-center py-20">
            <div className="text-6xl mb-4">😕</div>
            <h2 className="text-2xl font-bold text-stone-900 mb-4">
              {error || 'Event Not Found'}
            </h2>
            <button
              onClick={() => router.push('/')}
              className="inline-flex items-center space-x-2 bg-stone-900 text-white px-6 py-3 rounded-full font-medium hover:bg-stone-800 transition-colors"
            >
              <Icons.ArrowLeft />
              <span>Back to Home</span>
            </button>
          </div>
        </div>
      </div>
    );
  }

  const categoryStyle = categoryStyles[event.category as keyof typeof categoryStyles] || categoryStyles['Environment'];

  return (
    <div className="min-h-screen bg-stone-50">
      <Header />
      
      <main>
        {/* Back Button */}
        <div className="bg-white border-b border-stone-200">
          <div className="container mx-auto px-6 py-4">
            <button
              onClick={() => router.push('/')}
              className="inline-flex items-center space-x-2 text-stone-600 hover:text-stone-900 transition-colors"
            >
              <Icons.ArrowLeft />
              <span className="font-medium">Back</span>
            </button>
          </div>
        </div>

        {/* Event Header */}
        <section className={`bg-gradient-to-br ${categoryStyle.gradient} py-12 md:py-16`}>
          <div className="container mx-auto px-6">
            <div className="max-w-4xl">
              <div className="flex items-center space-x-3 mb-6">
                <span className="inline-block bg-white/20 backdrop-blur-sm px-4 py-1.5 rounded-full text-sm font-medium text-white">
                  {event.category}
                </span>
                <div className="flex items-center space-x-4 text-white/80 text-sm">
                  <span className="flex items-center space-x-1">
                    <Icons.Eye />
                    <span>{event.viewCount?.toLocaleString() || 0} Reads</span>
                  </span>
                  <span className="flex items-center space-x-1">
                    <Icons.Fire />
                    <span>{event.hotScore?.toFixed(1) || 0}° Hot</span>
                  </span>
                  <span className="flex items-center space-x-1">
                    <Icons.Newspaper />
                    <span>{sources.length} Sources</span>
                  </span>
                </div>
              </div>
              
              <h1 className="text-3xl md:text-5xl font-bold text-white mb-6 leading-tight">
                {event.title}
              </h1>
              
              <p className="text-lg md:text-xl text-white/90 leading-relaxed mb-8">
                {event.summary}
              </p>
              
              <div className="flex flex-wrap gap-3">
                <button className="flex items-center space-x-2 bg-white text-stone-900 px-5 py-2.5 rounded-full font-medium hover:bg-stone-100 transition-colors shadow-lg">
                  <Icons.Bookmark />
                  <span>Save</span>
                </button>
                <button className="flex items-center space-x-2 bg-white/20 backdrop-blur-sm text-white px-5 py-2.5 rounded-full font-medium hover:bg-white/30 transition-colors border border-white/30">
                  <Icons.Share />
                  <span>Share</span>
                </button>
              </div>
            </div>
          </div>
        </section>

        {/* 内容区域 */}
        <section className="container mx-auto px-6 py-12">
          <div className="grid lg:grid-cols-3 gap-8">
            {/* 主内容区 */}
            <div className="lg:col-span-2 space-y-8">
              {/* 选项卡 */}
              <div className="bg-white rounded-2xl border border-stone-200 overflow-hidden">
                <div className="flex border-b border-stone-200">
                  <button
                    onClick={() => setActiveTab('summary')}
                    className={`flex-1 px-6 py-4 font-medium transition-colors ${
                      activeTab === 'summary'
                        ? 'bg-stone-50 text-stone-900 border-b-2 border-stone-900'
                        : 'text-stone-600 hover:text-stone-900'
                    }`}
                  >
                    <div className="flex items-center justify-center space-x-2">
                      <Icons.Sparkles />
                      <span>AI Multi-perspective Summary</span>
                    </div>
                  </button>
                  <button
                    onClick={() => setActiveTab('sources')}
                    className={`flex-1 px-6 py-4 font-medium transition-colors ${
                      activeTab === 'sources'
                        ? 'bg-stone-50 text-stone-900 border-b-2 border-stone-900'
                        : 'text-stone-600 hover:text-stone-900'
                    }`}
                  >
                    <div className="flex items-center justify-center space-x-2">
                      <Icons.Newspaper />
                      <span>Sources ({sources.length})</span>
                    </div>
                  </button>
                  <button
                    onClick={() => setActiveTab('timeline')}
                    className={`flex-1 px-6 py-4 font-medium transition-colors ${
                      activeTab === 'timeline'
                        ? 'bg-stone-50 text-stone-900 border-b-2 border-stone-900'
                        : 'text-stone-600 hover:text-stone-900'
                    }`}
                  >
                    <div className="flex items-center justify-center space-x-2">
                      <Icons.Clock />
                      <span>Timeline</span>
                    </div>
                  </button>
                </div>

                <div className="p-6 md:p-8">
                  {/* AI Summary */}
                  {activeTab === 'summary' && (
                    <div className="space-y-6">
                      {summary ? (
                        <>
                          {/* Left Perspective */}
                          <div className={`rounded-xl border-2 ${biasColors.left.border} ${biasColors.left.bg} p-6`}>
                            <div className="flex items-center space-x-3 mb-4">
                              <div className={`w-3 h-3 rounded-full bg-gradient-to-r ${biasColors.left.gradient}`}></div>
                              <h3 className={`text-lg font-bold ${biasColors.left.text}`}>
                                Left Perspective · {biasColors.left.label}
                              </h3>
                            </div>
                            <p className="text-stone-800 leading-relaxed mb-4">
                              {summary.left_perspective.summary}
                            </p>
                            {summary.left_perspective.sources.length > 0 && (
                              <div className="flex flex-wrap gap-2">
                                {summary.left_perspective.sources.map((source, idx) => (
                                  <span key={idx} className="text-xs text-stone-600 bg-white/50 px-3 py-1 rounded-full">
                                    {source}
                                  </span>
                                ))}
                              </div>
                            )}
                          </div>

                          {/* Center Perspective */}
                          <div className={`rounded-xl border-2 ${biasColors.center.border} ${biasColors.center.bg} p-6`}>
                            <div className="flex items-center space-x-3 mb-4">
                              <div className={`w-3 h-3 rounded-full bg-gradient-to-r ${biasColors.center.gradient}`}></div>
                              <h3 className={`text-lg font-bold ${biasColors.center.text}`}>
                                Center Perspective · {biasColors.center.label}
                              </h3>
                            </div>
                            <p className="text-stone-800 leading-relaxed mb-4">
                              {summary.center_perspective.summary}
                            </p>
                            {summary.center_perspective.sources.length > 0 && (
                              <div className="flex flex-wrap gap-2">
                                {summary.center_perspective.sources.map((source, idx) => (
                                  <span key={idx} className="text-xs text-stone-600 bg-white/50 px-3 py-1 rounded-full">
                                    {source}
                                  </span>
                                ))}
                              </div>
                            )}
                          </div>

                          {/* Right Perspective */}
                          <div className={`rounded-xl border-2 ${biasColors.right.border} ${biasColors.right.bg} p-6`}>
                            <div className="flex items-center space-x-3 mb-4">
                              <div className={`w-3 h-3 rounded-full bg-gradient-to-r ${biasColors.right.gradient}`}></div>
                              <h3 className={`text-lg font-bold ${biasColors.right.text}`}>
                                Right Perspective · {biasColors.right.label}
                              </h3>
                            </div>
                            <p className="text-stone-800 leading-relaxed mb-4">
                              {summary.right_perspective.summary}
                            </p>
                            {summary.right_perspective.sources.length > 0 && (
                              <div className="flex flex-wrap gap-2">
                                {summary.right_perspective.sources.map((source, idx) => (
                                  <span key={idx} className="text-xs text-stone-600 bg-white/50 px-3 py-1 rounded-full">
                                    {source}
                                  </span>
                                ))}
                              </div>
                            )}
                          </div>

                          <div className="flex items-center justify-center space-x-2 text-sm text-stone-500 pt-4 border-t border-stone-200">
                            <Icons.Robot />
                            <span>Content generated by AI, for reference only</span>
                          </div>
                        </>
                      ) : (
                        <div className="text-center py-12">
                          <div className="text-4xl mb-4">🤖</div>
                          <p className="text-stone-600 mb-4">AI Summary is being generated</p>
                          <p className="text-sm text-stone-500">Please check back later</p>
                        </div>
                      )}
                    </div>
                  )}

                  {/* Sources */}
                  {activeTab === 'sources' && (
                    <div className="space-y-4">
                      {sources.length > 0 ? (
                        sources.map((sourceItem, index) => (
                          <div
                            key={sourceItem.id || index}
                            className="rounded-xl border border-stone-200 p-5 hover:border-stone-300 hover:shadow-md transition-all"
                          >
                            <div className="flex items-start justify-between mb-3">
                              <div className="flex-1">
                                <h4 className="font-semibold text-stone-900 mb-1">
                                  {sourceItem.source.name}
                                </h4>
                                <p className="text-sm text-stone-600 line-clamp-2">
                                  {sourceItem.article_title}
                                </p>
                              </div>
                              <BiasBadge bias={sourceItem.source.bias_label} />
                            </div>
                            
                            <div className="flex items-center justify-between">
                              <span className="text-xs text-stone-500">
                                {new Date(sourceItem.published_at).toLocaleDateString('en-US')}
                              </span>
                              <a
                                href={sourceItem.article_url}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="flex items-center space-x-1 text-sm text-blue-600 hover:text-blue-700 hover:underline"
                              >
                                <span>Read Original</span>
                                <Icons.ExternalLink />
                              </a>
                            </div>
                          </div>
                        ))
                      ) : (
                        <div className="text-center py-12">
                          <div className="text-4xl mb-4">📰</div>
                          <p className="text-stone-600">No Sources Yet</p>
                          <p className="text-sm text-stone-500 mt-1">Data is being collected</p>
                        </div>
                      )}
                    </div>
                  )}

                  {/* Timeline */}
                  {activeTab === 'timeline' && (
                    <div className="space-y-6">
                      {timeline.map((item, index) => (
                        <div key={index} className="relative pl-8 pb-6 border-l-2 border-stone-200 last:pb-0">
                          <div className="absolute left-0 top-0 w-4 h-4 rounded-full bg-stone-300 border-2 border-white transform -translate-x-1/2"></div>
                          
                          <div className="bg-stone-50 rounded-lg p-4">
                            <div className="flex items-center space-x-2 mb-2">
                              <Icons.Clock />
                              <span className="text-sm font-medium text-stone-600">
                                {new Date(item.time).toLocaleString('en-US')}
                              </span>
                            </div>
                            <h4 className="font-semibold text-stone-900 mb-2">
                              {item.title}
                            </h4>
                            <p className="text-stone-600 text-sm leading-relaxed">
                              {item.description}
                            </p>
                            {item.sourceCount && (
                              <span className="inline-block mt-2 text-xs text-stone-500 bg-white px-2 py-1 rounded">
                                {item.sourceCount} Sources
                              </span>
                            )}
                          </div>
                        </div>
                      ))}
                      
                      {timeline.length === 0 && (
                        <div className="text-center py-12">
                          <div className="text-4xl mb-4">🕐</div>
                          <p className="text-stone-600">Timeline data is being collected</p>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              </div>
            </div>

            {/* Sidebar */}
            <div className="space-y-6">
              {/* Event Stats */}
              <div className="bg-white rounded-2xl border border-stone-200 p-6">
                <h3 className="font-bold text-stone-900 mb-4">Event Stats</h3>
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-stone-600">Views</span>
                    <span className="font-semibold text-stone-900">{event.viewCount?.toLocaleString() || 0}</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-stone-600">Hot Score</span>
                    <span className="font-semibold text-stone-900">{event.hotScore?.toFixed(1) || 0}°</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-stone-600">Sources</span>
                    <span className="font-semibold text-stone-900">{sources.length}</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-stone-600">Updated</span>
                    <span className="font-semibold text-stone-900 text-sm">
                      {new Date(event.updatedAt || event.createdAt || '').toLocaleDateString('en-US')}
                    </span>
                  </div>
                </div>
              </div>

              {/* Related Events */}
              {relatedEvents.length > 0 && (
                <div className="bg-white rounded-2xl border border-stone-200 p-6">
                  <h3 className="font-bold text-stone-900 mb-4">Related Events</h3>
                  <div className="space-y-4">
                    {relatedEvents.map((relatedEvent) => (
                      <div
                        key={relatedEvent.id}
                        onClick={() => router.push(`/events/${relatedEvent.id}`)}
                        className="group cursor-pointer"
                      >
                        <div className={`h-1 w-full rounded-full bg-gradient-to-r ${categoryStyles[relatedEvent.category as keyof typeof categoryStyles]?.gradient || categoryStyles['Environment'].gradient} mb-2`}></div>
                        <h4 className="font-medium text-stone-900 text-sm group-hover:text-blue-600 transition-colors line-clamp-2">
                          {relatedEvent.title}
                        </h4>
                        <div className="flex items-center space-x-2 mt-1 text-xs text-stone-500">
                          <span>{relatedEvent.sourceCount} Sources</span>
                          <span>·</span>
                          <span>{relatedEvent.hotScore?.toFixed(0) || 0}° Hot</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        </section>

        {/* 评论区 */}
        <section className="container mx-auto px-6 py-12">
          <div className="max-w-4xl">
            <CommentSection
              eventId={eventId}
              currentUser={{
                id: 'test-user-id',
                email: 'test@example.com',
              }}
            />
          </div>
        </section>

        {/* Footer */}
        <footer className="bg-stone-100 border-t border-stone-200 py-12 mt-12">
          <div className="container mx-auto px-6">
            <div className="text-center text-sm text-stone-500">
              <p>© 2026 WRHITW · See the Full Story</p>
            </div>
          </div>
        </footer>
      </main>
    </div>
  );
}
