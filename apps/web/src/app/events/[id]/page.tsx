'use client';

import React, { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Header from '../../../components/Header';
import StakeholderDeclare from '../../../components/StakeholderDeclare';
import { API_BASE_URL } from '../../../lib/config';


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
  updated_at?: string;
  background?: string;
}

interface Source {
  id: string;
  source: { id: string; name: string; bias_label: string; bias_score?: number };
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

const getCatClass = (cat?: string): string => {
  const map: Record<string, string> = {
    'Environment': 'cat-environment',
    'Economy': 'cat-economy',
    'Technology': 'cat-technology',
    'Politics': 'cat-politics',
    'War & Conflict': 'cat-conflict',
    'Geopolitics': 'cat-geopolitics',
    'Health': 'cat-health',
    'Science': 'cat-science',
    'Entertainment': 'cat-entertainment',
    'Society': 'cat-society',
  };
  return (cat && map[cat]) || 'bg-neutral-100 text-neutral-700';
};

const stakeholderAccents = [
  { border: 'border-l-blue-500', text: 'text-blue-700', bg: 'bg-blue-50' },
  { border: 'border-l-amber-500', text: 'text-amber-700', bg: 'bg-amber-50' },
  { border: 'border-l-rose-500', text: 'text-rose-700', bg: 'bg-rose-50' },
  { border: 'border-l-emerald-500', text: 'text-emerald-700', bg: 'bg-emerald-50' },
  { border: 'border-l-violet-500', text: 'text-violet-700', bg: 'bg-violet-50' },
  { border: 'border-l-cyan-500', text: 'text-cyan-700', bg: 'bg-cyan-50' },
  { border: 'border-l-orange-500', text: 'text-orange-700', bg: 'bg-orange-50' },
];

type TabKey = 'overview' | 'perspectives' | 'analysis' | 'sources' | 'timeline';

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
      Promise.all([fetchEvent(), fetchSources(), fetchThreads(), fetchStakeholders()])
        .then(() => setIsLoading(false))
        .catch(() => { setIsLoading(false); setError('Failed to load event'); });
      fetchAnalysis();
    }
  }, [eventId]);

  if (isLoading) {
    return (
      <div className="min-h-screen bg-neutral-50">
        <Header />
        <div className="container mx-auto px-6 py-12">
          <div className="animate-pulse space-y-6 max-w-3xl">
            <div className="h-6 bg-neutral-200 rounded w-1/4"></div>
            <div className="h-10 bg-neutral-200 rounded w-3/4"></div>
            <div className="h-4 bg-neutral-200 rounded w-full"></div>
            <div className="h-4 bg-neutral-200 rounded w-2/3"></div>
          </div>
        </div>
      </div>
    );
  }

  if (error || !event) {
    return (
      <div className="min-h-screen bg-neutral-50">
        <Header />
        <div className="container mx-auto px-6 py-20 text-center">
          <h2 className="font-serif text-title text-neutral-900 mb-4">{error || 'Event Not Found'}</h2>
          <button onClick={() => router.push('/')} className="text-sm text-neutral-500 hover:text-neutral-900 underline">
            Back to Home
          </button>
        </div>
      </div>
    );
  }

  const perspectives = analysis?.stakeholder_perspectives || [];
  const timeline = analysis?.timeline || [];
  const perspectiveCount = perspectives.length || stakeholders.length;

  const tabs: { key: TabKey; label: string; count?: number }[] = [
    { key: 'overview', label: 'Overview' },
    { key: 'perspectives', label: 'Perspectives', count: perspectiveCount },
    { key: 'analysis', label: 'Deep Analysis' },
    { key: 'sources', label: 'Sources', count: sources.length },
    { key: 'timeline', label: 'Timeline', count: timeline.length },
  ];

  return (
    <div className="min-h-screen bg-neutral-50">
      <Header />
      <main>
        {/* Back + Event Header */}
        <section className="bg-white border-b border-neutral-200">
          <div className="container mx-auto px-6 pt-6 pb-8">
            <button onClick={() => router.push('/')} className="text-sm text-neutral-500 hover:text-neutral-900 mb-6 inline-block">
              &larr; Back
            </button>
            <div className="max-w-3xl">
              <div className="flex items-center gap-3 mb-4">
                <span className={`text-xs px-2.5 py-0.5 rounded-md font-medium ${getCatClass(event.category)}`}>{event.category}</span>
                <span className="text-xs text-neutral-400">{event.view_count?.toLocaleString() || 0} reads</span>
                <span className="text-xs text-neutral-400">{sources.length} sources</span>
              </div>
              <h1 className="font-serif text-3xl md:text-4xl font-bold text-neutral-900 mb-4 leading-tight">{event.title}</h1>
              <p className="text-neutral-600 leading-relaxed">{event.summary}</p>
            </div>
          </div>
        </section>

        {/* Tab Bar — Sticky */}
        <div className="sticky top-[57px] z-30 bg-white border-b border-neutral-200">
          <div className="container mx-auto px-6">
            <div className="max-w-3xl flex">
              {tabs.map((tab) => (
                <button
                  key={tab.key}
                  onClick={() => setActiveTab(tab.key)}
                  className={`px-4 py-3 text-sm transition-colors border-b-2 ${
                    activeTab === tab.key
                      ? 'text-neutral-900 font-semibold border-neutral-900'
                      : 'text-neutral-500 hover:text-neutral-900 border-transparent'
                  }`}
                >
                  {tab.label}
                  {tab.count !== undefined && tab.count > 0 && (
                    <span className="ml-1.5 text-xs text-neutral-400">{tab.count}</span>
                  )}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Tab Content */}
        <section className="container mx-auto px-6 py-8">
          <div className="max-w-3xl">

            {/* ===== Overview Tab ===== */}
            {activeTab === 'overview' && (
              <div className="space-y-6">
                {analysis?.background ? (
                  <>
                    <div>
                      <h3 className="font-serif text-title text-neutral-900 mb-3">Background</h3>
                      <p className="text-neutral-700 leading-relaxed">
                        {analysis.background.length > 600
                          ? analysis.background.slice(0, 600) + '...'
                          : analysis.background}
                      </p>
                      {analysis.background.length > 600 && (
                        <button
                          onClick={() => setActiveTab('analysis')}
                          className="text-sm text-accent hover:underline mt-2"
                        >
                          Read full analysis
                        </button>
                      )}
                    </div>

                    {/* Quick Stats */}
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                      <button onClick={() => setActiveTab('perspectives')} className="border border-neutral-200 rounded-lg p-4 text-left hover:border-neutral-400 transition-colors bg-white">
                        <div className="text-2xl font-serif font-bold text-neutral-900">{perspectiveCount}</div>
                        <div className="text-xs text-neutral-500 mt-1">Perspectives</div>
                      </button>
                      <button onClick={() => setActiveTab('analysis')} className="border border-neutral-200 rounded-lg p-4 text-left hover:border-neutral-400 transition-colors bg-white">
                        <div className="text-2xl font-serif font-bold text-neutral-900">{analysis.cause_chain?.length || 0}</div>
                        <div className="text-xs text-neutral-500 mt-1">Root Causes</div>
                      </button>
                      <button onClick={() => setActiveTab('sources')} className="border border-neutral-200 rounded-lg p-4 text-left hover:border-neutral-400 transition-colors bg-white">
                        <div className="text-2xl font-serif font-bold text-neutral-900">{sources.length}</div>
                        <div className="text-xs text-neutral-500 mt-1">Sources</div>
                      </button>
                      <button onClick={() => setActiveTab('timeline')} className="border border-neutral-200 rounded-lg p-4 text-left hover:border-neutral-400 transition-colors bg-white">
                        <div className="text-2xl font-serif font-bold text-neutral-900">{timeline.length}</div>
                        <div className="text-xs text-neutral-500 mt-1">Timeline</div>
                      </button>
                    </div>

                    <p className="text-xs text-neutral-400">Auto-generated from source articles. May contain inaccuracies.</p>
                  </>
                ) : (
                  <div className="text-center py-12 border border-neutral-200 rounded-lg bg-white">
                    <p className="text-neutral-600 mb-1">Analysis is being prepared</p>
                    <p className="text-sm text-neutral-400">Check back soon for background, perspectives, and impact breakdown</p>
                  </div>
                )}
              </div>
            )}

            {/* ===== Perspectives Tab ===== */}
            {activeTab === 'perspectives' && (
              <div className="space-y-4">
                <h3 className="font-serif text-title text-neutral-900 mb-2">Stakeholder Perspectives</h3>
                {perspectives.length > 0 ? (
                  perspectives.map((sp, i) => {
                    const accent = stakeholderAccents[i % stakeholderAccents.length];
                    return (
                      <div key={sp.stakeholder_id || i} className={`border-l-4 ${accent.border} bg-white border border-neutral-200 rounded-lg p-5`}>
                        <h4 className={`font-semibold ${accent.text} mb-2`}>{sp.stakeholder_name}</h4>
                        <p className="text-neutral-700 text-sm leading-relaxed mb-3">{sp.perspective_text}</p>
                        {sp.key_arguments?.length > 0 && (
                          <ul className="space-y-1">
                            {sp.key_arguments.map((arg, j) => (
                              <li key={j} className="text-sm text-neutral-600 flex items-start gap-2">
                                <span className="text-neutral-300 mt-0.5">&bull;</span>
                                <span>{arg}</span>
                              </li>
                            ))}
                          </ul>
                        )}
                      </div>
                    );
                  })
                ) : stakeholders.length > 0 ? (
                  stakeholders.map((sh, i) => {
                    const accent = stakeholderAccents[i % stakeholderAccents.length];
                    return (
                      <div key={sh.id} className={`border-l-4 ${accent.border} bg-white border border-neutral-200 rounded-lg p-5`}>
                        <h4 className={`font-semibold ${accent.text} mb-2`}>{sh.stakeholder_name}</h4>
                        {sh.perspective_summary && <p className="text-neutral-700 text-sm leading-relaxed mb-3">{sh.perspective_summary}</p>}
                        {sh.key_concerns?.length > 0 && (
                          <ul className="space-y-1">
                            {sh.key_concerns.map((c, j) => (
                              <li key={j} className="text-sm text-neutral-600">&bull; {c}</li>
                            ))}
                          </ul>
                        )}
                      </div>
                    );
                  })
                ) : (
                  <div className="text-center py-12 border border-neutral-200 rounded-lg bg-white">
                    <p className="text-neutral-600">No perspectives generated yet</p>
                  </div>
                )}
                <p className="text-xs text-neutral-400 mt-3">Generated from source articles, not editorial opinions</p>
              </div>
            )}

            {/* ===== Deep Analysis Tab ===== */}
            {activeTab === 'analysis' && (
              <div className="space-y-8">
                {analysis ? (
                  <>
                    {analysis.background && (
                      <div>
                        <h3 className="font-serif text-title text-neutral-900 mb-3">Background</h3>
                        <p className="text-neutral-700 leading-relaxed">{analysis.background}</p>
                      </div>
                    )}

                    {analysis.cause_chain?.length > 0 && (
                      <div>
                        <h3 className="font-serif text-title text-neutral-900 mb-4">Cause Chain</h3>
                        <div className="space-y-3">
                          {analysis.cause_chain.map((item, i) => (
                            <div key={i} className="flex items-start gap-4 bg-white border border-neutral-200 rounded-lg p-4">
                              <span className="flex-shrink-0 w-7 h-7 rounded-full bg-neutral-900 text-white text-sm flex items-center justify-center font-bold">{i + 1}</span>
                              <div>
                                <h4 className="font-semibold text-neutral-900">{item.cause}</h4>
                                <p className="text-neutral-600 text-sm mt-1">{item.description}</p>
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {analysis.impact_analysis?.length > 0 && (
                      <div>
                        <h3 className="font-serif text-title text-neutral-900 mb-4">Impact Analysis</h3>
                        <div className="grid md:grid-cols-2 gap-4">
                          {analysis.impact_analysis.map((item, i) => (
                            <div key={i} className="bg-white border border-neutral-200 rounded-lg p-4">
                              <h4 className="font-semibold text-neutral-900 mb-2">{item.dimension}</h4>
                              <p className="text-neutral-600 text-sm mb-2">{item.impact}</p>
                              {item.affected_groups?.length > 0 && (
                                <div className="flex flex-wrap gap-1">
                                  {item.affected_groups.map((g, j) => (
                                    <span key={j} className="text-xs bg-neutral-100 text-neutral-600 px-2 py-0.5 rounded-md">{g}</span>
                                  ))}
                                </div>
                              )}
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {analysis.disputed_claims?.length > 0 && (
                      <div>
                        <h3 className="font-serif text-title text-neutral-900 mb-4">Disputed Claims</h3>
                        {analysis.disputed_claims.map((item, i) => (
                          <div key={i} className="bg-amber-50 border border-amber-200 rounded-lg p-4 mb-3">
                            <p className="font-medium text-amber-900">{item.claim}</p>
                            <p className="text-amber-700 text-sm mt-1">Disputed by: {item.disputed_by}</p>
                            {item.evidence && <p className="text-amber-600 text-sm mt-1">Evidence: {item.evidence}</p>}
                          </div>
                        ))}
                      </div>
                    )}

                    <p className="text-xs text-neutral-400 pt-4 border-t border-neutral-200">
                      Auto-generated from source articles. May contain inaccuracies.
                    </p>
                  </>
                ) : (
                  <div className="text-center py-12 border border-neutral-200 rounded-lg bg-white">
                    <p className="text-neutral-600">Deep analysis is being prepared</p>
                  </div>
                )}
              </div>
            )}

            {/* ===== Sources Tab ===== */}
            {activeTab === 'sources' && (
              <div className="space-y-3">
                {sources.length > 0 ? (
                  sources.map((sourceItem, index) => (
                    <div key={sourceItem.id || index} className="bg-white border border-neutral-200 rounded-lg p-4 hover:border-neutral-400 transition-colors">
                      <div className="flex items-start justify-between mb-2">
                        <div className="flex-1">
                          <h4 className="font-semibold text-neutral-900 text-sm mb-1">{sourceItem.source.name}</h4>
                          <p className="text-sm text-neutral-600 line-clamp-2">{sourceItem.article_title}</p>
                        </div>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-xs text-neutral-400">{new Date(sourceItem.published_at).toLocaleDateString('en-US')}</span>
                        <a href={sourceItem.article_url} target="_blank" rel="noopener noreferrer" className="text-sm text-accent hover:underline">
                          Read Original
                        </a>
                      </div>
                    </div>
                  ))
                ) : (
                  <div className="text-center py-12 border border-neutral-200 rounded-lg bg-white">
                    <p className="text-neutral-600">No sources yet</p>
                  </div>
                )}
              </div>
            )}

            {/* ===== Timeline Tab ===== */}
            {activeTab === 'timeline' && (
              <div className="space-y-0">
                {timeline.length > 0 ? (
                  timeline.map((item, index) => (
                    <div key={index} className="relative pl-8 pb-6 border-l-2 border-neutral-200 last:pb-0">
                      <div className="absolute left-0 top-1.5 w-3 h-3 rounded-full bg-neutral-400 border-2 border-neutral-50 transform -translate-x-[7px]"></div>
                      <div className="bg-white border border-neutral-200 rounded-lg p-4">
                        <span className="text-xs text-neutral-400 mb-1 block">{item.timestamp}</span>
                        <h4 className="font-semibold text-neutral-900 mb-1">{item.title}</h4>
                        <p className="text-neutral-600 text-sm">{item.description}</p>
                      </div>
                    </div>
                  ))
                ) : (
                  <div className="text-center py-12 border border-neutral-200 rounded-lg bg-white">
                    <p className="text-neutral-600">Timeline data is being generated</p>
                  </div>
                )}
              </div>
            )}

          </div>
        </section>

        {/* Stakeholder Declaration */}
        {(perspectives.length > 0 || stakeholders.length > 0) && (
          <section className="container mx-auto px-6 pb-4">
            <div className="max-w-3xl">
              <StakeholderDeclare
                eventId={eventId}
                stakeholders={
                  perspectives.length > 0
                    ? perspectives.map(p => ({ stakeholder_id: p.stakeholder_id, stakeholder_name: p.stakeholder_name }))
                    : stakeholders.map(s => ({ stakeholder_id: s.stakeholder_id, stakeholder_name: s.stakeholder_name }))
                }
              />
            </div>
          </section>
        )}

        {/* Discussion */}
        <section id="discussion" className="container mx-auto px-6 pb-12">
          <div className="max-w-3xl">
            {/* Community reminder */}
            <div className="bg-amber-50 border border-amber-200 rounded-lg px-4 py-3 mb-4">
              <p className="text-sm text-neutral-600">
                If you&apos;re directly affected by this event, claim your stakeholder identity above. Your first-hand perspective matters most here.
              </p>
            </div>

            <div className="bg-white border border-neutral-200 rounded-lg overflow-hidden">
              <div className="border-b border-neutral-200 px-5 py-3 flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <h2 className="font-serif text-lg font-semibold text-neutral-900">Discussion</h2>
                  <span className="text-xs text-neutral-400">{threads.length}</span>
                </div>
                <button
                  onClick={() => router.push(`/events/${eventId}/threads/new`)}
                  className="bg-neutral-900 text-white px-3 py-1.5 rounded-md text-sm hover:bg-neutral-800 transition-colors"
                >
                  New Thread
                </button>
              </div>

              <div className="p-5">
                {threads.length > 0 ? (
                  <div className="space-y-3">
                    {threads.map((thread) => (
                      <div
                        key={thread.id}
                        onClick={() => router.push(`/events/${eventId}/threads/${thread.id}`)}
                        className="border border-neutral-200 rounded-lg p-4 hover:border-neutral-400 transition-colors cursor-pointer"
                      >
                        <h4 className="font-semibold text-neutral-900 mb-1.5 hover:text-accent">{thread.title}</h4>
                        <p className="text-neutral-600 text-sm line-clamp-2 mb-3">{thread.content}</p>
                        <div className="flex items-center gap-4 text-xs text-neutral-400">
                          <span>{thread.persona_name}</span>
                          <span>{thread.reply_count} replies</span>
                          <span>{thread.like_count} likes</span>
                          <span>{new Date(thread.created_at).toLocaleDateString('en-US')}</span>
                        </div>
                        {thread.tags?.length > 0 && (
                          <div className="flex flex-wrap gap-1 mt-2">
                            {thread.tags.map((tag, i) => (
                              <span key={i} className="text-xs bg-neutral-100 text-neutral-600 px-2 py-0.5 rounded-md">{tag}</span>
                            ))}
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-8">
                    <p className="text-neutral-600 mb-1">No threads yet</p>
                    <p className="text-sm text-neutral-400">Be the first to start a discussion about this event</p>
                  </div>
                )}
              </div>
            </div>
          </div>
        </section>

        <footer className="border-t border-neutral-200 py-10 bg-white">
          <div className="container mx-auto px-6 text-center text-xs text-neutral-400">
            <p>&copy; 2026 Gaze &middot; See Every Perspective</p>
          </div>
        </footer>
      </main>
    </div>
  );
}
