'use client';

import { useEffect } from 'react';
import Link from 'next/link';

export default function EventError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    console.error('Event page error:', error);
  }, [error]);

  return (
    <div className="min-h-screen bg-stone-900 flex items-center justify-center px-4">
      <div className="text-center max-w-md">
        <div className="text-6xl mb-4">📰</div>
        <h2 className="text-2xl font-bold text-stone-100 mb-2">Failed to load event</h2>
        <p className="text-stone-400 mb-6">
          We couldn&apos;t load this event. It may have been removed, or there was a temporary issue.
        </p>
        <div className="flex gap-3 justify-center">
          <button
            onClick={reset}
            className="px-5 py-2.5 bg-amber-600 hover:bg-amber-500 text-white rounded-lg font-medium transition-colors"
          >
            Try Again
          </button>
          <Link
            href="/stories"
            className="px-5 py-2.5 bg-stone-700 hover:bg-stone-600 text-stone-200 rounded-lg font-medium transition-colors"
          >
            Browse Stories
          </Link>
        </div>
      </div>
    </div>
  );
}
