'use client';

import { useEffect } from 'react';

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    console.error('Page error:', error);
  }, [error]);

  return (
    <div className="min-h-screen bg-stone-900 flex items-center justify-center px-4">
      <div className="text-center max-w-md">
        <div className="text-6xl mb-4">&#x26A0;&#xFE0F;</div>
        <h2 className="text-2xl font-bold text-stone-100 mb-2">Something went wrong</h2>
        <p className="text-stone-400 mb-6">
          An unexpected error occurred. Please try again.
        </p>
        <div className="flex gap-3 justify-center">
          <button
            onClick={reset}
            className="px-5 py-2.5 bg-amber-600 hover:bg-amber-500 text-white rounded-lg font-medium transition-colors"
          >
            Try Again
          </button>
          <a
            href="/"
            className="px-5 py-2.5 bg-stone-700 hover:bg-stone-600 text-stone-200 rounded-lg font-medium transition-colors"
          >
            Go Home
          </a>
        </div>
        {error.digest && (
          <p className="text-stone-600 text-xs mt-6">Error ID: {error.digest}</p>
        )}
      </div>
    </div>
  );
}
