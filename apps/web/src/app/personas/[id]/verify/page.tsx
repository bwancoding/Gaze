'use client';

import React, { useState, useEffect } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080';

interface Persona {
  id: string;
  persona_name: string;
  avatar_color: string;
}

interface Stakeholder {
  id: string;
  name: string;
  description: string;
  category: string;
}

interface Event {
  id: string;
  title: string;
  summary: string;
  category: string;
}

export default function VerifyForEvent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const personaIdFromUrl = searchParams.get('persona');
  const eventIdFromUrl = searchParams.get('event');

  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [personas, setPersonas] = useState<Persona[]>([]);
  const [stakeholders, setStakeholders] = useState<Stakeholder[]>([]);
  const [events, setEvents] = useState<Event[]>([]);
  
  const [selectedPersona, setSelectedPersona] = useState('');
  const [selectedEvent, setSelectedEvent] = useState('');
  const [selectedStakeholder, setSelectedStakeholder] = useState('');
  const [applicationText, setApplicationText] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  // Check authentication on mount
  useEffect(() => {
    console.log('[Verify Page] Checking authentication...');
    const storedAuth = localStorage.getItem('user_auth');
    console.log('[Verify Page] Stored auth:', storedAuth ? 'Found' : 'Not found');
    
    if (storedAuth) {
      try {
        const { username: storedUsername, password: storedPassword } = JSON.parse(storedAuth);
        if (storedUsername && storedPassword) {
          setUsername(storedUsername);
          setPassword(storedPassword);
          setIsAuthenticated(true);
          console.log('[Verify Page] Authenticated as:', storedUsername);
          // Fetch data immediately (state will be updated synchronously)
          fetchData();
          return;
        }
      } catch (err) {
        console.error('[Verify Page] Failed to parse stored auth:', err);
      }
    }
    
    console.log('[Verify Page] No valid auth found, showing login form');
  }, []);
  
  // Set pre-selected values from URL
  useEffect(() => {
    if (personaIdFromUrl) {
      setSelectedPersona(personaIdFromUrl);
    }
    if (eventIdFromUrl) {
      setSelectedEvent(eventIdFromUrl);
    }
  }, [personaIdFromUrl, eventIdFromUrl]);

  const getAuthHeaders = () => {
    // First check local state
    if (username && password) {
      const authString = btoa(`${username}:${password}`);
      console.log('[Auth] Using state credentials:', username);
      return {
        'Authorization': 'Basic ' + authString,
        'Content-Type': 'application/json',
      };
    }
    
    // Fallback: try to get from localStorage
    try {
      const storedAuth = localStorage.getItem('user_auth');
      if (storedAuth) {
        const { username: storedUsername, password: storedPassword } = JSON.parse(storedAuth);
        if (storedUsername && storedPassword) {
          const authString = btoa(`${storedUsername}:${storedPassword}`);
          console.log('[Auth] Using stored credentials:', storedUsername);
          return {
            'Authorization': 'Basic ' + authString,
            'Content-Type': 'application/json',
          };
        }
      }
    } catch (err) {
      console.error('[Auth] Failed to parse stored auth:', err);
    }
    
    console.warn('[Auth] No auth credentials found');
    return {};
  };

  const fetchData = async () => {
    try {
      const headers = getAuthHeaders();
      console.log('[Verify Page] Fetching data...');
      console.log('[Verify Page] Auth headers:', headers ? 'Has auth' : 'No auth');
      
      if (!headers || Object.keys(headers).length === 0) {
        console.error('[Verify Page] No authentication headers available');
        setError('Not authenticated. Please log in first.');
        return;
      }
      
      // Fetch in parallel but handle errors individually
      const [personasRes, stakeholdersRes, eventsRes] = await Promise.all([
        fetch(`${API_BASE_URL}/api/personas`, { headers }).catch(() => null),
        fetch(`${API_BASE_URL}/api/stakeholders/list`, { headers }).catch(() => null),
        fetch(`${API_BASE_URL}/api/events?status=active&page_size=50`, { headers }).catch(() => null),
      ]);

      console.log('[Verify Page] Responses:', {
        personas: personasRes?.status,
        stakeholders: stakeholdersRes?.status,
        events: eventsRes?.status,
      });

      if (personasRes?.ok) {
        const data = await personasRes.json();
        setPersonas(data.items || []);
        console.log('[Verify Page] Loaded personas:', data.items.length);
      }

      if (stakeholdersRes?.ok) {
        const data = await stakeholdersRes.json();
        setStakeholders(data.items || []);
        console.log('[Verify Page] Loaded stakeholders:', data.items.length);
      }

      if (eventsRes?.ok) {
        const data = await eventsRes.json();
        setEvents(data.items || []);
        console.log('[Verify Page] Loaded events:', data.items.length);
      }
    } catch (err) {
      console.error('[Verify Page] Failed to fetch data:', err);
      setError('Failed to load data. Please refresh the page.');
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    
    // Validate required fields
    if (!selectedPersona) {
      setError('Please select an identity');
      return;
    }
    if (!selectedEvent) {
      setError('Please select an event');
      return;
    }
    if (!selectedStakeholder) {
      setError('Please select a stakeholder');
      return;
    }
    if (!applicationText.trim()) {
      setError('Please provide an application text');
      return;
    }
    
    setIsLoading(true);

    try {
      const response = await fetch(`${API_BASE_URL}/api/personas/${selectedPersona}/verify`, {
        method: 'POST',
        headers: getAuthHeaders(),
        body: JSON.stringify({
          event_id: selectedEvent,
          stakeholder_id: selectedStakeholder,
          application_text: applicationText,
          proof_type: 'self_declaration',
        }),
      });

      if (response.ok) {
        alert('Application submitted successfully! Your request will be reviewed by an admin.');
        router.push('/personas');
      } else {
        const result = await response.json();
        // Handle both string and object error messages
        const errorMessage = typeof result.detail === 'string' 
          ? result.detail 
          : JSON.stringify(result.detail);
        setError(errorMessage || 'Failed to submit application');
      }
    } catch (err) {
      console.error('Submit error:', err);
      setError('Network error. Please check your connection and try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    try {
      // Test credentials with personas API
      const response = await fetch(`${API_BASE_URL}/api/personas`, {
        headers: getAuthHeaders(),
      });

      if (response.ok) {
        setIsAuthenticated(true);
        localStorage.setItem('user_auth', JSON.stringify({ username, password }));
        fetchData();
      } else if (response.status === 401) {
        setError('Invalid credentials. Please check your email and password.');
      } else {
        setError('Failed to connect to server');
      }
    } catch (err) {
      setError('Network error. Please make sure the backend is running.');
    } finally {
      setIsLoading(false);
    }
  };

  if (!isAuthenticated) {
    return (
      <div className="min-h-screen bg-stone-50 flex items-center justify-center">
        <div className="bg-white p-8 rounded-2xl shadow-xl max-w-md w-full">
          <div className="text-center mb-8">
            <h1 className="text-2xl font-bold text-stone-900 mb-2">Apply for Verification</h1>
            <p className="text-stone-600">Sign in to apply as a stakeholder</p>
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
              <h1 className="text-xl font-bold text-stone-900">Apply for Verification</h1>
              <p className="text-xs text-stone-500">Get verified as a stakeholder for an event</p>
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-sm text-stone-600">{username}</span>
              <button
                onClick={() => router.push('/personas')}
                className="text-stone-600 hover:text-stone-900 text-sm"
              >
                Back to Personas
              </button>
            </div>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-6 py-8">
        <div className="max-w-3xl mx-auto">
          {/* Info Box */}
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
            <h3 className="font-semibold text-blue-800 mb-2">What is stakeholder verification?</h3>
            <p className="text-sm text-blue-700">
              Get verified as a stakeholder (e.g., "Iranian Civilian", "Tech Worker") for a specific event. 
              Once approved, your comments on that event will show your verified badge, helping others 
              understand your perspective.
            </p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Select Persona */}
            <div className="bg-white rounded-xl border border-stone-200 p-6">
              <label className="block text-sm font-medium text-stone-700 mb-2">
                Select Your Identity *
              </label>
              <select
                value={selectedPersona}
                onChange={(e) => setSelectedPersona(e.target.value)}
                className="w-full px-4 py-2 border border-stone-300 rounded-lg focus:ring-2 focus:ring-stone-500"
                required
                disabled={personas.length === 0}
              >
                <option value="">Choose an identity...</option>
                {personas && personas.length > 0 ? (
                  personas.map((p) => (
                    <option key={p.id} value={p.id}>
                      {p.persona_name}
                    </option>
                  ))
                ) : null}
              </select>
              {personas.length === 0 && (
                <p className="mt-2 text-sm text-amber-600">
                  ⚠️ You don't have any personas yet.{' '}
                  <button
                    type="button"
                    onClick={() => router.push('/personas')}
                    className="text-blue-600 hover:underline"
                  >
                    Create one first
                  </button>
                </p>
              )}
            </div>

            {/* Select Event */}
            <div className="bg-white rounded-xl border border-stone-200 p-6">
              <label className="block text-sm font-medium text-stone-700 mb-2">
                Select Event *
              </label>
              <select
                value={selectedEvent}
                onChange={(e) => setSelectedEvent(e.target.value)}
                className="w-full px-4 py-2 border border-stone-300 rounded-lg focus:ring-2 focus:ring-stone-500"
                required
                disabled={events.length === 0}
              >
                <option value="">Choose an event...</option>
                {events && events.length > 0 ? (
                  events.map((e) => (
                    <option key={e.id} value={e.id}>
                      {e.title} ({e.category})
                    </option>
                  ))
                ) : null}
              </select>
              {events.length === 0 && (
                <p className="mt-2 text-sm text-amber-600">
                  ⚠️ No events available yet.
                </p>
              )}
            </div>

            {/* Select Stakeholder Type */}
            <div className="bg-white rounded-xl border border-stone-200 p-6">
              <label className="block text-sm font-medium text-stone-700 mb-2">
                Apply as Stakeholder *
              </label>
              <select
                value={selectedStakeholder}
                onChange={(e) => setSelectedStakeholder(e.target.value)}
                className="w-full px-4 py-2 border border-stone-300 rounded-lg focus:ring-2 focus:ring-stone-500"
                required
                disabled={stakeholders.length === 0}
              >
                <option value="">Choose a stakeholder type...</option>
                {stakeholders && stakeholders.length > 0 ? (
                  stakeholders.map((s) => (
                    <option key={s.id} value={s.id}>
                      {s.name} - {s.description}
                    </option>
                  ))
                ) : null}
              </select>
              {stakeholders.length === 0 && (
                <p className="mt-2 text-sm text-amber-600">
                  ⚠️ No stakeholder types available yet.
                </p>
              )}
            </div>

            {/* Application Text */}
            <div className="bg-white rounded-xl border border-stone-200 p-6">
              <label className="block text-sm font-medium text-stone-700 mb-2">
                Why do you qualify? *
              </label>
              <textarea
                value={applicationText}
                onChange={(e) => setApplicationText(e.target.value)}
                rows={4}
                className="w-full px-4 py-2 border border-stone-300 rounded-lg focus:ring-2 focus:ring-stone-500"
                placeholder="Explain why you belong to this stakeholder group. For example: 'I live in Iran and can share my personal experience...' or 'I work at NVIDIA as a software engineer...'"
                required
              />
              <p className="mt-2 text-xs text-stone-500">
                Your application will be reviewed by an admin. Be honest and specific.
              </p>
            </div>

            {/* Error Message */}
            {error && (
              <div className="bg-red-50 border border-red-200 text-red-800 px-4 py-2 rounded-lg text-sm">
                {error}
              </div>
            )}

            {/* Submit Button */}
            <div className="flex items-center justify-end space-x-4">
              <button
                type="button"
                onClick={() => router.push('/personas')}
                className="px-6 py-2.5 border border-stone-300 rounded-lg text-stone-700 font-medium hover:bg-stone-50 transition-colors"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={isLoading || !selectedPersona || !selectedEvent || !selectedStakeholder}
                className="px-6 py-2.5 bg-stone-900 text-white rounded-lg font-medium hover:bg-stone-800 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isLoading ? 'Submitting...' : 'Submit Application'}
              </button>
            </div>
          </form>

          {/* Help Text */}
          <div className="mt-8 bg-amber-50 border border-amber-200 rounded-lg p-4">
            <h3 className="font-semibold text-amber-800 mb-2">What happens next?</h3>
            <ol className="text-sm text-amber-700 space-y-1 list-decimal list-inside">
              <li>Submit your application with a detailed explanation</li>
              <li>An admin will review your application (usually within 1-3 days)</li>
              <li>If approved, your persona will be verified for this specific event</li>
              <li>When you comment on this event, your verified badge will be shown</li>
              <li>You can check your application status in "My Personas" page</li>
            </ol>
          </div>
        </div>
      </main>
    </div>
  );
}
