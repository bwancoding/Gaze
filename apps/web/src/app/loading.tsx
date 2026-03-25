export default function RootLoading() {
  return (
    <div className="min-h-screen bg-stone-900 flex items-center justify-center">
      <div className="text-center">
        <div className="inline-block w-10 h-10 border-3 border-amber-400 border-t-transparent rounded-full animate-spin mb-4" />
        <p className="text-stone-400 text-sm">Loading...</p>
      </div>
    </div>
  );
}
