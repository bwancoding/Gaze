'use client';

import React, { useState, useMemo } from 'react';
import Link from 'next/link';
import StakeholderBadge from './StakeholderBadge';

/**
 * StakeholderVoices — Groups and highlights comments from verified/declared
 * stakeholders at the top of the Discussion tab. Editorial "featured voices" feel.
 */

interface Comment {
  id: string;
  content: string;
  persona_name: string;
  avatar_color: string;
  stakeholder_name?: string | null;
  verification_level?: 'verified' | 'declared' | null;
  thread_id?: string | null;
  created_at: string;
}

interface StakeholderInfo {
  stakeholder_name: string;
}

interface StakeholderVoicesProps {
  comments: Comment[];
  stakeholders: StakeholderInfo[];
  eventId: string;
}

// Same accent palette as Perspectives tab for visual consistency
const accents = [
  { border: '#C2410C', bgVerified: 'rgba(255, 237, 213, 0.55)', bgDeclared: 'rgba(255, 237, 213, 0.25)', text: '#C2410C' },
  { border: '#1E40AF', bgVerified: 'rgba(219, 234, 254, 0.55)', bgDeclared: 'rgba(219, 234, 254, 0.25)', text: '#1E40AF' },
  { border: '#166534', bgVerified: 'rgba(220, 252, 231, 0.55)', bgDeclared: 'rgba(220, 252, 231, 0.25)', text: '#166534' },
  { border: '#92400E', bgVerified: 'rgba(254, 243, 199, 0.55)', bgDeclared: 'rgba(254, 243, 199, 0.25)', text: '#92400E' },
  { border: '#5B21B6', bgVerified: 'rgba(237, 233, 254, 0.55)', bgDeclared: 'rgba(237, 233, 254, 0.25)', text: '#5B21B6' },
  { border: '#9D174D', bgVerified: 'rgba(252, 231, 243, 0.55)', bgDeclared: 'rgba(252, 231, 243, 0.25)', text: '#9D174D' },
  { border: '#134E4A', bgVerified: 'rgba(204, 251, 241, 0.55)', bgDeclared: 'rgba(204, 251, 241, 0.25)', text: '#134E4A' },
];

function timeAgo(dateStr: string): string {
  const diff = Date.now() - new Date(dateStr).getTime();
  const mins = Math.floor(diff / 60000);
  if (mins < 1) return 'just now';
  if (mins < 60) return `${mins}m ago`;
  const hours = Math.floor(mins / 60);
  if (hours < 24) return `${hours}h ago`;
  const days = Math.floor(hours / 24);
  return `${days}d ago`;
}

interface StakeholderGroup {
  name: string;
  level: 'verified' | 'declared';
  comments: Comment[];
}

