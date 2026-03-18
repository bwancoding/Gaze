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
      className="group bg-white rounded-2xl border border-neutral-200 p-5 hover:shadow-xl hover:border-indigo-200 hover:-translate-y-1 transition-all duration-300 cursor-pointer h-full flex flex-col"
    >
      {/* Header */}
      <div className="flex items-start justify-between mb-3">
        <div className="flex-1 min-w-0">
          <h2 className="text-lg font-semibold text-neutral-900 mb-3 line-clamp-2 group-hover:text-indigo-600 transition-colors duration-200">
            {title}
          </h2>
          
          {category && (
            <span className="inline-block bg-gradient-to-r from-indigo-50 to-violet-50 text-indigo-700 px-3 py-1.5 rounded-full text-xs font-medium border border-indigo-100">
              {category}
            </span>
          )}
        </div>
        
        {/* Hot Score - Enhanced */}
        {hotScore > 0 && (
          <div className="flex items-center bg-gradient-to-r from-orange-50 to-amber-50 px-3 py-1.5 rounded-full">
            <svg className="w-4 h-4 mr-1.5 text-orange-500" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M12.395 2.553a1 1 0 00-1.45-.385c-.345.23-.614.558-.822.88-.214.33-.403.713-.57 1.116-.334.804-.614 1.768-.84 2.734a31.365 31.365 0 00-.613 3.58 2.64 2.64 0 01-.945-1.067c-.328-.68-.398-1.534-.398-2.654A1 1 0 005.05 6.05 6.981 6.981 0 003 11a7 7 0 1011.95-4.95c-.592-.591-.98-.985-1.348-1.467-.363-.476-.724-1.063-1.207-2.03zM12.12 15.12A3 3 0 017 13s.879.5 2.5.5c0-1 .5-4 1.25-4.5.5 1 .786 1.293 1.371 1.879A2.99 2.99 0 0113 13a2.99 2.99 0 01-.879 2.121z" clipRule="evenodd" />
            </svg>
            <span className="font-bold text-orange-600">{hotScore.toFixed(1)}</span>
          </div>
        )}
      </div>

      {/* Summary */}
      {summary && (
        <p className="text-neutral-600 text-sm mb-4 line-clamp-2 leading-relaxed flex-1">
          {summary}
        </p>
      )}

      {/* Stakeholder Analysis Indicator */}
      <div className="mb-4 p-3 bg-gradient-to-r from-slate-50 to-neutral-50 rounded-xl border border-neutral-100">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <span className="text-xs font-medium text-neutral-600">Stakeholder Analysis</span>
            <span className="text-xs text-neutral-400">·</span>
            <span className="text-xs text-neutral-500">{sourceCount} Sources</span>
          </div>
          <div className="flex items-center space-x-1.5">
            <div className="w-5 h-5 rounded-full bg-gradient-to-r from-amber-400 to-orange-500 flex items-center justify-center">
              <span className="text-[8px] font-bold text-white">AI</span>
            </div>
            <svg className="w-4 h-4 text-neutral-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z" /></svg>
          </div>
        </div>
      </div>

      {/* Footer */}
      <div className="flex items-center justify-between pt-4 border-t border-neutral-100">
        <div className="flex items-center space-x-4 text-sm text-neutral-500">
          {/* Source Count */}
          <span className="flex items-center group-hover:text-indigo-600 transition-colors duration-200">
            <svg className="w-4 h-4 mr-1.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
            </svg>
            {sourceCount}
          </span>
          
          {/* View Count */}
          {viewCount > 0 && (
            <span className="flex items-center group-hover:text-indigo-600 transition-colors duration-200">
              <svg className="w-4 h-4 mr-1.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
              </svg>
              {viewCount >= 1000 ? `${(viewCount / 1000).toFixed(1)}k` : viewCount}
            </span>
          )}
        </div>

        {/* Time */}
        {occurredAt && (
          <time dateTime={occurredAt} className="text-xs text-neutral-400 group-hover:text-neutral-600 transition-colors duration-200">
            {formatTime(occurredAt)}
          </time>
        )}
      </div>

      {/* Hover Arrow Indicator */}
      <div className="absolute bottom-5 right-5 opacity-0 group-hover:opacity-100 transform translate-x-2 group-hover:translate-x-0 transition-all duration-300">
        <svg className="w-5 h-5 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
        </svg>
      </div>
    </article>
  );
}
