import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'My Profile | Gaze',
  description: 'Manage your Gaze profile, threads, and comments.',
  robots: { index: false, follow: false },
};

export default function ProfileLayout({ children }: { children: React.ReactNode }) {
  return children;
}
