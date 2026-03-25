export default function TrendingLoading() {
  return (
    <div className="min-h-screen bg-stone-900">
      {/* Header skeleton */}
      <div className="border-b border-stone-800 bg-stone-900/95 backdrop-blur">
        <div className="max-w-7xl mx-auto px-4 py-3 flex items-center justify-between">
          <div className="h-6 w-32 bg-stone-800 rounded animate-pulse" />
          <div className="flex gap-3">
            <div className="h-8 w-20 bg-stone-800 rounded animate-pulse" />
            <div className="h-8 w-20 bg-stone-800 rounded animate-pulse" />
          </div>
        </div>
      </div>

      <div className="max-w-4xl mx-auto px-4 py-8">
        <div className="h-8 w-48 bg-stone-700 rounded animate-pulse mb-6" />

        {/* Trending cards skeleton */}
        <div className="space-y-4">
          {Array.from({ length: 5 }).map((_, i) => (
            <div key={i} className="bg-stone-800/50 rounded-xl p-5 border border-stone-700/50 flex gap-4">
              <div className="h-12 w-12 bg-stone-700 rounded-lg animate-pulse shrink-0 flex items-center justify-center text-stone-600 font-bold text-lg">
                {i + 1}
              </div>
              <div className="flex-1">
                <div className="h-5 w-full bg-stone-700 rounded animate-pulse mb-2" />
                <div className="h-4 w-3/4 bg-stone-700/50 rounded animate-pulse mb-3" />
                <div className="flex gap-4">
                  <div className="h-4 w-20 bg-stone-700 rounded animate-pulse" />
                  <div className="h-4 w-20 bg-stone-700 rounded animate-pulse" />
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
