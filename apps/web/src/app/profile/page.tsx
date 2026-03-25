'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Header from '../../components/Header';
import { isAuthenticated, fetchWithAuth, getAuthHeaders } from '../../lib/auth';
import { API_BASE_URL } from '../../lib/config';


interface Persona {
  id: string;
  persona_name: string;
  avatar_color: string;
  is_verified: boolean;
  is_deleted?: boolean;
  created_at: string;
}

interface Verification {
  id: string;
  event_id: string;
  event_title: string;
  stakeholder_name: string;
  persona_name?: string;
  status: string;
  review_notes?: string;
  reviewed_at?: string;
  created_at: string;
}

interface ThreadItem {
  id: string;
  title: string;
  event_id: string;
  event_title: string;
  persona_name: string;
  avatar_color: string;
  reply_count: number;
  like_count: number;
  view_count: number;
  created_at: string;
}

interface CommentItem {
  id: string;
  content_preview: string;
  event_id: string;
  event_title: string;
  thread_id: string | null;
  thread_title: string | null;
  persona_name: string;
  avatar_color: string;
  like_count: number;
  reply_count: number;
  created_at: string;
}

type TabKey = 'personas' | 'threads' | 'comments' | 'settings';

function getAvatarColor(colorName: string): string {
  const colors: Record<string, string> = {
    blue: '#3B82F6', green: '#10B981', purple: '#8B5CF6', orange: '#F59E0B',
    red: '#EF4444', teal: '#14B8A6', indigo: '#6366F1', pink: '#EC4899',
  };
  return colors[colorName] || '#3B82F6';
}

