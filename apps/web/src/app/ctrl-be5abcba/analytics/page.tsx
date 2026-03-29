'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { API_BASE_URL } from '../../../lib/config';

const GATE_PASSWORD = process.env.NEXT_PUBLIC_ADMIN_GATE_PASSWORD || 'wrhitw2026';

interface AnalyticsData {
  period: { days: number; start: string; end: string };
  users: {
    total: number;
    new_registrations: number;
    active_users: number;
    today_registrations: number;
    today_active_users: number;
    registrations_by_day: { date: string; count: number }[];
  };
  engagement: {
    total_threads: number;
    new_threads: number;
    total_comments: number;
    new_comments: number;
    new_likes: number;
    threads_by_day: { date: string; count: number }[];
    comments_by_day: { date: string; count: number }[];
  };
  content: {
    total_active_events: number;
    events_by_category: { category: string; count: number }[];
    most_viewed_events: { id: string; title: string; view_count: number; comment_count: number }[];
    most_discussed_events: { id: string; title: string; comment_count: number; view_count: number }[];
  };
  traffic: {
    total_requests: number;
    unique_ips: number;
    requests_by_day: { date: string; count: number }[];
    slow_requests: number;
    error_count: number;
    top_paths: { path: string; count: number }[];
    status_breakdown: Record<string, number>;
  };
  page_views: {
    total: number;
    unique_visitors: number;
    today_pv: number;
    today_uv: number;
    views_by_day: { date: string; count: number }[];
    uv_by_day: { date: string; count: number }[];
    top_pages: { path: string; count: number }[];
    top_referrers: { referrer: string; count: number }[];
  };
  recent_errors: { id: number; timestamp: string; method: string; path: string; error_type: string; error_message: string }[];
}

