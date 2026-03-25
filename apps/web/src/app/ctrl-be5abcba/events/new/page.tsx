'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import { API_BASE_URL } from '../../../../lib/config';


export default function CreateEventPage() {
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  
  const [formData, setFormData] = useState({
    title: '',
    summary: '',
    category: 'Politics',
    tags: '',
  });

  const categories = [
    'Environment',
    'Economy',
    'Technology',
    'Politics',
  ];

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    try {
      // Parse tags
      const tagsArray = formData.tags
        .split(',')
        .map(tag => tag.trim())
        .filter(tag => tag.length > 0);

      const eventData = {
        title: formData.title,
        summary: formData.summary,
        category: formData.category,
        tags: tagsArray,
      };

      const storedAuth = localStorage.getItem('admin_auth');
      const headers: HeadersInit = {
        'Content-Type': 'application/json',
      };

      if (storedAuth) {
        const { username, password } = JSON.parse(storedAuth);
        headers['Authorization'] = 'Basic ' + btoa(`${username}:${password}`);
      }

      const response = await fetch(`${API_BASE_URL}/api/admin/events`, {
        method: 'POST',
        headers,
        body: JSON.stringify(eventData),
      });

      if (response.ok) {
        alert('Event created successfully!');
        router.push('/ctrl-be5abcba');
      } else {
        const data = await response.json();
        setError(data.detail || 'Failed to create event');
      }
    } catch (err) {
      setError('Network error');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-stone-50">
      {/* Header */}
      <header className="bg-white border-b border-stone-200 sticky top-0 z-50">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-xl font-bold text-stone-900">Create New Event</h1>
              <p className="text-xs text-stone-500">Add a new event to the system</p>
            </div>
            <div className="flex items-center space-x-4">
              <button
                onClick={() => router.push('/ctrl-be5abcba')}
                className="text-stone-600 hover:text-stone-900 text-sm"
              >
                ← Back to Dashboard
              </button>
            </div>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-6 py-8">
        <div className="max-w-3xl mx-auto">
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Title */}
            <div className="bg-white p-6 rounded-xl border border-stone-200">
              <label className="block text-sm font-medium text-stone-700 mb-2">
                Event Title *
              </label>
              <input
                type="text"
                name="title"
                value={formData.title}
                onChange={handleChange}
                className="w-full px-4 py-2 border border-stone-300 rounded-lg focus:ring-2 focus:ring-stone-500 focus:border-transparent"
                placeholder="e.g., Global Climate Summit Reaches New Agreement"
                required
              />
              <p className="mt-1 text-xs text-stone-500">
                Clear, neutral title for the event
              </p>
            </div>

            {/* Summary */}
            <div className="bg-white p-6 rounded-xl border border-stone-200">
              <label className="block text-sm font-medium text-stone-700 mb-2">
                Summary *
              </label>
              <textarea
                name="summary"
                value={formData.summary}
                onChange={handleChange}
                rows={4}
                className="w-full px-4 py-2 border border-stone-300 rounded-lg focus:ring-2 focus:ring-stone-500 focus:border-transparent"
                placeholder="Brief summary of the event (1-2 sentences)"
                required
              />
              <p className="mt-1 text-xs text-stone-500">
                Short description that will appear in lists
              </p>
            </div>

            {/* Category */}
            <div className="bg-white p-6 rounded-xl border border-stone-200">
              <label className="block text-sm font-medium text-stone-700 mb-2">
                Category *
              </label>
              <select
                name="category"
                value={formData.category}
                onChange={handleChange}
                className="w-full px-4 py-2 border border-stone-300 rounded-lg focus:ring-2 focus:ring-stone-500 focus:border-transparent"
                required
              >
                {categories.map(cat => (
                  <option key={cat} value={cat}>{cat}</option>
                ))}
              </select>
              <p className="mt-1 text-xs text-stone-500">
                Choose the most relevant category
              </p>
            </div>

            {/* Tags */}
            <div className="bg-white p-6 rounded-xl border border-stone-200">
              <label className="block text-sm font-medium text-stone-700 mb-2">
                Tags
              </label>
              <input
                type="text"
                name="tags"
                value={formData.tags}
                onChange={handleChange}
                className="w-full px-4 py-2 border border-stone-300 rounded-lg focus:ring-2 focus:ring-stone-500 focus:border-transparent"
                placeholder="climate, environment, summit (comma-separated)"
              />
              <p className="mt-1 text-xs text-stone-500">
                Comma-separated tags for better searchability
              </p>
            </div>

            {/* Error Message */}
            {error && (
              <div className="bg-red-50 border border-red-200 text-red-800 px-4 py-3 rounded-lg text-sm">
                {error}
              </div>
            )}

            {/* Submit Button */}
            <div className="flex items-center justify-end space-x-4">
              <button
                type="button"
                onClick={() => router.push('/ctrl-be5abcba')}
                className="px-6 py-2.5 border border-stone-300 rounded-lg text-stone-700 font-medium hover:bg-stone-50 transition-colors"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={isLoading}
                className="px-6 py-2.5 bg-stone-900 text-white rounded-lg font-medium hover:bg-stone-800 transition-colors disabled:opacity-50"
              >
                {isLoading ? 'Creating...' : 'Create Event'}
              </button>
            </div>
          </form>

          {/* Help Text */}
          <div className="mt-8 bg-amber-50 border border-amber-200 rounded-lg p-4">
            <h3 className="font-semibold text-amber-800 mb-2">Tips for Creating Events</h3>
            <ul className="text-sm text-amber-700 space-y-1">
              <li>• Use neutral, unbiased language in titles</li>
              <li>• Keep summaries concise (1-2 sentences)</li>
              <li>• Choose the most relevant category</li>
              <li>• Add 2-5 tags for better discoverability</li>
              <li>• Events will appear on the homepage with hot_score = 50.0</li>
            </ul>
          </div>
        </div>
      </main>
    </div>
  );
}
