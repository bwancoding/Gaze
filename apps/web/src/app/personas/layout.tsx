import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'My Personas | WRHITW',
  description: 'Manage your discussion personas for engaging with news stories on WRHITW.',
  robots: { index: false, follow: false },
};

export default function PersonasLayout({ children }: { children: React.ReactNode }) {
  return children;
}
