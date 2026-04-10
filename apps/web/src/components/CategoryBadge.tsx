/**
 * CategoryBadge — editorial-style category chip with inline SVG icon.
 *
 * Icons are hand-picked to read at 12px and match the newspaper aesthetic:
 * stroke-based, 1.75 width, no fill, rounded caps.
 *
 * Color: colored background + darker tone icon/text (kept close to the
 * existing pastel palette so switching is non-disruptive, but the icon
 * gives each category a distinct silhouette).
 */
import React from 'react';

type IconProps = { className?: string };

const Icon = {
  // Politics — classical building with columns
  Politics: ({ className }: IconProps) => (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.75} strokeLinecap="round" strokeLinejoin="round">
      <path d="M3 21h18M3 10h18M5 6l7-3 7 3M4 10v11M20 10v11M8 14v4M12 14v4M16 14v4" />
    </svg>
  ),
  // Economy — trending line with endpoint
  Economy: ({ className }: IconProps) => (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.75} strokeLinecap="round" strokeLinejoin="round">
      <path d="M3 17l6-6 4 4 8-8" />
      <path d="M14 7h7v7" />
    </svg>
  ),
  // Technology — CPU chip
  Technology: ({ className }: IconProps) => (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.75} strokeLinecap="round" strokeLinejoin="round">
      <rect x="5" y="5" width="14" height="14" rx="1.5" />
      <rect x="9" y="9" width="6" height="6" />
      <path d="M9 2v3M15 2v3M9 19v3M15 19v3M2 9h3M2 15h3M19 9h3M19 15h3" />
    </svg>
  ),
  // Environment — leaf
  Environment: ({ className }: IconProps) => (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.75} strokeLinecap="round" strokeLinejoin="round">
      <path d="M11 20A7 7 0 019.8 6.1C15.5 5 17 4.48 19.8 2c1 3 1 5-1 8-1.3 2-3 4-5 5-2 1-5 1-5 1" />
      <path d="M2 21c2-3 5-7 12-8" />
    </svg>
  ),
  // Geopolitics — globe
  Geopolitics: ({ className }: IconProps) => (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.75} strokeLinecap="round" strokeLinejoin="round">
      <circle cx="12" cy="12" r="9" />
      <path d="M3 12h18M12 3a14 14 0 010 18M12 3a14 14 0 000 18" />
    </svg>
  ),
  // Society — three people
  Society: ({ className }: IconProps) => (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.75} strokeLinecap="round" strokeLinejoin="round">
      <path d="M16 21v-2a4 4 0 00-4-4H6a4 4 0 00-4 4v2" />
      <circle cx="9" cy="7" r="3" />
      <path d="M22 21v-2a4 4 0 00-3-3.87M16 3.13a4 4 0 010 7.75" />
    </svg>
  ),
  // Health — heart with pulse line
  Health: ({ className }: IconProps) => (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.75} strokeLinecap="round" strokeLinejoin="round">
      <path d="M20.84 4.61a5.5 5.5 0 00-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 00-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 000-7.78z" />
    </svg>
  ),
  // Science — atom
  Science: ({ className }: IconProps) => (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.75} strokeLinecap="round" strokeLinejoin="round">
      <circle cx="12" cy="12" r="1.5" />
      <ellipse cx="12" cy="12" rx="10" ry="4" />
      <ellipse cx="12" cy="12" rx="10" ry="4" transform="rotate(60 12 12)" />
      <ellipse cx="12" cy="12" rx="10" ry="4" transform="rotate(120 12 12)" />
    </svg>
  ),
  // Culture — paint brush tip
  Culture: ({ className }: IconProps) => (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.75} strokeLinecap="round" strokeLinejoin="round">
      <path d="M3 21c3 0 7-1 9-5" />
      <path d="M9 10a4 4 0 10.5-3c-1.5 2-3 5-3.5 7 3.5 0 5 1 5 3" />
      <path d="M18 3l3 3-9 9-3-3z" />
    </svg>
  ),
  // Entertainment — clapper / play
  Entertainment: ({ className }: IconProps) => (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.75} strokeLinecap="round" strokeLinejoin="round">
      <rect x="3" y="6" width="18" height="14" rx="1.5" />
      <path d="M3 10h18M7 6l-2 4M12 6l-2 4M17 6l-2 4" />
      <path d="M10 14l4 2.5-4 2.5z" fill="currentColor" stroke="none" />
    </svg>
  ),
  // Sports — trophy
  Sports: ({ className }: IconProps) => (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.75} strokeLinecap="round" strokeLinejoin="round">
      <path d="M8 21h8M12 17v4M7 4h10v4a5 5 0 01-10 0V4z" />
      <path d="M17 5h3v2a3 3 0 01-3 3M7 5H4v2a3 3 0 003 3" />
    </svg>
  ),
  Conflict: ({ className }: IconProps) => (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.75} strokeLinecap="round" strokeLinejoin="round">
      <path d="M14.5 17.5L3 6V3h3l11.5 11.5M13 19l6-6M16 16l4 4M19 21l2-2" />
    </svg>
  ),
};

const CATEGORY_META: Record<string, { icon: React.FC<IconProps>; className: string }> = {
  'Politics': { icon: Icon.Politics, className: 'cat-politics' },
  'Economy': { icon: Icon.Economy, className: 'cat-economy' },
  'Technology': { icon: Icon.Technology, className: 'cat-technology' },
  'Environment': { icon: Icon.Environment, className: 'cat-environment' },
  'Geopolitics': { icon: Icon.Geopolitics, className: 'cat-geopolitics' },
  'Society': { icon: Icon.Society, className: 'cat-society' },
  'Health': { icon: Icon.Health, className: 'cat-health' },
  'Science': { icon: Icon.Science, className: 'cat-science' },
  'Culture': { icon: Icon.Culture, className: 'cat-culture' },
  'Entertainment': { icon: Icon.Entertainment, className: 'cat-entertainment' },
  'Sports': { icon: Icon.Sports, className: 'cat-sports' },
  'War & Conflict': { icon: Icon.Conflict, className: 'cat-conflict' },
};

type Size = 'sm' | 'md';

export default function CategoryBadge({
  category,
  size = 'sm',
  className = '',
}: {
  category?: string | null;
  size?: Size;
  className?: string;
}) {
  if (!category) return null;
  const meta = CATEGORY_META[category];
  if (!meta) {
    return (
      <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-sm text-xs font-medium bg-neutral-100 text-neutral-700 ${className}`}>
        {category}
      </span>
    );
  }
  const IconComp = meta.icon;
  const iconSize = size === 'md' ? 'w-3.5 h-3.5' : 'w-3 h-3';
  const padding = size === 'md' ? 'px-2.5 py-1' : 'px-2 py-0.5';
  return (
    <span
      className={`inline-flex items-center gap-1.5 ${padding} rounded-sm text-xs font-medium ${meta.className} ${className}`}
    >
      <IconComp className={iconSize} />
      {category}
    </span>
  );
}
