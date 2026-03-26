import type { Metadata } from 'next';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface EventData {
  id: string;
  title: string;
  summary?: string;
  category?: string;
}

async function fetchEvent(id: string): Promise<EventData | null> {
  try {
    const res = await fetch(`${API_BASE_URL}/api/events/${id}`, {
      next: { revalidate: 300 }, // Cache for 5 minutes
    });
    if (!res.ok) return null;
    return await res.json();
  } catch {
    return null;
  }
}

export async function generateMetadata({
  params,
}: {
  params: Promise<{ id: string }>;
}): Promise<Metadata> {
  const { id } = await params;
  const event = await fetchEvent(id);

  if (!event) {
    return {
      title: 'Event Not Found | Gaze',
      description: 'This event could not be found.',
    };
  }

  const title = `${event.title} | Gaze`;
  const description = event.summary
    ? event.summary.slice(0, 160)
    : `View "${event.title}" from multiple perspectives on Gaze.`;

  return {
    title,
    description,
    openGraph: {
      title: event.title,
      description,
      type: 'article',
      siteName: 'Gaze',
      ...(event.category && { tags: [event.category] }),
    },
    twitter: {
      card: 'summary_large_image',
      title: event.title,
      description,
    },
  };
}

export default function EventDetailLayout({ children }: { children: React.ReactNode }) {
  return children;
}
