export default function StoriesLoading() {
  return (
    <div className="min-h-screen" style={{ background: 'var(--color-paper)' }}>
      {/* Header skeleton */}
      <div className="border-b" style={{ borderColor: 'var(--color-rule)', background: 'var(--color-paper)' }}>
        <div className="container mx-auto px-6 py-3 flex items-center justify-between">
          <div className="h-6 w-32 rounded animate-pulse" style={{ background: 'var(--color-rule)' }} />
          <div className="flex gap-3">
            <div className="h-8 w-20 rounded animate-pulse" style={{ background: 'var(--color-rule)' }} />
            <div className="h-8 w-20 rounded animate-pulse" style={{ background: 'var(--color-rule)' }} />
          </div>
        </div>
      </div>

      <div className="container mx-auto px-6 py-8">
        {/* Category filter skeleton */}
        <div className="flex gap-4 mb-6">
          {Array.from({ length: 5 }).map((_, i) => (
            <div key={i} className="h-6 w-20 rounded animate-pulse" style={{ background: 'var(--color-rule)' }} />
          ))}
        </div>

        {/* Event list skeleton */}
        <div className="space-y-0">
          {Array.from({ length: 6 }).map((_, i) => (
            <div key={i} className="py-4 border-b" style={{ borderColor: 'var(--color-rule)' }}>
              <div className="flex items-center gap-2 mb-2">
                <div className="h-4 w-16 rounded-sm animate-pulse" style={{ background: 'var(--color-rule)' }} />
                <div className="h-3 w-12 rounded animate-pulse" style={{ background: 'var(--color-rule)' }} />
              </div>
              <div className="h-5 w-full rounded animate-pulse mb-2" style={{ background: 'var(--color-rule)' }} />
              <div className="h-5 w-3/4 rounded animate-pulse mb-3" style={{ background: 'var(--color-rule)' }} />
              <div className="flex gap-4">
                <div className="h-3 w-16 rounded animate-pulse" style={{ background: 'var(--color-rule)' }} />
                <div className="h-3 w-16 rounded animate-pulse" style={{ background: 'var(--color-rule)' }} />
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
