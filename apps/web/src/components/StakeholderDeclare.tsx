'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import { isAuthenticated, fetchWithAuth } from '../lib/auth';
import { API_BASE_URL } from '../lib/config';

interface Stakeholder {
  stakeholder_id: string;
  stakeholder_name: string;
}

interface StakeholderDeclareProps {
  eventId: string;
  stakeholders: Stakeholder[];
  onDeclared?: (stakeholderName: string) => void;
}

export default function StakeholderDeclare({ eventId, stakeholders, onDeclared }: StakeholderDeclareProps) {
  const router = useRouter();
  const [declaring, setDeclaring] = useState<string | null>(null);
  const [undeclaring, setUndeclaring] = useState<string | null>(null);
  const [declared, setDeclared] = useState<Set<string>>(new Set());
  const [error, setError] = useState<string | null>(null);
  const [showCustom, setShowCustom] = useState(false);
  const [customName, setCustomName] = useState('');
  const [customDeclared, setCustomDeclared] = useState<string[]>([]);

  const handleDeclare = async (stakeholderId: string, stakeholderName: string) => {
    if (!isAuthenticated()) {
      router.push(`/auth/login?redirect=/events/${eventId}`);
      return;
    }

    setDeclaring(stakeholderId);
    setError(null);

    try {
      const response = await fetchWithAuth(`${API_BASE_URL}/api/personas/quick-declare`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          event_id: eventId,
          stakeholder_id: stakeholderId,
        }),
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || 'Failed to declare');
      }

      setDeclared(prev => new Set(prev).add(stakeholderId));
      onDeclared?.(stakeholderName);
    } catch (err: any) {
      setError(err.message || 'Failed to declare');
    } finally {
      setDeclaring(null);
    }
  };

  const handleUndeclare = async (stakeholderId: string) => {
    setUndeclaring(stakeholderId);
    setError(null);

    try {
      const response = await fetchWithAuth(`${API_BASE_URL}/api/personas/quick-undeclare`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          event_id: eventId,
          stakeholder_id: stakeholderId,
        }),
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || 'Failed to cancel declaration');
      }

      setDeclared(prev => {
        const next = new Set(prev);
        next.delete(stakeholderId);
        return next;
      });
    } catch (err: any) {
      setError(err.message || 'Failed to cancel declaration');
    } finally {
      setUndeclaring(null);
    }
  };

  const handleCustomDeclare = async () => {
    const name = customName.trim();
    if (!name) return;

    if (!isAuthenticated()) {
      router.push(`/auth/login?redirect=/events/${eventId}`);
      return;
    }

    setDeclaring('custom');
    setError(null);

    try {
      const response = await fetchWithAuth(`${API_BASE_URL}/api/personas/quick-declare`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          event_id: eventId,
          custom_name: name,
        }),
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || 'Failed to declare');
      }

      setCustomDeclared(prev => [...prev, name]);
      setCustomName('');
      setShowCustom(false);
      onDeclared?.(name);
    } catch (err: any) {
      setError(err.message || 'Failed to declare');
    } finally {
      setDeclaring(null);
    }
  };

  if (stakeholders.length === 0) return null;

  return (
    <div className="bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200/60 rounded-xl p-5">
      <div className="flex items-center space-x-2 mb-3">
        <svg className="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5.882V19.24a1.76 1.76 0 01-3.417.592l-2.147-6.15M18 13a3 3 0 100-6M5.436 13.683A4.001 4.001 0 017 6h1.832c4.1 0 7.625-1.234 9.168-3v14c-1.543-1.766-5.067-3-9.168-3H7a3.988 3.988 0 01-1.564-.317z" />
        </svg>
        <h3 className="font-bold text-stone-900 text-sm">Are you a stakeholder in this event?</h3>
      </div>
      <p className="text-xs text-stone-500 mb-4">
        Declare your connection to speak with a stakeholder badge. You can submit verification proof later.
      </p>

      <div className="flex flex-wrap gap-2">
        {stakeholders.map((sh) => {
          const isDeclared = declared.has(sh.stakeholder_id);
          const isLoading = declaring === sh.stakeholder_id;
          const isCancelling = undeclaring === sh.stakeholder_id;

          return (
            <button
              key={sh.stakeholder_id}
              onClick={() => isDeclared ? handleUndeclare(sh.stakeholder_id) : handleDeclare(sh.stakeholder_id, sh.stakeholder_name)}
              disabled={isLoading || isCancelling}
              className={`inline-flex items-center space-x-1.5 px-3 py-1.5 rounded-full text-sm font-medium transition-all ${
                isDeclared
                  ? 'bg-green-100 text-green-700 border border-green-300 hover:bg-red-50 hover:text-red-600 hover:border-red-300 cursor-pointer'
                  : isLoading
                  ? 'bg-blue-100 text-blue-500 border border-blue-200 cursor-wait'
                  : 'bg-white text-stone-700 border border-stone-300 hover:border-blue-400 hover:text-blue-700 hover:bg-blue-50 cursor-pointer'
              }`}
              title={isDeclared ? 'Click to cancel declaration' : undefined}
            >
              {isCancelling ? (
                <>
                  <svg className="w-3.5 h-3.5 animate-spin" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                  </svg>
                  <span>Cancelling...</span>
                </>
              ) : isDeclared ? (
                <>
                  <svg className="w-3.5 h-3.5" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                  </svg>
                  <span>{sh.stakeholder_name}</span>
                </>
              ) : isLoading ? (
                <>
                  <svg className="w-3.5 h-3.5 animate-spin" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                  </svg>
                  <span>Declaring...</span>
                </>
              ) : (
                <span>I am {sh.stakeholder_name}</span>
              )}
            </button>
          );
        })}

        {/* Custom declared items */}
        {customDeclared.map((name) => (
          <span
            key={name}
            className="inline-flex items-center space-x-1.5 px-3 py-1.5 rounded-full text-sm font-medium bg-green-100 text-green-700 border border-green-300"
          >
            <svg className="w-3.5 h-3.5" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
            </svg>
            <span>{name}</span>
          </span>
        ))}

        {/* Other / Custom identity button */}
        {!showCustom ? (
          <button
            onClick={() => {
              if (!isAuthenticated()) {
                router.push(`/auth/login?redirect=/events/${eventId}`);
                return;
              }
              setShowCustom(true);
            }}
            className="inline-flex items-center space-x-1.5 px-3 py-1.5 rounded-full text-sm font-medium bg-white text-stone-500 border border-dashed border-stone-300 hover:border-blue-400 hover:text-blue-600 cursor-pointer transition-all"
          >
            <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
            </svg>
            <span>Other</span>
          </button>
        ) : (
          <div className="flex items-center gap-2 w-full mt-1">
            <input
              type="text"
              value={customName}
              onChange={(e) => setCustomName(e.target.value)}
              onKeyDown={(e) => { if (e.key === 'Enter') handleCustomDeclare(); if (e.key === 'Escape') setShowCustom(false); }}
              placeholder="e.g. Local Journalist, Military Family..."
              className="flex-1 px-3 py-1.5 rounded-lg border border-stone-300 text-sm focus:outline-none focus:border-blue-400 focus:ring-1 focus:ring-blue-200"
              maxLength={100}
              autoFocus
            />
            <button
              onClick={handleCustomDeclare}
              disabled={!customName.trim() || declaring === 'custom'}
              className="px-3 py-1.5 bg-blue-600 text-white text-sm rounded-lg font-medium hover:bg-blue-700 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
            >
              {declaring === 'custom' ? '...' : 'Declare'}
            </button>
            <button
              onClick={() => { setShowCustom(false); setCustomName(''); }}
              className="px-2 py-1.5 text-stone-400 hover:text-stone-600 text-sm transition-colors"
            >
              Cancel
            </button>
          </div>
        )}
      </div>

      {error && (
        <p className="text-xs text-red-500 mt-2">{error}</p>
      )}
    </div>
  );
}
