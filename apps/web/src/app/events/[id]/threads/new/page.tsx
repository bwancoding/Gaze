'use client';

import React, { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Header from '../../../../../components/Header';
import { API_BASE_URL } from '../../../../../lib/config';


interface Persona {
  id: string;
  persona_name: string;
  avatar_color: string;
}

export default function NewThreadPage() {
  const params = useParams();
  const router = useRouter();
  const eventId = params.id as string;

  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');
  const [tags, setTags] = useState('');
  const [selectedPersona, setSelectedPersona] = useState('');
  const [personas, setPersonas] = useState<Persona[]>([]);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    const token = localStorage.getItem('access_token');
    if (!token) {
      router.push('/auth/login');
      return;
    }
    fetch(`${API_BASE_URL}/api/personas`, {
      headers: { 'Authorization': `Bearer ${token}` },
    })
      .then(r => r.ok ? r.json() : Promise.reject())
      .then(data => {
        const list = data.personas || [];
        setPersonas(list);
        if (list.length > 0) setSelectedPersona(list[0].id);
      })
      .catch(() => {});
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!title.trim() || !content.trim()) {
      setError('Title and content are required');
      return;
    }

    const token = localStorage.getItem('access_token');
    if (!token) {
      router.push('/auth/login');
      return;
    }

    setIsSubmitting(true);
    setError('');

    try {
      const body: any = {
        title: title.trim(),
        content: content.trim(),
        user_persona_id: selectedPersona || null,
      };
      if (tags.trim()) {
        body.tags = tags.split(',').map(t => t.trim()).filter(Boolean);
      }

      const r = await fetch(`${API_BASE_URL}/api/events/${eventId}/threads`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(body),
      });

      if (r.ok) {
        const data = await r.json();
        router.push(`/events/${eventId}/threads/${data.id}`);
      } else {
        const err = await r.json();
        setError(err.detail || 'Failed to create thread');
      }
    } catch {
      setError('Network error');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-stone-50">
      <Header />
      <main className="container mx-auto px-6 py-8">
        <div className="max-w-2xl mx-auto">
          <div className="flex items-center space-x-2 text-sm text-stone-500 mb-6">
            <button onClick={() => router.push(`/events/${eventId}`)} className="hover:text-stone-900">Event</button>
            <span>/</span>
            <span className="text-stone-900">New Thread</span>
          </div>

          <div className="bg-white rounded-2xl border border-stone-200 p-8">
            <h1 className="text-xl font-bold text-stone-900 mb-6">Start a Discussion</h1>

            <form onSubmit={handleSubmit} className="space-y-5">
              {personas.length > 0 && (
                <div>
                  <label className="block text-sm font-medium text-stone-700 mb-1">Post as</label>
                  <select
                    value={selectedPersona}
                    onChange={(e) => setSelectedPersona(e.target.value)}
                    className="w-full border border-stone-300 rounded-lg px-3 py-2 text-sm"
                  >
                    {personas.map(p => (
                      <option key={p.id} value={p.id}>{p.persona_name}</option>
                    ))}
                  </select>
                </div>
              )}

              <div>
                <label className="block text-sm font-medium text-stone-700 mb-1">Title</label>
                <input
                  type="text"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  maxLength={500}
                  className="w-full border border-stone-300 rounded-lg px-3 py-2"
                  placeholder="Thread title..."
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-stone-700 mb-1">Content</label>
                <textarea
                  value={content}
                  onChange={(e) => setContent(e.target.value)}
                  rows={8}
                  className="w-full border border-stone-300 rounded-lg px-3 py-2"
                  placeholder="Share your thoughts..."
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-stone-700 mb-1">Tags (comma-separated, optional)</label>
                <input
                  type="text"
                  value={tags}
                  onChange={(e) => setTags(e.target.value)}
                  className="w-full border border-stone-300 rounded-lg px-3 py-2"
                  placeholder="e.g. analysis, question, opinion"
                />
              </div>

              {error && <p className="text-red-600 text-sm">{error}</p>}

              <div className="flex space-x-3">
                <button
                  type="submit"
                  disabled={isSubmitting}
                  className="bg-stone-900 text-white px-6 py-2.5 rounded-lg font-medium hover:bg-stone-800 disabled:opacity-50"
                >
                  {isSubmitting ? 'Posting...' : 'Post Thread'}
                </button>
                <button
                  type="button"
                  onClick={() => router.push(`/events/${eventId}`)}
                  className="text-stone-600 px-6 py-2.5 rounded-lg font-medium hover:text-stone-900"
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        </div>
      </main>
    </div>
  );
}
