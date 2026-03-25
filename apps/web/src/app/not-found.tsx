import Link from 'next/link';

export default function NotFound() {
  return (
    <div className="min-h-screen bg-stone-50 flex items-center justify-center">
      <main className="px-6 py-24 text-center">
        <div className="max-w-md mx-auto">
          <div className="text-8xl mb-6">🌍</div>
          <h1 className="text-4xl font-bold text-stone-900 mb-4">Page Not Found</h1>
          <p className="text-stone-600 mb-8 leading-relaxed">
            The page you&apos;re looking for doesn&apos;t exist or has been moved.
            Let&apos;s get you back on track.
          </p>
          <div className="flex flex-col sm:flex-row gap-3 justify-center">
            <Link
              href="/"
              className="inline-flex items-center justify-center px-6 py-3 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition-colors"
            >
              Go Home
            </Link>
            <Link
              href="/stories"
              className="inline-flex items-center justify-center px-6 py-3 bg-stone-200 text-stone-700 rounded-lg font-medium hover:bg-stone-300 transition-colors"
            >
              Browse Stories
            </Link>
          </div>
        </div>
      </main>
    </div>
  );
}
