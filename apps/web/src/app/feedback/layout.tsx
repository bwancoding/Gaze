import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Feedback | Gaze',
  description: 'Share your feedback and help us improve Gaze. We value your input on our multi-perspective news platform.',
  openGraph: {
    title: 'Feedback | Gaze',
    description: 'Share your feedback and help us improve Gaze.',
  },
};

export default function FeedbackLayout({ children }: { children: React.ReactNode }) {
  return children;
}
