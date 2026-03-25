'use client';

import React, { useState, useEffect } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { API_BASE_URL } from '../../../../lib/config';


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
  const [personas, setPersonas] = useState<Persona[]>([]);
  const [stakeholders, setStakeholders] = useState<Stakeholder[]>([]);
  const [events, setEvents] = useState<Event[]>([]);

  const [selectedPersona, setSelectedPersona] = useState('');
  const [selectedEvent, setSelectedEvent] = useState('');
  const [selectedStakeholder, setSelectedStakeholder] = useState('');
  const [applicationText, setApplicationText] = useState('');
  const [uploadedFiles, setUploadedFiles] = useState<{filename: string; original_name: string; url: string}[]>([]);
  const [isUploading, setIsUploading] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  // Check authentication via JWT token
  useEffect(() => {
    const token = localStorage.getItem('access_token');
    if (token) {
      setIsAuthenticated(true);
      fetchData();
    }
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

  const getAuthHeaders = (): HeadersInit => {
    const headers: Record<string, string> = { 'Content-Type': 'application/json' };
    const token = localStorage.getItem('access_token');
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }
    return headers;
  };

  const fetchData = async () => {
    try {
      const headers = getAuthHeaders();

      if (!headers || Object.keys(headers).length === 0) {
        setError('Not authenticated. Please log in first.');
        return;
      }
      
      // Fetch in parallel but handle errors individually
      const [personasRes, stakeholdersRes, eventsRes] = await Promise.all([
        fetch(`${API_BASE_URL}/api/personas`, { headers }).catch(() => null),
        fetch(`${API_BASE_URL}/api/stakeholders/list`, { headers }).catch(() => null),
        fetch(`${API_BASE_URL}/api/events?status=active&page_size=50`, { headers }).catch(() => null),
      ]);

      if (personasRes?.ok) {
        const data = await personasRes.json();
        setPersonas(data.items || []);
      }

      if (stakeholdersRes?.ok) {
        const data = await stakeholdersRes.json();
        setStakeholders(data.items || []);
      }

      if (eventsRes?.ok) {
        const data = await eventsRes.json();
        setEvents(data.items || []);
      }
    } catch (err) {
      setError('Failed to load data. Please refresh the page.');
    }
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (!files || files.length === 0) return;

    const allowedTypes = ['application/pdf', 'image/png', 'image/jpeg', 'image/jpg'];
    const maxSize = 10 * 1024 * 1024; // 10MB

    for (let i = 0; i < files.length; i++) {
      if (!allowedTypes.includes(files[i].type)) {
        setError(`File "${files[i].name}" is not supported. Accepted: PDF, PNG, JPG`);
        return;
      }
      if (files[i].size > maxSize) {
        setError(`File "${files[i].name}" exceeds 10MB limit`);
        return;
      }
    }

    if (uploadedFiles.length + files.length > 5) {
      setError('Maximum 5 files allowed');
      return;
    }

    setIsUploading(true);
    setError('');

    try {
      const formData = new FormData();
      for (let i = 0; i < files.length; i++) {
        formData.append('files', files[i]);
      }

      const token = localStorage.getItem('access_token');
      const res = await fetch(`${API_BASE_URL}/api/personas/verify/upload`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` },
        body: formData,
      });

      if (res.ok) {
        const result = await res.json();
        setUploadedFiles(prev => [...prev, ...result.files]);
      } else {
        const result = await res.json();
        setError(typeof result.detail === 'string' ? result.detail : 'Upload failed');
      }
    } catch {
      setError('Failed to upload files');
    } finally {
      setIsUploading(false);
      e.target.value = '';
    }
  };

  const removeFile = (index: number) => {
    setUploadedFiles(prev => prev.filter((_, i) => i !== index));
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
          proof_type: uploadedFiles.length > 0 ? 'document' : 'self_declaration',
          proof_files: uploadedFiles.map(f => f.url),
        }),
      });

      if (response.ok) {
        alert('Application submitted successfully! Your request will be reviewed by an admin.');
        router.replace('/personas');
      } else {
        const result = await response.json();
        // Handle both string and object error messages
        const errorMessage = typeof result.detail === 'string' 
          ? result.detail 
          : JSON.stringify(result.detail);
        setError(errorMessage || 'Failed to submit application');
      }
    } catch (err) {
      setError('Network error. Please check your connection and try again.');
    } finally {
      setIsLoading(false);
    }
  };

  if (!isAuthenticated) {
    return (
      <div className="min-h-screen bg-stone-50 flex items-center justify-center">
        <div className="bg-white p-8 rounded-2xl shadow-xl max-w-md w-full text-center">
          <div className="text-6xl mb-4">🔒</div>
          <h1 className="text-2xl font-bold text-stone-900 mb-2">Apply for Verification</h1>
          <p className="text-stone-600 mb-6">Sign in to apply as a stakeholder</p>
          <button
            onClick={() => router.push('/auth/login')}
            className="w-full bg-stone-900 text-white py-2.5 rounded-lg font-medium hover:bg-stone-800 transition-colors"
          >
            Sign In
          </button>
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

            {/* File Upload */}
            <div className="bg-white rounded-xl border border-stone-200 p-6">
              <label className="block text-sm font-medium text-stone-700 mb-2">
                Supporting Documents (Optional)
              </label>
              <p className="text-xs text-stone-500 mb-3">
                Upload proof files to strengthen your application. Accepted: PDF, PNG, JPG (max 10MB each, up to 5 files)
              </p>

              <div className="border-2 border-dashed border-stone-300 rounded-lg p-6 text-center hover:border-stone-400 transition-colors">
                <input
                  type="file"
                  accept=".pdf,.png,.jpg,.jpeg"
                  multiple
                  onChange={handleFileUpload}
                  disabled={isUploading || uploadedFiles.length >= 5}
                  className="hidden"
                  id="file-upload"
                />
                <label htmlFor="file-upload" className={`cursor-pointer ${isUploading || uploadedFiles.length >= 5 ? 'opacity-50 cursor-not-allowed' : ''}`}>
                  <div className="text-3xl mb-2">📎</div>
                  <p className="text-sm text-stone-600">
                    {isUploading ? 'Uploading...' : 'Click to upload files'}
                  </p>
                  <p className="text-xs text-stone-400 mt-1">
                    {uploadedFiles.length}/5 files uploaded
                  </p>
                </label>
              </div>

              {/* Uploaded files list */}
              {uploadedFiles.length > 0 && (
                <div className="mt-4 space-y-2">
                  {uploadedFiles.map((file, index) => (
                    <div key={index} className="flex items-center justify-between bg-stone-50 rounded-lg px-4 py-2">
                      <div className="flex items-center space-x-2 min-w-0">
                        <span className="text-sm">
                          {file.original_name?.endsWith('.pdf') ? '📄' : '🖼️'}
                        </span>
                        <span className="text-sm text-stone-700 truncate">{file.original_name}</span>
                      </div>
                      <button
                        type="button"
                        onClick={() => removeFile(index)}
                        className="text-red-500 hover:text-red-700 text-sm ml-2 flex-shrink-0"
                      >
                        ✕
                      </button>
                    </div>
                  ))}
                </div>
              )}
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