export default function ProfilePage() {
  const router = useRouter();
  const [activeTab, setActiveTab] = useState<TabKey>('personas');
  const [userEmail, setUserEmail] = useState('');
  const [displayName, setDisplayName] = useState('');

  // Personas state
  const [personas, setPersonas] = useState<Persona[]>([]);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [editingPersona, setEditingPersona] = useState<{id: string, name: string, color: string} | null>(null);
  const [deletingPersona, setDeletingPersona] = useState<{id: string, name: string} | null>(null);
  const [showVerifications, setShowVerifications] = useState<string | null>(null);
  const [verifications, setVerifications] = useState<Verification[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  // Threads state
  const [threads, setThreads] = useState<ThreadItem[]>([]);
  const [threadsTotal, setThreadsTotal] = useState(0);
  const [threadsPage, setThreadsPage] = useState(1);

  // Comments state
  const [comments, setComments] = useState<CommentItem[]>([]);
  const [commentsTotal, setCommentsTotal] = useState(0);
  const [commentsPage, setCommentsPage] = useState(1);

  // Settings state
  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [newDisplayName, setNewDisplayName] = useState('');
  const [settingsMsg, setSettingsMsg] = useState('');

  useEffect(() => {
    if (!isAuthenticated()) {
      router.push('/auth/login');
      return;
    }
    fetchUserInfo();
    fetchPersonas();
  }, []);

  useEffect(() => {
    if (activeTab === 'threads') fetchThreads();
    if (activeTab === 'comments') fetchComments();
  }, [activeTab, threadsPage, commentsPage]);

  const fetchUserInfo = async () => {
    try {
      const res = await fetchWithAuth(`${API_BASE_URL}/api/auth/me`);
      if (res.ok) {
        const data = await res.json();
        setUserEmail(data.email);
        setDisplayName(data.display_name || '');
        setNewDisplayName(data.display_name || '');
      }
    } catch {}
  };

  const fetchPersonas = async () => {
    try {
      const res = await fetchWithAuth(`${API_BASE_URL}/api/personas?auto_create=true`);
      if (res.ok) {
        const data = await res.json();
        setPersonas(data.items);
      }
    } catch {}
  };

  const fetchThreads = async () => {
    try {
      const res = await fetchWithAuth(`${API_BASE_URL}/api/users/me/threads?page=${threadsPage}&page_size=10`);
      if (res.ok) {
        const data = await res.json();
        setThreads(data.items);
        setThreadsTotal(data.total);
      }
    } catch {}
  };

  const fetchComments = async () => {
    try {
      const res = await fetchWithAuth(`${API_BASE_URL}/api/users/me/comments?page=${commentsPage}&page_size=10`);
      if (res.ok) {
        const data = await res.json();
        setComments(data.items);
        setCommentsTotal(data.total);
      }
    } catch {}
  };

  const handleCreatePersona = async (data: { persona_name: string; avatar_color: string }) => {
    setIsLoading(true);
    try {
      const res = await fetchWithAuth(`${API_BASE_URL}/api/personas`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
      });
      if (res.ok) {
        setShowCreateModal(false);
        fetchPersonas();
      } else {
        const result = await res.json();
        alert(result.detail || 'Failed to create');
      }
    } catch { alert('Network error'); }
    finally { setIsLoading(false); }
  };

  const handleEditPersona = async (name: string, color: string) => {
    if (!editingPersona) return;
    setIsLoading(true);
    try {
      const res = await fetchWithAuth(`${API_BASE_URL}/api/personas/${editingPersona.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ persona_name: name, avatar_color: color }),
      });
      if (res.ok) {
        setEditingPersona(null);
        fetchPersonas();
      } else {
        const result = await res.json();
        alert(result.detail || 'Failed to update');
      }
    } catch { alert('Network error'); }
    finally { setIsLoading(false); }
  };

  const handleDeleteConfirm = async () => {
    if (!deletingPersona) return;
    try {
      const res = await fetchWithAuth(`${API_BASE_URL}/api/personas/${deletingPersona.id}`, { method: 'DELETE' });
      if (res.ok) {
        setDeletingPersona(null);
        fetchPersonas();
      } else {
        const errorData = await res.json();
        alert(`Failed to delete: ${errorData.detail || 'Unknown error'}`);
      }
    } catch { alert('Network error'); }
  };

  const handleViewVerifications = async (personaId: string) => {
    if (showVerifications === personaId) { setShowVerifications(null); return; }
    try {
      const res = await fetchWithAuth(`${API_BASE_URL}/api/personas/${personaId}/verifications`);
      if (res.ok) {
        const data = await res.json();
        setVerifications(data.items);
        setShowVerifications(personaId);
      }
    } catch { alert('Failed to load verifications'); }
  };

  const handleCancelApplication = async (verificationId: string) => {
    if (!confirm('Are you sure you want to cancel this application?')) return;
    try {
      const res = await fetchWithAuth(`${API_BASE_URL}/api/personas/verifications/${verificationId}/cancel`, { method: 'POST' });
      if (res.ok) {
        setVerifications(prev => prev.filter(v => v.id !== verificationId));
      } else {
        const result = await res.json();
        alert(result.detail || 'Cancel failed');
      }
    } catch { alert('Network error'); }
  };

  const handleChangePassword = async (e: React.FormEvent) => {
    e.preventDefault();
    setSettingsMsg('');
    if (newPassword !== confirmPassword) { setSettingsMsg('New passwords do not match'); return; }
    if (newPassword.length < 6) { setSettingsMsg('Password must be at least 6 characters'); return; }
    try {
      const res = await fetchWithAuth(`${API_BASE_URL}/api/users/me/change-password`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ current_password: currentPassword, new_password: newPassword }),
      });
      if (res.ok) {
        setSettingsMsg('Password changed successfully');
        setCurrentPassword(''); setNewPassword(''); setConfirmPassword('');
      } else {
        const data = await res.json();
        setSettingsMsg(data.detail || 'Failed to change password');
      }
    } catch { setSettingsMsg('Network error'); }
  };

  const handleUpdateDisplayName = async () => {
    if (!newDisplayName.trim()) return;
    try {
      const res = await fetchWithAuth(`${API_BASE_URL}/api/users/me/display-name`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ display_name: newDisplayName.trim() }),
      });
      if (res.ok) {
        const data = await res.json();
        setDisplayName(data.display_name);
        setSettingsMsg('Display name updated');
      } else {
        const data = await res.json();
        setSettingsMsg(data.detail || 'Failed to update');
      }
    } catch { setSettingsMsg('Network error'); }
  };

  const tabs: { key: TabKey; label: string; icon: string }[] = [
    { key: 'personas', label: 'My Personas', icon: 'M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z' },
    { key: 'threads', label: 'My Threads', icon: 'M7 8h10M7 12h4m1 8l-4-4H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-3l-4 4z' },
    { key: 'comments', label: 'My Comments', icon: 'M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z' },
    { key: 'settings', label: 'Settings', icon: 'M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.066 2.573c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.573 1.066c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.066-2.573c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z M15 12a3 3 0 11-6 0 3 3 0 016 0z' },
  ];

  const formatDate = (dateStr: string) => {
    if (!dateStr) return '';
    const d = new Date(dateStr);
    const now = new Date();
    const diff = now.getTime() - d.getTime();
    const days = Math.floor(diff / 86400000);
    if (days === 0) return 'Today';
    if (days === 1) return 'Yesterday';
    if (days < 30) return `${days}d ago`;
    return d.toLocaleDateString();
  };

  return (
    <div className="min-h-screen bg-stone-50">
      <Header />

      <div className="container mx-auto px-4 py-8 max-w-5xl">
        {/* Profile Header */}
        <div className="bg-white rounded-2xl border border-stone-200 p-6 mb-6">
          <div className="flex items-center space-x-4">
            <div className="w-16 h-16 bg-stone-900 rounded-full flex items-center justify-center text-white text-2xl font-bold">
              {(displayName || userEmail || '?').charAt(0).toUpperCase()}
            </div>
            <div>
              <h1 className="text-xl font-bold text-stone-900">{displayName || userEmail}</h1>
              <p className="text-sm text-stone-500">{userEmail}</p>
              <p className="text-xs text-stone-400 mt-1">{personas.length} personas | {threadsTotal} threads | {commentsTotal} comments</p>
            </div>
          </div>
        </div>

        {/* Tabs */}
        <div className="flex space-x-1 bg-white rounded-xl border border-stone-200 p-1 mb-6">
          {tabs.map(tab => (
            <button
              key={tab.key}
              onClick={() => setActiveTab(tab.key)}
              className={`flex-1 flex items-center justify-center space-x-2 py-2.5 px-3 rounded-lg text-sm font-medium transition-colors ${
                activeTab === tab.key
                  ? 'bg-stone-900 text-white'
                  : 'text-stone-600 hover:bg-stone-100'
              }`}
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d={tab.icon} />
              </svg>
              <span className="hidden sm:inline">{tab.label}</span>
            </button>
          ))}
        </div>

        {/* Tab Content */}
        {activeTab === 'personas' && (
          <div>
            <div className="flex items-center justify-between mb-4">
              <p className="text-sm text-stone-600">{personas.length} / 10 personas</p>
              <button
                onClick={() => setShowCreateModal(true)}
                disabled={personas.length >= 10}
                className="bg-stone-900 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-stone-800 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                + New Persona
              </button>
            </div>

            <div className="grid md:grid-cols-2 gap-4">
              {personas.map(persona => (
                <div key={persona.id} className={`rounded-xl border p-5 ${persona.is_deleted ? 'bg-stone-100 border-stone-300 opacity-75' : 'bg-white border-stone-200 hover:shadow-md transition-shadow'}`}>
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex items-center space-x-3">
                      <div className="w-10 h-10 rounded-full flex items-center justify-center text-white font-bold"
                        style={{ backgroundColor: persona.is_deleted ? '#9CA3AF' : getAvatarColor(persona.avatar_color) }}>
                        {persona.persona_name.charAt(0).toUpperCase()}
                      </div>
                      <div>
                        <h3 className={`font-semibold ${persona.is_deleted ? 'text-stone-500 line-through' : 'text-stone-900'}`}>
                          {persona.persona_name}
                        </h3>
                        <p className="text-xs text-stone-500">{formatDate(persona.created_at)}</p>
                      </div>
                    </div>
                    {!persona.is_deleted && persona.is_verified && (
                      <span className="px-2 py-0.5 rounded-full text-xs font-medium bg-emerald-100 text-emerald-700">Verified</span>
                    )}
                  </div>

                  {!persona.is_deleted && (
                    <div className="flex flex-wrap gap-2">
                      <button onClick={() => setEditingPersona({ id: persona.id, name: persona.persona_name, color: persona.avatar_color })}
                        className="px-3 py-1.5 bg-stone-50 hover:bg-stone-100 rounded-lg text-xs text-stone-700">Edit</button>
                      <button onClick={() => handleViewVerifications(persona.id)}
                        className="px-3 py-1.5 bg-stone-50 hover:bg-stone-100 rounded-lg text-xs text-stone-700">Verifications</button>
                      <button onClick={() => router.push(`/personas/${persona.id}/verify`)}
                        className="px-3 py-1.5 bg-stone-50 hover:bg-stone-100 rounded-lg text-xs text-stone-700">Apply Verify</button>
                      <button onClick={() => setDeletingPersona({ id: persona.id, name: persona.persona_name })}
                        className="px-3 py-1.5 bg-red-50 hover:bg-red-100 rounded-lg text-xs text-red-700">Delete</button>
                    </div>
                  )}
                </div>
              ))}
            </div>

            {personas.length === 0 && (
              <div className="text-center py-16 bg-white rounded-xl border border-stone-200">
                <p className="text-4xl mb-3">🎭</p>
                <h3 className="text-lg font-semibold text-stone-900 mb-2">No Personas Yet</h3>
                <p className="text-stone-600 mb-4 text-sm">Create your first anonymous identity</p>
                <button onClick={() => setShowCreateModal(true)}
                  className="bg-stone-900 text-white px-5 py-2 rounded-lg text-sm font-medium hover:bg-stone-800">
                  Create Persona
                </button>
              </div>
            )}

            {/* Verifications Panel */}
            {showVerifications && (
              <div className="mt-6 bg-white rounded-xl border border-stone-200 p-5">
                <h3 className="text-base font-bold text-stone-900 mb-3">Verifications</h3>
                {verifications.length > 0 ? (
                  <div className="space-y-3">
                    {verifications.map(v => (
                      <div key={v.id} className="border border-stone-200 rounded-lg p-3">
                        <div className="flex items-center justify-between">
                          <div>
                            <p className="font-medium text-stone-900 text-sm">{v.event_title}</p>
                            <p className="text-xs text-stone-600">As: {v.stakeholder_name}</p>
                            <p className="text-xs text-stone-400">{formatDate(v.created_at)}</p>
                          </div>
                          <div className="flex flex-col items-end space-y-1">
                            <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${
                              v.status === 'approved' ? 'bg-emerald-100 text-emerald-700' :
                              v.status === 'rejected' || v.status === 'revoked' ? 'bg-red-100 text-red-700' :
                              'bg-amber-100 text-amber-700'
                            }`}>{v.status.charAt(0).toUpperCase() + v.status.slice(1)}</span>
                            {v.status === 'pending' && (
                              <button onClick={() => handleCancelApplication(v.id)}
                                className="text-xs text-red-600 hover:underline">Cancel</button>
                            )}
                            {v.status === 'rejected' && (
                              <button onClick={() => router.push(`/personas/${showVerifications}/verify?persona=${showVerifications}&event=${v.event_id}`)}
                                className="text-xs text-blue-600 hover:underline">Re-apply</button>
                            )}
                          </div>
                        </div>
                        {v.review_notes && (
                          <div className={`mt-2 p-2 rounded text-xs ${
                            v.status === 'rejected' ? 'bg-red-50 text-red-700' :
                            v.status === 'approved' ? 'bg-emerald-50 text-emerald-700' :
                            'bg-stone-50 text-stone-600'
                          }`}>
                            <span className="font-medium">Admin feedback: </span>{v.review_notes}
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-stone-500 text-center py-6 text-sm">No verification applications</p>
                )}
              </div>
            )}
          </div>
        )}

        {activeTab === 'threads' && (
          <div>
            {threads.length > 0 ? (
              <div className="space-y-3">
                {threads.map(t => (
                  <div key={t.id}
                    onClick={() => router.push(`/events/${t.event_id}/threads/${t.id}`)}
                    className="bg-white rounded-xl border border-stone-200 p-4 hover:shadow-md transition-shadow cursor-pointer">
                    <h3 className="font-semibold text-stone-900 mb-1">{t.title}</h3>
                    <p className="text-xs text-stone-500 mb-2">in {t.event_title}</p>
                    <div className="flex items-center space-x-4 text-xs text-stone-500">
                      <span className="flex items-center space-x-1">
                        <div className="w-4 h-4 rounded-full flex items-center justify-center text-white text-[8px]"
                          style={{ backgroundColor: getAvatarColor(t.avatar_color) }}>
                          {t.persona_name.charAt(0)}
                        </div>
                        <span>{t.persona_name}</span>
                      </span>
                      <span>{t.reply_count} replies</span>
                      <span>{t.like_count} likes</span>
                      <span>{t.view_count} views</span>
                      <span>{formatDate(t.created_at)}</span>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-16 bg-white rounded-xl border border-stone-200">
                <p className="text-4xl mb-3">💬</p>
                <h3 className="text-lg font-semibold text-stone-900 mb-2">No Threads Yet</h3>
                <p className="text-stone-600 text-sm">Start a discussion on any event</p>
              </div>
            )}

            {threadsTotal > 10 && (
              <div className="flex items-center justify-center space-x-4 mt-6">
                <button onClick={() => setThreadsPage(p => Math.max(1, p - 1))} disabled={threadsPage === 1}
                  className="px-4 py-2 bg-white border border-stone-200 rounded-lg text-sm disabled:opacity-50">Previous</button>
                <span className="text-sm text-stone-600">Page {threadsPage} of {Math.ceil(threadsTotal / 10)}</span>
                <button onClick={() => setThreadsPage(p => p + 1)} disabled={threadsPage >= Math.ceil(threadsTotal / 10)}
                  className="px-4 py-2 bg-white border border-stone-200 rounded-lg text-sm disabled:opacity-50">Next</button>
              </div>
            )}
          </div>
        )}

        {activeTab === 'comments' && (
          <div>
            {comments.length > 0 ? (
              <div className="space-y-3">
                {comments.map(c => (
                  <div key={c.id}
                    onClick={() => {
                      if (c.thread_id) router.push(`/events/${c.event_id}/threads/${c.thread_id}`);
                      else router.push(`/events/${c.event_id}`);
                    }}
                    className="bg-white rounded-xl border border-stone-200 p-4 hover:shadow-md transition-shadow cursor-pointer">
                    <p className="text-stone-900 text-sm mb-2">{c.content_preview}</p>
                    <div className="text-xs text-stone-500 mb-2">
                      in <span className="font-medium">{c.event_title}</span>
                      {c.thread_title && <> &rarr; <span className="font-medium">{c.thread_title}</span></>}
                    </div>
                    <div className="flex items-center space-x-4 text-xs text-stone-400">
                      <span className="flex items-center space-x-1">
                        <div className="w-4 h-4 rounded-full flex items-center justify-center text-white text-[8px]"
                          style={{ backgroundColor: getAvatarColor(c.avatar_color) }}>
                          {c.persona_name.charAt(0)}
                        </div>
                        <span>{c.persona_name}</span>
                      </span>
                      <span>{c.like_count} likes</span>
                      <span>{c.reply_count} replies</span>
                      <span>{formatDate(c.created_at)}</span>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-16 bg-white rounded-xl border border-stone-200">
                <p className="text-4xl mb-3">💭</p>
                <h3 className="text-lg font-semibold text-stone-900 mb-2">No Comments Yet</h3>
                <p className="text-stone-600 text-sm">Join discussions on events and threads</p>
              </div>
            )}

            {commentsTotal > 10 && (
              <div className="flex items-center justify-center space-x-4 mt-6">
                <button onClick={() => setCommentsPage(p => Math.max(1, p - 1))} disabled={commentsPage === 1}
                  className="px-4 py-2 bg-white border border-stone-200 rounded-lg text-sm disabled:opacity-50">Previous</button>
                <span className="text-sm text-stone-600">Page {commentsPage} of {Math.ceil(commentsTotal / 10)}</span>
                <button onClick={() => setCommentsPage(p => p + 1)} disabled={commentsPage >= Math.ceil(commentsTotal / 10)}
                  className="px-4 py-2 bg-white border border-stone-200 rounded-lg text-sm disabled:opacity-50">Next</button>
              </div>
            )}
          </div>
        )}

        {activeTab === 'settings' && (
          <div className="max-w-lg space-y-6">
            {settingsMsg && (
              <div className={`p-3 rounded-lg text-sm ${settingsMsg.includes('success') || settingsMsg.includes('updated') ? 'bg-emerald-50 text-emerald-700' : 'bg-red-50 text-red-700'}`}>
                {settingsMsg}
              </div>
            )}

            {/* Account Info */}
            <div className="bg-white rounded-xl border border-stone-200 p-5">
              <h3 className="text-base font-bold text-stone-900 mb-4">Account</h3>
              <div className="space-y-3">
                <div>
                  <label className="block text-xs font-medium text-stone-500 mb-1">Email</label>
                  <p className="text-sm text-stone-900">{userEmail}</p>
                </div>
                <div>
                  <label className="block text-xs font-medium text-stone-500 mb-1">Display Name</label>
                  <div className="flex space-x-2">
                    <input type="text" value={newDisplayName} onChange={e => setNewDisplayName(e.target.value)}
                      className="flex-1 px-3 py-1.5 border border-stone-300 rounded-lg text-sm focus:ring-2 focus:ring-stone-500"
                      placeholder="Your display name" />
                    <button onClick={handleUpdateDisplayName}
                      className="px-3 py-1.5 bg-stone-900 text-white rounded-lg text-sm hover:bg-stone-800">Save</button>
                  </div>
                </div>
              </div>
            </div>

            {/* Change Password */}
            <div className="bg-white rounded-xl border border-stone-200 p-5">
              <h3 className="text-base font-bold text-stone-900 mb-4">Change Password</h3>
              <form onSubmit={handleChangePassword} className="space-y-3">
                <div>
                  <label className="block text-xs font-medium text-stone-500 mb-1">Current Password</label>
                  <input type="password" value={currentPassword} onChange={e => setCurrentPassword(e.target.value)}
                    className="w-full px-3 py-1.5 border border-stone-300 rounded-lg text-sm focus:ring-2 focus:ring-stone-500" required />
                </div>
                <div>
                  <label className="block text-xs font-medium text-stone-500 mb-1">New Password</label>
                  <input type="password" value={newPassword} onChange={e => setNewPassword(e.target.value)}
                    className="w-full px-3 py-1.5 border border-stone-300 rounded-lg text-sm focus:ring-2 focus:ring-stone-500" required minLength={6} />
                </div>
                <div>
                  <label className="block text-xs font-medium text-stone-500 mb-1">Confirm New Password</label>
                  <input type="password" value={confirmPassword} onChange={e => setConfirmPassword(e.target.value)}
                    className="w-full px-3 py-1.5 border border-stone-300 rounded-lg text-sm focus:ring-2 focus:ring-stone-500" required minLength={6} />
                </div>
                <button type="submit" className="w-full px-3 py-2 bg-stone-900 text-white rounded-lg text-sm font-medium hover:bg-stone-800">
                  Update Password
                </button>
              </form>
            </div>
          </div>
        )}
      </div>

      {/* Modals */}
      {showCreateModal && <CreatePersonaModal onSubmit={handleCreatePersona} onClose={() => setShowCreateModal(false)} isLoading={isLoading} />}
      {editingPersona && <EditPersonaModal persona={editingPersona} onSubmit={handleEditPersona} onClose={() => setEditingPersona(null)} isLoading={isLoading} />}
      {deletingPersona && <DeleteConfirmModal personaName={deletingPersona.name} onConfirm={handleDeleteConfirm} onCancel={() => setDeletingPersona(null)} isLoading={isLoading} />}
    </div>
  );
}

/* --- Modals --- */

function CreatePersonaModal({ onSubmit, onClose, isLoading }: { onSubmit: (d: { persona_name: string; avatar_color: string }) => void; onClose: () => void; isLoading: boolean }) {
  const [name, setName] = useState('');
  const [color, setColor] = useState('blue');
  const colors = ['blue', 'green', 'purple', 'orange', 'red', 'teal', 'indigo', 'pink'];

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="bg-white rounded-xl max-w-md w-full mx-4">
        <div className="p-5 border-b border-stone-200">
          <h2 className="text-lg font-bold text-stone-900">Create Persona</h2>
        </div>
        <form onSubmit={e => { e.preventDefault(); onSubmit({ persona_name: name, avatar_color: color }); }} className="p-5 space-y-4">
          <div>
            <label className="block text-sm font-medium text-stone-700 mb-1">Name *</label>
            <input type="text" value={name} onChange={e => setName(e.target.value)}
              className="w-full px-3 py-2 border border-stone-300 rounded-lg focus:ring-2 focus:ring-stone-500" required />
          </div>
          <div>
            <label className="block text-sm font-medium text-stone-700 mb-2">Color</label>
            <div className="flex gap-2">
              {colors.map(c => (
                <button key={c} type="button" onClick={() => setColor(c)}
                  className={`w-9 h-9 rounded-full border-2 ${color === c ? 'border-stone-900 scale-110' : 'border-transparent'}`}
                  style={{ backgroundColor: getAvatarColor(c) }} />
              ))}
            </div>
          </div>
          <div className="flex justify-end space-x-3 pt-3 border-t border-stone-200">
            <button type="button" onClick={onClose} className="px-4 py-2 border border-stone-300 rounded-lg text-sm">Cancel</button>
            <button type="submit" disabled={isLoading} className="px-4 py-2 bg-stone-900 text-white rounded-lg text-sm disabled:opacity-50">
              {isLoading ? 'Creating...' : 'Create'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

function EditPersonaModal({ persona, onSubmit, onClose, isLoading }: { persona: { name: string; color: string }; onSubmit: (n: string, c: string) => void; onClose: () => void; isLoading: boolean }) {
  const [name, setName] = useState(persona.name);
  const [color, setColor] = useState(persona.color);
  const colors = ['blue', 'green', 'purple', 'orange', 'red', 'teal', 'indigo', 'pink'];

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="bg-white rounded-xl max-w-md w-full mx-4">
        <div className="p-5 border-b border-stone-200">
          <h2 className="text-lg font-bold text-stone-900">Edit Persona</h2>
        </div>
        <form onSubmit={e => { e.preventDefault(); onSubmit(name, color); }} className="p-5 space-y-4">
          <div>
            <label className="block text-sm font-medium text-stone-700 mb-1">Name *</label>
            <input type="text" value={name} onChange={e => setName(e.target.value)}
              className="w-full px-3 py-2 border border-stone-300 rounded-lg focus:ring-2 focus:ring-stone-500" required />
          </div>
          <div>
            <label className="block text-sm font-medium text-stone-700 mb-2">Color</label>
            <div className="flex gap-2">
              {colors.map(c => (
                <button key={c} type="button" onClick={() => setColor(c)}
                  className={`w-9 h-9 rounded-full border-2 ${color === c ? 'border-stone-900 scale-110' : 'border-transparent'}`}
                  style={{ backgroundColor: getAvatarColor(c) }} />
              ))}
            </div>
          </div>
          <div className="flex justify-end space-x-3 pt-3 border-t border-stone-200">
            <button type="button" onClick={onClose} className="px-4 py-2 border border-stone-300 rounded-lg text-sm">Cancel</button>
            <button type="submit" disabled={isLoading} className="px-4 py-2 bg-stone-900 text-white rounded-lg text-sm disabled:opacity-50">
              {isLoading ? 'Saving...' : 'Save'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

function DeleteConfirmModal({ personaName, onConfirm, onCancel, isLoading }: { personaName: string; onConfirm: () => void; onCancel: () => void; isLoading: boolean }) {
  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="bg-white rounded-xl max-w-md w-full mx-4 p-5">
        <h2 className="text-lg font-bold text-stone-900 mb-2">Delete "{personaName}"?</h2>
        <div className="bg-amber-50 border border-amber-200 rounded-lg p-3 mb-4 text-sm text-amber-800">
          <p>Comments will remain visible as "Deleted User". This cannot be undone.</p>
        </div>
        <div className="flex justify-end space-x-3">
          <button onClick={onCancel} disabled={isLoading} className="px-4 py-2 border border-stone-300 rounded-lg text-sm">Cancel</button>
          <button onClick={onConfirm} disabled={isLoading} className="px-4 py-2 bg-red-600 text-white rounded-lg text-sm hover:bg-red-700 disabled:opacity-50">
            {isLoading ? 'Deleting...' : 'Delete'}
          </button>
        </div>
      </div>
    </div>
  );
}
