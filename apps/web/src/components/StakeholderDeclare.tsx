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
  const [declared, setDeclared] = useState<Set<string>>(new Set());
  const [error, setError] = useState<string | null>(null);

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

          return (
            <button
              key={sh.stakeholder_id}
              onClick={() => !isDeclared && handleDeclare(sh.stakeholder_id, sh.stakeholder_name)}
              disabled={isDeclared || isLoading}
              className={`inline-flex items-center space-x-1.5 px-3 py-1.5 rounded-full text-sm font-medium transition-all ${
                isDeclared
                  ? 'bg-green-100 text-green-700 border border-green-300 cursor-default'
                  : isLoading
                  ? 'bg-blue-100 text-blue-500 border border-blue-200 cursor-wait'
                  : 'bg-white text-stone-700 border border-stone-300 hover:border-blue-400 hover:text-blue-700 hover:bg-blue-50 cursor-pointer'
              }`}
            >
              {isDeclared ? (
                <>
                  <svg className="w-3.5 h-3.5" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                  </svg>
                  <span>Declared as {sh.stakeholder_name}</span>
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
                <>
                  <span>I am {sh.stakeholder_name}</span>
                </>
              )}
            </button>
          );
        })}
      </div>

      {error && (
        <p className="text-xs text-red-500 mt-2">{error}</p>
      )}
    </div>
  );
}
