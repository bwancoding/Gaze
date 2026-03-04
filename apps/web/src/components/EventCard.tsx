import React from 'react';
import BiasBadge from './BiasBadge';

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
  return (
    <article className="bg-white rounded-lg border border-neutral-200 p-4 hover:shadow-lg transition-shadow cursor-pointer">
      {/* Header */}
      <div className="flex items-start justify-between mb-3">
        <div className="flex-1">
          <h2 className="text-lg font-semibold text-neutral-900 mb-2 line-clamp-2">
            {title}
          </h2>
          
          {category && (
            <span className="inline-block bg-neutral-100 text-neutral-600 px-2 py-1 rounded text-xs">
              {category}
            </span>
          )}
        </div>
        
        {/* Hot Score */}
        {hotScore > 0 && (
          <div className="flex items-center text-orange-500">
            <svg className="w-5 h-5 mr-1" fill="currentColor" viewBox="0 0 20 20">
              <path d="M10 2a1 1 0 011 1v1.323l3.954 1.582 1.699-3.181a1 1 0 111.794.852l-1.83 3.434a1 1 0 01-1.17.49L10 5.445V2z" />
            </svg>
            <span className="font-semibold">{hotScore.toFixed(1)}</span>
          </div>
        )}
      </div>

      {/* Summary */}
      {summary && (
        <p className="text-neutral-600 text-sm mb-4 line-clamp-2">
          {summary}
        </p>
      )}

      {/* Footer */}
      <div className="flex items-center justify-between text-sm text-neutral-500">
        <div className="flex items-center space-x-4">
          {/* Source Count */}
          <span className="flex items-center">
            <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
            </svg>
            {sourceCount} 个来源
          </span>
          
          {/* View Count */}
          {viewCount > 0 && (
            <span className="flex items-center">
              <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
              </svg>
              {viewCount.toLocaleString()}
            </span>
          )}
        </div>

        {/* Time */}
        {occurredAt && (
          <time dateTime={occurredAt}>
            {new Date(occurredAt).toLocaleDateString('zh-CN')}
          </time>
        )}
      </div>

      {/* Multi-perspective Indicator */}
      <div className="mt-3 pt-3 border-t border-neutral-100">
        <div className="flex items-center justify-between">
          <span className="text-xs text-neutral-500">多视角分析</span>
          <div className="flex space-x-1">
            <BiasBadge bias="left" size="sm" />
            <BiasBadge bias="center" size="sm" />
            <BiasBadge bias="right" size="sm" />
          </div>
        </div>
      </div>
    </article>
  );
}
