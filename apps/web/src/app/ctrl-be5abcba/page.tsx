'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { API_BASE_URL } from '../../lib/config';


interface Event {
  id: string;
  title: string;
  category: string;
  status: string;
  hot_score: number;
  view_count: number;
  source_count: number;
  created_at: string;
}

interface Stats {
  total_events: number;
  active_events: number;
  candidate_events: number;
  archived_events: number;
  closed_events: number;
  pending_trending: number;
}

const GATE_PASSWORD = process.env.NEXT_PUBLIC_ADMIN_GATE_PASSWORD || 'wrhitw2026';

export default function AdminDashboard() {
  const router = useRouter();
  const [gatePass, setGatePass] = useState('');
  const [gateUnlocked, setGateUnlocked] = useState(false);
  const [gateError, setGateError] = useState('');
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [events, setEvents] = useState<Event[]>([]);
  const [stats, setStats] = useState<Stats | null>(null);
  const [statusFilter, setStatusFilter] = useState('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const [totalEvents, setTotalEvents] = useState(0);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const PAGE_SIZE = 20;

  const getAuthHeaders = (): HeadersInit => {
    const headers: Record<string, string> = { 'Content-Type': 'application/json' };
    const storedAuth = localStorage.getItem('admin_auth');
    if (storedAuth) {
      const { username, password } = JSON.parse(storedAuth);
      headers['Authorization'] = 'Basic ' + btoa(`${username}:${password}`);
    }
    return headers;
  };

  const fetchData = async (page = currentPage) => {
    try {
      const searchParam = searchQuery ? `&search=${encodeURIComponent(searchQuery)}` : '';
      const [eventsRes, statsRes] = await Promise.all([
        fetch(`${API_BASE_URL}/api/admin/events?status_filter=${statusFilter}&page=${page}&page_size=${PAGE_SIZE}${searchParam}`, {
          headers: getAuthHeaders(),
        }),
        fetch(`${API_BASE_URL}/api/admin/stats`, {
          headers: getAuthHeaders(),
        }),
      ]);

      if (eventsRes.ok && statsRes.ok) {
        const eventsData = await eventsRes.json();
        const statsData = await statsRes.json();
        setEvents(eventsData.items);
        setTotalEvents(eventsData.total);
        setStats(statsData);
      }
    } catch (err) {
      console.error('Failed to fetch data:', err);
    }
  };

  const totalPages = Math.ceil(totalEvents / PAGE_SIZE);

  const handlePageChange = (page: number) => {
    setCurrentPage(page);
    fetchData(page);
  };

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    setCurrentPage(1);
    fetchData(1);
  };

  // Check if already authenticated
  useEffect(() => {
    const gateOk = sessionStorage.getItem('admin_gate');
    if (gateOk === 'unlocked') {
      setGateUnlocked(true);
    }
    const storedAuth = localStorage.getItem('admin_auth');
    if (storedAuth && gateOk === 'unlocked') {
      setIsAuthenticated(true);
    }
  }, []);

  useEffect(() => {
    if (isAuthenticated && gateUnlocked) {
      setCurrentPage(1);
      fetchData(1);
    }
  }, [statusFilter, isAuthenticated, gateUnlocked]);

  // Gate password check
  if (!gateUnlocked) {
    return (
      <div className="min-h-screen bg-stone-100 flex items-center justify-center">
        <div className="bg-white rounded-2xl shadow-lg p-8 max-w-sm w-full">
          <div className="text-center mb-6">
            <div className="w-12 h-12 bg-stone-900 rounded-xl flex items-center justify-center mx-auto mb-4">
              <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
              </svg>
            </div>
            <h2 className="text-lg font-semibold text-stone-800">Access Required</h2>
            <p className="text-sm text-stone-500 mt-1">Enter the access code to continue</p>
          </div>
          <form onSubmit={(e) => {
            e.preventDefault();
            if (gatePass === GATE_PASSWORD) {
              sessionStorage.setItem('admin_gate', 'unlocked');
              setGateUnlocked(true);
              setGateError('');
            } else {
              setGateError('Invalid access code');
            }
          }}>
            <input
              type="password"
              value={gatePass}
              onChange={(e) => setGatePass(e.target.value)}
              placeholder="Access code"
              className="w-full px-4 py-3 border border-stone-300 rounded-xl focus:ring-2 focus:ring-stone-500 focus:border-transparent mb-3"
              autoFocus
            />
            {gateError && <p className="text-red-500 text-sm mb-3">{gateError}</p>}
            <button
              type="submit"
              className="w-full py-3 bg-stone-900 text-white rounded-xl font-medium hover:bg-stone-800 transition-colors"
            >
              Enter
            </button>
          </form>
        </div>
      </div>
    );
  }

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    try {
      const response = await fetch(`${API_BASE_URL}/api/admin/events`, {
        headers: {
          'Authorization': 'Basic ' + btoa(`${username}:${password}`),
        },
      });

      if (response.ok) {
        setIsAuthenticated(true);
        localStorage.setItem('admin_auth', JSON.stringify({ username, password }));
        fetchData();
      } else {
        const data = await response.json();
        setError(data.detail || 'Login failed');
      }
    } catch (err) {
      setError('Network error');
    } finally {
      setIsLoading(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('admin_auth');
    setIsAuthenticated(false);
    setUsername('');
    setPassword('');
  };

  const handleArchive = async (eventId: string) => {
    if (!confirm('Archive this event?')) return;

    try {
      const response = await fetch(`${API_BASE_URL}/api/admin/events/${eventId}/archive`, {
        method: 'POST',
        headers: getAuthHeaders(),
      });

      if (response.ok) {
        fetchData();
        alert('Event archived');
      }
    } catch (err) {
      alert('Failed to archive event');
    }
  };

  const handleClose = async (eventId: string) => {
    if (!confirm('Close this event? No new comments will be allowed.')) return;

    try {
      const response = await fetch(`${API_BASE_URL}/api/admin/events/${eventId}/close`, {
        method: 'POST',
        headers: getAuthHeaders(),
      });

      if (response.ok) {
        fetchData();
        alert('Event closed');
      }
    } catch (err) {
      alert('Failed to close event');
    }
  };

  const handleDelete = async (eventId: string) => {
    if (!confirm('PERMANENTLY delete this event? This cannot be undone!')) return;

    try {
      const response = await fetch(`${API_BASE_URL}/api/admin/events/${eventId}`, {
        method: 'DELETE',
        headers: getAuthHeaders(),
      });

      if (response.ok) {
        fetchData();
        alert('Event deleted');
      }
    } catch (err) {
      alert('Failed to delete event');
    }
  };

  const handlePublish = async (eventId: string) => {
    if (!confirm('Publish this event?')) return;
    try {
      const response = await fetch(`${API_BASE_URL}/api/admin/events/${eventId}/publish`, {
        method: 'POST',
        headers: getAuthHeaders(),
      });
      if (response.ok) {
        fetchData();
      } else {
        alert('Failed to publish event');
      }
    } catch {
      alert('Failed to publish event');
    }
  };

  const handleReject = async (eventId: string) => {
    if (!confirm('Reject this candidate?')) return;
    try {
      const response = await fetch(`${API_BASE_URL}/api/admin/events/${eventId}/reject`, {
        method: 'POST',
        headers: getAuthHeaders(),
      });
      if (response.ok) {
        fetchData();
      } else {
        alert('Failed to reject event');
      }
    } catch {
      alert('Failed to reject event');
    }
  };

  const handleCreateEvent = () => {
    router.push('/ctrl-be5abcba/events/new');
  };

  if (!isAuthenticated) {
    return (
      <div className="min-h-screen bg-stone-50 flex items-center justify-center">
        <div className="bg-white p-8 rounded-2xl shadow-xl max-w-md w-full">
          <div className="text-center mb-8">
            <h1 className="text-2xl font-bold text-stone-900 mb-2">Gaze Admin</h1>
            <p className="text-stone-600">Sign in to manage events</p>
          </div>

          <form onSubmit={handleLogin} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-stone-700 mb-1">
                Username
              </label>
              <input
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                className="w-full px-4 py-2 border border-stone-300 rounded-lg focus:ring-2 focus:ring-stone-500 focus:border-transparent"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-stone-700 mb-1">
                Password
              </label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full px-4 py-2 border border-stone-300 rounded-lg focus:ring-2 focus:ring-stone-500 focus:border-transparent"
                required
              />
            </div>

            {error && (
              <div className="bg-red-50 border border-red-200 text-red-800 px-4 py-2 rounded-lg text-sm">
                {error}
              </div>
            )}

            <button
              type="submit"
              disabled={isLoading}
              className="w-full bg-stone-900 text-white py-2.5 rounded-lg font-medium hover:bg-stone-800 transition-colors disabled:opacity-50"
            >
              {isLoading ? 'Signing in...' : 'Sign In'}
            </button>
          </form>

          <div className="mt-6 text-center text-xs text-stone-500">
            <p>Admin access only</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-stone-50">
      {/* Header */}
      <header className="bg-white border-b border-stone-200 sticky top-0 z-50">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-xl font-bold text-stone-900">Gaze Admin</h1>
              <p className="text-xs text-stone-500">Event & Verification Management</p>
            </div>
            <div className="flex items-center space-x-3">
              <button
                onClick={() => router.push('/ctrl-be5abcba/candidates')}
                className="bg-amber-500 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-amber-600 transition-colors"
              >
                📋 Candidates
              </button>
              <button
                onClick={() => router.push('/ctrl-be5abcba/stakeholders')}
                className="bg-violet-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-violet-700 transition-colors"
              >
                👥 Stakeholders
              </button>
              <button
                onClick={() => router.push('/ctrl-be5abcba/verifications')}
                className="bg-indigo-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-indigo-700 transition-colors"
              >
                🔍 Verifications
              </button>
              <button
                onClick={() => router.push('/ctrl-be5abcba/analytics')}
                className="bg-emerald-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-emerald-700 transition-colors"
              >
                📊 Analytics
              </button>
              <button
                onClick={() => router.push('/')}
                className="text-stone-600 hover:text-stone-900 text-sm"
              >
                View Site
              </button>
              <button
                onClick={handleLogout}
                className="text-stone-600 hover:text-stone-900 text-sm"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-6 py-8">
        {/* Stats */}
        {stats && (
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4 mb-8">
            <div className="bg-white p-5 rounded-xl border border-stone-200">
              <p className="text-sm text-stone-600 mb-1">Total Events</p>
              <p className="text-3xl font-bold text-stone-900">{stats.total_events}</p>
            </div>
            <div className="bg-white p-5 rounded-xl border border-stone-200">
              <p className="text-sm text-stone-600 mb-1">Active</p>
              <p className="text-3xl font-bold text-emerald-600">{stats.active_events}</p>
            </div>
            <div
              className="bg-amber-50 p-5 rounded-xl border border-amber-200 cursor-pointer hover:bg-amber-100 transition-colors"
              onClick={() => router.push('/ctrl-be5abcba/candidates')}
            >
              <p className="text-sm text-amber-700 mb-1">Candidates</p>
              <p className="text-3xl font-bold text-amber-600">{stats.candidate_events}</p>
            </div>
            <div
              className="bg-orange-50 p-5 rounded-xl border border-orange-200 cursor-pointer hover:bg-orange-100 transition-colors"
              onClick={() => router.push('/ctrl-be5abcba/candidates')}
            >
              <p className="text-sm text-orange-700 mb-1">News Feed 🔥</p>
              <p className="text-3xl font-bold text-orange-600">{stats.pending_trending}</p>
            </div>
            <div className="bg-white p-5 rounded-xl border border-stone-200">
              <p className="text-sm text-stone-600 mb-1">Archived</p>
              <p className="text-3xl font-bold text-amber-600">{stats.archived_events}</p>
            </div>
            <div className="bg-white p-5 rounded-xl border border-stone-200">
              <p className="text-sm text-stone-600 mb-1">Closed</p>
              <p className="text-3xl font-bold text-stone-500">{stats.closed_events}</p>
            </div>
          </div>
        )}

        {/* Actions */}
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center space-x-3">
            <div className="flex items-center space-x-2">
              <span className="text-sm text-stone-600">Filter:</span>
              <select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
                className="border border-stone-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-stone-500"
              >
                <option value="all">All Events</option>
                <option value="active">Active</option>
                <option value="candidate">Candidate</option>
                <option value="archived">Archived</option>
                <option value="closed">Closed</option>
              </select>
            </div>

            <form onSubmit={handleSearch} className="flex items-center space-x-2">
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search events..."
                className="border border-stone-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-stone-500 w-64"
              />
              <button
                type="submit"
                className="bg-stone-200 text-stone-700 px-3 py-2 rounded-lg text-sm font-medium hover:bg-stone-300 transition-colors"
              >
                Search
              </button>
              {searchQuery && (
                <button
                  type="button"
                  onClick={() => {
                    setSearchQuery('');
                    setCurrentPage(1);
                    // Fetch without search - need to bypass stale searchQuery state
                    const headers = getAuthHeaders();
                    fetch(`${API_BASE_URL}/api/admin/events?status_filter=${statusFilter}&page=1&page_size=${PAGE_SIZE}`, { headers })
                      .then(r => r.json())
                      .then(data => { setEvents(data.items); setTotalEvents(data.total); });
                  }}
                  className="text-stone-400 hover:text-stone-600 text-sm"
                >
                  Clear
                </button>
              )}
            </form>
          </div>

          <div className="flex items-center space-x-2">
            <button
              onClick={async () => {
                if (!confirm('Generate fake discussions (threads, comments, votes) for all active events? This uses AI and may take a few minutes.')) return;
                try {
                  const res = await fetch(`${API_BASE_URL}/api/admin/seed-interactions`, {
                    method: 'POST', headers: getAuthHeaders(),
                  });
                  if (res.ok) {
                    alert('Seeding started in background. It may take a few minutes. Refresh the page later to see results.');
                  } else {
                    const data = await res.json();
                    alert(data.detail || 'Seed failed');
                  }
                } catch { alert('Network error'); }
              }}
              className="bg-violet-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-violet-700 transition-colors"
            >
              🌱 Seed Interactions
            </button>
            <button
              onClick={handleCreateEvent}
              className="bg-stone-900 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-stone-800 transition-colors"
            >
              + Create Event
            </button>
          </div>
        </div>

        {/* Events Table */}
        <div className="bg-white rounded-xl border border-stone-200 overflow-hidden">
          <table className="w-full">
            <thead className="bg-stone-50 border-b border-stone-200">
              <tr>
                <th className="text-left px-6 py-3 text-xs font-medium text-stone-600 uppercase">Title</th>
                <th className="text-left px-6 py-3 text-xs font-medium text-stone-600 uppercase">Category</th>
                <th className="text-left px-6 py-3 text-xs font-medium text-stone-600 uppercase">Status</th>
                <th className="text-left px-6 py-3 text-xs font-medium text-stone-600 uppercase">Hot</th>
                <th className="text-left px-6 py-3 text-xs font-medium text-stone-600 uppercase">Views</th>
                <th className="text-left px-6 py-3 text-xs font-medium text-stone-600 uppercase">Created</th>
                <th className="text-right px-6 py-3 text-xs font-medium text-stone-600 uppercase">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-stone-200">
              {events.map((event) => (
                <tr key={event.id} className="hover:bg-stone-50">
                  <td className="px-6 py-4">
                    <p className="font-medium text-stone-900 truncate max-w-xs">{event.title}</p>
                  </td>
                  <td className="px-6 py-4">
                    <span className="inline-block px-2 py-1 rounded text-xs font-medium bg-stone-100 text-stone-700">
                      {event.category}
                    </span>
                  </td>
                  <td className="px-6 py-4">
                    <span className={`inline-block px-2 py-1 rounded text-xs font-medium ${
                      event.status === 'active' ? 'bg-emerald-100 text-emerald-700' :
                      event.status === 'candidate' ? 'bg-amber-100 text-amber-700' :
                      event.status === 'archived' ? 'bg-stone-200 text-stone-600' :
                      'bg-stone-100 text-stone-500'
                    }`}>
                      {event.status}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-sm text-stone-600">{event.hot_score?.toFixed(1) || '0.0'}</td>
                  <td className="px-6 py-4 text-sm text-stone-600">{event.view_count?.toLocaleString() || '0'}</td>
                  <td className="px-6 py-4 text-sm text-stone-600">
                    {new Date(event.created_at).toLocaleDateString()}
                  </td>
                  <td className="px-6 py-4 text-right">
                    <div className="flex items-center justify-end space-x-2">
                      {event.status === 'candidate' && (
                        <>
                          <button
                            onClick={() => handlePublish(event.id)}
                            className="text-emerald-600 hover:text-emerald-700 text-sm font-medium"
                          >
                            Publish
                          </button>
                          <button
                            onClick={() => handleReject(event.id)}
                            className="text-red-600 hover:text-red-700 text-sm font-medium"
                          >
                            Reject
                          </button>
                        </>
                      )}
                      {event.status === 'active' && (
                        <>
                          <button
                            onClick={() => handleArchive(event.id)}
                            className="text-amber-600 hover:text-amber-700 text-sm font-medium"
                          >
                            Archive
                          </button>
                          <button
                            onClick={() => handleClose(event.id)}
                            className="text-stone-600 hover:text-stone-700 text-sm font-medium"
                          >
                            Close
                          </button>
                        </>
                      )}
                      <button
                        onClick={() => handleDelete(event.id)}
                        className="text-red-600 hover:text-red-700 text-sm font-medium"
                      >
                        Delete
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>

          {events.length === 0 && (
            <div className="text-center py-12 text-stone-500">
              No events found
            </div>
          )}
        </div>

        {/* Pagination */}
        {totalPages > 1 && (
          <div className="flex items-center justify-between mt-6">
            <p className="text-sm text-stone-500">
              Showing {(currentPage - 1) * PAGE_SIZE + 1}–{Math.min(currentPage * PAGE_SIZE, totalEvents)} of {totalEvents} events
            </p>
            <div className="flex items-center space-x-1">
              <button
                onClick={() => handlePageChange(currentPage - 1)}
                disabled={currentPage <= 1}
                className="px-3 py-2 rounded-lg text-sm font-medium border border-stone-300 hover:bg-stone-100 disabled:opacity-40 disabled:cursor-not-allowed"
              >
                ← Prev
              </button>
              {Array.from({ length: totalPages }, (_, i) => i + 1)
                .filter(p => p === 1 || p === totalPages || Math.abs(p - currentPage) <= 2)
                .reduce((acc: (number | string)[], p, i, arr) => {
                  if (i > 0 && typeof arr[i - 1] === 'number' && (p as number) - (arr[i - 1] as number) > 1) {
                    acc.push('...');
                  }
                  acc.push(p);
                  return acc;
                }, [])
                .map((p, i) =>
                  typeof p === 'string' ? (
                    <span key={`ellipsis-${i}`} className="px-2 py-2 text-stone-400">...</span>
                  ) : (
                    <button
                      key={p}
                      onClick={() => handlePageChange(p)}
                      className={`px-3 py-2 rounded-lg text-sm font-medium border ${
                        p === currentPage
                          ? 'bg-stone-900 text-white border-stone-900'
                          : 'border-stone-300 hover:bg-stone-100'
                      }`}
                    >
                      {p}
                    </button>
                  )
                )}
              <button
                onClick={() => handlePageChange(currentPage + 1)}
                disabled={currentPage >= totalPages}
                className="px-3 py-2 rounded-lg text-sm font-medium border border-stone-300 hover:bg-stone-100 disabled:opacity-40 disabled:cursor-not-allowed"
              >
                Next →
              </button>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
