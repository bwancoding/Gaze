import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'My Personas | Gaze',
  description: 'Manage your discussion personas for engaging with news stories on Gaze.',
  robots: { index: false, follow: false },
};

export default function PersonasLayout({ children }: { children: React.ReactNode }) {
  return children;
}
