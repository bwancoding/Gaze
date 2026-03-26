import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Trending News | Gaze',
  description: 'Discover the most discussed global news stories right now. Real-time trending topics with multi-perspective analysis.',
  openGraph: {
    title: 'Trending News | Gaze',
    description: 'Discover the most discussed global news stories right now.',
  },
};

export default function TrendingLayout({ children }: { children: React.ReactNode }) {
  return children;
}
