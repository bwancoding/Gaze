'use client';

import React from 'react';

/**
 * StakeholderBadge — Editorial-grade identity badges for comment headers.
 *
 * Two tiers:
 *   • verified  – proved identity, authoritative   (warm ink + accent rule)
 *   • declared  – self-declared, transparent        (muted, outlined)
 *
 * Design language: newspaper byline attribution, not social-media flair.
 * Compact inline element — sits between persona name and timestamp.
 */

interface StakeholderBadgeProps {
  stakeholderName: string;
  level: 'verified' | 'declared';
  /** Render at reduced size inside nested / reply comments */
  compact?: boolean;
}

export default function StakeholderBadge({
  stakeholderName,
  level,
  compact = false,
}: StakeholderBadgeProps) {
  if (level === 'verified') {
    return (
      <span
        className={`
          inline-flex items-center gap-[3px]
          ${compact ? 'px-[5px] py-[1px]' : 'px-[6px] py-[2px]'}
          rounded-[3px]
          ${compact ? 'text-[9px]' : 'text-[10px]'}
          font-semibold tracking-[0.01em] uppercase
          border
        `}
        style={{
          color: '#78350F',
          backgroundColor: 'rgba(254, 243, 199, 0.6)',
          borderColor: 'rgba(217, 119, 6, 0.25)',
        }}
        title={`Verified stakeholder: ${stakeholderName}`}
      >
        {/* Opening quote mark — editorial "voice of authority" */}
        <svg
          className={`${compact ? 'w-[9px] h-[9px]' : 'w-[10px] h-[10px]'} flex-shrink-0 opacity-80`}
          viewBox="0 0 16 16"
          fill="currentColor"
          aria-hidden="true"
        >
          <path d="M7.5 4.5C7.5 3.12 6.38 2 5 2S2.5 3.12 2.5 4.5c0 1.03.63 1.92 1.52 2.3C3.68 8.54 2.78 9.86 1.5 10.5c.28.47.78.5 1.17.27 1.72-.96 3.33-3.01 3.33-5.27v-1zm6 0C13.5 3.12 12.38 2 11 2s-2.5 1.12-2.5 2.5c0 1.03.63 1.92 1.52 2.3-.34 1.74-1.24 3.06-2.52 3.7.28.47.78.5 1.17.27 1.72-.96 3.33-3.01 3.33-5.27v-1z" />
        </svg>
        <span className="leading-none">{stakeholderName}</span>
      </span>
    );
  }

  // declared — subtle outlined pill with hollow quote icon, lower visual weight
  return (
    <span
      className={`
        inline-flex items-center gap-[3px]
        ${compact ? 'px-[5px] py-[1px]' : 'px-[6px] py-[2px]'}
        rounded-[3px]
        ${compact ? 'text-[9px]' : 'text-[10px]'}
        font-medium tracking-[0.01em]
        border
      `}
      style={{
        color: '#78716C',
        backgroundColor: 'transparent',
        borderColor: '#D6D3D1',
      }}
      title={`Self-declared: ${stakeholderName} (unverified)`}
    >
      {/* Hollow quote mark — "unconfirmed voice" */}
      <svg
        className={`${compact ? 'w-[9px] h-[9px]' : 'w-[10px] h-[10px]'} flex-shrink-0 opacity-60`}
        viewBox="0 0 16 16"
        fill="none"
        stroke="currentColor"
        strokeWidth="1.5"
        aria-hidden="true"
      >
        <path d="M6.5 4.5C6.5 3.4 5.6 2.5 4.5 2.5S2.5 3.4 2.5 4.5c0 .8.5 1.5 1.2 1.8C3.4 8 2.6 9.2 1.5 9.8M12.5 4.5c0-1.1-.9-2-2-2s-2 .9-2 2c0 .8.5 1.5 1.2 1.8-.3 1.7-1.1 2.9-2.2 3.5" />
      </svg>
      <span className="leading-none">{stakeholderName}</span>
    </span>
  );
}


/* ─── Preview / storybook context ──────────────────────────────
 *
 *  Comment header layout reference (how it sits in context):
 *
 *  ┌──────────────────────────────────────────────────────────┐
 *  │  [M]  Marcus T.  ┊ ❝ OCAML CORE TEAM ┊  · 3h ago      │   ← verified
 *  │  [P]  priya.k    ┊   OCaml Developer  ┊  · 1h ago      │   ← declared
 *  │  [D]  DaveFromTX                         · 45m ago      │   ← no badge
 *  └──────────────────────────────────────────────────────────┘
 *
 *  The badge inherits the flex-wrap gap from the comment header,
 *  so it naturally flows inline with the name and timestamp.
 *
 * ────────────────────────────────────────────────────────────── */
