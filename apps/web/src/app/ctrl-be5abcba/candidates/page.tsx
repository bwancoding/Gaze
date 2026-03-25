'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { API_BASE_URL } from '../../../lib/config';


interface CandidateEvent {
  id: string;
  title: string;
  summary: string;
  category: string;
  status: string;
  source_count: number;
  trending_origin_id: number | null;
  background: string | null;
  created_at: string;
}

interface TrendingEvent {
  id: number;
  title: string;
  summary: string;
  category: string;
  article_count: number;
  heat_score: number;
  status: string;
  keywords: string[];
  created_at: string;
}

export default function CandidateReviewPage() {
  const router = useRouter();
  const [candidates, setCandidates] = useState<CandidateEvent[]>([]);
  const [trendingEvents, setTrendingEvents] = useState<TrendingEvent[]>([]);
  const [activeTab, setActiveTab] = useState<'candidates' | 'trending'>('candidates');
  const [isLoading, setIsLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState<string | null>(null);
  const [pipelineRunning, setPipelineRunning] = useState(false);
  const [error, setError] = useState('');
  const [successMsg, setSuccessMsg] = useState('');

  // Batch selection
  const [selectedTrending, setSelectedTrending] = useState<Set<number>>(new Set());
  const [selectedCandidates, setSelectedCandidates] = useState<Set<string>>(new Set());

  const getAuthHeaders = (): HeadersInit => {
    const headers: Record<string, string> = { 'Content-Type': 'application/json' };
    const storedAuth = localStorage.getItem('admin_auth');
    if (storedAuth) {
      const { username, password } = JSON.parse(storedAuth);
      headers['Authorization'] = 'Basic ' + btoa(`${username}:${password}`);
    }
    return headers;
  };

  useEffect(() => {
    const storedAuth = localStorage.getItem('admin_auth');
    if (!storedAuth) {
      router.push('/ctrl-be5abcba');
      return;
    }
    fetchData();
  }, []);

  // Auto-clear success message
  useEffect(() => {
    if (successMsg) {
      const t = setTimeout(() => setSuccessMsg(''), 4000);
      return () => clearTimeout(t);
    }
  }, [successMsg]);

  const fetchData = async () => {
    setIsLoading(true);
    try {
      const [candidatesRes, trendingRes] = await Promise.all([
        fetch(`${API_BASE_URL}/api/admin/candidates`, { headers: getAuthHeaders() }),
        fetch(`${API_BASE_URL}/api/trending?page_size=50`, { headers: getAuthHeaders() }),
      ]);

      if (candidatesRes.ok) {
        const data = await candidatesRes.json();
        setCandidates(data.items || []);
      }
      if (trendingRes.ok) {
        const data = await trendingRes.json();
        const items = (data.items || data.events || []).filter((t: TrendingEvent) => t.status === 'raw');
        setTrendingEvents(items);
      }
    } catch (err) {
      setError('Failed to load data');
    } finally {
      setIsLoading(false);
    }
  };

  // --- Single actions ---

  const handlePublish = async (eventId: string) => {
    if (!confirm('Publish this event? It will become visible to all users.')) return;
    setActionLoading(eventId);
    try {
      const res = await fetch(`${API_BASE_URL}/api/admin/events/${eventId}/publish`, {
        method: 'POST', headers: getAuthHeaders(),
      });
      if (res.ok) {
        setCandidates(prev => prev.filter(c => c.id !== eventId));
        setSelectedCandidates(prev => { const s = new Set(prev); s.delete(eventId); return s; });
        setSuccessMsg('Event published successfully');
      } else {
        const data = await res.json();
        alert(data.detail || 'Failed to publish');
      }
    } catch { alert('Network error'); }
    finally { setActionLoading(null); }
  };

  const handleReject = async (eventId: string) => {
    if (!confirm('Reject this candidate? It will be closed.')) return;
    setActionLoading(eventId);
    try {
      const res = await fetch(`${API_BASE_URL}/api/admin/events/${eventId}/reject`, {
        method: 'POST', headers: getAuthHeaders(),
      });
      if (res.ok) {
        setCandidates(prev => prev.filter(c => c.id !== eventId));
        setSelectedCandidates(prev => { const s = new Set(prev); s.delete(eventId); return s; });
        setSuccessMsg('Event rejected');
      } else {
        const data = await res.json();
        alert(data.detail || 'Failed to reject');
      }
    } catch { alert('Network error'); }
    finally { setActionLoading(null); }
  };

  const handleGenerateAnalysis = async (eventId: string) => {
    setActionLoading(`analysis-${eventId}`);
    try {
      const res = await fetch(`${API_BASE_URL}/api/admin/events/${eventId}/generate-analysis`, {
        method: 'POST', headers: getAuthHeaders(),
      });
      if (res.ok) {
        const data = await res.json();
        setSuccessMsg(`Analysis generated! Quality: ${data.quality_score || 'N/A'}`);
        fetchData();
      } else {
        const data = await res.json();
        alert(data.detail || 'Failed to generate analysis');
      }
    } catch { alert('Network error'); }
    finally { setActionLoading(null); }
  };

  const handlePromote = async (trendingId: number) => {
    if (!confirm('Promote this news feed event to a candidate?')) return;
    setActionLoading(`promote-${trendingId}`);
    try {
      const res = await fetch(`${API_BASE_URL}/api/admin/trending/${trendingId}/promote`, {
        method: 'POST', headers: getAuthHeaders(),
      });
      if (res.ok) {
        setTrendingEvents(prev => prev.filter(t => t.id !== trendingId));
        setSelectedTrending(prev => { const s = new Set(prev); s.delete(trendingId); return s; });
        setSuccessMsg('Promoted to candidate!');
        fetchData();
      } else {
        const data = await res.json();
        alert(data.detail || 'Failed to promote');
      }
    } catch { alert('Network error'); }
    finally { setActionLoading(null); }
  };

  const handleRejectTrending = async (trendingId: number) => {
    if (!confirm('Dismiss this news feed event? It will be removed from review.')) return;
    setActionLoading(`reject-${trendingId}`);
    try {
      const res = await fetch(`${API_BASE_URL}/api/admin/trending/${trendingId}/reject`, {
        method: 'POST', headers: getAuthHeaders(),
      });
      if (res.ok) {
        setTrendingEvents(prev => prev.filter(t => t.id !== trendingId));
        setSelectedTrending(prev => { const s = new Set(prev); s.delete(trendingId); return s; });
        setSuccessMsg('News feed event dismissed');
      } else {
        const data = await res.json();
        alert(data.detail || 'Failed to dismiss');
      }
    } catch { alert('Network error'); }
    finally { setActionLoading(null); }
  };

  // --- Batch actions ---

  const handleBatchPromote = async () => {
    if (selectedTrending.size === 0) return;
    if (!confirm(`Promote ${selectedTrending.size} news feed events to candidates?`)) return;
    setActionLoading('batch-promote');
    try {
      const res = await fetch(`${API_BASE_URL}/api/admin/trending/batch-promote`, {
        method: 'POST',
        headers: getAuthHeaders(),
        body: JSON.stringify(Array.from(selectedTrending)),
      });
      if (res.ok) {
        const data = await res.json();
        setSuccessMsg(`Promoted ${data.promoted} events${data.errors > 0 ? `, ${data.errors} errors` : ''}`);
        setSelectedTrending(new Set());
        fetchData();
      } else {
        alert('Batch promote failed');
      }
    } catch { alert('Network error'); }
    finally { setActionLoading(null); }
  };

  const handleBatchPublish = async () => {
    if (selectedCandidates.size === 0) return;
    if (!confirm(`Publish ${selectedCandidates.size} events? They will become visible to all users.`)) return;
    setActionLoading('batch-publish');
    try {
      const res = await fetch(`${API_BASE_URL}/api/admin/events/batch-publish`, {
        method: 'POST',
        headers: getAuthHeaders(),
        body: JSON.stringify(Array.from(selectedCandidates)),
      });
      if (res.ok) {
        const data = await res.json();
        setSuccessMsg(`Published ${data.published} events${data.errors > 0 ? `, ${data.errors} errors` : ''}`);
        setSelectedCandidates(new Set());
        fetchData();
      } else {
        alert('Batch publish failed');
      }
    } catch { alert('Network error'); }
    finally { setActionLoading(null); }
  };

  // --- Pipeline ---

  const handleRefreshPipeline = async () => {
    if (!confirm('Run the full pipeline? This may take a minute (fetch → cluster → heat → trim).')) return;
    setPipelineRunning(true);
    setSuccessMsg('');
    try {
      const res = await fetch(`${API_BASE_URL}/api/admin/pipeline/refresh`, {
        method: 'POST', headers: getAuthHeaders(),
      });
      if (res.ok) {
        const data = await res.json();
        const r = data.result || {};
        setSuccessMsg(`Pipeline done: ${r.fetch || 0} fetched, ${r.new || 0} new, ${r.trim?.archived || 0} archived`);
        fetchData();
      } else {
        const data = await res.json();
        alert(data.detail || 'Pipeline failed');
      }
    } catch { alert('Network error'); }
    finally { setPipelineRunning(false); }
  };

  const handleRecalculateHeat = async () => {
    setActionLoading('heat');
    try {
      const res = await fetch(`${API_BASE_URL}/api/admin/pipeline/heat-recalculate`, {
        method: 'POST', headers: getAuthHeaders(),
      });
      if (res.ok) {
        setSuccessMsg('Heat scores recalculated');
        fetchData();
      } else {
        alert('Failed to recalculate');
      }
    } catch { alert('Network error'); }
    finally { setActionLoading(null); }
  };

  // --- Selection helpers ---

  const toggleTrending = (id: number) => {
    setSelectedTrending(prev => {
      const s = new Set(prev);
      if (s.has(id)) s.delete(id); else s.add(id);
      return s;
    });
  };

  const toggleCandidate = (id: string) => {
    setSelectedCandidates(prev => {
      const s = new Set(prev);
      if (s.has(id)) s.delete(id); else s.add(id);
      return s;
    });
  };

  const selectAllTrending = () => {
    if (selectedTrending.size === trendingEvents.length) {
      setSelectedTrending(new Set());
    } else {
      setSelectedTrending(new Set(trendingEvents.map(t => t.id)));
    }
  };

  const selectAllCandidates = () => {
    if (selectedCandidates.size === candidates.length) {
      setSelectedCandidates(new Set());
    } else {
      setSelectedCandidates(new Set(candidates.map(c => c.id)));
    }
  };

  return (
    <div className="min-h-screen bg-stone-50">
      {/* Header */}
      <header className="bg-white border-b border-stone-200 sticky top-0 z-50">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-xl font-bold text-stone-900">Candidate Review</h1>
              <p className="text-xs text-stone-500">Review, publish, or reject candidate events</p>
            </div>
            <div className="flex items-center space-x-3">
              <button
                onClick={handleRecalculateHeat}
                disabled={actionLoading === 'heat'}
                className="px-3 py-2 bg-stone-100 text-stone-700 rounded-lg text-sm font-medium hover:bg-stone-200 transition-colors disabled:opacity-50"
                title="Recalculate heat scores"
              >
                {actionLoading === 'heat' ? '...' : '🔄 Heat'}
              </button>
              <button
                onClick={handleRefreshPipeline}
                disabled={pipelineRunning}
                className="px-3 py-2 bg-orange-500 text-white rounded-lg text-sm font-medium hover:bg-orange-600 transition-colors disabled:opacity-50"
              >
                {pipelineRunning ? (
                  <span className="flex items-center space-x-1">
                    <span className="animate-spin inline-block w-3 h-3 border-2 border-white border-t-transparent rounded-full"></span>
                    <span>Running...</span>
                  </span>
                ) : '🚀 Run Pipeline'}
              </button>
              <button
                onClick={() => router.push('/ctrl-be5abcba')}
                className="text-stone-600 hover:text-stone-900 text-sm font-medium"
              >
                ← Dashboard
              </button>
            </div>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-6 py-8">
        {/* Success Message */}
        {successMsg && (
          <div className="bg-emerald-50 border border-emerald-200 text-emerald-800 px-4 py-3 rounded-lg mb-6 flex items-center justify-between">
            <span className="text-sm">{successMsg}</span>
            <button onClick={() => setSuccessMsg('')} className="text-emerald-500 hover:text-emerald-700 text-lg">&times;</button>
          </div>
        )}

        {error && (
          <div className="bg-red-50 border border-red-200 text-red-800 px-4 py-3 rounded-lg mb-6">{error}</div>
        )}

        {/* Tabs */}
        <div className="flex items-center justify-between mb-6">
          <div className="flex space-x-1 bg-stone-200 rounded-lg p-1">
            <button
              onClick={() => setActiveTab('candidates')}
              className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                activeTab === 'candidates' ? 'bg-white text-stone-900 shadow-sm' : 'text-stone-600 hover:text-stone-900'
              }`}
            >
              Candidates ({candidates.length})
            </button>
            <button
              onClick={() => setActiveTab('trending')}
              className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                activeTab === 'trending' ? 'bg-white text-stone-900 shadow-sm' : 'text-stone-600 hover:text-stone-900'
              }`}
            >
              News Feed ({trendingEvents.length})
            </button>
          </div>

          {/* Batch action bar */}
          {activeTab === 'trending' && selectedTrending.size > 0 && (
            <div className="flex items-center space-x-3 bg-blue-50 border border-blue-200 rounded-lg px-4 py-2">
              <span className="text-sm text-blue-700 font-medium">{selectedTrending.size} selected</span>
              <button onClick={handleBatchPromote} disabled={actionLoading === 'batch-promote'}
                className="px-3 py-1.5 bg-blue-600 text-white rounded-md text-xs font-medium hover:bg-blue-700 disabled:opacity-50">
                {actionLoading === 'batch-promote' ? 'Promoting...' : 'Promote All'}
              </button>
              <button onClick={() => setSelectedTrending(new Set())}
                className="text-xs text-blue-600 hover:underline">Clear</button>
            </div>
          )}
          {activeTab === 'candidates' && selectedCandidates.size > 0 && (
            <div className="flex items-center space-x-3 bg-emerald-50 border border-emerald-200 rounded-lg px-4 py-2">
              <span className="text-sm text-emerald-700 font-medium">{selectedCandidates.size} selected</span>
              <button onClick={handleBatchPublish} disabled={actionLoading === 'batch-publish'}
                className="px-3 py-1.5 bg-emerald-600 text-white rounded-md text-xs font-medium hover:bg-emerald-700 disabled:opacity-50">
                {actionLoading === 'batch-publish' ? 'Publishing...' : 'Publish All'}
              </button>
              <button onClick={() => setSelectedCandidates(new Set())}
                className="text-xs text-emerald-600 hover:underline">Clear</button>
            </div>
          )}
        </div>

        {isLoading ? (
          <div className="text-center py-20">
            <div className="animate-spin w-8 h-8 border-2 border-stone-300 border-t-stone-900 rounded-full mx-auto"></div>
          </div>
        ) : activeTab === 'candidates' ? (
          /* ===== Candidates Tab ===== */
          <div className="space-y-4">
            {candidates.length > 0 && (
              <div className="flex items-center space-x-2 mb-2">
                <label className="flex items-center space-x-2 text-sm text-stone-600 cursor-pointer">
                  <input type="checkbox"
                    checked={selectedCandidates.size === candidates.length && candidates.length > 0}
                    onChange={selectAllCandidates}
                    className="rounded border-stone-300" />
                  <span>Select all</span>
                </label>
              </div>
            )}

            {candidates.length === 0 ? (
              <div className="text-center py-20 bg-white rounded-xl border border-stone-200">
                <p className="text-stone-500 text-lg mb-2">No candidates awaiting review</p>
                <p className="text-stone-400 text-sm">Promote news feed events or create events manually</p>
              </div>
            ) : (
              candidates.map((event) => (
                <div key={event.id} className={`bg-white rounded-xl border p-6 transition-colors ${
                  selectedCandidates.has(event.id) ? 'border-emerald-300 bg-emerald-50/30' : 'border-stone-200'
                }`}>
                  <div className="flex items-start">
                    <div className="flex-shrink-0 mr-4 pt-1">
                      <input type="checkbox"
                        checked={selectedCandidates.has(event.id)}
                        onChange={() => toggleCandidate(event.id)}
                        className="rounded border-stone-300 w-4 h-4" />
                    </div>

                    <div className="flex-1 min-w-0 mr-6">
                      <div className="flex items-center space-x-3 mb-2">
                        <span className="inline-block px-2.5 py-1 rounded-full text-xs font-medium bg-amber-100 text-amber-700">
                          Candidate
                        </span>
                        {event.category && (
                          <span className="inline-block px-2.5 py-1 rounded-full text-xs font-medium bg-stone-100 text-stone-600">
                            {event.category}
                          </span>
                        )}
                        {event.trending_origin_id && (
                          <span className="inline-block px-2.5 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-700">
                            From Feed #{event.trending_origin_id}
                          </span>
                        )}
                      </div>

                      <h3 className="text-lg font-semibold text-stone-900 mb-2">{event.title}</h3>

                      {event.summary && (
                        <p className="text-stone-600 text-sm leading-relaxed mb-3 line-clamp-3">{event.summary}</p>
                      )}

                      {event.background && (
                        <div className="bg-stone-50 rounded-lg p-3 mb-3">
                          <p className="text-xs font-medium text-stone-500 mb-1">AI Background</p>
                          <p className="text-stone-600 text-sm line-clamp-2">{event.background}</p>
                        </div>
                      )}

                      <div className="flex items-center space-x-4 text-xs text-stone-500">
                        <span>{event.source_count || 0} sources</span>
                        <span>Created {new Date(event.created_at).toLocaleDateString()}</span>
                      </div>
                    </div>

                    <div className="flex flex-col space-y-2 flex-shrink-0">
                      <button onClick={() => handlePublish(event.id)}
                        disabled={actionLoading === event.id}
                        className="px-4 py-2 bg-emerald-600 text-white rounded-lg text-sm font-medium hover:bg-emerald-700 disabled:opacity-50">
                        Publish
                      </button>
                      <button onClick={() => handleGenerateAnalysis(event.id)}
                        disabled={actionLoading === `analysis-${event.id}`}
                        className="px-4 py-2 bg-amber-500 text-white rounded-lg text-sm font-medium hover:bg-amber-600 disabled:opacity-50">
                        AI Analysis
                      </button>
                      <button onClick={() => router.push(`/events/${event.id}`)}
                        className="px-4 py-2 bg-stone-100 text-stone-700 rounded-lg text-sm font-medium hover:bg-stone-200">
                        Preview
                      </button>
                      <button onClick={() => handleReject(event.id)}
                        disabled={actionLoading === event.id}
                        className="px-4 py-2 bg-red-50 text-red-600 rounded-lg text-sm font-medium hover:bg-red-100 disabled:opacity-50">
                        Reject
                      </button>
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        ) : (
          /* ===== Trending Tab ===== */
          <div className="space-y-4">
            {trendingEvents.length > 0 && (
              <div className="flex items-center space-x-2 mb-2">
                <label className="flex items-center space-x-2 text-sm text-stone-600 cursor-pointer">
                  <input type="checkbox"
                    checked={selectedTrending.size === trendingEvents.length && trendingEvents.length > 0}
                    onChange={selectAllTrending}
                    className="rounded border-stone-300" />
                  <span>Select all</span>
                </label>
                <span className="text-xs text-stone-400">Top 20 by heat score (auto-trimmed)</span>
              </div>
            )}

            {trendingEvents.length === 0 ? (
              <div className="text-center py-20 bg-white rounded-xl border border-stone-200">
                <p className="text-stone-500 text-lg mb-2">No pending news feed events</p>
                <p className="text-stone-400 text-sm mb-4">Run the pipeline to discover new events</p>
                <button onClick={handleRefreshPipeline} disabled={pipelineRunning}
                  className="px-4 py-2 bg-orange-500 text-white rounded-lg text-sm font-medium hover:bg-orange-600 disabled:opacity-50">
                  {pipelineRunning ? 'Running...' : 'Run Pipeline'}
                </button>
              </div>
            ) : (
              trendingEvents.map((trending, index) => (
                <div key={trending.id} className={`bg-white rounded-xl border p-6 transition-colors ${
                  selectedTrending.has(trending.id) ? 'border-blue-300 bg-blue-50/30' : 'border-stone-200'
                }`}>
                  <div className="flex items-start">
                    <div className="flex-shrink-0 mr-4 pt-1">
                      <input type="checkbox"
                        checked={selectedTrending.has(trending.id)}
                        onChange={() => toggleTrending(trending.id)}
                        className="rounded border-stone-300 w-4 h-4" />
                    </div>

                    <div className="flex-1 min-w-0 mr-6">
                      <div className="flex items-center space-x-3 mb-2">
                        <span className="inline-block px-2 py-0.5 rounded-full text-xs font-bold bg-stone-900 text-white">
                          #{index + 1}
                        </span>
                        <span className="inline-block px-2.5 py-1 rounded-full text-xs font-medium bg-orange-100 text-orange-700">
                          {trending.heat_score?.toFixed(1) || '0'}°
                        </span>
                        {trending.category && (
                          <span className="inline-block px-2.5 py-1 rounded-full text-xs font-medium bg-stone-100 text-stone-600">
                            {trending.category}
                          </span>
                        )}
                        <span className="text-xs text-stone-400">
                          {trending.article_count} articles
                        </span>
                      </div>

                      <h3 className="text-lg font-semibold text-stone-900 mb-2">{trending.title}</h3>

                      {trending.summary && (
                        <p className="text-stone-600 text-sm leading-relaxed mb-3 line-clamp-3">{trending.summary}</p>
                      )}

                      {trending.keywords && trending.keywords.length > 0 && (
                        <div className="flex flex-wrap gap-1.5 mb-3">
                          {trending.keywords.slice(0, 8).map((kw, i) => (
                            <span key={i} className="px-2 py-0.5 bg-stone-100 text-stone-600 rounded text-xs capitalize">
                              {kw}
                            </span>
                          ))}
                        </div>
                      )}

                      <div className="text-xs text-stone-500">
                        Discovered {new Date(trending.created_at).toLocaleDateString()}
                      </div>
                    </div>

                    <div className="flex flex-col space-y-2 flex-shrink-0">
                      <button onClick={() => handlePromote(trending.id)}
                        disabled={!!actionLoading}
                        className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700 disabled:opacity-50">
                        Promote
                      </button>
                      <button onClick={() => handleRejectTrending(trending.id)}
                        disabled={!!actionLoading}
                        className="px-4 py-2 bg-red-50 text-red-600 rounded-lg text-sm font-medium hover:bg-red-100 disabled:opacity-50">
                        Dismiss
                      </button>
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        )}
      </main>
    </div>
  );
}
