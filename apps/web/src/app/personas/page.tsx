'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080';

interface Persona {
  id: string;
  persona_name: string;
  avatar_color: string;
  is_verified: boolean;
  created_at: string;
}

interface Verification {
  id: string;
  event_id: string;
  event_title: string;
  stakeholder_name: string;
  status: string;
  created_at: string;
}

export default function PersonaManagement() {
  const router = useRouter();
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [personas, setPersonas] = useState<Persona[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [selectedPersona, setSelectedPersona] = useState<Persona | null>(null);
  const [showVerifications, setShowVerifications] = useState<string | null>(null);
  const [verifications, setVerifications] = useState<Verification[]>([]);
  const [showAutoCreateTip, setShowAutoCreateTip] = useState(false);
  const [editingPersona, setEditingPersona] = useState<{id: string, name: string, color: string} | null>(null);
  const [deletingPersona, setDeletingPersona] = useState<{id: string, name: string} | null>(null);

  // Check authentication
  useEffect(() => {
    const token = localStorage.getItem('access_token');
    if (token) {
      setIsAuthenticated(true);
      fetchPersonas();
    }
  }, []);

  const getAuthHeaders = () => {
    const token = localStorage.getItem('access_token');
    if (token) {
      return {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      };
    }
    return {};
  };

  const fetchPersonas = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/personas?auto_create=true`, {
        headers: getAuthHeaders(),
      });

      if (response.ok) {
        const data = await response.json();
        setPersonas(data.items);
        
        // Show auto-create tip if a new persona was created
        if (data.auto_created) {
          setShowAutoCreateTip(true);
        }
      } else if (response.status === 401) {
        // Only logout on confirmed 401, not on network errors
        console.warn('Authentication failed, clearing stored auth');
        handleLogout();
      } else {
        console.error('Failed to fetch personas:', response.status);
      }
    } catch (err) {
      console.error('Failed to fetch personas:', err);
      // Don't logout on network errors - keep user logged in
    }
  };

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    try {
      // 1. Call login API to get token
      const loginResponse = await fetch(`${API_BASE_URL}/api/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email: username, password }),
      });

      if (!loginResponse.ok) {
        const errorData = await loginResponse.json();
        setError(errorData.detail || 'Invalid credentials');
        setIsLoading(false);
        return;
      }

      const loginData = await loginResponse.json();
      
      // 2. Save token to localStorage
      localStorage.setItem('access_token', loginData.access_token);
      localStorage.setItem('refresh_token', loginData.refresh_token);
      localStorage.setItem('token_expires_at', (Date.now() + loginData.expires_in * 1000).toString());
      
      // 3. Fetch personas with new token
      const personasResponse = await fetch(`${API_BASE_URL}/api/personas?auto_create=true`, {
        headers: {
          'Authorization': `Bearer ${loginData.access_token}`,
          'Content-Type': 'application/json',
        },
      });

      if (personasResponse.ok) {
        setIsAuthenticated(true);
        fetchPersonas();
      } else {
        setError('Failed to load personas');
      }
    } catch (err) {
      console.error('Login error:', err);
      setError('Network error');
    } finally {
      setIsLoading(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('user_auth');
    setIsAuthenticated(false);
    setUsername('');
    setPassword('');
  };

  const handleCreatePersona = async (data: any) => {
    setIsLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/api/personas`, {
        method: 'POST',
        headers: getAuthHeaders(),
        body: JSON.stringify(data),
      });

      if (response.ok) {
        alert('Persona created successfully!');
        setShowCreateModal(false);
        fetchPersonas();
      } else {
        const result = await response.json();
        alert(result.detail || 'Failed to create');
      }
    } catch (err) {
      alert('Network error');
    } finally {
      setIsLoading(false);
    }
  };

  const handleEditPersona = async (name: string, color: string) => {
    if (!editingPersona) return;
    
    setIsLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/api/personas/${editingPersona.id}`, {
        method: 'PUT',
        headers: getAuthHeaders(),
        body: JSON.stringify({
          persona_name: name,
          avatar_color: color,
        }),
      });

      if (response.ok) {
        alert('✅ Persona updated!');
        setEditingPersona(null);
        fetchPersonas();
      } else {
        const result = await response.json();
        alert(result.detail || 'Failed to update');
      }
    } catch (err) {
      alert('Network error');
    } finally {
      setIsLoading(false);
    }
  };

  const handleDeleteConfirm = async () => {
    if (!deletingPersona) return;

    try {
      const response = await fetch(`${API_BASE_URL}/api/personas/${deletingPersona.id}`, {
        method: 'DELETE',
        headers: getAuthHeaders(),
      });

      if (response.ok) {
        const data = await response.json();
        alert(`✅ Persona deleted\n\n${data.note || 'Comments and verifications are preserved'}`);
        setDeletingPersona(null);
        fetchPersonas();
      } else {
        const errorData = await response.json();
        alert(`Failed to delete: ${errorData.detail || 'Unknown error'}`);
      }
    } catch (err) {
      alert('Failed to delete: Network error');
    }
  };

  const handleDeleteCancel = () => {
    setDeletingPersona(null);
  };

  const handleViewVerifications = async (personaId: string, personaName: string) => {
    if (showVerifications === personaId) {
      setShowVerifications(null);
      return;
    }

    try {
      const response = await fetch(`${API_BASE_URL}/api/personas/${personaId}/verifications`, {
        headers: getAuthHeaders(),
      });

      if (response.ok) {
        const data = await response.json();
        setVerifications(data.items);
        setShowVerifications(personaId);
        setSelectedPersona({ ...data, persona_name: personaName } as any);
      }
    } catch (err) {
      alert('Failed to load verifications');
    }
  };

  const handleCancelApplication = async (e: React.MouseEvent, verificationId: string, personaName: string) => {
    e.preventDefault();
    e.stopPropagation();
    
    if (!confirm(`确定要取消 "${personaName}" 的申请吗？\n\n此操作不可恢复。`)) {
      return;
    }

    setIsLoading(true);
    try {
      const response = await fetch(
        `${API_BASE_URL}/api/personas/verifications/${verificationId}/cancel`,
        {
          method: 'POST',
          headers: getAuthHeaders(),
        }
      );

      if (response.ok) {
        alert('申请已取消');
        // 直接从本地状态中移除已取消的申请，避免重新获取数据导致面板关闭
        setVerifications(prev => prev.filter(v => v.id !== verificationId));
      } else {
        const result = await response.json();
        alert(result.detail || '取消失败');
      }
    } catch (err) {
      alert('网络错误');
    } finally {
      setIsLoading(false);
    }
  };

  if (!isAuthenticated) {
    return (
      <div className="min-h-screen bg-stone-50 flex items-center justify-center">
        <div className="bg-white p-8 rounded-2xl shadow-xl max-w-md w-full">
          <div className="text-center mb-8">
            <h1 className="text-2xl font-bold text-stone-900 mb-2">My Personas</h1>
            <p className="text-stone-600">Sign in to manage your identities</p>
          </div>

          <form onSubmit={handleLogin} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-stone-700 mb-1">
                Email
              </label>
              <input
                type="email"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                className="w-full px-4 py-2 border border-stone-300 rounded-lg focus:ring-2 focus:ring-stone-500"
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
                className="w-full px-4 py-2 border border-stone-300 rounded-lg focus:ring-2 focus:ring-stone-500"
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
            <p>Test account: test@example.com / test123</p>
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
              <h1 className="text-xl font-bold text-stone-900">My Personas</h1>
              <p className="text-xs text-stone-500">Manage your anonymous identities</p>
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-sm text-stone-600">{username}</span>
              <button
                onClick={() => router.push('/')}
                className="text-stone-600 hover:text-stone-900 text-sm"
              >
                Home
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
        {/* Auto-create Tip */}
        {showAutoCreateTip && (
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
            <div className="flex items-start justify-between">
              <div className="flex items-start space-x-3">
                <span className="text-2xl">💡</span>
                <div>
                  <p className="font-semibold text-blue-800">我们为你创建了一个默认身份</p>
                  <p className="text-sm text-blue-700 mt-1">
                    你可以修改名称和颜色，或者创建更多身份来表达不同观点
                  </p>
                </div>
              </div>
              <button
                onClick={() => setShowAutoCreateTip(false)}
                className="text-blue-600 hover:text-blue-800 text-sm font-medium"
              >
                知道了
              </button>
            </div>
          </div>
        )}

        {/* Header Actions */}
        <div className="flex items-center justify-between mb-6">
          <div>
            <h2 className="text-2xl font-bold text-stone-900">Your Identities</h2>
            <p className="text-sm text-stone-600 mt-1">
              {personas.length} / 10 personas created
            </p>
          </div>

          <button
            onClick={() => setShowCreateModal(true)}
            disabled={personas.length >= 5}
            className="bg-stone-900 text-white px-6 py-2.5 rounded-lg font-medium hover:bg-stone-800 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            + Create New Persona
          </button>
        </div>

        {/* Persona Limit Warning */}
        {personas.length >= 10 && (
          <div className="bg-amber-50 border border-amber-200 rounded-lg p-4 mb-6">
            <p className="text-amber-800 text-sm">
              ⚠️ You've reached the maximum limit of 10 personas. Delete one to create a new persona.
            </p>
          </div>
        )}

        {/* Personas Grid */}
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {personas.map((persona) => (
            <div
              key={persona.id}
              className={`rounded-xl border p-6 transition-shadow ${
                persona.is_deleted
                  ? 'bg-stone-100 border-stone-300 opacity-75'
                  : 'bg-white border-stone-200 hover:shadow-lg'
              }`}
            >
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center space-x-3">
                  <div
                    className={`w-12 h-12 rounded-full flex items-center justify-center text-white font-bold text-lg ${
                      persona.is_deleted ? 'bg-stone-400' : `bg-${persona.avatar_color}-500`
                    }`}
                    style={{ 
                      backgroundColor: persona.is_deleted 
                        ? '#9CA3AF' 
                        : getAvatarColor(persona.avatar_color) 
                    }}
                  >
                    {persona.persona_name.charAt(0).toUpperCase()}
                  </div>
                  <div>
                    <h3 className={`font-semibold ${persona.is_deleted ? 'text-stone-500 line-through' : 'text-stone-900'}`}>
                      {persona.persona_name}
                    </h3>
                    <p className="text-xs text-stone-500">
                      Created {new Date(persona.created_at).toLocaleDateString()}
                    </p>
                    {persona.is_deleted && (
                      <p className="text-xs text-red-600 font-medium mt-1">
                        🗑️ Deleted
                      </p>
                    )}
                  </div>
                </div>

                {!persona.is_deleted && persona.is_verified && (
                  <span className="inline-block px-2 py-1 rounded-full text-xs font-medium bg-emerald-100 text-emerald-700">
                    ✅ Verified
                  </span>
                )}
              </div>

              <div className="space-y-2">
                {persona.is_deleted ? (
                  <div className="text-xs text-stone-500 italic px-3 py-2">
                    ℹ️ This persona has been deleted<br/>
                    Comments and verifications are preserved
                  </div>
                ) : (
                  <>
                    <button
                      onClick={() => setEditingPersona({id: persona.id, name: persona.persona_name, color: persona.avatar_color})}
                      className="w-full text-left px-3 py-2 bg-stone-50 hover:bg-stone-100 rounded-lg text-sm text-stone-700 transition-colors"
                    >
                      ✏️ Edit Persona
                    </button>

                    <button
                      onClick={() => handleViewVerifications(persona.id, persona.persona_name)}
                      className="w-full text-left px-3 py-2 bg-stone-50 hover:bg-stone-100 rounded-lg text-sm text-stone-700 transition-colors"
                    >
                      {showVerifications === persona.id ? 'Hide' : 'View'} Verifications
                    </button>

                    <button
                      onClick={() => router.push(`/personas/${persona.id}/verify`)}
                      className="w-full text-left px-3 py-2 bg-stone-50 hover:bg-stone-100 rounded-lg text-sm text-stone-700 transition-colors"
                    >
                      Apply for Verification
                    </button>

                    <button
                      onClick={() => setDeletingPersona({id: persona.id, name: persona.persona_name})}
                      className="w-full text-left px-3 py-2 bg-red-50 hover:bg-red-100 rounded-lg text-sm text-red-700 transition-colors"
                    >
                      Delete Persona
                    </button>
                  </>
                )}
              </div>
            </div>
          ))}
        </div>

        {/* Empty State */}
        {personas.length === 0 && (
          <div className="text-center py-20">
            <div className="text-6xl mb-4">🎭</div>
            <h3 className="text-xl font-semibold text-stone-900 mb-2">No Personas Yet</h3>
            <p className="text-stone-600 mb-6">Create your first anonymous identity to get started</p>
            <button
              onClick={() => setShowCreateModal(true)}
              className="bg-stone-900 text-white px-6 py-3 rounded-lg font-medium hover:bg-stone-800 transition-colors"
            >
              Create Your First Persona
            </button>
          </div>
        )}

        {/* Verifications Panel */}
        {showVerifications && selectedPersona && (
          <div className="mt-8 bg-white rounded-xl border border-stone-200 p-6">
            <h3 className="text-lg font-bold text-stone-900 mb-4">
              Verifications for {selectedPersona.persona_name}
            </h3>

            {verifications.length > 0 ? (
              <div className="space-y-4">
                {verifications.map((v) => (
                  <div
                    key={v.id}
                    className="border border-stone-200 rounded-lg p-4"
                  >
                    <div className="flex items-start justify-between mb-2">
                      <div className="flex-1">
                        <h4 className="font-semibold text-stone-900">{v.event_title}</h4>
                        <p className="text-sm text-stone-600">
                          Applying as: {v.stakeholder_name}
                        </p>
                        <p className="text-xs text-stone-500 mt-1">
                          Applied on {new Date(v.created_at).toLocaleDateString()}
                        </p>
                      </div>
                      <div className="flex flex-col items-end space-y-2">
                        <span
                          className={`inline-block px-3 py-1 rounded-full text-xs font-medium ${
                            v.status === 'approved'
                              ? 'bg-emerald-100 text-emerald-700'
                              : v.status === 'rejected' || v.status === 'revoked'
                              ? 'bg-red-100 text-red-700'
                              : 'bg-amber-100 text-amber-700'
                          }`}
                        >
                          {v.status === 'revoked' 
                            ? 'Revoked' 
                            : v.status.charAt(0).toUpperCase() + v.status.slice(1)}
                        </span>
                        {v.status === 'pending' && (
                          <button
                            onClick={(e) => handleCancelApplication(e, v.id, v.persona_name)}
                            className="text-xs text-red-600 hover:text-red-800 hover:underline"
                            disabled={isLoading}
                            type="button"
                          >
                            Cancel Application
                          </button>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-stone-500 text-center py-8">
                No verification applications yet
              </p>
            )}
          </div>
        )}
      </main>

      {/* Delete Confirmation Modal */}
      {deletingPersona && (
        <DeleteConfirmModal
          personaName={deletingPersona.name}
          onConfirm={handleDeleteConfirm}
          onCancel={handleDeleteCancel}
          isLoading={isLoading}
        />
      )}

      {/* Edit Modal */}
      {editingPersona && (
        <EditPersonaModal
          persona={editingPersona}
          onSubmit={handleEditPersona}
          onClose={() => setEditingPersona(null)}
          isLoading={isLoading}
        />
      )}

      {/* Create Modal */}
      {showCreateModal && (
        <CreatePersonaModal
          onSubmit={handleCreatePersona}
          onClose={() => setShowCreateModal(false)}
          isLoading={isLoading}
        />
      )}
    </div>
  );
}

// Helper function to convert color name to hex
function getAvatarColor(colorName: string): string {
  const colors: Record<string, string> = {
    blue: '#3B82F6',
    green: '#10B981',
    purple: '#8B5CF6',
    orange: '#F59E0B',
    red: '#EF4444',
    teal: '#14B8A6',
    indigo: '#6366F1',
    pink: '#EC4899',
  };
  return colors[colorName] || '#3B82F6';
}

// Create Modal Component
function CreatePersonaModal({ onSubmit, onClose, isLoading }: any) {
  const [personaName, setPersonaName] = useState('');
  const [avatarColor, setAvatarColor] = useState('blue');

  const colors = ['blue', 'green', 'purple', 'orange', 'red', 'teal', 'indigo', 'pink'];

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit({ persona_name: personaName, avatar_color: avatarColor });
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="bg-white rounded-xl max-w-md w-full mx-4">
        <div className="p-6 border-b border-stone-200">
          <h2 className="text-xl font-bold text-stone-900">Create New Persona</h2>
          <p className="text-sm text-stone-500 mt-1">Choose an anonymous identity name</p>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          <div>
            <label className="block text-sm font-medium text-stone-700 mb-1">
              Persona Name *
            </label>
            <input
              type="text"
              value={personaName}
              onChange={(e) => setPersonaName(e.target.value)}
              className="w-full px-4 py-2 border border-stone-300 rounded-lg focus:ring-2 focus:ring-stone-500"
              placeholder="e.g., Iranian Civilian, Tech Worker"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-stone-700 mb-2">
              Avatar Color
            </label>
            <div className="flex flex-wrap gap-2">
              {colors.map((color) => (
                <button
                  key={color}
                  type="button"
                  onClick={() => setAvatarColor(color)}
                  className={`w-10 h-10 rounded-full border-2 transition-transform ${
                    avatarColor === color ? 'border-stone-900 scale-110' : 'border-transparent'
                  }`}
                  style={{ backgroundColor: getAvatarColor(color) }}
                />
              ))}
            </div>
          </div>

          <div className="flex items-center justify-end space-x-3 pt-4 border-t border-stone-200">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 border border-stone-300 rounded-lg text-stone-700 hover:bg-stone-50"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isLoading}
              className="px-4 py-2 bg-stone-900 text-white rounded-lg hover:bg-stone-800 disabled:opacity-50"
            >
              {isLoading ? 'Creating...' : 'Create Persona'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

// Delete Confirmation Modal Component
function DeleteConfirmModal({ personaName, onConfirm, onCancel, isLoading }: any) {
  const handleConfirmClick = (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    onConfirm();
  };

  const handleCancelClick = (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    onCancel();
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="bg-white rounded-xl max-w-md w-full mx-4 p-6" onClick={(e) => e.stopPropagation()}>
        <div className="mb-4">
          <div className="w-12 h-12 rounded-full bg-red-100 flex items-center justify-center mb-4">
            <span className="text-2xl">⚠️</span>
          </div>
          <h2 className="text-xl font-bold text-stone-900 mb-2">Confirm Delete</h2>
          <p className="text-stone-600">
            Are you sure you want to delete <strong className="text-stone-900">"{personaName}"</strong>?
          </p>
        </div>

        <div className="bg-amber-50 border border-amber-200 rounded-lg p-4 mb-6">
          <ul className="text-sm text-amber-800 space-y-1">
            <li>• Your comments will remain visible (shown as "Deleted User")</li>
            <li>• Verification records will be preserved</li>
            <li>• This action CANNOT be undone</li>
          </ul>
        </div>

        <div className="flex items-center justify-end space-x-3">
          <button
            type="button"
            onClick={handleCancelClick}
            disabled={isLoading}
            className="px-4 py-2 border border-stone-300 rounded-lg text-stone-700 hover:bg-stone-50 disabled:opacity-50"
          >
            Cancel
          </button>
          <button
            type="button"
            onClick={handleConfirmClick}
            disabled={isLoading}
            className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:opacity-50"
          >
            {isLoading ? 'Deleting...' : 'Delete'}
          </button>
        </div>
      </div>
    </div>
  );
}

// Edit Modal Component
function EditPersonaModal({ persona, onSubmit, onClose, isLoading }: any) {
  const [personaName, setPersonaName] = useState(persona.name);
  const [avatarColor, setAvatarColor] = useState(persona.color);

  const colors = ['blue', 'green', 'purple', 'orange', 'red', 'teal', 'indigo', 'pink'];

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit(personaName, avatarColor);
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="bg-white rounded-xl max-w-md w-full mx-4">
        <div className="p-6 border-b border-stone-200">
          <h2 className="text-xl font-bold text-stone-900">Edit Persona</h2>
          <p className="text-sm text-stone-500 mt-1">Customize your identity</p>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          <div>
            <label className="block text-sm font-medium text-stone-700 mb-1">
              Persona Name *
            </label>
            <input
              type="text"
              value={personaName}
              onChange={(e) => setPersonaName(e.target.value)}
              className="w-full px-4 py-2 border border-stone-300 rounded-lg focus:ring-2 focus:ring-stone-500"
              placeholder="e.g., Iranian Civilian, Tech Worker"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-stone-700 mb-2">
              Avatar Color
            </label>
            <div className="flex flex-wrap gap-2">
              {colors.map((color) => (
                <button
                  key={color}
                  type="button"
                  onClick={() => setAvatarColor(color)}
                  className={`w-10 h-10 rounded-full border-2 transition-transform ${
                    avatarColor === color ? 'border-stone-900 scale-110' : 'border-transparent'
                  }`}
                  style={{ backgroundColor: getAvatarColor(color) }}
                />
              ))}
            </div>
          </div>

          <div className="flex items-center justify-end space-x-3 pt-4 border-t border-stone-200">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 border border-stone-300 rounded-lg text-stone-700 hover:bg-stone-50"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isLoading}
              className="px-4 py-2 bg-stone-900 text-white rounded-lg hover:bg-stone-800 disabled:opacity-50"
            >
              {isLoading ? 'Saving...' : 'Save Changes'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
