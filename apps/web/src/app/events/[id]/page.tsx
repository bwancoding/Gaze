'use client';

import React, { useState, useEffect, useRef, useCallback } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Header from '../../../components/Header';
import StakeholderDeclare from '../../../components/StakeholderDeclare';
import StakeholderBadge from '../../../components/StakeholderBadge';
import StakeholderVoices from '../../../components/StakeholderVoices';
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
  stakeholder_name?: string;
  verification_level?: string;
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

/* ── Helpers ── */

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
    'Culture': 'cat-culture',
    'Society': 'cat-society',
  };
  return (cat && map[cat]) || 'bg-neutral-100 text-neutral-700';
};

const stakeholderAccents = [
  { border: 'border-l-[#C2410C]', text: 'text-[#C2410C]', bg: 'bg-orange-50/50' },
  { border: 'border-l-[#1E40AF]', text: 'text-[#1E40AF]', bg: 'bg-blue-50/50' },
  { border: 'border-l-[#166534]', text: 'text-[#166534]', bg: 'bg-emerald-50/50' },
  { border: 'border-l-[#92400E]', text: 'text-[#92400E]', bg: 'bg-amber-50/50' },
  { border: 'border-l-[#5B21B6]', text: 'text-[#5B21B6]', bg: 'bg-violet-50/50' },
  { border: 'border-l-[#9D174D]', text: 'text-[#9D174D]', bg: 'bg-rose-50/50' },
  { border: 'border-l-[#134E4A]', text: 'text-[#134E4A]', bg: 'bg-teal-50/50' },
];

const timeAgo = (dateStr?: string): string => {
  if (!dateStr) return '';
  const diff = Date.now() - new Date(dateStr).getTime();
  const hours = Math.floor(diff / 3600000);
  if (hours < 1) return 'just now';
  if (hours < 24) return `${hours}h ago`;
  const days = Math.floor(hours / 24);
  if (days < 7) return `${days}d ago`;
  return new Date(dateStr).toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
};

const biasLabel = (label?: string) => {
  const map: Record<string, { text: string; color: string }> = {
    'left': { text: 'Left', color: 'text-blue-600' },
    'center-left': { text: 'Center-Left', color: 'text-blue-500' },
    'center': { text: 'Center', color: 'text-neutral-500' },
    'center-right': { text: 'Center-Right', color: 'text-red-400' },
    'right': { text: 'Right', color: 'text-red-600' },
  };
  return label ? map[label] || { text: label, color: 'text-neutral-400' } : null;
};

/* ── Scroll reveal hook ── */
function useScrollReveal() {
  useEffect(() => {
    const els = document.querySelectorAll('.reveal, .reveal-left, .reveal-right, .reveal-scale');
    if (!els.length) return;
    const io = new IntersectionObserver(
      (entries) => entries.forEach((e) => { if (e.isIntersecting) { e.target.classList.add('is-visible'); io.unobserve(e.target); } }),
      { threshold: 0.12 }
    );
    els.forEach((el) => io.observe(el));
    return () => io.disconnect();
  });
}

type TabKey = 'overview' | 'discussion' | 'perspectives' | 'analysis' | 'sources' | 'timeline';

