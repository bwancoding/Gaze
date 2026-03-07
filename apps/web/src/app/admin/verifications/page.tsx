'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080';

interface Verification {
  id: string;
  persona_name: string;
  user_email: string;
  event_id: string;
  event_title: string;
  stakeholder_name: string;
  application_text: string;
  proof_type: string;
  status: string;
  created_at: string;
  review_notes: string;
}

export default function AdminVerifications() {
  const router = useRouter();
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [verifications, setVerifications] = useState<Verification[]>([]);
  const [statusFilter, setStatusFilter] = useState('pending');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [reviewModal, setReviewModal] = useState<{
    isOpen: boolean;
    verificationId: string | null;
    action: 'approve' | 'reject' | 'revoke' | null;
    notes: string;
  }>({
    isOpen: false,
    verificationId: null,
    action: null,
    notes: '',
  });

  // Check authentication
  useEffect(() => {
    const storedAuth = localStorage.getItem('admin_auth');
    if (storedAuth) {
      const { username, password } = JSON.parse(storedAuth);
      setUsername(username);
      setPassword(password);
      setIsAuthenticated(true);
      fetchVerifications();
    } else {
      router.push('/admin');
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

  const fetchVerifications = async () => {
    try {
      const response = await fetch(
        `${API_BASE_URL}/api/personas/admin/verifications?status_filter=${statusFilter}`,
        {
          headers: getAuthHeaders(),
        }
      );

      if (response.ok) {
        const data = await response.json();
        setVerifications(data.items);
      }
    } catch (err) {
      console.error('Failed to fetch verifications:', err);
    }
  };

  useEffect(() => {
    if (isAuthenticated) {
      fetchVerifications();
    }
  }, [statusFilter, isAuthenticated]);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    try {
      const response = await fetch(`${API_BASE_URL}/api/admin/stats`, {
        headers: getAuthHeaders(),
      });

      if (response.ok) {
        setIsAuthenticated(true);
        localStorage.setItem('admin_auth', JSON.stringify({ username, password }));
        fetchVerifications();
      } else {
        setError('Invalid credentials');
      }
    } catch (err) {
      setError('Network error');
    } finally {
      setIsLoading(false);
    }
  };

  const handleReview = async () => {
    if (!reviewModal.verificationId || !reviewModal.action) return;

    setIsLoading(true);
    try {
      let endpoint = '';
      let successMessage = '';
      
      if (reviewModal.action === 'approve') {
        endpoint = 'approve';
        successMessage = 'Application approved successfully!';
      } else if (reviewModal.action === 'reject') {
        endpoint = 'reject';
        successMessage = 'Application rejected successfully!';
      } else if (reviewModal.action === 'revoke') {
        endpoint = 'revoke';
        successMessage = 'Approval revoked successfully!';
      }

      const response = await fetch(
        `${API_BASE_URL}/api/personas/admin/verifications/${reviewModal.verificationId}/${endpoint}`,
        {
          method: 'POST',
          headers: getAuthHeaders(),
          body: JSON.stringify({ review_notes: reviewModal.notes }),
        }
      );

      if (response.ok) {
        alert(successMessage);
        setReviewModal({ isOpen: false, verificationId: null, action: null, notes: '' });
        fetchVerifications();
      } else {
        const result = await response.json();
        alert(result.detail || 'Failed to process');
      }
    } catch (err) {
      alert('Network error');
    } finally {
      setIsLoading(false);
    }
  };

  const openReviewModal = (verificationId: string, action: 'approve' | 'reject' | 'revoke') => {
    setReviewModal({
      isOpen: true,
      verificationId,
      action,
      notes: '',
    });
  };

  if (!isAuthenticated) {
    return (
      <div className="min-h-screen bg-stone-50 flex items-center justify-center">
        <div className="bg-white p-8 rounded-2xl shadow-xl max-w-md w-full">
          <div className="text-center mb-8">
            <h1 className="text-2xl font-bold text-stone-900 mb-2">Admin Verification Review</h1>
            <p className="text-stone-600">Sign in to review stakeholder applications</p>
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
            <p>Default: admin / wrhitw_admin_2026</p>
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
              <h1 className="text-xl font-bold text-stone-900">Verification Applications</h1>
              <p className="text-xs text-stone-500">Review and approve stakeholder verifications</p>
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-sm text-stone-600">{username}</span>
              <button
                onClick={() => router.push('/admin')}
                className="text-stone-600 hover:text-stone-900 text-sm"
              >
                Back to Dashboard
              </button>
            </div>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-6 py-8">
        {/* Filter */}
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center space-x-2">
            <span className="text-sm text-stone-600">Filter:</span>
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="border border-stone-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-stone-500"
            >
              <option value="pending">Pending</option>
              <option value="approved">Approved</option>
              <option value="rejected">Rejected</option>
              <option value="all">All</option>
            </select>
          </div>

          <div className="text-sm text-stone-600">
            {verifications.length} application{verifications.length !== 1 ? 's' : ''}
          </div>
        </div>

        {/* Applications List */}
        <div className="space-y-4">
          {verifications.map((v) => (
            <div
              key={v.id}
              className="bg-white rounded-xl border border-stone-200 p-6 hover:shadow-md transition-shadow"
            >
              <div className="flex items-start justify-between mb-4">
                <div className="flex-1">
                  <div className="flex items-center space-x-3 mb-2">
                    <span className="text-sm font-medium text-stone-600">
                      {v.persona_name}
                    </span>
                    <span className="text-xs text-stone-400">·</span>
                    <span className="text-sm text-stone-600">{v.user_email}</span>
                  </div>

                  <h3 className="text-lg font-semibold text-stone-900 mb-1">
                    {v.event_title}
                  </h3>

                  <p className="text-sm text-stone-600 mb-3">
                    Applying as: <span className="font-medium">{v.stakeholder_name}</span>
                  </p>

                  <div className="bg-stone-50 rounded-lg p-3 mb-3">
                    <p className="text-xs font-medium text-stone-600 mb-1">Application:</p>
                    <p className="text-sm text-stone-700">{v.application_text}</p>
                  </div>

                  <div className="flex items-center space-x-4 text-xs text-stone-500">
                    <span>Proof: {v.proof_type}</span>
                    <span>·</span>
                    <span>Applied: {new Date(v.created_at).toLocaleString()}</span>
                  </div>
                </div>

                <div className="flex flex-col items-end space-y-2">
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

                  {v.status === 'pending' && (
                    <div className="flex space-x-2 mt-2">
                      <button
                        onClick={() => openReviewModal(v.id, 'approve')}
                        className="px-3 py-1.5 bg-emerald-600 text-white text-xs rounded-lg hover:bg-emerald-700 transition-colors"
                      >
                        Approve
                      </button>
                      <button
                        onClick={() => openReviewModal(v.id, 'reject')}
                        className="px-3 py-1.5 bg-red-600 text-white text-xs rounded-lg hover:bg-red-700 transition-colors"
                      >
                        Reject
                      </button>
                    </div>
                  )}

                  {v.status === 'approved' && (
                    <button
                      onClick={() => openReviewModal(v.id, 'revoke')}
                      className="px-3 py-1.5 bg-amber-600 text-white text-xs rounded-lg hover:bg-amber-700 transition-colors mt-2"
                    >
                      ↩️ Revoke Approval
                    </button>
                  )}

                  {v.review_notes && (
                    <div className="mt-2 text-xs text-stone-500 text-right">
                      <p className="font-medium">Admin Notes:</p>
                      <p>{v.review_notes}</p>
                    </div>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Empty State */}
        {verifications.length === 0 && (
          <div className="text-center py-20">
            <div className="text-6xl mb-4">📋</div>
            <h3 className="text-xl font-semibold text-stone-900 mb-2">
              No {statusFilter !== 'all' ? statusFilter : ''} Applications
            </h3>
            <p className="text-stone-600">
              {statusFilter === 'pending'
                ? 'All caught up! No pending applications.'
                : 'No applications found for this filter.'}
            </p>
          </div>
        )}
      </main>

      {/* Review Modal */}
      {reviewModal.isOpen && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl max-w-md w-full mx-4">
            <div className="p-6 border-b border-stone-200">
              <h2 className="text-xl font-bold text-stone-900">
                {reviewModal.action === 'approve' ? 'Approve' : 
                 reviewModal.action === 'reject' ? 'Reject' : 'Revoke'} Application
              </h2>
            </div>

            <div className="p-6 space-y-4">
              <div>
                <label className="block text-sm font-medium text-stone-700 mb-1">
                  Review Notes (Optional)
                </label>
                <textarea
                  value={reviewModal.notes}
                  onChange={(e) =>
                    setReviewModal({ ...reviewModal, notes: e.target.value })
                  }
                  rows={3}
                  className="w-full px-4 py-2 border border-stone-300 rounded-lg focus:ring-2 focus:ring-stone-500"
                  placeholder="Add any notes about this decision..."
                />
              </div>

              {reviewModal.action === 'reject' && (
                <div className="bg-amber-50 border border-amber-200 rounded-lg p-3">
                  <p className="text-sm text-amber-800">
                    ⚠️ The user will be notified that their application was rejected.
                  </p>
                </div>
              )}

              <div className="flex items-center justify-end space-x-3 pt-4 border-t border-stone-200">
                <button
                  type="button"
                  onClick={() =>
                    setReviewModal({
                      isOpen: false,
                      verificationId: null,
                      action: null,
                      notes: '',
                    })
                  }
                  className="px-4 py-2 border border-stone-300 rounded-lg text-stone-700 hover:bg-stone-50"
                >
                  Cancel
                </button>
                <button
                  onClick={handleReview}
                  disabled={isLoading}
                  className={`px-4 py-2 rounded-lg font-medium transition-colors disabled:opacity-50 ${
                    reviewModal.action === 'approve'
                      ? 'bg-emerald-600 text-white hover:bg-emerald-700'
                      : reviewModal.action === 'reject'
                      ? 'bg-red-600 text-white hover:bg-red-700'
                      : 'bg-amber-600 text-white hover:bg-amber-700'
                  }`}
                >
                  {isLoading
                    ? 'Processing...'
                    : reviewModal.action === 'approve'
                    ? 'Approve Application'
                    : reviewModal.action === 'reject'
                    ? 'Reject Application'
                    : 'Revoke Approval'}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