export default function StakeholderVoices({ comments, stakeholders, eventId }: StakeholderVoicesProps) {
  const [expandedGroups, setExpandedGroups] = useState<Set<string>>(new Set());

  const groups = useMemo(() => {
    // Filter to stakeholder-attributed comments only
    const stakeholderComments = comments.filter(
      c => c.stakeholder_name && c.verification_level
    );

    if (stakeholderComments.length === 0) return [];

    // Group by stakeholder_name
    const groupMap = new Map<string, StakeholderGroup>();
    for (const comment of stakeholderComments) {
      const name = comment.stakeholder_name!;
      const existing = groupMap.get(name);
      if (existing) {
        existing.comments.push(comment);
        // Upgrade to verified if any comment in group is verified
        if (comment.verification_level === 'verified') {
          existing.level = 'verified';
        }
      } else {
        groupMap.set(name, {
          name,
          level: comment.verification_level as 'verified' | 'declared',
          comments: [comment],
        });
      }
    }

    // Sort: verified first, then by comment count desc
    const sorted = Array.from(groupMap.values()).sort((a, b) => {
      if (a.level !== b.level) return a.level === 'verified' ? -1 : 1;
      return b.comments.length - a.comments.length;
    });

    return sorted;
  }, [comments]);

  if (groups.length === 0) return null;

  // Match stakeholder name to color index (same order as stakeholders list for consistency)
  const getColorIndex = (name: string): number => {
    const idx = stakeholders.findIndex(s => s.stakeholder_name === name);
    if (idx >= 0) return idx % accents.length;
    // Fallback: hash the name to get a stable index
    let hash = 0;
    for (let i = 0; i < name.length; i++) hash = ((hash << 5) - hash + name.charCodeAt(i)) | 0;
    return Math.abs(hash) % accents.length;
  };

  const toggleExpand = (name: string) => {
    setExpandedGroups(prev => {
      const next = new Set(prev);
      if (next.has(name)) next.delete(name);
      else next.add(name);
      return next;
    });
  };

  const PREVIEW_COUNT = 3;

  return (
    <div className="mb-8">
      {/* Section header */}
      <div className="mb-4">
        <h3 className="font-serif text-xl font-bold" style={{ color: 'var(--color-ink)' }}>
          Stakeholder Voices
        </h3>
        <p className="text-sm mt-0.5" style={{ color: 'var(--color-ink-light)' }}>
          Featured perspectives from identified parties
        </p>
      </div>

      {/* Stakeholder groups */}
      <div className="space-y-3">
        {groups.map((group) => {
          const colorIdx = getColorIndex(group.name);
          const accent = accents[colorIdx];
          const isExpanded = expandedGroups.has(group.name);
          const visibleComments = isExpanded
            ? group.comments
            : group.comments.slice(0, PREVIEW_COUNT);
          const hasMore = group.comments.length > PREVIEW_COUNT;

          return (
            <div
              key={group.name}
              className="rounded-r-lg border-l-4 px-4 py-3"
              style={{
                borderLeftColor: accent.border,
                backgroundColor: group.level === 'verified' ? accent.bgVerified : accent.bgDeclared,
              }}
            >
              {/* Group header */}
              <div className="flex items-center gap-2 mb-2.5">
                <span
                  className="text-[11px] font-bold uppercase tracking-wider"
                  style={{ color: accent.text }}
                >
                  {group.name}
                </span>
                <StakeholderBadge stakeholderName="" level={group.level} compact />
                <span className="text-[10px] ml-auto" style={{ color: 'var(--color-ink-light)' }}>
                  {group.comments.length} {group.comments.length === 1 ? 'voice' : 'voices'}
                </span>
              </div>

              {/* Comments */}
              <div className="space-y-2">
                {visibleComments.map((comment) => {
                  const truncated = comment.content.length > 140
                    ? comment.content.slice(0, 140).trimEnd() + '…'
                    : comment.content;

                  const inner = (
                    <div className="group">
                      <p className="text-[13px] leading-relaxed" style={{ color: 'var(--color-ink)' }}>
                        <span style={{ color: accent.text, fontWeight: 600 }}>&ldquo;</span>
                        {truncated}
                        {comment.content.length <= 140 && (
                          <span style={{ color: accent.text, fontWeight: 600 }}>&rdquo;</span>
                        )}
                      </p>
                      <p className="text-[11px] mt-0.5" style={{ color: 'var(--color-ink-light)' }}>
                        — {comment.persona_name} · {timeAgo(comment.created_at)}
                      </p>
                    </div>
                  );

                  if (comment.thread_id) {
                    return (
                      <Link
                        key={comment.id}
                        href={`/events/${eventId}/threads/${comment.thread_id}`}
                        className="block hover:opacity-80 transition-opacity"
                      >
                        {inner}
                      </Link>
                    );
                  }

                  return <div key={comment.id}>{inner}</div>;
                })}
              </div>

              {/* Expand/collapse */}
              {hasMore && (
                <button
                  onClick={() => toggleExpand(group.name)}
                  className="text-[12px] font-medium mt-2 hover:underline transition-colors"
                  style={{ color: accent.text }}
                >
                  {isExpanded
                    ? 'Show less'
                    : `View all ${group.comments.length} comments →`}
                </button>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
