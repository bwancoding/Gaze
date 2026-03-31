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
    <div className="bg-white border border-neutral-200 rounded-lg p-5">
      <h3 className="font-semibold text-neutral-900 text-sm mb-1">Are you a stakeholder in this event?</h3>
      <p className="text-xs text-neutral-500 mb-4">
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
              className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-md text-sm transition-colors ${
                isDeclared
                  ? 'bg-emerald-50 text-emerald-700 border border-emerald-300 hover:bg-red-50 hover:text-red-600 hover:border-red-300'
                  : isLoading
                  ? 'bg-neutral-100 text-neutral-400 border border-neutral-200 cursor-wait'
                  : 'bg-white text-neutral-700 border border-neutral-300 hover:border-neutral-900 hover:text-neutral-900'
              }`}
              title={isDeclared ? 'Click to cancel declaration' : undefined}
            >
              {isCancelling ? (
                <span>Cancelling...</span>
              ) : isDeclared ? (
                <>
                  <svg className="w-3.5 h-3.5" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                  </svg>
                  <span>{sh.stakeholder_name}</span>
                </>
              ) : isLoading ? (
                <span>Declaring...</span>
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
            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-md text-sm bg-emerald-50 text-emerald-700 border border-emerald-300"
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
            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-md text-sm text-neutral-500 border border-dashed border-neutral-300 hover:border-neutral-900 hover:text-neutral-900 transition-colors"
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
              className="flex-1 px-3 py-1.5 rounded-md border border-neutral-300 text-sm focus:outline-none focus:border-neutral-900 focus:ring-1 focus:ring-neutral-900"
              maxLength={100}
              autoFocus
            />
            <button
              onClick={handleCustomDeclare}
              disabled={!customName.trim() || declaring === 'custom'}
              className="px-3 py-1.5 bg-neutral-900 text-white text-sm rounded-md hover:bg-neutral-800 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
            >
              {declaring === 'custom' ? '...' : 'Declare'}
            </button>
            <button
              onClick={() => { setShowCustom(false); setCustomName(''); }}
              className="px-2 py-1.5 text-neutral-400 hover:text-neutral-600 text-sm transition-colors"
            >
              Cancel
            </button>
          </div>
        )}
      </div>

      {error && (
        <p className="text-xs text-red-600 mt-2">{error}</p>
      )}
    </div>
  );
}
