import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Sign In | WRHITW',
  description: 'Sign in to WRHITW to join discussions, share perspectives, and engage with global news stories.',
  robots: { index: false, follow: false },
};

export default function AuthLayout({ children }: { children: React.ReactNode }) {
  return children;
}
