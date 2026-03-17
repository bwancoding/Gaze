'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface StakeholderType {
  id: string;
  name: string;
  description: string;
  category: string;
  verification_required?: boolean;
  verification_method?: string;
}

interface Stakeholder {
  id: string;
  name: string;
  type_id: string;
  description: string;
  category: string;
  is_active: boolean;
  is_ai_generated?: boolean;
}

export default function StakeholderManagement() {
  const router = useRouter();
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [types, setTypes] = useState<StakeholderType[]>([]);
  const [stakeholders, setStakeholders] = useState<Stakeholder[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [activeTab, setActiveTab] = useState<'types' | 'stakeholders'>('stakeholders');

  // Check authentication
  useEffect(() => {
    const storedAuth = localStorage.getItem('admin_auth');
    if (storedAuth) {
      setIsAuthenticated(true);
      fetchData();
    } else {
      router.push('/admin');
    }
  }, []);

  const getAuthHeaders = (): HeadersInit => {
    const headers: Record<string, string> = { 'Content-Type': 'application/json' };
    const storedAuth = localStorage.getItem('admin_auth');
    if (storedAuth) {
      const { username, password } = JSON.parse(storedAuth);
      headers['Authorization'] = 'Basic ' + btoa(`${username}:${password}`);
    }
    return headers;
  };

  const fetchData = async () => {
    try {
      const [typesRes, stakeholdersRes] = await Promise.all([
        fetch(`${API_BASE_URL}/api/admin/stakeholders/types`, {
          headers: getAuthHeaders(),
        }),
        fetch(`${API_BASE_URL}/api/admin/stakeholders`, {
          headers: getAuthHeaders(),
        }),
      ]);

      if (typesRes.ok && stakeholdersRes.ok) {
        const typesData = await typesRes.json();
        const stakeholdersData = await stakeholdersRes.json();
        setTypes(typesData.items);
        setStakeholders(stakeholdersData.items);
      }
    } catch (err) {
      console.error('Failed to fetch data:', err);
    }
  };

  const handleCreateStakeholder = async (data: any) => {
    setIsLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/api/admin/stakeholders`, {
        method: 'POST',
        headers: getAuthHeaders(),
        body: JSON.stringify(data),
      });

      if (response.ok) {
        alert('Stakeholder created successfully!');
        setShowCreateModal(false);
        fetchData();
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

  const handleDeactivate = async (id: string) => {
    if (!confirm('Deactivate this stakeholder?')) return;

    try {
      const response = await fetch(`${API_BASE_URL}/api/admin/stakeholders/${id}/deactivate`, {
        method: 'POST',
        headers: getAuthHeaders(),
      });

      if (response.ok) {
        alert('Stakeholder deactivated');
        fetchData();
      }
    } catch (err) {
      alert('Failed to deactivate');
    }
  };

  if (!isAuthenticated) {
    return <div className="min-h-screen flex items-center justify-center">Redirecting...</div>;
  }

  return (
    <div className="min-h-screen bg-stone-50">
      {/* Header */}
      <header className="bg-white border-b border-stone-200 sticky top-0 z-50">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-xl font-bold text-stone-900">Stakeholder Management</h1>
              <p className="text-xs text-stone-500">Manage event stakeholders and types</p>
            </div>
            <div className="flex items-center space-x-4">
              <button
                onClick={() => router.push('/admin')}
                className="text-stone-600 hover:text-stone-900 text-sm"
              >
                ← Back to Dashboard
              </button>
            </div>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-6 py-8">
        {/* Tabs */}
        <div className="flex items-center space-x-4 mb-6">
          <button
            onClick={() => setActiveTab('stakeholders')}
            className={`px-4 py-2 rounded-lg font-medium transition-colors ${
              activeTab === 'stakeholders'
                ? 'bg-stone-900 text-white'
                : 'bg-white text-stone-600 hover:bg-stone-100'
            }`}
          >
            Stakeholders ({stakeholders.length})
          </button>
          <button
            onClick={() => setActiveTab('types')}
            className={`px-4 py-2 rounded-lg font-medium transition-colors ${
              activeTab === 'types'
                ? 'bg-stone-900 text-white'
                : 'bg-white text-stone-600 hover:bg-stone-100'
            }`}
          >
            Types ({types.length})
          </button>

          {activeTab === 'stakeholders' && (
            <button
              onClick={() => setShowCreateModal(true)}
              className="ml-auto bg-stone-900 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-stone-800 transition-colors"
            >
              + Create Stakeholder
            </button>
          )}
        </div>

        {/* Stakeholders Tab */}
        {activeTab === 'stakeholders' && (
          <div className="bg-white rounded-xl border border-stone-200 overflow-hidden">
            <table className="w-full">
              <thead className="bg-stone-50 border-b border-stone-200">
                <tr>
                  <th className="text-left px-6 py-3 text-xs font-medium text-stone-600 uppercase">Name</th>
                  <th className="text-left px-6 py-3 text-xs font-medium text-stone-600 uppercase">Type</th>
                  <th className="text-left px-6 py-3 text-xs font-medium text-stone-600 uppercase">Category</th>
                  <th className="text-left px-6 py-3 text-xs font-medium text-stone-600 uppercase">Status</th>
                  <th className="text-right px-6 py-3 text-xs font-medium text-stone-600 uppercase">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-stone-200">
                {stakeholders.map((stakeholder) => (
                  <tr key={stakeholder.id} className="hover:bg-stone-50">
                    <td className="px-6 py-4">
                      <div className="flex items-center space-x-2">
                        <p className="font-medium text-stone-900">{stakeholder.name}</p>
                        {stakeholder.is_ai_generated && (
                          <span className="inline-block px-1.5 py-0.5 rounded text-[10px] font-medium bg-amber-100 text-amber-700">AI</span>
                        )}
                      </div>
                      <p className="text-xs text-stone-500 truncate max-w-xs">{stakeholder.description}</p>
                    </td>
                    <td className="px-6 py-4">
                      <span className="text-sm text-stone-600">
                        {types.find(t => t.id === stakeholder.type_id)?.name || 'Unknown'}
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      <span className="inline-block px-2 py-1 rounded text-xs font-medium bg-stone-100 text-stone-700">
                        {stakeholder.category}
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      <span className={`inline-block px-2 py-1 rounded text-xs font-medium ${
                        stakeholder.is_active
                          ? 'bg-emerald-100 text-emerald-700'
                          : 'bg-stone-100 text-stone-500'
                      }`}>
                        {stakeholder.is_active ? 'Active' : 'Inactive'}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-right">
                      {stakeholder.is_active && (
                        <button
                          onClick={() => handleDeactivate(stakeholder.id)}
                          className="text-amber-600 hover:text-amber-700 text-sm font-medium"
                        >
                          Deactivate
                        </button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>

            {stakeholders.length === 0 && (
              <div className="text-center py-12 text-stone-500">
                No stakeholders yet. Click "Create Stakeholder" to add one.
              </div>
            )}
          </div>
        )}

        {/* Types Tab */}
        {activeTab === 'types' && (
          <div className="bg-white rounded-xl border border-stone-200 overflow-hidden">
            <table className="w-full">
              <thead className="bg-stone-50 border-b border-stone-200">
                <tr>
                  <th className="text-left px-6 py-3 text-xs font-medium text-stone-600 uppercase">Type</th>
                  <th className="text-left px-6 py-3 text-xs font-medium text-stone-600 uppercase">Description</th>
                  <th className="text-left px-6 py-3 text-xs font-medium text-stone-600 uppercase">Category</th>
                  <th className="text-left px-6 py-3 text-xs font-medium text-stone-600 uppercase">Verification</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-stone-200">
                {types.map((type) => (
                  <tr key={type.id} className="hover:bg-stone-50">
                    <td className="px-6 py-4">
                      <p className="font-medium text-stone-900">{type.name}</p>
                    </td>
                    <td className="px-6 py-4">
                      <p className="text-sm text-stone-600">{type.description}</p>
                    </td>
                    <td className="px-6 py-4">
                      <span className="inline-block px-2 py-1 rounded text-xs font-medium bg-stone-100 text-stone-700">
                        {type.category}
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      <span className="text-sm text-stone-600">
                        {type.verification_required ? 'Required' : 'Optional'}
                      </span>
                      {type.verification_method && (
                        <p className="text-xs text-stone-500 mt-1">{type.verification_method}</p>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </main>

      {/* Create Modal */}
      {showCreateModal && (
        <CreateStakeholderModal
          types={types}
          onSubmit={handleCreateStakeholder}
          onClose={() => setShowCreateModal(false)}
          isLoading={isLoading}
        />
      )}
    </div>
  );
}

// Create Modal Component
function CreateStakeholderModal({ types, onSubmit, onClose, isLoading }: any) {
  const [formData, setFormData] = useState({
    name: '',
    type_id: types[0]?.id || '',
    description: '',
    category: 'geopolitics',
    verification_required: true,
    verification_method: '',
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit(formData);
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="bg-white rounded-xl max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
        <div className="p-6 border-b border-stone-200">
          <h2 className="text-xl font-bold text-stone-900">Create New Stakeholder</h2>
          <p className="text-sm text-stone-500 mt-1">Define a group that can be verified for events</p>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          <div>
            <label className="block text-sm font-medium text-stone-700 mb-1">
              Name *
            </label>
            <input
              type="text"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              className="w-full px-4 py-2 border border-stone-300 rounded-lg focus:ring-2 focus:ring-stone-500"
              placeholder="e.g., Iranian Civilians, US Soldiers, NVIDIA Employees"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-stone-700 mb-1">
              Type *
            </label>
            <select
              value={formData.type_id}
              onChange={(e) => setFormData({ ...formData, type_id: e.target.value })}
              className="w-full px-4 py-2 border border-stone-300 rounded-lg focus:ring-2 focus:ring-stone-500"
              required
            >
              {types.map((t: StakeholderType) => (
                <option key={t.id} value={t.id}>{t.name}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-stone-700 mb-1">
              Description *
            </label>
            <textarea
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              rows={3}
              className="w-full px-4 py-2 border border-stone-300 rounded-lg focus:ring-2 focus:ring-stone-500"
              placeholder="e.g., Ordinary citizens living in Iran"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-stone-700 mb-1">
              Category *
            </label>
            <select
              value={formData.category}
              onChange={(e) => setFormData({ ...formData, category: e.target.value })}
              className="w-full px-4 py-2 border border-stone-300 rounded-lg focus:ring-2 focus:ring-stone-500"
              required
            >
              <option value="geopolitics">Geopolitics</option>
              <option value="technology">Technology</option>
              <option value="economy">Economy</option>
            </select>
          </div>

          <div className="flex items-center space-x-2">
            <input
              type="checkbox"
              id="verification_required"
              checked={formData.verification_required}
              onChange={(e) => setFormData({ ...formData, verification_required: e.target.checked })}
              className="rounded border-stone-300"
            />
            <label htmlFor="verification_required" className="text-sm text-stone-700">
              Verification required for this stakeholder
            </label>
          </div>

          <div>
            <label className="block text-sm font-medium text-stone-700 mb-1">
              Verification Method
            </label>
            <input
              type="text"
              value={formData.verification_method}
              onChange={(e) => setFormData({ ...formData, verification_method: e.target.value })}
              className="w-full px-4 py-2 border border-stone-300 rounded-lg focus:ring-2 focus:ring-stone-500"
              placeholder="e.g., IP address, Email domain, Document upload"
            />
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
              {isLoading ? 'Creating...' : 'Create Stakeholder'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