export default function AnalyticsDashboard() {
  const router = useRouter();
  const [gatePass, setGatePass] = useState('');
  const [gateUnlocked, setGateUnlocked] = useState(false);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [data, setData] = useState<AnalyticsData | null>(null);
  const [days, setDays] = useState(7);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    const unlocked = sessionStorage.getItem('admin_gate_unlocked');
    if (unlocked === 'true') setGateUnlocked(true);
    const stored = localStorage.getItem('admin_auth');
    if (stored) {
      setIsAuthenticated(true);
    }
  }, []);

  useEffect(() => {
    if (isAuthenticated) fetchAnalytics();
  }, [isAuthenticated, days]);

  const getAuthHeaders = (): HeadersInit => {
    const headers: Record<string, string> = { 'Content-Type': 'application/json' };
    const stored = localStorage.getItem('admin_auth');
    if (stored) {
      const { username, password } = JSON.parse(stored);
      headers['Authorization'] = 'Basic ' + btoa(`${username}:${password}`);
    }
    return headers;
  };

  const fetchAnalytics = async () => {
    setIsLoading(true);
    setError('');
    try {
      const res = await fetch(`${API_BASE_URL}/api/admin/analytics?days=${days}`, {
        headers: getAuthHeaders(),
      });
      if (res.ok) {
        setData(await res.json());
      } else if (res.status === 401) {
        setIsAuthenticated(false);
        localStorage.removeItem('admin_auth');
      } else {
        setError('Failed to fetch analytics');
      }
    } catch {
      setError('Network error');
    } finally {
      setIsLoading(false);
    }
  };

  const handleGateSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (gatePass === GATE_PASSWORD) {
      setGateUnlocked(true);
      sessionStorage.setItem('admin_gate_unlocked', 'true');
    }
  };

  const handleLogin = (e: React.FormEvent) => {
    e.preventDefault();
    localStorage.setItem('admin_auth', JSON.stringify({ username, password }));
    setIsAuthenticated(true);
  };

  // Gate screen
  if (!gateUnlocked) {
    return (
      <div className="min-h-screen bg-stone-100 flex items-center justify-center p-4">
        <form onSubmit={handleGateSubmit} className="bg-white p-8 rounded-xl shadow-sm max-w-sm w-full">
          <h2 className="text-lg font-bold mb-4 text-center">Admin Access</h2>
          <input type="password" value={gatePass} onChange={e => setGatePass(e.target.value)}
            className="w-full px-4 py-2 border rounded-lg mb-3" placeholder="Gate password" autoFocus />
          <button type="submit" className="w-full bg-stone-900 text-white py-2 rounded-lg">Enter</button>
        </form>
      </div>
    );
  }

  // Login screen
  if (!isAuthenticated) {
    return (
      <div className="min-h-screen bg-stone-100 flex items-center justify-center p-4">
        <form onSubmit={handleLogin} className="bg-white p-8 rounded-xl shadow-sm max-w-sm w-full">
          <h2 className="text-lg font-bold mb-4 text-center">Admin Login</h2>
          <input type="text" value={username} onChange={e => setUsername(e.target.value)}
            className="w-full px-4 py-2 border rounded-lg mb-3" placeholder="Username" autoFocus />
          <input type="password" value={password} onChange={e => setPassword(e.target.value)}
            className="w-full px-4 py-2 border rounded-lg mb-3" placeholder="Password" />
          <button type="submit" className="w-full bg-stone-900 text-white py-2 rounded-lg">Sign In</button>
        </form>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-stone-100">
      {/* Header */}
      <div className="bg-white border-b border-stone-200 px-6 py-4">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div>
            <h1 className="text-xl font-bold text-stone-900">📊 Analytics Dashboard</h1>
            <p className="text-xs text-stone-500">User activity, traffic, and engagement metrics</p>
          </div>
          <div className="flex items-center space-x-3">
            <button onClick={() => router.push('/ctrl-be5abcba')}
              className="bg-stone-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-stone-700">
              ← Admin
            </button>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-6 py-6">
        {/* Period Selector */}
        <div className="flex items-center space-x-2 mb-6">
          {[7, 14, 30, 90].map(d => (
            <button key={d} onClick={() => setDays(d)}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                days === d ? 'bg-emerald-600 text-white' : 'bg-white text-stone-600 hover:bg-stone-50 border border-stone-200'
              }`}>
              {d}d
            </button>
          ))}
          <button onClick={fetchAnalytics} className="ml-4 px-3 py-2 text-stone-500 hover:text-stone-700 text-sm">
            🔄 Refresh
          </button>
          {isLoading && <span className="text-sm text-stone-400">Loading...</span>}
        </div>

        {error && <div className="bg-red-50 text-red-600 p-3 rounded-lg mb-4 text-sm">{error}</div>}

        {data && (
          <>
            {/* KPI Cards */}
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4 mb-8">
              <KPICard label="Total Users" value={data.users.total} />
              <KPICard label="New Users" value={data.users.new_registrations} suffix={`in ${days}d`} color="emerald" />
              <KPICard label="Active Users" value={data.users.active_users} suffix={`in ${days}d`} color="blue" />
              <KPICard label="Page Views" value={data.page_views.total} suffix={`in ${days}d`} color="violet" />
              <KPICard label="UV" value={data.page_views.unique_visitors} suffix={`in ${days}d`} color="indigo" />
              <KPICard label="Errors" value={data.traffic.error_count} suffix={`in ${days}d`}
                color={data.traffic.error_count > 0 ? 'red' : 'emerald'} />
            </div>

            {/* Today's Stats */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
              <KPICard label="Today PV" value={data.page_views.today_pv} color="violet" />
              <KPICard label="Today UV" value={data.page_views.today_uv} color="indigo" />
              <KPICard label="Today New Users" value={data.users.today_registrations} color="emerald" />
              <KPICard label="Today Active Users" value={data.users.today_active_users} color="blue" />
            </div>

            {/* Engagement Row */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
              <KPICard label="New Threads" value={data.engagement.new_threads} suffix={`/ ${data.engagement.total_threads} total`} color="blue" />
              <KPICard label="New Comments" value={data.engagement.new_comments} suffix={`/ ${data.engagement.total_comments} total`} color="violet" />
              <KPICard label="New Likes" value={data.engagement.new_likes} color="rose" />
              <KPICard label="Active Events" value={data.content.total_active_events} color="amber" />
            </div>

            {/* Charts Row */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
              <BarChart title="PV by Day" data={data.page_views.views_by_day} color="bg-violet-500" />
              <BarChart title="UV by Day" data={data.page_views.uv_by_day || []} color="bg-indigo-500" />
              <BarChart title="New Comments by Day" data={data.engagement.comments_by_day} color="bg-blue-500" />
              <BarChart title="New Registrations by Day" data={data.users.registrations_by_day} color="bg-emerald-500" />
            </div>

            {/* Tables Row */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
              <TableCard title="🏆 Most Viewed Events" items={data.content.most_viewed_events.map(e => ({
                label: e.title, value: `${e.view_count} views`
              }))} />
              <TableCard title="💬 Most Discussed Events" items={data.content.most_discussed_events.map(e => ({
                label: e.title, value: `${e.comment_count} comments`
              }))} />
              <TableCard title="📄 Top Pages" items={data.page_views.top_pages.map(p => ({
                label: p.path, value: `${p.count}`
              }))} />
              <TableCard title="🔗 Top Referrers" items={data.page_views.top_referrers.map(r => ({
                label: r.referrer, value: `${r.count}`
              }))} />
              <TableCard title="🛤️ Top API Paths" items={data.traffic.top_paths.map(p => ({
                label: p.path, value: `${p.count}`
              }))} />
              <TableCard title="📊 Events by Category" items={data.content.events_by_category.map(c => ({
                label: c.category || 'Uncategorized', value: `${c.count}`
              }))} />
            </div>

            {/* Traffic Health */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
              <div className="bg-white p-5 rounded-xl border border-stone-200">
                <h3 className="font-semibold text-stone-900 mb-3">🚦 Traffic Health</h3>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between"><span className="text-stone-600">Unique IPs</span><span className="font-medium">{data.traffic.unique_ips}</span></div>
                  <div className="flex justify-between"><span className="text-stone-600">Unique Visitors (PV)</span><span className="font-medium">{data.page_views.unique_visitors}</span></div>
                  <div className="flex justify-between"><span className="text-stone-600">Slow Requests (&gt;2s)</span>
                    <span className={`font-medium ${data.traffic.slow_requests > 0 ? 'text-amber-600' : 'text-emerald-600'}`}>{data.traffic.slow_requests}</span>
                  </div>
                  <div className="flex justify-between"><span className="text-stone-600">Server Errors (5xx)</span>
                    <span className={`font-medium ${data.traffic.error_count > 0 ? 'text-red-600' : 'text-emerald-600'}`}>{data.traffic.error_count}</span>
                  </div>
                  <div className="border-t border-stone-100 pt-2 mt-2">
                    <p className="text-xs text-stone-400 mb-1">Status Breakdown</p>
                    <div className="flex space-x-3">
                      {Object.entries(data.traffic.status_breakdown).map(([k, v]) => (
                        <span key={k} className={`text-xs px-2 py-1 rounded ${
                          k === '5xx' ? 'bg-red-100 text-red-700' :
                          k === '4xx' ? 'bg-amber-100 text-amber-700' :
                          'bg-emerald-100 text-emerald-700'
                        }`}>{k}: {v}</span>
                      ))}
                    </div>
                  </div>
                </div>
              </div>

              {/* Recent Errors */}
              <div className="bg-white p-5 rounded-xl border border-stone-200">
                <h3 className="font-semibold text-stone-900 mb-3">🔴 Recent Errors</h3>
                {data.recent_errors.length === 0 ? (
                  <p className="text-sm text-stone-400">No errors in this period ✅</p>
                ) : (
                  <div className="space-y-2 max-h-64 overflow-y-auto">
                    {data.recent_errors.slice(0, 10).map(err => (
                      <div key={err.id} className="text-xs border-l-2 border-red-300 pl-3 py-1">
                        <div className="text-stone-400">{new Date(err.timestamp).toLocaleString()}</div>
                        <div className="font-medium text-red-700">{err.error_type}</div>
                        <div className="text-stone-600 truncate">{err.method} {err.path}</div>
                        <div className="text-stone-500 truncate">{err.error_message}</div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
}


// ─── Sub Components ────────────────────────────────────────

function KPICard({ label, value, suffix, color = 'stone' }: {
  label: string; value: number; suffix?: string; color?: string;
}) {
  const colorMap: Record<string, string> = {
    stone: 'text-stone-900', emerald: 'text-emerald-600', blue: 'text-blue-600',
    violet: 'text-violet-600', amber: 'text-amber-600', red: 'text-red-600', rose: 'text-rose-600',
    indigo: 'text-indigo-600',
  };
  return (
    <div className="bg-white p-4 rounded-xl border border-stone-200">
      <p className="text-xs text-stone-500 mb-1">{label}</p>
      <p className={`text-2xl font-bold ${colorMap[color] || colorMap.stone}`}>
        {value.toLocaleString()}
      </p>
      {suffix && <p className="text-xs text-stone-400 mt-0.5">{suffix}</p>}
    </div>
  );
}


function BarChart({ title, data, color = 'bg-blue-500' }: {
  title: string; data: { date: string; count: number }[]; color?: string;
}) {
  if (!data || data.length === 0) {
    return (
      <div className="bg-white p-5 rounded-xl border border-stone-200">
        <h3 className="font-semibold text-stone-900 mb-3 text-sm">{title}</h3>
        <p className="text-xs text-stone-400">No data for this period</p>
      </div>
    );
  }

  const maxCount = Math.max(...data.map(d => d.count), 1);

  return (
    <div className="bg-white p-5 rounded-xl border border-stone-200">
      <h3 className="font-semibold text-stone-900 mb-3 text-sm">{title}</h3>
      <div className="space-y-1.5">
        {data.map(d => (
          <div key={d.date} className="flex items-center space-x-2">
            <span className="text-xs text-stone-400 w-16 shrink-0">{d.date.slice(5)}</span>
            <div className="flex-1 bg-stone-100 rounded-full h-4 overflow-hidden">
              <div className={`h-full ${color} rounded-full transition-all`}
                style={{ width: `${Math.max((d.count / maxCount) * 100, 2)}%` }} />
            </div>
            <span className="text-xs text-stone-600 w-10 text-right">{d.count}</span>
          </div>
        ))}
      </div>
    </div>
  );
}


function TableCard({ title, items }: {
  title: string; items: { label: string; value: string }[];
}) {
  return (
    <div className="bg-white p-5 rounded-xl border border-stone-200">
      <h3 className="font-semibold text-stone-900 mb-3 text-sm">{title}</h3>
      {items.length === 0 ? (
        <p className="text-xs text-stone-400">No data</p>
      ) : (
        <div className="space-y-2">
          {items.map((item, i) => (
            <div key={i} className="flex items-center justify-between text-sm">
              <span className="text-stone-700 truncate mr-3 flex-1" title={item.label}>{item.label}</span>
              <span className="text-stone-500 font-medium whitespace-nowrap">{item.value}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
