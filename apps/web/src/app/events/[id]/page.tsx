'use client';

import React, { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Header from '../../../components/Header';

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
  createdAt?: string;
  updatedAt?: string;
  background?: string;
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

interface EventAnalysis {
  id: string;
  event_id: string;
  background: string;
  cause_chain: Array<{ cause: string; description: string; sources: string[] }>;
  impact_analysis: Array<{ dimension: string; impact: string; affected_groups: string[] }>;
  timeline: Array<{ timestamp: string; title: string; description: string }>;
  stakeholder_perspectives: Array<{
    stakeholder_id: string;
    stakeholder_name: string;
    perspective_text: string;
    key_arguments: string[];
    sources_cited: string[];
  }>;
  disputed_claims: Array<{ claim: string; disputed_by: string; evidence: string }>;
  generated_at: string;
}

interface ThreadItem {
  id: string;
  event_id: string;
  title: string;
  content: string;
  persona_name: string;
  avatar_color: string;
  reply_count: number;
  like_count: number;
  view_count: number;
  created_at: string;
  tags: string[];
}

interface StakeholderInfo {
  id: string;
  stakeholder_id: string;
  stakeholder_name: string;
  perspective_summary: string;
  key_concerns: string[];
  is_ai_generated: boolean;
  status: string;
}

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
  Newspaper: () => (
    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1m2 13a2 2 0 01-2-2V7m2 13a2 2 0 002-2V9a2 2 0 00-2-2h-2m-4-3H9M7 16h6M7 8h6v4H7V8z" />
    </svg>
  ),
  Users: () => (
    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
    </svg>
  ),
  Chat: () => (
    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
    </svg>
  ),
  Robot: () => (
    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
    </svg>
  ),
};

const categoryStyles: Record<string, { gradient: string; bg: string; text: string; border: string }> = {
  'Environment': { gradient: 'from-emerald-500 to-teal-600', bg: 'bg-emerald-50', text: 'text-emerald-700', border: 'border-emerald-200' },
  'Economy': { gradient: 'from-blue-500 to-indigo-600', bg: 'bg-blue-50', text: 'text-blue-700', border: 'border-blue-200' },
  'Technology': { gradient: 'from-violet-500 to-purple-600', bg: 'bg-violet-50', text: 'text-violet-700', border: 'border-violet-200' },
  'Politics': { gradient: 'from-amber-500 to-orange-600', bg: 'bg-amber-50', text: 'text-amber-700', border: 'border-amber-200' },
};

const stakeholderColors = [
  { bg: 'bg-blue-50', border: 'border-blue-200', text: 'text-blue-700', dot: 'bg-blue-400' },
  { bg: 'bg-amber-50', border: 'border-amber-200', text: 'text-amber-700', dot: 'bg-amber-400' },
  { bg: 'bg-rose-50', border: 'border-rose-200', text: 'text-rose-700', dot: 'bg-rose-400' },
  { bg: 'bg-emerald-50', border: 'border-emerald-200', text: 'text-emerald-700', dot: 'bg-emerald-400' },
  { bg: 'bg-violet-50', border: 'border-violet-200', text: 'text-violet-700', dot: 'bg-violet-400' },
  { bg: 'bg-cyan-50', border: 'border-cyan-200', text: 'text-cyan-700', dot: 'bg-cyan-400' },
  { bg: 'bg-orange-50', border: 'border-orange-200', text: 'text-orange-700', dot: 'bg-orange-400' },
];

type TabKey = 'overview' | 'sources' | 'timeline';

