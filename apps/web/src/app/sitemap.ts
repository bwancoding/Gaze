import type { MetadataRoute } from 'next';

const SITE_URL = process.env.NEXT_PUBLIC_SITE_URL || 'https://wrhitw.com';
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface EventItem {
  id: string;
  updated_at?: string;
}

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  // Static pages
  const staticPages: MetadataRoute.Sitemap = [
    {
      url: SITE_URL,
      lastModified: new Date(),
      changeFrequency: 'daily',
      priority: 1,
    },
    {
      url: `${SITE_URL}/stories`,
      lastModified: new Date(),
      changeFrequency: 'hourly',
      priority: 0.9,
    },
    {
      url: `${SITE_URL}/trending`,
      lastModified: new Date(),
      changeFrequency: 'hourly',
      priority: 0.9,
    },
    {
      url: `${SITE_URL}/feedback`,
      lastModified: new Date(),
      changeFrequency: 'monthly',
      priority: 0.3,
    },
  ];

  // Dynamic event pages
  let eventPages: MetadataRoute.Sitemap = [];
  try {
    const res = await fetch(`${API_BASE_URL}/api/events?page_size=100&status=active`, {
      next: { revalidate: 3600 },
    });
    if (res.ok) {
      const data = await res.json();
      eventPages = (data.items || []).map((event: EventItem) => ({
        url: `${SITE_URL}/events/${event.id}`,
        lastModified: event.updated_at ? new Date(event.updated_at) : new Date(),
        changeFrequency: 'daily' as const,
        priority: 0.7,
      }));
    }
  } catch {
    // Silently fail - sitemap will just have static pages
  }

  return [...staticPages, ...eventPages];
}
