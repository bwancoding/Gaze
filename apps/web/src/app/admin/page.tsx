'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080';

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
  archived_events: number;
  closed_events: number;
}

export default function AdminDashboard() {
  const router = useRouter();
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [events, setEvents] = useState<Event[]>([]);
  const [stats, setStats] = useState<Stats | null>(null);
  const [statusFilter, setStatusFilter] = useState('all');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  // Check if already authenticated
  useEffect(() => {
    const storedAuth = localStorage.getItem('admin_auth');
    if (storedAuth) {
      setIsAuthenticated(true);
      fetchData();
    }
  }, []);

  const fetchData = async () => {
    if (!isAuthenticated) return;
    
    try {
      const [eventsRes, statsRes] = await Promise.all([
        fetch(`${API_BASE_URL}/api/admin/events?status_filter=${statusFilter}`, {
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
        setStats(statsData);
      }
    } catch (err) {
      console.error('Failed to fetch data:', err);
    }
  };

  useEffect(() => {
    if (isAuthenticated) {
      fetchData();
    }
  }, [statusFilter, isAuthenticated]);

  const getAuthHeaders = () => {
    const storedAuth = localStorage.getItem('admin_auth');
    if (storedAuth) {
      const { username, password } = JSON.parse(storedAuth);
      return {
        'Authorization': 'Basic ' + btoa(`${username}:${password}`),
        'Content-Type': 'application/json',
      };
    }
    return {};
  };

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

  const handleCreateEvent = () => {
    router.push('/admin/events/new');
  };

  if (!isAuthenticated) {
    return (
      <div className="min-h-screen bg-stone-50 flex items-center justify-center">
        <div className="bg-white p-8 rounded-2xl shadow-xl max-w-md w-full">
          <div className="text-center mb-8">
            <h1 className="text-2xl font-bold text-stone-900 mb-2">WRHITW Admin</h1>
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
            <p>Default credentials: admin / wrhitw_admin_2026</p>
            <p className="mt-1">Change in production!</p>
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
              <h1 className="text-xl font-bold text-stone-900">WRHITW Admin</h1>
              <p className="text-xs text-stone-500">Event Management Dashboard</p>
            </div>
            <div className="flex items-center space-x-4">
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
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
            <div className="bg-white p-6 rounded-xl border border-stone-200">
              <p className="text-sm text-stone-600 mb-1">Total Events</p>
              <p className="text-3xl font-bold text-stone-900">{stats.total_events}</p>
            </div>
            <div className="bg-white p-6 rounded-xl border border-stone-200">
              <p className="text-sm text-stone-600 mb-1">Active</p>
              <p className="text-3xl font-bold text-emerald-600">{stats.active_events}</p>
            </div>
            <div className="bg-white p-6 rounded-xl border border-stone-200">
              <p className="text-sm text-stone-600 mb-1">Archived</p>
              <p className="text-3xl font-bold text-amber-600">{stats.archived_events}</p>
            </div>
            <div className="bg-white p-6 rounded-xl border border-stone-200">
              <p className="text-sm text-stone-600 mb-1">Closed</p>
              <p className="text-3xl font-bold text-stone-600">{stats.closed_events}</p>
            </div>
          </div>
        )}

        {/* Actions */}
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center space-x-2">
            <span className="text-sm text-stone-600">Filter:</span>
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="border border-stone-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-stone-500"
            >
              <option value="all">All Events</option>
              <option value="active">Active</option>
              <option value="archived">Archived</option>
              <option value="closed">Closed</option>
            </select>
          </div>

          <button
            onClick={handleCreateEvent}
            className="bg-stone-900 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-stone-800 transition-colors"
          >
            + Create Event
          </button>
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
                      event.status === 'archived' ? 'bg-amber-100 text-amber-700' :
                      'bg-stone-100 text-stone-700'
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
                      {event.status === 'active' && (
                        <>
                          <button
                            onClick={() => handleArchive(event.id)}
                            className="text-amber-600 hover:text-amber-700 text-sm font-medium"
                            title="Archive"
                          >
                            Archive
                          </button>
                          <button
                            onClick={() => handleClose(event.id)}
                            className="text-stone-600 hover:text-stone-700 text-sm font-medium"
                            title="Close"
                          >
                            Close
                          </button>
                        </>
                      )}
                      <button
                        onClick={() => handleDelete(event.id)}
                        className="text-red-600 hover:text-red-700 text-sm font-medium"
                        title="Delete Permanently"
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
      </main>
    </div>
  );
}
