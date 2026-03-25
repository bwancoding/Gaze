export default function EventDetailLoading() {
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
        {/* Back button */}
        <div className="h-8 w-24 bg-stone-800 rounded animate-pulse mb-6" />

        {/* Title section */}
        <div className="mb-6">
          <div className="flex items-center gap-2 mb-3">
            <div className="h-6 w-20 bg-stone-700 rounded-full animate-pulse" />
            <div className="h-5 w-32 bg-stone-700 rounded animate-pulse" />
          </div>
          <div className="h-8 w-full bg-stone-700 rounded animate-pulse mb-2" />
          <div className="h-8 w-2/3 bg-stone-700 rounded animate-pulse mb-4" />
          <div className="flex gap-6">
            <div className="h-5 w-20 bg-stone-800 rounded animate-pulse" />
            <div className="h-5 w-20 bg-stone-800 rounded animate-pulse" />
            <div className="h-5 w-20 bg-stone-800 rounded animate-pulse" />
          </div>
        </div>

        {/* Tabs skeleton */}
        <div className="flex gap-1 mb-6 border-b border-stone-700">
          {Array.from({ length: 5 }).map((_, i) => (
            <div key={i} className="h-10 w-24 bg-stone-800 rounded-t animate-pulse" />
          ))}
        </div>

        {/* Content skeleton */}
        <div className="space-y-4">
          <div className="bg-stone-800/50 rounded-xl p-6 border border-stone-700/50">
            <div className="h-5 w-40 bg-stone-700 rounded animate-pulse mb-4" />
            <div className="space-y-2">
              <div className="h-4 w-full bg-stone-700/50 rounded animate-pulse" />
              <div className="h-4 w-full bg-stone-700/50 rounded animate-pulse" />
              <div className="h-4 w-4/5 bg-stone-700/50 rounded animate-pulse" />
              <div className="h-4 w-full bg-stone-700/50 rounded animate-pulse" />
              <div className="h-4 w-3/4 bg-stone-700/50 rounded animate-pulse" />
            </div>
          </div>
          <div className="bg-stone-800/50 rounded-xl p-6 border border-stone-700/50">
            <div className="h-5 w-32 bg-stone-700 rounded animate-pulse mb-4" />
            <div className="space-y-2">
              <div className="h-4 w-full bg-stone-700/50 rounded animate-pulse" />
              <div className="h-4 w-5/6 bg-stone-700/50 rounded animate-pulse" />
              <div className="h-4 w-full bg-stone-700/50 rounded animate-pulse" />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