export default function EventDetailPage() {
  const params = useParams();
  const router = useRouter();
  const eventId = params.id as string;

  const [event, setEvent] = useState<Event | null>(null);
  const [sources, setSources] = useState<Source[]>([]);
  const [analysis, setAnalysis] = useState<EventAnalysis | null>(null);
  const [threads, setThreads] = useState<ThreadItem[]>([]);
  const [stakeholders, setStakeholders] = useState<StakeholderInfo[]>([]);
  const [eventComments, setEventComments] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<TabKey>('overview');
  const [sourcePage, setSourcePage] = useState(1);
  const SOURCES_PER_PAGE = 10;

  useScrollReveal();

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

  const fetchEventComments = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/comments/event/${eventId}?limit=100`);
      if (response.ok) {
        const data = await response.json();
        setEventComments(data.items || []);
      }
    } catch {}
  };

  useEffect(() => {
    if (eventId) {
      setIsLoading(true);
      setError(null);
      Promise.all([fetchEvent(), fetchSources(), fetchThreads(), fetchStakeholders(), fetchEventComments()])
        .then(() => setIsLoading(false))
        .catch(() => { setIsLoading(false); setError('Failed to load event'); });
      fetchAnalysis();
    }
  }, [eventId]);

  /* ── Loading state ── */
  if (isLoading) {
    return (
      <div className="min-h-screen" style={{ background: 'var(--color-paper)' }}>
        <Header />
        <div className="max-w-6xl mx-auto px-6 py-16">
          <div className="animate-pulse space-y-6">
            <div className="h-4 bg-neutral-200/60 rounded w-20" />
            <div className="h-10 bg-neutral-200/60 rounded w-3/4" />
            <div className="h-5 bg-neutral-200/60 rounded w-full" />
            <div className="h-5 bg-neutral-200/60 rounded w-2/3" />
            <div className="h-px bg-neutral-200/60 my-8" />
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-10">
              <div className="lg:col-span-8 space-y-4">
                <div className="h-4 bg-neutral-200/60 rounded w-full" />
                <div className="h-4 bg-neutral-200/60 rounded w-5/6" />
                <div className="h-4 bg-neutral-200/60 rounded w-4/6" />
              </div>
              <div className="lg:col-span-4 space-y-4">
                <div className="h-32 bg-neutral-200/60 rounded" />
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  /* ── Error state ── */
  if (error || !event) {
    return (
      <div className="min-h-screen" style={{ background: 'var(--color-paper)' }}>
        <Header />
        <div className="max-w-6xl mx-auto px-6 py-20 text-center">
          <h2 className="font-serif text-2xl text-neutral-900 mb-4">{error || 'Event Not Found'}</h2>
          <button onClick={() => router.push('/stories')} className="text-sm text-neutral-500 hover:text-neutral-900 underline">
            Back to Stories
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
    { key: 'discussion', label: 'Discussion', count: threads.length },
    { key: 'perspectives', label: 'Perspectives', count: perspectiveCount },
    { key: 'analysis', label: 'Deep Analysis' },
    { key: 'sources', label: 'Sources', count: sources.length },
    { key: 'timeline', label: 'Timeline', count: timeline.length },
  ];

  /* ── Source breakdown by outlet name ── */
  const sourcesByOutlet = sources.reduce<Record<string, number>>((acc, s) => {
    const name = s.source?.name || 'Unknown';
    acc[name] = (acc[name] || 0) + 1;
    return acc;
  }, {});

  return (
    <div className="min-h-screen" style={{ background: 'var(--color-paper)' }}>
      <Header />
      <main>

        {/* ── Hero Header ─────────────────────────────────── */}
        <section className="relative grain" style={{ background: 'var(--color-warm-dark)' }}>
          <div className="max-w-6xl mx-auto px-6 pt-8 pb-12 lg:pb-16">
            {/* Back link */}
            <button
              onClick={() => router.back()}
              className="text-sm text-neutral-400 hover:text-white mb-8 inline-flex items-center gap-1.5 transition-colors"
            >
              <svg width="16" height="16" viewBox="0 0 16 16" fill="none" className="opacity-60"><path d="M10 12L6 8l4-4" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/></svg>
              Back
            </button>

            <div className="max-w-4xl">
              {/* Category + meta */}
              <div className="flex items-center gap-3 mb-5">
                <span className={`text-xs px-2.5 py-1 rounded font-medium ${getCatClass(event.category)}`}>
                  {event.category}
                </span>
                <span className="text-xs text-neutral-400">{timeAgo(event.occurred_at || event.created_at)}</span>
              </div>

              {/* Title */}
              <h1 className="font-serif text-3xl md:text-4xl lg:text-[2.75rem] font-bold text-white mb-5 leading-[1.15] tracking-tight">
                {event.title}
              </h1>

              {/* Summary */}
              {event.summary && (
                <p className="text-neutral-300 text-lg leading-relaxed max-w-3xl">
                  {event.summary}
                </p>
              )}

              {/* Inline stats row */}
              <div className="flex items-center gap-6 mt-8 pt-6 border-t border-white/10">
                <div>
                  <span className="text-2xl font-serif font-bold text-white stat-number">{sources.length}</span>
                  <span className="text-xs text-neutral-400 ml-1.5 uppercase tracking-wider">Sources</span>
                </div>
                <div className="w-px h-6 bg-white/10" />
                <div>
                  <span className="text-2xl font-serif font-bold text-white stat-number">{event.view_count?.toLocaleString() || 0}</span>
                  <span className="text-xs text-neutral-400 ml-1.5 uppercase tracking-wider">Reads</span>
                </div>
                <div className="w-px h-6 bg-white/10" />
                <div>
                  <span className="text-2xl font-serif font-bold text-white stat-number">{perspectiveCount}</span>
                  <span className="text-xs text-neutral-400 ml-1.5 uppercase tracking-wider">Perspectives</span>
                </div>
                {(event.hot_score ?? 0) > 0 && (
                  <>
                    <div className="w-px h-6 bg-white/10" />
                    <div>
                      <span className="text-2xl font-serif font-bold text-[#C2410C] stat-number">{event.hot_score?.toFixed(1)}</span>
                      <span className="text-xs text-neutral-400 ml-1.5 uppercase tracking-wider">Heat</span>
                    </div>
                  </>
                )}
              </div>
            </div>
          </div>
        </section>

        {/* ── Tab Bar ──────────────────────────────────────── */}
        <div className="border-b" style={{ background: 'var(--color-paper)', borderColor: 'var(--color-rule)' }}>
          <div className="max-w-6xl mx-auto px-6">
            <div className="flex gap-1 overflow-x-auto scrollbar-hide">
              {tabs.map((tab) => (
                <button
                  key={tab.key}
                  onClick={() => setActiveTab(tab.key)}
                  className={`relative px-4 py-3.5 text-sm whitespace-nowrap transition-colors ${
                    activeTab === tab.key
                      ? 'text-neutral-900 font-semibold'
                      : 'text-neutral-400 hover:text-neutral-700'
                  }`}
                >
                  {tab.label}
                  {tab.count !== undefined && tab.count > 0 && (
                    <span className={`ml-1.5 text-xs ${activeTab === tab.key ? 'text-[#C2410C]' : 'text-neutral-300'}`}>
                      {tab.count}
                    </span>
                  )}
                  {/* Active underline */}
                  {activeTab === tab.key && (
                    <span className="absolute bottom-0 left-2 right-2 h-[2px] bg-neutral-900 rounded-full" />
                  )}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* ── Two-column body ─────────────────────────────── */}
        <div className="max-w-6xl mx-auto px-6 py-10">
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-10 lg:gap-14">

            {/* ── Main content (8 cols) ── */}
            <div className="lg:col-span-8 min-w-0">

              {/* ===== Overview Tab ===== */}
              {activeTab === 'overview' && (
                <div className="space-y-8 reveal">
                  {analysis?.background ? (
                    <>
                      <div>
                        <h3 className="font-serif text-xl text-neutral-900 mb-3">Background</h3>
                        <p className="text-neutral-600 leading-[1.8]">
                          {analysis.background.length > 800
                            ? analysis.background.slice(0, 800) + '...'
                            : analysis.background}
                        </p>
                        {analysis.background.length > 800 && (
                          <button
                            onClick={() => setActiveTab('analysis')}
                            className="text-sm text-[#C2410C] hover:underline mt-3 font-medium"
                          >
                            Read full analysis &rarr;
                          </button>
                        )}
                      </div>

                      {/* Quick stats — editorial inline */}
                      <div className="flex flex-wrap items-baseline gap-x-6 gap-y-2 py-4 border-y" style={{ borderColor: 'var(--color-rule)' }}>
                        {[
                          { label: 'Perspectives', value: perspectiveCount, tab: 'perspectives' as TabKey },
                          { label: 'Root Causes', value: analysis.cause_chain?.length || 0, tab: 'analysis' as TabKey },
                          { label: 'Sources', value: sources.length, tab: 'sources' as TabKey },
                          { label: 'Timeline Events', value: timeline.length, tab: 'timeline' as TabKey },
                          { label: 'Discussions', value: threads.length, tab: 'discussion' as TabKey },
                        ].map((stat, i, arr) => (
                          <button
                            key={stat.label}
                            onClick={() => setActiveTab(stat.tab)}
                            className="flex items-baseline gap-1.5 group"
                          >
                            <span className="font-serif font-bold text-lg stat-number group-hover:text-[#C2410C] transition-colors" style={{ color: 'var(--color-ink)' }}>{stat.value}</span>
                            <span className="text-xs uppercase tracking-wider group-hover:text-[#C2410C] transition-colors" style={{ color: 'var(--color-ink-light)' }}>{stat.label}</span>
                            {i < arr.length - 1 && <span className="text-neutral-300 ml-3">·</span>}
                          </button>
                        ))}
                      </div>

                      <p className="text-xs text-neutral-400 italic">Auto-generated from source articles. May contain inaccuracies.</p>

                      {/* Discussion preview — guide users to participate */}
                      {threads.length > 0 && (() => {
                        const previewThreads = [...threads]
                          .sort((a, b) => {
                            const aHas = a.stakeholder_name ? 1 : 0;
                            const bHas = b.stakeholder_name ? 1 : 0;
                            if (bHas !== aHas) return bHas - aHas;
                            return new Date(b.created_at).getTime() - new Date(a.created_at).getTime();
                          })
                          .slice(0, 3);
                        return (
                          <div className="pt-2">
                            <div className="flex items-center justify-between mb-4">
                              <h3 className="font-serif text-xl text-neutral-900">Join the Discussion</h3>
                              <button
                                onClick={() => setActiveTab('discussion')}
                                className="text-sm font-medium hover:underline"
                                style={{ color: 'var(--color-accent)' }}
                              >
                                View all {threads.length} threads &rarr;
                              </button>
                            </div>
                            <div className="space-y-3">
                              {previewThreads.map((thread) => (
                                <div
                                  key={thread.id}
                                  onClick={() => router.push(`/events/${eventId}/threads/${thread.id}`)}
                                  className="border rounded-lg p-4 cursor-pointer group hover:border-[#C2410C]/30 transition-colors"
                                  style={{ borderColor: 'var(--color-rule)', background: 'white' }}
                                >
                                  <h4 className="font-semibold text-neutral-900 mb-2 group-hover:text-[#C2410C] transition-colors text-sm">{thread.title}</h4>
                                  <div className="flex items-center gap-3 text-xs text-neutral-400">
                                    <span className="font-medium text-neutral-500">{thread.persona_name}</span>
                                    {thread.stakeholder_name && thread.verification_level && (
                                      <StakeholderBadge
                                        stakeholderName={thread.stakeholder_name}
                                        level={thread.verification_level as 'verified' | 'declared'}
                                        compact
                                      />
                                    )}
                                    <span>{thread.reply_count} replies</span>
                                    <span>{thread.like_count} likes</span>
                                  </div>
                                </div>
                              ))}
                            </div>
                          </div>
                        );
                      })()}
                    </>
                  ) : (
                    <div className="text-center py-16 rounded-lg border" style={{ borderColor: 'var(--color-rule)', background: 'white' }}>
                      <div className="text-3xl mb-3 opacity-30">&#9998;</div>
                      <p className="text-neutral-600 mb-1">Analysis is being prepared</p>
                      <p className="text-sm text-neutral-400">Check back soon for background, perspectives, and impact breakdown</p>
                    </div>
                  )}
                </div>
              )}

              {/* ===== Perspectives Tab ===== */}
              {activeTab === 'perspectives' && (
                <div className="space-y-5 reveal">
                  <div className="mb-2">
                    <h3 className="font-serif text-xl text-neutral-900 mb-1">Stakeholder Perspectives</h3>
                    <p className="text-sm text-neutral-400">How different groups view this event</p>
                  </div>
                  {perspectives.length > 0 ? (
                    perspectives.map((sp, i) => {
                      const accent = stakeholderAccents[i % stakeholderAccents.length];
                      return (
                        <div key={sp.stakeholder_id || i} className={`border-l-4 ${accent.border} ${accent.bg} rounded-r-lg p-5 reveal reveal-delay-${Math.min(i + 1, 4)}`}>
                          <h4 className={`font-semibold ${accent.text} mb-2 text-sm uppercase tracking-wide`}>{sp.stakeholder_name}</h4>
                          <p className="text-neutral-700 text-[0.925rem] leading-relaxed mb-3">{sp.perspective_text}</p>
                          {sp.key_arguments?.length > 0 && (
                            <ul className="space-y-1.5 mt-3 pt-3 border-t border-neutral-200/50">
                              {sp.key_arguments.map((arg, j) => (
                                <li key={j} className="text-sm text-neutral-600 flex items-start gap-2">
                                  <span className="text-neutral-300 mt-0.5 flex-shrink-0">&bull;</span>
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
                        <div key={sh.id} className={`border-l-4 ${accent.border} ${accent.bg} rounded-r-lg p-5`}>
                          <h4 className={`font-semibold ${accent.text} mb-2 text-sm uppercase tracking-wide`}>{sh.stakeholder_name}</h4>
                          {sh.perspective_summary && <p className="text-neutral-700 text-[0.925rem] leading-relaxed mb-3">{sh.perspective_summary}</p>}
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
                    <div className="text-center py-16 rounded-lg border" style={{ borderColor: 'var(--color-rule)', background: 'white' }}>
                      <p className="text-neutral-600">No perspectives generated yet</p>
                    </div>
                  )}
                  <p className="text-xs text-neutral-400 mt-4 italic">Generated from source articles, not editorial opinions</p>
                </div>
              )}

              {/* ===== Deep Analysis Tab ===== */}
              {activeTab === 'analysis' && (
                <div className="space-y-10 reveal">
                  {analysis ? (
                    <>
                      {analysis.background && (
                        <div>
                          <h3 className="font-serif text-xl text-neutral-900 mb-4">Background</h3>
                          <p className="text-neutral-600 leading-[1.8]">{analysis.background}</p>
                        </div>
                      )}

                      {analysis.cause_chain?.length > 0 && (
                        <div>
                          <h3 className="font-serif text-xl text-neutral-900 mb-5">Cause Chain</h3>
                          <div className="divide-y" style={{ borderColor: 'var(--color-rule)' }}>
                            {analysis.cause_chain.map((item, i) => (
                              <div key={i} className={`py-5 ${i === 0 ? 'pt-0' : ''}`}>
                                <h4 className="font-semibold text-neutral-900 mb-1.5">{item.cause}</h4>
                                <p className="text-neutral-600 text-sm leading-relaxed">{item.description}</p>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}

                      {analysis.impact_analysis?.length > 0 && (
                        <div>
                          <h3 className="font-serif text-xl text-neutral-900 mb-5">Impact Analysis</h3>
                          <div className="grid md:grid-cols-2 gap-4">
                            {analysis.impact_analysis.map((item, i) => (
                              <div key={i} className="p-5 rounded-lg border bg-white" style={{ borderColor: 'var(--color-rule)' }}>
                                <h4 className="font-semibold text-neutral-900 mb-2">{item.dimension}</h4>
                                <p className="text-neutral-600 text-sm leading-relaxed mb-3">{item.impact}</p>
                                {item.affected_groups?.length > 0 && (
                                  <div className="flex flex-wrap gap-1.5">
                                    {item.affected_groups.map((g, j) => (
                                      <span key={j} className="text-xs px-2 py-0.5 rounded-md" style={{ background: '#F0ECE3', color: 'var(--color-ink-light)' }}>{g}</span>
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
                          <h3 className="font-serif text-xl text-neutral-900 mb-5">Disputed Claims</h3>
                          {analysis.disputed_claims.map((item, i) => (
                            <div key={i} className="bg-amber-50/80 border border-amber-200/60 rounded-lg p-5 mb-3">
                              <p className="font-medium text-amber-900">{item.claim}</p>
                              <p className="text-amber-700 text-sm mt-2">Disputed by: {item.disputed_by}</p>
                              {item.evidence && <p className="text-amber-600 text-sm mt-1">Evidence: {item.evidence}</p>}
                            </div>
                          ))}
                        </div>
                      )}

                      <p className="text-xs text-neutral-400 pt-6 border-t italic" style={{ borderColor: 'var(--color-rule)' }}>
                        Auto-generated from source articles. May contain inaccuracies.
                      </p>
                    </>
                  ) : (
                    <div className="text-center py-16 rounded-lg border" style={{ borderColor: 'var(--color-rule)', background: 'white' }}>
                      <p className="text-neutral-600">Deep analysis is being prepared</p>
                    </div>
                  )}
                </div>
              )}

              {/* ===== Sources Tab ===== */}
              {activeTab === 'sources' && (
                <div className="space-y-3 reveal">
                  <div className="mb-4">
                    <h3 className="font-serif text-xl text-neutral-900 mb-1">Source Coverage</h3>
                    <p className="text-sm text-neutral-400">{sources.length} articles from {Object.keys(sourcesByOutlet).length} outlets</p>
                  </div>
                  {sources.length > 0 ? (
                    <>
                      {sources.slice((sourcePage - 1) * SOURCES_PER_PAGE, sourcePage * SOURCES_PER_PAGE).map((sourceItem, index) => {
                        const bias = biasLabel(sourceItem.source?.bias_label);
                        return (
                          <div
                            key={sourceItem.id || index}
                            className="p-4 rounded-lg border bg-white transition-all hover:border-neutral-300 hover:shadow-sm group"
                            style={{ borderColor: 'var(--color-rule)' }}
                          >
                            <div className="flex items-start justify-between gap-4">
                              <div className="flex-1 min-w-0">
                                <div className="flex items-center gap-2 mb-1.5">
                                  <h4 className="font-semibold text-neutral-900 text-sm">{sourceItem.source.name}</h4>
                                  {bias && <span className={`text-[10px] ${bias.color} font-medium`}>{bias.text}</span>}
                                </div>
                                <p className="text-sm text-neutral-600 line-clamp-2 leading-relaxed">{sourceItem.article_title}</p>
                              </div>
                              <a
                                href={sourceItem.article_url}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="flex-shrink-0 text-xs font-medium px-3 py-1.5 rounded-md transition-colors opacity-60 group-hover:opacity-100"
                                style={{ color: '#C2410C' }}
                              >
                                Read &rarr;
                              </a>
                            </div>
                            <div className="mt-2 text-xs text-neutral-400">
                              {new Date(sourceItem.published_at).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}
                            </div>
                          </div>
                        );
                      })}
                      {/* Pagination */}
                      {sources.length > SOURCES_PER_PAGE && (
                        <div className="flex items-center justify-between pt-4 mt-2 border-t" style={{ borderColor: 'var(--color-rule)' }}>
                          <span className="text-xs" style={{ color: 'var(--color-ink-light)' }}>
                            {(sourcePage - 1) * SOURCES_PER_PAGE + 1}&ndash;{Math.min(sourcePage * SOURCES_PER_PAGE, sources.length)} of {sources.length}
                          </span>
                          <div className="flex items-center gap-1">
                            <button
                              onClick={() => setSourcePage(p => Math.max(1, p - 1))}
                              disabled={sourcePage === 1}
                              className="px-3 py-1.5 text-sm rounded-md border transition-colors disabled:opacity-30"
                              style={{ borderColor: 'var(--color-rule)', color: 'var(--color-ink)' }}
                            >
                              Prev
                            </button>
                            <button
                              onClick={() => setSourcePage(p => Math.min(Math.ceil(sources.length / SOURCES_PER_PAGE), p + 1))}
                              disabled={sourcePage >= Math.ceil(sources.length / SOURCES_PER_PAGE)}
                              className="px-3 py-1.5 text-sm rounded-md border transition-colors disabled:opacity-30"
                              style={{ borderColor: 'var(--color-rule)', color: 'var(--color-ink)' }}
                            >
                              Next
                            </button>
                          </div>
                        </div>
                      )}
                    </>
                  ) : (
                    <div className="text-center py-16 rounded-lg border" style={{ borderColor: 'var(--color-rule)', background: 'white' }}>
                      <p className="text-neutral-600">No sources yet</p>
                    </div>
                  )}
                </div>
              )}

              {/* ===== Timeline Tab ===== */}
              {activeTab === 'timeline' && (
                <div className="reveal">
                  <div className="mb-6">
                    <h3 className="font-serif text-xl text-neutral-900 mb-1">Event Timeline</h3>
                    <p className="text-sm text-neutral-400">Key developments in chronological order</p>
                  </div>
                  {timeline.length > 0 ? (
                    <div className="space-y-0">
                      {timeline.map((item, index) => (
                        <div key={index} className="relative pl-8 pb-8 last:pb-0" style={{ borderLeft: '2px solid var(--color-rule)' }}>
                          <div
                            className="absolute left-0 top-1.5 w-3 h-3 rounded-full border-2 transform -translate-x-[7px]"
                            style={{ background: index === 0 ? '#C2410C' : 'var(--color-paper)', borderColor: index === 0 ? '#C2410C' : '#A8A29E' }}
                          />
                          <div className="p-4 rounded-lg border bg-white" style={{ borderColor: 'var(--color-rule)' }}>
                            <span className="text-xs text-neutral-400 mb-1 block font-medium">{item.timestamp}</span>
                            <h4 className="font-semibold text-neutral-900 mb-1">{item.title}</h4>
                            <p className="text-neutral-600 text-sm leading-relaxed">{item.description}</p>
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="text-center py-16 rounded-lg border" style={{ borderColor: 'var(--color-rule)', background: 'white' }}>
                      <p className="text-neutral-600">Timeline data is being generated</p>
                    </div>
                  )}
                </div>
              )}

              {/* ===== Discussion Tab ===== */}
              {activeTab === 'discussion' && (
                <div className="space-y-6 reveal">
                  {/* Stakeholder Declaration */}
                  {(perspectives.length > 0 || stakeholders.length > 0) && (
                    <StakeholderDeclare
                      eventId={eventId}
                      stakeholders={
                        perspectives.length > 0
                          ? perspectives.map(p => ({ stakeholder_id: p.stakeholder_id, stakeholder_name: p.stakeholder_name }))
                          : stakeholders.map(s => ({ stakeholder_id: s.stakeholder_id, stakeholder_name: s.stakeholder_name }))
                      }
                    />
                  )}

                  {/* Stakeholder Voices — grouped stakeholder comments */}
                  <StakeholderVoices comments={eventComments} stakeholders={stakeholders} eventId={eventId} />

                  {/* Thread list */}
                  <div>
                    <div className="flex items-center justify-between mb-5">
                      <div>
                        <h3 className="font-serif text-xl text-neutral-900 mb-1">Community Discussion</h3>
                        <p className="text-sm" style={{ color: 'var(--color-ink-light)' }}>Share your perspective on this event</p>
                      </div>
                      <button
                        onClick={() => router.push(`/events/${eventId}/threads/new`)}
                        className="text-white px-4 py-2 rounded-md text-sm font-medium transition-all hover:opacity-90 btn-press"
                        style={{ background: 'var(--color-accent)' }}
                      >
                        New Thread
                      </button>
                    </div>

                    {threads.length > 0 ? (
                      <div className="divide-y" style={{ borderColor: 'var(--color-rule)' }}>
                        {threads.map((thread) => (
                          <div
                            key={thread.id}
                            onClick={() => router.push(`/events/${eventId}/threads/${thread.id}`)}
                            className="py-5 first:pt-0 cursor-pointer group"
                          >
                            <h4 className="font-semibold text-neutral-900 mb-1.5 group-hover:text-[#C2410C] transition-colors">{thread.title}</h4>
                            <p className="text-neutral-600 text-sm line-clamp-2 mb-3 leading-relaxed">{thread.content}</p>
                            <div className="flex items-center gap-4 text-xs text-neutral-400">
                              <span className="font-medium text-neutral-500">{thread.persona_name}</span>
                              {thread.stakeholder_name && thread.verification_level && (
                                <StakeholderBadge
                                  stakeholderName={thread.stakeholder_name}
                                  level={thread.verification_level as 'verified' | 'declared'}
                                  compact
                                />
                              )}
                              <span>{thread.reply_count} replies</span>
                              <span>{thread.like_count} likes</span>
                              <span>{new Date(thread.created_at).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}</span>
                            </div>
                            {thread.tags?.length > 0 && (
                              <div className="flex flex-wrap gap-1.5 mt-2">
                                {thread.tags.map((tag, i) => (
                                  <span key={i} className="text-xs px-2 py-0.5 rounded-md" style={{ background: '#F0ECE3', color: 'var(--color-ink-light)' }}>{tag}</span>
                                ))}
                              </div>
                            )}
                          </div>
                        ))}
                      </div>
                    ) : (
                      <div className="text-center py-14 border rounded-lg" style={{ borderColor: 'var(--color-rule)' }}>
                        <p className="text-neutral-500 mb-1">No threads yet</p>
                        <p className="text-sm text-neutral-400">Be the first to start a discussion about this event</p>
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>

            {/* ── Sidebar (4 cols) — sticky on desktop ── */}
            <aside className="lg:col-span-4">
              <div className="lg:sticky lg:top-[120px] space-y-6">

                {/* Event metadata card */}
                <div className="rounded-lg border p-5 space-y-4" style={{ borderColor: 'var(--color-rule)', background: 'white' }}>
                  <h4 className="text-xs text-neutral-400 uppercase tracking-wider font-medium">Event Details</h4>
                  <dl className="space-y-3 text-sm">
                    {event.occurred_at && (
                      <div className="flex justify-between">
                        <dt className="text-neutral-400">Occurred</dt>
                        <dd className="text-neutral-900 font-medium">{new Date(event.occurred_at).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}</dd>
                      </div>
                    )}
                    <div className="flex justify-between">
                      <dt className="text-neutral-400">First tracked</dt>
                      <dd className="text-neutral-900 font-medium">{new Date(event.created_at!).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}</dd>
                    </div>
                    {event.updated_at && (
                      <div className="flex justify-between">
                        <dt className="text-neutral-400">Last updated</dt>
                        <dd className="text-neutral-900 font-medium">{timeAgo(event.updated_at)}</dd>
                      </div>
                    )}
                    {(event.hot_score ?? 0) > 0 && (
                      <div className="flex justify-between">
                        <dt className="text-neutral-400">Heat score</dt>
                        <dd className="font-bold stat-number" style={{ color: '#C2410C' }}>{event.hot_score?.toFixed(1)}</dd>
                      </div>
                    )}
                  </dl>
                </div>

                {/* Source breakdown card */}
                {Object.keys(sourcesByOutlet).length > 0 && (
                  <div className="rounded-lg border p-5" style={{ borderColor: 'var(--color-rule)', background: 'white' }}>
                    <h4 className="text-xs text-neutral-400 uppercase tracking-wider font-medium mb-4">Coverage by Outlet</h4>
                    <div className="space-y-2.5">
                      {Object.entries(sourcesByOutlet)
                        .sort((a, b) => b[1] - a[1])
                        .slice(0, 8)
                        .map(([name, count]) => (
                          <div key={name} className="flex items-center justify-between text-sm">
                            <span className="text-neutral-700 truncate mr-3">{name}</span>
                            <span className="text-neutral-400 flex-shrink-0 stat-number">{count}</span>
                          </div>
                        ))}
                    </div>
                    {Object.keys(sourcesByOutlet).length > 8 && (
                      <button
                        onClick={() => setActiveTab('sources')}
                        className="text-xs mt-3 font-medium hover:underline"
                        style={{ color: '#C2410C' }}
                      >
                        View all {Object.keys(sourcesByOutlet).length} outlets &rarr;
                      </button>
                    )}
                  </div>
                )}


              </div>
            </aside>

          </div>
        </div>

        {/* ── Footer ──────────────────────────────────────── */}
        <footer className="relative grain" style={{ background: 'var(--color-warm-dark)' }}>
          <div className="container mx-auto px-6 py-8">
            <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
              <div className="flex items-center gap-6">
                <span className="font-serif text-xl font-bold text-white">Gaze</span>
                <nav className="flex items-center gap-4 text-sm text-neutral-500">
                  <a href="/stories" className="hover:text-white transition-colors">Stories</a>
                  <span className="text-neutral-700">&middot;</span>
                  <a href="/feedback" className="hover:text-white transition-colors">Feedback</a>
                  <span className="text-neutral-700">&middot;</span>
                  <a href="/auth/login" className="hover:text-white transition-colors">Sign In</a>
                </nav>
              </div>
              <p className="font-serif italic text-sm text-neutral-600">We Gaze Upon the Same Moon</p>
            </div>
            <div className="mt-6 pt-4 border-t border-white/[0.06] text-xs text-neutral-700">
              <p>&copy; 2026 Gaze</p>
            </div>
          </div>
        </footer>
      </main>
    </div>
  );
}
