import { API_BASE_URL } from './config';

/**
 * Track a page view by sending it to the backend analytics endpoint.
 * Uses navigator.sendBeacon for fire-and-forget (survives page navigations).
 */
export function trackPageView() {
  try {
    const data = {
      path: window.location.pathname,
      referrer: document.referrer || null,
      screen_width: window.innerWidth,
    };

    const blob = new Blob([JSON.stringify(data)], { type: 'application/json' });
    navigator.sendBeacon(`${API_BASE_URL}/api/analytics/pageview`, blob);
  } catch {
    // Silently fail - analytics should never break the app
  }
}
