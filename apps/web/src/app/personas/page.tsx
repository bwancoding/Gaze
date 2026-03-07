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

  // Check authentication
  useEffect(() => {
    const storedAuth = localStorage.getItem('user_auth');
    if (storedAuth) {
      const { username, password } = JSON.parse(storedAuth);
      setUsername(username);
      setPassword(password);
      setIsAuthenticated(true);
      fetchPersonas();
    }
  }, []);

  const getAuthHeaders = () => {
    if (username && password) {
      return {
        'Authorization': 'Basic ' + btoa(`${username}:${password}`),
        'Content-Type': 'application/json',
      };
    }
    return {};
  };

  const fetchPersonas = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/personas`, {
        headers: getAuthHeaders(),
      });

      if (response.ok) {
        const data = await response.json();
        setPersonas(data.items);
      } else if (response.status === 401) {
        handleLogout();
      }
    } catch (err) {
      console.error('Failed to fetch personas:', err);
    }
  };

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    try {
      const response = await fetch(`${API_BASE_URL}/api/personas`, {
        headers: getAuthHeaders(),
      });

      if (response.ok) {
        setIsAuthenticated(true);
        localStorage.setItem('user_auth', JSON.stringify({ username, password }));
        fetchPersonas();
      } else {
        setError('Invalid credentials');
      }
    } catch (err) {
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

  const handleDeletePersona = async (id: string, name: string) => {
    const confirmed = window.confirm(
      `⚠️ Confirm Delete\n\n` +
      `Are you sure you want to delete "${name}"?\n\n` +
      `• Your comments will remain visible (shown as "Deleted User")\n` +
      `• Verification records will be preserved\n` +
      `• This action CANNOT be undone\n\n` +
      `Click OK to confirm deletion.`
    );
    
    if (!confirmed) return;

    try {
      const response = await fetch(`${API_BASE_URL}/api/personas/${id}`, {
        method: 'DELETE',
        headers: getAuthHeaders(),
      });

      if (response.ok) {
        const data = await response.json();
        alert(`✅ Persona deleted\n\n${data.note || 'Comments and verifications are preserved'}`);
        fetchPersonas();
      } else {
        const errorData = await response.json();
        alert(`Failed to delete: ${errorData.detail || 'Unknown error'}`);
      }
    } catch (err) {
      alert('Failed to delete: Network error');
    }
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
        {/* Header Actions */}
        <div className="flex items-center justify-between mb-6">
          <div>
            <h2 className="text-2xl font-bold text-stone-900">Your Identities</h2>
            <p className="text-sm text-stone-600 mt-1">
              {personas.length} / 5 personas created
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
                      onClick={() => handleDeletePersona(persona.id, persona.persona_name)}
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
                      <div>
                        <h4 className="font-semibold text-stone-900">{v.event_title}</h4>
                        <p className="text-sm text-stone-600">
                          Applying as: {v.stakeholder_name}
                        </p>
                      </div>
                      <span
                        className={`inline-block px-3 py-1 rounded-full text-xs font-medium ${
                          v.status === 'approved'
                            ? 'bg-emerald-100 text-emerald-700'
                            : v.status === 'rejected'
                            ? 'bg-red-100 text-red-700'
                            : 'bg-amber-100 text-amber-700'
                        }`}
                      >
                        {v.status.charAt(0).toUpperCase() + v.status.slice(1)}
                      </span>
                    </div>
                    <p className="text-xs text-stone-500">
                      Applied on {new Date(v.created_at).toLocaleDateString()}
                    </p>
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
