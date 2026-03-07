'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080';

interface Stakeholder {
  id: string;
  name: string;
  description: string;
  category: string;
  verification_required: boolean;
}

interface Application {
  id: string;
  stakeholder_name: string;
  status: string;
  created_at: string;
  review_notes: string;
}

export default function VerificationApplication() {
  const router = useRouter();
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [stakeholders, setStakeholders] = useState<Stakeholder[]>([]);
  const [applications, setApplications] = useState<Application[]>([]);
  const [selectedStakeholder, setSelectedStakeholder] = useState('');
  const [applicationText, setApplicationText] = useState('');
  const [proofType, setProofType] = useState('self_declaration');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [activeTab, setActiveTab] = useState('apply');

  // Check authentication
  useEffect(() => {
    const storedAuth = localStorage.getItem('user_auth');
    if (storedAuth) {
      const { username, password } = JSON.parse(storedAuth);
      setUsername(username);
      setPassword(password);
      setIsAuthenticated(true);
      fetchData();
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

  const fetchData = async () => {
    try {
      const [stakeholdersRes, applicationsRes] = await Promise.all([
        fetch(`${API_BASE_URL}/api/stakeholders/list`),
        fetch(`${API_BASE_URL}/api/stakeholders/my-applications`, {
          headers: getAuthHeaders(),
        }),
      ]);

      if (stakeholdersRes.ok) {
        const data = await stakeholdersRes.json();
        setStakeholders(data.items.filter((s: any) => s.is_active));
      }

      if (applicationsRes.ok) {
        const data = await applicationsRes.json();
        setApplications(data.items);
      }
    } catch (err) {
      console.error('Failed to fetch data:', err);
    }
  };

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    try {
      const response = await fetch(`${API_BASE_URL}/api/stakeholders/my-applications`, {
        headers: getAuthHeaders(),
      });

      if (response.ok) {
        setIsAuthenticated(true);
        localStorage.setItem('user_auth', JSON.stringify({ username, password }));
        fetchData();
      } else {
        setError('Invalid credentials');
      }
    } catch (err) {
      setError('Network error');
    } finally {
      setIsLoading(false);
    }
  };

  const handleSubmitApplication = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    try {
      const response = await fetch(`${API_BASE_URL}/api/stakeholders/apply`, {
        method: 'POST',
        headers: getAuthHeaders(),
        body: JSON.stringify({
          stakeholder_id: selectedStakeholder,
          application_text: applicationText,
          proof_type: proofType,
        }),
      });

      if (response.ok) {
        alert('Application submitted successfully!');
        setApplicationText('');
        setSelectedStakeholder('');
        setActiveTab('applications');
        fetchData();
      } else {
        const data = await response.json();
        setError(data.detail || 'Failed to submit application');
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

  if (!isAuthenticated) {
    return (
      <div className="min-h-screen bg-stone-50 flex items-center justify-center">
        <div className="bg-white p-8 rounded-2xl shadow-xl max-w-md w-full">
          <div className="text-center mb-8">
            <h1 className="text-2xl font-bold text-stone-900 mb-2">Stakeholder Verification</h1>
            <p className="text-stone-600">Sign in to apply for verification</p>
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
            <p>Don't have an account? Contact admin to create one.</p>
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
              <h1 className="text-xl font-bold text-stone-900">Stakeholder Verification</h1>
              <p className="text-xs text-stone-500">Apply to be verified as a stakeholder</p>
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-sm text-stone-600">{username}</span>
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
        {/* Tabs */}
        <div className="flex items-center space-x-4 mb-6">
          <button
            onClick={() => setActiveTab('apply')}
            className={`px-4 py-2 rounded-lg font-medium transition-colors ${
              activeTab === 'apply'
                ? 'bg-stone-900 text-white'
                : 'bg-white text-stone-600 hover:bg-stone-100'
            }`}
          >
            Apply for Verification
          </button>
          <button
            onClick={() => setActiveTab('applications')}
            className={`px-4 py-2 rounded-lg font-medium transition-colors ${
              activeTab === 'applications'
                ? 'bg-stone-900 text-white'
                : 'bg-white text-stone-600 hover:bg-stone-100'
            }`}
          >
            My Applications ({applications.length})
          </button>
        </div>

        {/* Apply Tab */}
        {activeTab === 'apply' && (
          <div className="max-w-2xl">
            <div className="bg-white rounded-xl border border-stone-200 p-6">
              <h2 className="text-lg font-bold text-stone-900 mb-4">Submit Application</h2>
              
              <form onSubmit={handleSubmitApplication} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-stone-700 mb-1">
                    Select Stakeholder *
                  </label>
                  <select
                    value={selectedStakeholder}
                    onChange={(e) => setSelectedStakeholder(e.target.value)}
                    className="w-full px-4 py-2 border border-stone-300 rounded-lg focus:ring-2 focus:ring-stone-500"
                    required
                  >
                    <option value="">Choose a stakeholder group...</option>
                    {stakeholders.map((s) => (
                      <option key={s.id} value={s.id}>
                        {s.name} ({s.category})
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-stone-700 mb-1">
                    Why do you qualify? *
                  </label>
                  <textarea
                    value={applicationText}
                    onChange={(e) => setApplicationText(e.target.value)}
                    rows={4}
                    className="w-full px-4 py-2 border border-stone-300 rounded-lg focus:ring-2 focus:ring-stone-500"
                    placeholder="Explain why you belong to this stakeholder group..."
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-stone-700 mb-1">
                    Proof Type
                  </label>
                  <select
                    value={proofType}
                    onChange={(e) => setProofType(e.target.value)}
                    className="w-full px-4 py-2 border border-stone-300 rounded-lg focus:ring-2 focus:ring-stone-500"
                  >
                    <option value="self_declaration">Self Declaration</option>
                    <option value="ip_address">IP Address</option>
                    <option value="email">Email Verification</option>
                    <option value="document">Document Upload</option>
                  </select>
                </div>

                {error && (
                  <div className="bg-red-50 border border-red-200 text-red-800 px-4 py-2 rounded-lg text-sm">
                    {error}
                  </div>
                )}

                <button
                  type="submit"
                  disabled={isLoading || !selectedStakeholder}
                  className="w-full bg-stone-900 text-white py-2.5 rounded-lg font-medium hover:bg-stone-800 transition-colors disabled:opacity-50"
                >
                  {isLoading ? 'Submitting...' : 'Submit Application'}
                </button>
              </form>
            </div>

            <div className="mt-6 bg-amber-50 border border-amber-200 rounded-lg p-4">
              <h3 className="font-semibold text-amber-800 mb-2">What happens next?</h3>
              <ol className="text-sm text-amber-700 space-y-1 list-decimal list-inside">
                <li>Submit your application with explanation</li>
                <li>Admin will review your application (1-3 days)</li>
                <li>If approved, you'll be able to comment with verified badge</li>
                <li>You can check status in "My Applications" tab</li>
              </ol>
            </div>
          </div>
        )}

        {/* Applications Tab */}
        {activeTab === 'applications' && (
          <div className="space-y-4">
            {applications.map((app) => (
              <div
                key={app.id}
                className="bg-white rounded-xl border border-stone-200 p-6"
              >
                <div className="flex items-start justify-between mb-3">
                  <div>
                    <h3 className="font-semibold text-stone-900">{app.stakeholder_name}</h3>
                    <p className="text-xs text-stone-500">
                      Applied on {new Date(app.created_at).toLocaleDateString()}
                    </p>
                  </div>
                  <span
                    className={`inline-block px-3 py-1 rounded-full text-xs font-medium ${
                      app.status === 'approved'
                        ? 'bg-emerald-100 text-emerald-700'
                        : app.status === 'rejected'
                        ? 'bg-red-100 text-red-700'
                        : 'bg-amber-100 text-amber-700'
                    }`}
                  >
                    {app.status.charAt(0).toUpperCase() + app.status.slice(1)}
                  </span>
                </div>

                {app.review_notes && (
                  <div className="bg-stone-50 rounded-lg p-3 mt-3">
                    <p className="text-xs font-medium text-stone-600 mb-1">Admin Notes:</p>
                    <p className="text-sm text-stone-700">{app.review_notes}</p>
                  </div>
                )}
              </div>
            ))}

            {applications.length === 0 && (
              <div className="text-center py-12 text-stone-500">
                No applications yet. Click "Apply for Verification" to submit your first application.
              </div>
            )}
          </div>
        )}
      </main>
    </div>
  );
}
