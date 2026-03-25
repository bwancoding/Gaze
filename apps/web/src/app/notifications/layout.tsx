import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Notifications | WRHITW',
  description: 'View your notifications and stay updated on discussions you follow.',
  robots: { index: false, follow: false },
};

export default function NotificationsLayout({ children }: { children: React.ReactNode }) {
  return children;
}
