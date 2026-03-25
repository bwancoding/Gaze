import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Browse Stories | WRHITW',
  description: 'Explore global news stories from multiple perspectives. Search and filter events across regions, categories, and stakeholders.',
  openGraph: {
    title: 'Browse Stories | WRHITW',
    description: 'Explore global news stories from multiple perspectives.',
  },
};

export default function StoriesLayout({ children }: { children: React.ReactNode }) {
  return children;
}
