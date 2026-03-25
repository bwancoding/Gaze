import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Feedback | WRHITW',
  description: 'Share your feedback and help us improve WRHITW. We value your input on our multi-perspective news platform.',
  openGraph: {
    title: 'Feedback | WRHITW',
    description: 'Share your feedback and help us improve WRHITW.',
  },
};

export default function FeedbackLayout({ children }: { children: React.ReactNode }) {
  return children;
}
