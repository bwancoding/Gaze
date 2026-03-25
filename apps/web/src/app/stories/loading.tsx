export default function StoriesLoading() {
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

      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Category filter skeleton */}
        <div className="flex gap-2 mb-6 overflow-x-auto">
          {Array.from({ length: 5 }).map((_, i) => (
            <div key={i} className="h-8 w-24 bg-stone-800 rounded-full animate-pulse shrink-0" />
          ))}
        </div>

        {/* Event cards skeleton */}
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {Array.from({ length: 6 }).map((_, i) => (
            <div key={i} className="bg-stone-800/50 rounded-xl p-5 border border-stone-700/50">
              <div className="flex items-center gap-2 mb-3">
                <div className="h-5 w-16 bg-stone-700 rounded-full animate-pulse" />
                <div className="h-4 w-24 bg-stone-700 rounded animate-pulse" />
              </div>
              <div className="h-5 w-full bg-stone-700 rounded animate-pulse mb-2" />
              <div className="h-5 w-3/4 bg-stone-700 rounded animate-pulse mb-3" />
              <div className="h-4 w-full bg-stone-700/50 rounded animate-pulse mb-1" />
              <div className="h-4 w-5/6 bg-stone-700/50 rounded animate-pulse mb-4" />
              <div className="flex gap-4">
                <div className="h-4 w-16 bg-stone-700 rounded animate-pulse" />
                <div className="h-4 w-16 bg-stone-700 rounded animate-pulse" />
                <div className="h-4 w-16 bg-stone-700 rounded animate-pulse" />
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
