'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { isAuthenticated, getAuthHeaders, fetchWithAuth } from '../lib/auth';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080';

interface CommentFormProps {
  eventId: string;
  onSuccess?: () => void;
  parentId?: string;
  onCancel?: () => void;
}

export default function CommentForm({ eventId, onSuccess, parentId, onCancel }: CommentFormProps) {
  const router = useRouter();
  const [content, setContent] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedPersona, setSelectedPersona] = useState<string>('');
  const [isLoggedIn, setIsLoggedIn] = useState(false);

  // 获取用户 Persona 列表
  const [personas, setPersonas] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    checkLoginAndFetchPersonas();
  }, []);

  const checkLoginAndFetchPersonas = async () => {
    const authenticated = isAuthenticated();
    setIsLoggedIn(authenticated);
    
    if (authenticated) {
      await fetchPersonas();
    } else {
      setIsLoading(false);
    }
  };

  const fetchPersonas = async () => {
    try {
      const response = await fetchWithAuth(`${API_BASE_URL}/api/personas`);
      if (response.ok) {
        const data = await response.json();
        setPersonas(data.items || []);
        if (data.items && data.items.length > 0) {
          setSelectedPersona(data.items[0].id);
        }
      }
    } catch (err) {
      console.error('Failed to fetch personas:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!content.trim()) {
      setError('Comment cannot be empty');
      return;
    }

    if (!selectedPersona) {
      setError('Please select a persona');
      return;
    }

    setIsSubmitting(true);
    setError(null);

    try {
      const response = await fetchWithAuth(`${API_BASE_URL}/api/comments`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          event_id: eventId,
          user_persona_id: selectedPersona,
          content: content.trim(),
          parent_id: parentId,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to create comment');
      }

      setContent('');
      onSuccess?.();
    } catch (err: any) {
      setError(err.message || 'Failed to post comment');
    } finally {
      setIsSubmitting(false);
    }
  };

  // 未登录状态
  if (!isLoggedIn) {
    return (
      <div className="p-6 bg-stone-50 rounded-xl border border-stone-200 text-center">
        <div className="text-4xl mb-4">🔐</div>
        <p className="text-stone-700 font-medium mb-2">
          Sign in to share your perspective
        </p>
        <p className="text-sm text-stone-500 mb-4">
          Join the discussion and comment on this event
        </p>
        <button
          onClick={() => router.push('/auth/login')}
          className="inline-flex items-center space-x-2 bg-stone-900 text-white px-6 py-2.5 rounded-full font-medium hover:bg-stone-800 transition-colors"
        >
          <span>Sign In</span>
        </button>
      </div>
    );
  }

  // 加载中
  if (isLoading) {
    return (
      <div className="animate-pulse space-y-4">
        <div className="h-24 bg-stone-200 rounded-xl"></div>
      </div>
    );
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {parentId && onCancel && (
        <div className="flex items-center justify-between p-3 bg-blue-50 rounded-lg border border-blue-200">
          <span className="text-sm text-blue-700">
            Replying to comment
          </span>
          <button
            type="button"
            onClick={onCancel}
            className="text-sm text-blue-600 hover:text-blue-800 font-medium"
          >
            Cancel
          </button>
        </div>
      )}

      {/* Persona 选择 */}
      {personas.length > 1 && (
        <div>
          <label className="block text-sm font-medium text-stone-700 mb-2">
            Comment as
          </label>
          <div className="flex flex-wrap gap-2">
            {personas.map(persona => (
              <button
                key={persona.id}
                type="button"
                onClick={() => setSelectedPersona(persona.id)}
                className={`px-4 py-2 rounded-full text-sm font-medium transition-colors ${
                  selectedPersona === persona.id
                    ? 'bg-stone-900 text-white'
                    : 'bg-stone-100 text-stone-700 hover:bg-stone-200'
                }`}
              >
                {persona.persona_name}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* 评论输入框 */}
      <div>
        <textarea
          value={content}
          onChange={(e) => setContent(e.target.value)}
          placeholder="Share your perspective..."
          rows={4}
          className="w-full px-4 py-3 border border-stone-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none transition-all"
          maxLength={5000}
        />
        <div className="flex items-center justify-between mt-2">
          <span className={`text-xs ${content.length > 4500 ? 'text-red-600' : 'text-stone-500'}`}>
            {content.length}/5000
          </span>
        </div>
      </div>

      {/* 错误提示 */}
      {error && (
        <div className="p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
          {error}
        </div>
      )}

      {/* 提交按钮 */}
      <div className="flex items-center space-x-3">
        <button
          type="submit"
          disabled={isSubmitting || !content.trim()}
          className="px-6 py-2.5 bg-stone-900 text-white rounded-full font-medium hover:bg-stone-800 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {isSubmitting ? 'Posting...' : parentId ? 'Post Reply' : 'Post Comment'}
        </button>
        {onCancel && (
          <button
            type="button"
            onClick={onCancel}
            className="px-6 py-2.5 bg-stone-100 text-stone-700 rounded-full font-medium hover:bg-stone-200 transition-colors"
          >
            Cancel
          </button>
        )}
      </div>
    </form>
  );
}
