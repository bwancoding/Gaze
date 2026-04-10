import React from 'react';
import { useRouter } from 'next/navigation';

interface EventCardProps {
  id: string;
  title: string;
  summary?: string;
  category?: string;
  sourceCount: number;
  viewCount?: number;
  hotScore?: number;
  occurredAt?: string;
}

const getCatClass = (cat?: string): string => {
  const map: Record<string, string> = {
    'Environment': 'cat-environment',
    'Economy': 'cat-economy',
    'Technology': 'cat-technology',
    'Politics': 'cat-politics',
    'War & Conflict': 'cat-conflict',
    'Geopolitics': 'cat-geopolitics',
    'Health': 'cat-health',
    'Science': 'cat-science',
    'Entertainment': 'cat-entertainment',
    'Culture': 'cat-culture',
    'Society': 'cat-society',
    'Sports': 'cat-sports',
  };
  return (cat && map[cat]) || 'bg-neutral-100 text-neutral-700';
};

export default function EventCard({
  id,
  title,
  summary,
  category,
  sourceCount,
  viewCount = 0,
  hotScore = 0,
  occurredAt,
}: EventCardProps) {
  const router = useRouter();
  const formatTime = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    const hours = Math.floor(diff / (1000 * 60 * 60));
    const days = Math.floor(diff / (1000 * 60 * 60 * 24));

    if (hours < 1) return 'Just now';
    if (hours < 24) return `${hours}h ago`;
    if (days < 7) return `${days}d ago`;
    return date.toLocaleDateString('en-US');
  };

  return (
    <article
      onClick={() => router.push(`/events/${id}`)}
      className="group bg-white border border-neutral-200 rounded-lg p-5 hover:border-neutral-400 transition-colors cursor-pointer h-full flex flex-col"
    >
      {/* Header */}
      <div className="flex items-start justify-between mb-3">
        <div className="flex-1 min-w-0">
          <h2 className="font-serif text-lg font-semibold text-neutral-900 mb-2.5 line-clamp-2 group-hover:text-accent transition-colors leading-snug">
            {title}
          </h2>

          {category && (
            <span className={`inline-block text-xs px-2 py-0.5 rounded-md font-medium ${getCatClass(category)}`}>
              {category}
            </span>
          )}
        </div>

        {/* Hot Score */}
        {hotScore > 0 && (
          <span className="text-sm font-medium text-neutral-400 flex-shrink-0 ml-3">
            {hotScore.toFixed(1)}
          </span>
        )}
      </div>

      {/* Summary */}
      {summary && (
        <p className="text-neutral-600 text-sm mb-4 line-clamp-2 leading-relaxed flex-1">
          {summary}
        </p>
      )}

      {/* Footer */}
      <div className="flex items-center justify-between pt-3 border-t border-neutral-100 text-xs text-neutral-400">
        <div className="flex items-center gap-3">
          <span>{sourceCount} sources</span>
          {viewCount > 0 && (
            <span>{viewCount >= 1000 ? `${(viewCount / 1000).toFixed(1)}k` : viewCount} views</span>
          )}
        </div>

        {occurredAt && (
          <time dateTime={occurredAt}>
            {formatTime(occurredAt)}
          </time>
        )}
      </div>
    </article>
  );
}