export default function EventDetailPage() {
  const params = useParams();
  const router = useRouter();
  const eventId = params.id as string;

  const [event, setEvent] = useState<Event | null>(null);
  const [sources, setSources] = useState<Source[]>([]);
  const [analysis, setAnalysis] = useState<EventAnalysis | null>(null);
  const [threads, setThreads] = useState<ThreadItem[]>([]);
  const [stakeholders, setStakeholders] = useState<StakeholderInfo[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<TabKey>('overview');
  const [showAllPerspectives, setShowAllPerspectives] = useState(false);

  const fetchEvent = async () => {
    const response = await fetch(`${API_BASE_URL}/api/events/${eventId}`);
    if (!response.ok) throw new Error('Failed to fetch event');
    setEvent(await response.json());
  };

  const fetchSources = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/events/${eventId}/sources`);
      if (response.ok) setSources(await response.json());
    } catch {}
  };

  const fetchAnalysis = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/events/${eventId}/analysis`);
      if (response.ok) setAnalysis(await response.json());
    } catch {}
  };

  const fetchThreads = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/events/${eventId}/threads`);
      if (response.ok) {
        const data = await response.json();
        setThreads(data.items || []);
      }
    } catch {}
  };

  const fetchStakeholders = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/events/${eventId}/stakeholders`);
      if (response.ok) setStakeholders(await response.json());
    } catch {}
  };

  useEffect(() => {
    if (eventId) {
      setIsLoading(true);
      setError(null);
      Promise.all([fetchEvent(), fetchSources(), fetchAnalysis(), fetchThreads(), fetchStakeholders()])
        .then(() => setIsLoading(false))
        .catch(() => { setIsLoading(false); setError('Failed to load event'); });
    }
  }, [eventId]);

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
        <div className="container mx-auto px-6 py-12 text-center py-20">
          <h2 className="text-2xl font-bold text-stone-900 mb-4">{error || 'Event Not Found'}</h2>
          <button onClick={() => router.push('/')} className="inline-flex items-center space-x-2 bg-stone-900 text-white px-6 py-3 rounded-full font-medium hover:bg-stone-800">
            <Icons.ArrowLeft /><span>Back to Home</span>
          </button>
        </div>
      </div>
    );
  }

  const categoryStyle = categoryStyles[event.category || ''] || categoryStyles['Environment'];
  const perspectives = analysis?.stakeholder_perspectives || [];
  const timeline = analysis?.timeline || [];

  const tabs: { key: TabKey; label: string; icon: React.ReactNode; count?: number }[] = [
    { key: 'overview', label: 'Overview', icon: <Icons.Robot /> },
    { key: 'sources', label: 'Sources', icon: <Icons.Newspaper />, count: sources.length },
    { key: 'timeline', label: 'Timeline', icon: <Icons.Clock />, count: timeline.length },
  ];

  return (
    <div className="min-h-screen bg-stone-50">
      <Header />
      <main>
        {/* Back */}
        <div className="bg-white border-b border-stone-200">
          <div className="container mx-auto px-6 py-4">
            <button onClick={() => router.push('/')} className="inline-flex items-center space-x-2 text-stone-600 hover:text-stone-900">
              <Icons.ArrowLeft /><span className="font-medium">Back</span>
            </button>
          </div>
        </div>

        {/* Event Header */}
        <section className={`bg-gradient-to-br ${categoryStyle.gradient} py-12 md:py-16`}>
          <div className="container mx-auto px-6">
            <div className="max-w-4xl">
              <div className="flex items-center space-x-3 mb-6">
                <span className="inline-block bg-white/20 backdrop-blur-sm px-4 py-1.5 rounded-full text-sm font-medium text-white">{event.category}</span>
                <div className="flex items-center space-x-4 text-white/80 text-sm">
                  <span className="flex items-center space-x-1"><Icons.Eye /><span>{event.viewCount?.toLocaleString() || 0} Reads</span></span>
                  <span className="flex items-center space-x-1"><Icons.Fire /><span>{event.hotScore?.toFixed(1) || 0}</span></span>
                  <span className="flex items-center space-x-1"><Icons.Newspaper /><span>{sources.length} Sources</span></span>
                </div>
              </div>
              <h1 className="text-3xl md:text-5xl font-bold text-white mb-6 leading-tight">{event.title}</h1>
              <p className="text-lg md:text-xl text-white/90 leading-relaxed">{event.summary}</p>
            </div>
          </div>
        </section>

        {/* Tab Bar - Sticky */}
        <div className="sticky top-0 z-30 bg-white border-b border-stone-200 shadow-sm">
          <div className="container mx-auto px-6">
            <div className="max-w-5xl mx-auto flex overflow-x-auto">
                {tabs.map((tab) => (
                  <button
                    key={tab.key}
                    onClick={() => setActiveTab(tab.key)}
                    className={`flex-shrink-0 px-5 py-4 font-medium transition-colors ${
                      activeTab === tab.key
                        ? 'bg-stone-50 text-stone-900 border-b-2 border-stone-900'
                        : 'text-stone-500 hover:text-stone-900'
                    }`}
                  >
                    <div className="flex items-center space-x-2">
                      {tab.icon}
                      <span>{tab.label}</span>
                      {tab.count !== undefined && tab.count > 0 && (
                        <span className="text-xs bg-stone-200 text-stone-600 px-2 py-0.5 rounded-full">{tab.count}</span>
                      )}
                    </div>
                  </button>
                ))}
            </div>
          </div>
        </div>

        {/* Tab Content */}
        <section className="container mx-auto px-6 py-8">
          <div className="max-w-5xl mx-auto">
            <div className="bg-white rounded-2xl border border-stone-200 overflow-hidden">
              <div className="p-6 md:p-8">
                {/* Overview Tab */}
                {activeTab === 'overview' && (
                  <div className="space-y-8">
                    {analysis?.background ? (
                      <>
                        <div>
                          <h3 className="text-xl font-bold text-stone-900 mb-3">Background</h3>
                          <p className="text-stone-700 leading-relaxed">{analysis.background}</p>
                        </div>

                        {analysis.cause_chain.length > 0 && (
                          <div>
                            <h3 className="text-xl font-bold text-stone-900 mb-4">Cause Chain</h3>
                            <div className="space-y-3">
                              {analysis.cause_chain.map((item, i) => (
                                <div key={i} className="flex items-start space-x-3 bg-stone-50 rounded-lg p-4">
                                  <span className="flex-shrink-0 w-7 h-7 rounded-full bg-stone-900 text-white text-sm flex items-center justify-center font-bold">{i + 1}</span>
                                  <div>
                                    <h4 className="font-semibold text-stone-900">{item.cause}</h4>
                                    <p className="text-stone-600 text-sm mt-1">{item.description}</p>
                                  </div>
                                </div>
                              ))}
                            </div>
                          </div>
                        )}

                        {analysis.impact_analysis.length > 0 && (
                          <div>
                            <h3 className="text-xl font-bold text-stone-900 mb-4">Impact Analysis</h3>
                            <div className="grid md:grid-cols-2 gap-4">
                              {analysis.impact_analysis.map((item, i) => (
                                <div key={i} className="border border-stone-200 rounded-xl p-4">
                                  <h4 className="font-semibold text-stone-900 mb-2">{item.dimension}</h4>
                                  <p className="text-stone-600 text-sm mb-2">{item.impact}</p>
                                  {item.affected_groups.length > 0 && (
                                    <div className="flex flex-wrap gap-1">
                                      {item.affected_groups.map((g, j) => (
                                        <span key={j} className="text-xs bg-stone-100 text-stone-600 px-2 py-0.5 rounded">{g}</span>
                                      ))}
                                    </div>
                                  )}
                                </div>
                              ))}
                            </div>
                          </div>
                        )}

                        {/* Stakeholder Perspectives - embedded in Overview */}
                        {(() => {
                          const allPerspectives = perspectives.length > 0 ? perspectives : [];
                          const allStakeholders = stakeholders.length > 0 ? stakeholders : [];
                          const hasContent = allPerspectives.length > 0 || allStakeholders.length > 0;
                          if (!hasContent) return null;

                          const DEFAULT_SHOW = 3;
                          const perspectivesToShow = showAllPerspectives ? allPerspectives : allPerspectives.slice(0, DEFAULT_SHOW);
                          const stakeholdersToShow = showAllPerspectives ? allStakeholders : allStakeholders.slice(0, DEFAULT_SHOW);
                          const totalCount = allPerspectives.length || allStakeholders.length;
                          const hasMore = totalCount > DEFAULT_SHOW;

                          return (
                            <div>
                              <div className="flex items-center justify-between mb-4">
                                <div className="flex items-center space-x-2">
                                  <Icons.Users />
                                  <h3 className="text-xl font-bold text-stone-900">Stakeholder Perspectives</h3>
                                  <span className="text-sm bg-stone-200 text-stone-600 px-2 py-0.5 rounded-full">{totalCount}</span>
                                </div>
                              </div>
                              <div className="space-y-4">
                                {perspectivesToShow.length > 0 ? (
                                  perspectivesToShow.map((sp, i) => {
                                    const color = stakeholderColors[i % stakeholderColors.length];
                                    return (
                                      <div key={sp.stakeholder_id} className={`rounded-xl border ${color.border} ${color.bg} p-5`}>
                                        <div className="flex items-center space-x-2 mb-3">
                                          <div className={`w-2.5 h-2.5 rounded-full ${color.dot}`}></div>
                                          <h4 className={`font-bold ${color.text}`}>{sp.stakeholder_name}</h4>
                                        </div>
                                        <p className="text-stone-700 text-sm leading-relaxed mb-3">{sp.perspective_text}</p>
                                        {sp.key_arguments.length > 0 && (
                                          <ul className="space-y-1">
                                            {sp.key_arguments.map((arg, j) => (
                                              <li key={j} className="text-sm text-stone-600 flex items-start space-x-2">
                                                <span className="text-stone-400 mt-0.5">&#x2022;</span>
                                                <span>{arg}</span>
                                              </li>
                                            ))}
                                          </ul>
                                        )}
                                      </div>
                                    );
                                  })
                                ) : (
                                  stakeholdersToShow.map((sh, i) => {
                                    const color = stakeholderColors[i % stakeholderColors.length];
                                    return (
                                      <div key={sh.id} className={`rounded-xl border ${color.border} ${color.bg} p-5`}>
                                        <div className="flex items-center space-x-2 mb-3">
                                          <div className={`w-2.5 h-2.5 rounded-full ${color.dot}`}></div>
                                          <h4 className={`font-bold ${color.text}`}>{sh.stakeholder_name}</h4>
                                          {sh.is_ai_generated && <span className="text-xs bg-white/60 text-stone-500 px-2 py-0.5 rounded">AI</span>}
                                        </div>
                                        {sh.perspective_summary && <p className="text-stone-700 text-sm leading-relaxed mb-3">{sh.perspective_summary}</p>}
                                        {sh.key_concerns.length > 0 && (
                                          <ul className="space-y-1">
                                            {sh.key_concerns.map((c, j) => (
                                              <li key={j} className="text-sm text-stone-600">&#x2022; {c}</li>
                                            ))}
                                          </ul>
                                        )}
                                      </div>
                                    );
                                  })
                                )}
                                {hasMore && (
                                  <button
                                    onClick={() => setShowAllPerspectives(!showAllPerspectives)}
                                    className="w-full py-3 text-sm font-medium text-stone-600 hover:text-stone-900 bg-stone-50 hover:bg-stone-100 rounded-xl border border-stone-200 transition-colors"
                                  >
                                    {showAllPerspectives ? 'Show fewer perspectives' : `View all ${totalCount} perspectives`}
                                  </button>
                                )}
                              </div>
                              <div className="flex items-center space-x-2 text-xs text-stone-400 mt-3">
                                <Icons.Robot />
                                <span>AI-generated from source articles, not editorial opinions</span>
                              </div>
                            </div>
                          );
                        })()}

                        {analysis.disputed_claims.length > 0 && (
                          <div>
                            <h3 className="text-xl font-bold text-stone-900 mb-4">Disputed Claims</h3>
                            {analysis.disputed_claims.map((item, i) => (
                              <div key={i} className="bg-amber-50 border border-amber-200 rounded-lg p-4 mb-3">
                                <p className="font-medium text-amber-900">{item.claim}</p>
                                <p className="text-amber-700 text-sm mt-1">Disputed by: {item.disputed_by}</p>
                                {item.evidence && <p className="text-amber-600 text-sm mt-1">Evidence: {item.evidence}</p>}
                              </div>
                            ))}
                          </div>
                        )}

                        <div className="flex items-center space-x-2 text-sm text-stone-400 pt-4 border-t border-stone-200">
                          <Icons.Robot />
                          <span>AI-generated analysis, for reference only</span>
                        </div>
                      </>
                    ) : (
                      <div className="text-center py-12">
                        <div className="text-4xl mb-4">&#x1F916;</div>
                        <p className="text-stone-600 mb-2">Deep analysis is being generated</p>
                        <p className="text-sm text-stone-400">Check back soon for background, cause chain, and impact analysis</p>
                      </div>
                    )}
                  </div>
                )}

                {/* Sources Tab */}
                {activeTab === 'sources' && (
                  <div className="space-y-4">
                    {sources.length > 0 ? (
                      sources.map((sourceItem, index) => (
                        <div key={sourceItem.id || index} className="rounded-xl border border-stone-200 p-5 hover:border-stone-300 hover:shadow-md transition-all">
                          <div className="flex items-start justify-between mb-3">
                            <div className="flex-1">
                              <h4 className="font-semibold text-stone-900 mb-1">{sourceItem.source.name}</h4>
                              <p className="text-sm text-stone-600 line-clamp-2">{sourceItem.article_title}</p>
                            </div>
                          </div>
                          <div className="flex items-center justify-between">
                            <span className="text-xs text-stone-500">{new Date(sourceItem.published_at).toLocaleDateString('en-US')}</span>
                            <a href={sourceItem.article_url} target="_blank" rel="noopener noreferrer" className="flex items-center space-x-1 text-sm text-blue-600 hover:underline">
                              <span>Read Original</span>
                              <Icons.ExternalLink />
                            </a>
                          </div>
                        </div>
                      ))
                    ) : (
                      <div className="text-center py-12">
                        <div className="text-4xl mb-4">&#x1F4F0;</div>
                        <p className="text-stone-600">No sources yet</p>
                      </div>
                    )}
                  </div>
                )}

                {/* Timeline Tab */}
                {activeTab === 'timeline' && (
                  <div className="space-y-6">
                    {timeline.length > 0 ? (
                      timeline.map((item, index) => (
                        <div key={index} className="relative pl-8 pb-6 border-l-2 border-stone-200 last:pb-0">
                          <div className="absolute left-0 top-0 w-4 h-4 rounded-full bg-stone-400 border-2 border-white transform -translate-x-1/2"></div>
                          <div className="bg-stone-50 rounded-lg p-4">
                            <div className="flex items-center space-x-2 mb-2">
                              <Icons.Clock />
                              <span className="text-sm font-medium text-stone-600">{item.timestamp}</span>
                            </div>
                            <h4 className="font-semibold text-stone-900 mb-1">{item.title}</h4>
                            <p className="text-stone-600 text-sm">{item.description}</p>
                          </div>
                        </div>
                      ))
                    ) : (
                      <div className="text-center py-12">
                        <div className="text-4xl mb-4">&#x1F552;</div>
                        <p className="text-stone-600">Timeline data is being generated</p>
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>
          </div>
        </section>

        {/* Discussion - Always Visible */}
        <section id="discussion" className="container mx-auto px-6 pb-12">
          <div className="max-w-5xl mx-auto">
            <div className="bg-white rounded-2xl border border-stone-200 overflow-hidden">
              <div className="border-b border-stone-200 px-6 py-4 flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <Icons.Chat />
                  <h2 className="text-xl font-bold text-stone-900">Discussion</h2>
                  <span className="text-sm bg-stone-200 text-stone-600 px-2.5 py-0.5 rounded-full">{threads.length}</span>
                </div>
                <button
                  onClick={() => router.push(`/events/${eventId}/threads/new`)}
                  className="bg-stone-900 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-stone-800 transition-colors"
                >
                  New Thread
                </button>
              </div>

              <div className="p-6">
                {threads.length > 0 ? (
                  <div className="space-y-4">
                    {threads.map((thread) => (
                      <div
                        key={thread.id}
                        onClick={() => router.push(`/events/${eventId}/threads/${thread.id}`)}
                        className="border border-stone-200 rounded-xl p-5 hover:border-stone-300 hover:shadow-md transition-all cursor-pointer"
                      >
                        <h4 className="font-semibold text-stone-900 mb-2 hover:text-blue-600">{thread.title}</h4>
                        <p className="text-stone-600 text-sm line-clamp-2 mb-3">{thread.content}</p>
                        <div className="flex items-center space-x-4 text-xs text-stone-500">
                          <span className="flex items-center space-x-1">
                            <span className={`w-2 h-2 rounded-full bg-${thread.avatar_color}-400`}></span>
                            <span>{thread.persona_name}</span>
                          </span>
                          <span>{thread.reply_count} replies</span>
                          <span>{thread.like_count} likes</span>
                          <span>{new Date(thread.created_at).toLocaleDateString('en-US')}</span>
                        </div>
                        {thread.tags?.length > 0 && (
                          <div className="flex flex-wrap gap-1 mt-2">
                            {thread.tags.map((tag, i) => (
                              <span key={i} className="text-xs bg-stone-100 text-stone-600 px-2 py-0.5 rounded">{tag}</span>
                            ))}
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-8">
                    <div className="text-4xl mb-4">&#x1F4AC;</div>
                    <p className="text-stone-600 mb-2">No threads yet</p>
                    <p className="text-sm text-stone-400">Be the first to start a discussion about this event</p>
                  </div>
                )}

              </div>
            </div>
          </div>
        </section>

        <footer className="bg-stone-100 border-t border-stone-200 py-12">
          <div className="container mx-auto px-6 text-center text-sm text-stone-500">
            <p>&copy; 2026 WRHITW &middot; See Every Perspective</p>
          </div>
        </footer>
      </main>
    </div>
  );
}
