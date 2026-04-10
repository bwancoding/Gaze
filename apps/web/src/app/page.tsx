'use client';

import React from 'react';
import { useRouter } from 'next/navigation';
import Header from '../components/Header';
import CategoryBadge from '../components/CategoryBadge';
import { isAuthenticated } from '../lib/auth';
import { API_BASE_URL } from '../lib/config';

/* ── Types ────────────────────────────────────────── */
interface TrendingEvent {
  rank: number;
  id: number;
  title: string;
  summary?: string;
  keywords: string[];
  category?: string;
  heat_score: number;
  article_count: number;
  media_count: number;
  sources: string[];
  created_at?: string;
  last_updated?: string;
  event_id?: string;
  published_event_id?: string;
}

/* ── Scroll reveal hook — watches for dynamically added elements ── */
function useScrollReveal() {
  React.useEffect(() => {
    const prefersReduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    const selectors = '.reveal:not(.is-visible), .reveal-left:not(.is-visible), .reveal-right:not(.is-visible), .reveal-scale:not(.is-visible)';

    if (prefersReduced) {
      const makeVisible = () => document.querySelectorAll(selectors).forEach(el => el.classList.add('is-visible'));
      makeVisible();
      const mo = new MutationObserver(makeVisible);
      mo.observe(document.body, { childList: true, subtree: true });
      return () => mo.disconnect();
    }

    const io = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add('is-visible');
            io.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.12, rootMargin: '0px 0px -40px 0px' },
    );

    // Observe existing elements
    document.querySelectorAll(selectors).forEach(el => io.observe(el));

    // Watch for new elements added to DOM (e.g. after async data load)
    const mo = new MutationObserver(() => {
      document.querySelectorAll(selectors).forEach(el => io.observe(el));
    });
    mo.observe(document.body, { childList: true, subtree: true });

    return () => { io.disconnect(); mo.disconnect(); };
  }, []);
}

/* ── Count-up hook ─────────────────────────────────── */
function useCountUp(target: number, suffix = '', duration = 1400) {
  const [display, setDisplay] = React.useState('0' + suffix);
  const ref = React.useRef<HTMLSpanElement | null>(null);
  const hasRun = React.useRef(false);

  React.useEffect(() => {
    const el = ref.current;
    if (!el) return;

    const prefersReduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (prefersReduced) {
      setDisplay(target.toLocaleString() + suffix);
      return;
    }

    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting && !hasRun.current) {
          hasRun.current = true;
          observer.unobserve(el);
          const start = performance.now();
          const tick = (now: number) => {
            const t = Math.min((now - start) / duration, 1);
            const eased = 1 - Math.pow(1 - t, 3);
            const current = Math.round(eased * target);
            setDisplay(current.toLocaleString() + suffix);
            if (t < 1) requestAnimationFrame(tick);
          };
          requestAnimationFrame(tick);
        }
      },
      { threshold: 0.3 },
    );

    observer.observe(el);
    return () => observer.disconnect();
  }, [target, suffix, duration]);

  return { ref, display };
}

/* ── Parallax hook ─────────────────────────────────── */
function useParallax(speed = 0.3) {
  const ref = React.useRef<HTMLDivElement>(null);

  React.useEffect(() => {
    const prefersReduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (prefersReduced) return;

    const el = ref.current;
    if (!el) return;

    let ticking = false;
    const handleScroll = () => {
      if (!ticking) {
        requestAnimationFrame(() => {
          const rect = el.getBoundingClientRect();
          const offset = (rect.top - window.innerHeight / 2) * speed;
          el.style.transform = `translateY(${offset}px)`;
          ticking = false;
        });
        ticking = true;
      }
    };

    window.addEventListener('scroll', handleScroll, { passive: true });
    return () => window.removeEventListener('scroll', handleScroll);
  }, [speed]);

  return ref;
}

/* ── Stats data ────────────────────────────────────── */
const stats = [
  { target: 200, suffix: '+', label: 'Sources' },
  { target: 50, suffix: '+', label: 'Countries' },
  { target: 1000, suffix: '+', label: 'Events' },
  { target: 24, suffix: '/7', label: 'Coverage' },
];

/* ── Stat cell component ───────────────────────────── */
function StatCell({ target, suffix, label, delay }: { target: number; suffix: string; label: string; delay: number }) {
  const { ref, display } = useCountUp(target, suffix);
  return (
    <div className={`reveal ${delay > 0 ? `reveal-delay-${delay}` : ''}`}>
      <span ref={ref} className="font-serif text-3xl md:text-4xl stat-number block font-bold text-accent">
        {display}
      </span>
      <span className="text-[11px] uppercase tracking-[0.1em] text-neutral-500 mt-1 block">
        {label}
      </span>
    </div>
  );
}

/* ── Marquee strip ─────────────────────────────────── */
const marqueeItems = ['Aggregate', 'Analyze', 'Discuss', 'Understand', 'Compare', 'Verify', 'Contextualize', 'Engage', 'Decode', 'Illuminate'];

function MarqueeStrip() {
  return (
    <div className="overflow-hidden border-y py-4" style={{ borderColor: 'var(--color-rule)', background: 'var(--color-paper)' }}>
      <div className="marquee-track flex whitespace-nowrap">
        {[...marqueeItems, ...marqueeItems].map((item, i) => (
          <span key={i} className="inline-flex items-center mx-8">
            <span className="font-serif text-lg md:text-xl italic" style={{ color: 'rgba(28,25,23,0.15)' }}>{item}</span>
            <span className="ml-8 text-xs" style={{ color: 'rgba(194,65,12,0.4)' }}>&#9670;</span>
          </span>
        ))}
      </div>
    </div>
  );
}

/* ── Category class helper ─────────────────────────── */
/* ── Time ago helper ───────────────────────────────── */
function formatTimeAgo(dateStr?: string): string {
  if (!dateStr) return '';
  const date = new Date(dateStr);
  if (isNaN(date.getTime())) return '';
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffMins = Math.floor(diffMs / 60000);
  if (diffMins < 60) return `${diffMins}m ago`;
  const diffHours = Math.floor(diffMins / 60);
  if (diffHours < 24) return `${diffHours}h ago`;
  const diffDays = Math.floor(diffHours / 24);
  return `${diffDays}d ago`;
}

/* ═══════════════════════════════════════════════════════
   Home Page
   ═══════════════════════════════════════════════════════ */
export default function Home() {
  const router = useRouter();
  const [loggedIn, setLoggedIn] = React.useState(false);
  const [mounted, setMounted] = React.useState(false);
  const [trending, setTrending] = React.useState<TrendingEvent[]>([]);
  const [trendingLoading, setTrendingLoading] = React.useState(true);
  const parallaxRef = useParallax(0.15);

  React.useEffect(() => {
    setLoggedIn(isAuthenticated());
    setMounted(true);
  }, []);

  // Fetch trending data
  React.useEffect(() => {
    (async () => {
      try {
        const res = await fetch(`${API_BASE_URL}/api/trending?limit=10&published_only=true`);
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const data = await res.json();
        setTrending(data.events || []);
      } catch (err) {
        console.error('Failed to fetch trending:', err);
      } finally {
        setTrendingLoading(false);
      }
    })();
  }, []);

  useScrollReveal();

  const getEventLink = (t: TrendingEvent) => t.published_event_id || t.event_id;
  const leadStory = trending[0];
  const topStories = trending.slice(1, 5);
  const restStories = trending.slice(5);

  return (
    <div className="min-h-screen" style={{ background: 'var(--color-paper)' }}>
      <Header />

      <main>
        {/* ═══ Hero — cinematic, warm dark ═══ */}
        <section className="relative overflow-hidden grain" style={{ background: 'var(--color-warm-dark)' }}>
          <div className="relative container mx-auto px-6 py-16 md:py-24 lg:py-28">
            <div className="grid lg:grid-cols-12 gap-8 items-end">
              {/* Left: main content */}
              <div className="lg:col-span-7">
                <p className="text-xs uppercase tracking-[0.25em] text-neutral-500 mb-6">
                  Global News Platform
                </p>
                <h1 className="font-serif text-white mb-6 text-clip-reveal" style={{ fontSize: 'clamp(2.5rem, 6vw, 4.5rem)', lineHeight: 1.05, letterSpacing: '-0.03em' }}>
                  <span className="italic">We Gaze Upon</span><br />
                  <span className="not-italic font-bold">the Same Moon.</span>
                </h1>
                <p className="text-neutral-400 mb-8 max-w-md leading-relaxed text-sm md:text-base">
                  Every global event carries multiple perspectives.
                  We bring them together so you can see the full picture.
                </p>
                <div className="flex items-center gap-4">
                  <button
                    onClick={() => router.push('/stories')}
                    className="btn-press bg-accent text-white px-6 py-2.5 rounded-md font-medium text-sm hover:bg-accent-light hover:-translate-y-px hover:shadow-lg transition-all"
                  >
                    Explore Stories
                  </button>
                  {!loggedIn && (
                    <button
                      onClick={() => router.push('/auth/register')}
                      className="text-sm text-neutral-400 hover:text-white transition-colors border border-white/[0.15] px-5 py-2 rounded-md hover:border-white/[0.3]"
                    >
                      Join the Conversation
                    </button>
                  )}
                </div>
              </div>

              {/* Right: floating stats card */}
              <div className="lg:col-span-5 hidden lg:block" ref={parallaxRef}>
                <div className="bg-white/[0.04] backdrop-blur-sm border border-white/[0.06] rounded-lg p-8">
                  <p className="text-[10px] uppercase tracking-[0.2em] text-neutral-500 mb-5">Platform at a Glance</p>
                  <div className="grid grid-cols-2 gap-6">
                    {stats.map((s, i) => (
                      <StatCell key={s.label} target={s.target} suffix={s.suffix} label={s.label} delay={i} />
                    ))}
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Diagonal accent line */}
          <div className="absolute bottom-0 left-0 right-0 h-px" style={{ background: 'linear-gradient(90deg, transparent, var(--color-accent), transparent)' }} />
        </section>

        {/* ═══ Marquee strip ═══ */}
        <MarqueeStrip />

        {/* ═══ Trending Section ═══ */}
        <section className="container mx-auto px-6 py-12 md:py-16">
          <div className="reveal flex items-baseline justify-between mb-0">
            <hr className="rule-thick flex-1" />
            <span className="text-xs uppercase tracking-[0.2em] pl-4 flex-shrink-0" style={{ color: 'var(--color-ink-light)' }}>
              Right now
            </span>
          </div>
          <div className="h-6" />

          {trendingLoading ? (
            <div className="space-y-4">
              {[1,2,3].map(i => (
                <div key={i} className="animate-pulse h-24 rounded-lg" style={{ background: 'var(--color-rule)' }} />
              ))}
            </div>
          ) : trending.length === 0 ? (
            <div className="text-center py-16 reveal">
              <p className="font-serif text-lg mb-2" style={{ color: 'var(--color-ink)' }}>No trending stories right now</p>
              <p className="text-sm" style={{ color: 'var(--color-ink-light)' }}>Check back soon for the latest global coverage</p>
            </div>
          ) : (
            <>
              {/* ── #1 Lead Story — light editorial with accent border ── */}
              {leadStory && (() => {
                const link = getEventLink(leadStory);
                return (
                  <article
                    onClick={() => link ? router.push(`/events/${link}`) : undefined}
                    className="reveal mb-8 cursor-pointer group flex gap-6"
                  >
                    <div className="w-1 flex-shrink-0 rounded-full" style={{ background: 'var(--color-accent)' }} />
                    <div className="flex-1 py-2">
                      <div className="flex items-center gap-3 mb-3">
                        <CategoryBadge category={leadStory.category} size="md" />
                        {mounted && leadStory.last_updated && (
                          <span className="text-xs" style={{ color: 'var(--color-ink-light)' }} suppressHydrationWarning>
                            {formatTimeAgo(leadStory.last_updated)}
                          </span>
                        )}
                        <span className="text-xs" style={{ color: 'var(--color-ink-light)' }}>
                          {leadStory.article_count} articles · {leadStory.sources?.length || leadStory.media_count} sources
                        </span>
                      </div>
                      <h3
                        className="font-serif font-bold leading-tight mb-3 group-hover:opacity-75 transition-opacity"
                        style={{ color: 'var(--color-ink)', fontSize: 'clamp(1.75rem, 4vw, 2.75rem)', letterSpacing: '-0.02em' }}
                      >
                        {leadStory.title}
                      </h3>
                      {leadStory.summary && (
                        <p className="leading-relaxed max-w-2xl line-clamp-2 text-sm" style={{ color: 'var(--color-ink-light)' }}>
                          {leadStory.summary}
                        </p>
                      )}
                    </div>
                  </article>
                );
              })()}

              {/* ── #2–#5 — two-column grid ── */}
              {topStories.length > 0 && (
                <div className="grid md:grid-cols-2 gap-x-8 gap-y-0 mb-2">
                  {topStories.map((t, i) => {
                    const link = getEventLink(t);
                    return (
                      <article
                        key={t.id}
                        onClick={() => link ? router.push(`/events/${link}`) : undefined}
                        className={`reveal reveal-delay-${i + 1} group py-5 cursor-pointer border-b`}
                        style={{ borderColor: 'var(--color-rule)' }}
                      >
                        <div className="flex items-start gap-4">
                          <span
                            className="font-serif font-bold text-2xl flex-shrink-0 w-8 text-right leading-none pt-0.5"
                            style={{ color: 'var(--color-accent)', opacity: 0.5 }}
                          >
                            {t.rank}
                          </span>
                          <div className="flex-1 min-w-0">
                            <div className="flex items-center gap-2 mb-1.5">
                              <CategoryBadge category={t.category} />
                              {mounted && t.last_updated && (
                                <span className="text-xs" style={{ color: 'var(--color-ink-light)' }} suppressHydrationWarning>
                                  {formatTimeAgo(t.last_updated)}
                                </span>
                              )}
                            </div>
                            <h3
                              className="font-serif font-semibold leading-snug mb-1.5 group-hover:opacity-75 transition-opacity"
                              style={{ color: 'var(--color-ink)' }}
                            >
                              {t.title}
                            </h3>
                            <div className="flex items-center gap-3 text-xs" style={{ color: 'var(--color-ink-light)' }}>
                              <span>{t.article_count} articles</span>
                              <span className="w-1 h-1 rounded-full" style={{ background: 'var(--color-rule)' }} />
                              <span>{t.sources?.length || t.media_count} sources</span>
                            </div>
                          </div>
                        </div>
                      </article>
                    );
                  })}
                </div>
              )}

              {/* ── Diamond divider ── */}
              {restStories.length > 0 && (
                <div className="flex items-center gap-4 my-8">
                  <div className="flex-1 h-px" style={{ background: 'var(--color-rule)' }} />
                  <span className="text-xs" style={{ color: 'var(--color-rule)' }}>◆</span>
                  <div className="flex-1 h-px" style={{ background: 'var(--color-rule)' }} />
                </div>
              )}

              {/* ── #6–#10 — compact list ── */}
              {restStories.length > 0 && (
                <div className="reveal">
                  <p className="text-xs uppercase tracking-[0.2em] mb-4" style={{ color: 'var(--color-ink-light)' }}>
                    Also trending
                  </p>
                  {restStories.map(t => {
                    const link = getEventLink(t);
                    return (
                      <article
                        key={t.id}
                        onClick={() => link ? router.push(`/events/${link}`) : undefined}
                        className="group flex items-center gap-4 py-3 cursor-pointer border-b"
                        style={{ borderColor: 'var(--color-rule)' }}
                      >
                        <span
                          className="font-serif text-sm flex-shrink-0 w-6 text-right"
                          style={{ color: 'var(--color-ink-light)', opacity: 0.5 }}
                        >
                          {t.rank}
                        </span>
                        <CategoryBadge category={t.category} className="flex-shrink-0" />
                        <h3
                          className="font-serif text-sm flex-1 min-w-0 truncate group-hover:opacity-75 transition-opacity"
                          style={{ color: 'var(--color-ink)' }}
                        >
                          {t.title}
                        </h3>
                        {mounted && t.last_updated && (
                          <span className="text-xs flex-shrink-0" style={{ color: 'var(--color-ink-light)' }} suppressHydrationWarning>
                            {formatTimeAgo(t.last_updated)}
                          </span>
                        )}
                      </article>
                    );
                  })}
                </div>
              )}
            </>
          )}
        </section>

        {/* ═══ Mobile stats (only visible on mobile) ═══ */}
        <section className="lg:hidden border-y py-10 container mx-auto px-6" style={{ borderColor: 'var(--color-rule)' }}>
          <div className="grid grid-cols-2 gap-6 max-w-sm mx-auto">
            {stats.map((s, i) => (
              <StatCell key={s.label} target={s.target} suffix={s.suffix} label={s.label} delay={i} />
            ))}
          </div>
        </section>

        {/* ═══ How It Works — asymmetric editorial layout ═══ */}
        <section className="container mx-auto px-6 py-16 md:py-20">
          <div className="reveal mb-10">
            <hr className="rule-thick" />
            <p className="text-xs uppercase tracking-[0.25em] mt-4" style={{ color: 'var(--color-ink-light)' }}>
              How Gaze works
            </p>
          </div>

          <div className="grid md:grid-cols-12 gap-y-10 md:gap-x-12">
            {/* Left: large editorial text */}
            <div className="md:col-span-5 reveal">
              <p className="font-serif leading-snug" style={{ color: 'var(--color-ink)', fontSize: 'clamp(1.25rem, 2.5vw, 1.75rem)', letterSpacing: '-0.01em' }}>
                We aggregate global coverage, break it into perspectives, then invite the
                people <em>actually involved</em> to weigh in.
              </p>
            </div>

            {/* Right: three steps — stacked, separated by rules */}
            <div className="md:col-span-6 md:col-start-7">
              <div className="reveal reveal-delay-1 py-5 border-b" style={{ borderColor: 'var(--color-rule)' }}>
                <h3 className="font-serif font-semibold mb-1.5" style={{ color: 'var(--color-ink)' }}>Aggregate &amp; Analyze</h3>
                <p className="text-sm leading-relaxed" style={{ color: 'var(--color-ink-light)' }}>
                  We pull from 200+ sources across 50+ countries, then cluster articles into events
                  and identify the stakeholders affected.
                </p>
              </div>
              <div className="reveal reveal-delay-2 py-5 border-b" style={{ borderColor: 'var(--color-rule)' }}>
                <h3 className="font-serif font-semibold mb-1.5" style={{ color: 'var(--color-ink)' }}>Present Every Angle</h3>
                <p className="text-sm leading-relaxed" style={{ color: 'var(--color-ink-light)' }}>
                  Each event page shows coverage side by side — how different regions, outlets, and
                  political leanings frame the same story.
                </p>
              </div>
              <div className="reveal reveal-delay-3 py-5">
                <h3 className="font-serif font-semibold mb-1.5" style={{ color: 'var(--color-ink)' }}>Verified Discussion</h3>
                <p className="text-sm leading-relaxed" style={{ color: 'var(--color-ink-light)' }}>
                  Stakeholders verify their identity and join the conversation as who they really are —
                  not anonymous handles.
                </p>
              </div>
            </div>
          </div>
        </section>

        {/* ═══ Identity Verification — the core differentiator ═══ */}
        <section className="relative overflow-hidden grain" style={{ background: 'var(--color-warm-dark)' }}>
          <div className="container mx-auto px-6 py-16 md:py-20">
            <div className="grid md:grid-cols-12 gap-8 items-start">
              {/* Left: headline */}
              <div className="md:col-span-5 reveal">
                <p className="text-xs uppercase tracking-[0.25em] mb-4" style={{ color: 'var(--color-accent)' }}>
                  What makes us different
                </p>
                <h2 className="font-serif text-white font-bold leading-tight" style={{ fontSize: 'clamp(1.75rem, 3.5vw, 2.5rem)', letterSpacing: '-0.02em' }}>
                  Speak as<br />Who You Are.
                </h2>
              </div>

              {/* Right: explanation */}
              <div className="md:col-span-6 md:col-start-7 reveal reveal-delay-1">
                <p className="text-neutral-400 leading-relaxed mb-6">
                  Anonymous comment sections breed noise. Gaze takes a different approach:
                  when you join a discussion, you declare your relationship to the event —
                  as a local resident, industry professional, policy researcher, or anyone
                  with a genuine stake in the story.
                </p>
                <div className="space-y-4">
                  <div className="flex items-start gap-3">
                    <span className="flex-shrink-0 mt-0.5 text-base leading-none" style={{ color: 'var(--color-accent)' }}>&#9670;</span>
                    <div>
                      <p className="text-white text-sm font-medium mb-0.5">Verified stakeholder identity</p>
                      <p className="text-neutral-500 text-xs leading-relaxed">
                        Declare and verify who you are relative to the event — not just a username, but a real perspective.
                      </p>
                    </div>
                  </div>
                  <div className="flex items-start gap-3">
                    <span className="flex-shrink-0 mt-0.5 text-base leading-none" style={{ color: 'var(--color-accent)' }}>&#9671;</span>
                    <div>
                      <p className="text-white text-sm font-medium mb-0.5">Perspectives you can trust</p>
                      <p className="text-neutral-500 text-xs leading-relaxed">
                        Every comment carries context: who is speaking, and why they have a stake. Readers judge accordingly.
                      </p>
                    </div>
                  </div>
                  <div className="flex items-start gap-3">
                    <span className="flex-shrink-0 mt-0.5 text-base leading-none" style={{ color: 'var(--color-accent)' }}>&#9674;</span>
                    <div>
                      <p className="text-white text-sm font-medium mb-0.5">Discussion, not debate</p>
                      <p className="text-neutral-500 text-xs leading-relaxed">
                        The goal is understanding, not winning. When stakeholders speak openly, conversations become richer.
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div className="absolute bottom-0 left-0 right-0 h-px" style={{ background: 'linear-gradient(90deg, transparent, var(--color-accent), transparent)' }} />
        </section>

        {/* ═══ Closing — vision statement ═══ */}
        <section className="relative overflow-hidden" style={{ background: '#F0ECE3' }}>
          <div className="container mx-auto px-6 py-16 md:py-20">
            <div className="max-w-2xl mx-auto text-center">
              <p className="reveal font-serif leading-snug" style={{ color: 'var(--color-ink)', fontSize: 'clamp(1.25rem, 2.5vw, 1.75rem)' }}>
                The world doesn&rsquo;t need another news aggregator.
                It needs a place where the people behind the headlines
                can finally be heard.
              </p>
              <div className="reveal reveal-delay-1 flex items-center justify-center gap-3 mt-6">
                <div className="w-8 h-px" style={{ background: 'var(--color-accent)', opacity: 0.4 }} />
                <span className="text-xs uppercase tracking-[0.2em]" style={{ color: 'var(--color-ink-light)' }}>That&rsquo;s Gaze</span>
                <div className="w-8 h-px" style={{ background: 'var(--color-accent)', opacity: 0.4 }} />
              </div>
            </div>
          </div>
        </section>

        {/* ═══ Footer ═══ */}
        <footer className="relative grain" style={{ background: 'var(--color-warm-dark)' }}>
          <div className="container mx-auto px-6 py-8">
            <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
              <div className="flex items-center gap-6">
                <span className="font-serif text-xl font-bold text-white">Gaze</span>
                <nav className="flex items-center gap-4 text-sm text-neutral-500">
                  <a href="/stories" className="hover:text-white transition-colors">Stories</a>
                  <span className="text-neutral-700">·</span>
                  <a href="/feedback" className="hover:text-white transition-colors">Feedback</a>
                  <span className="text-neutral-700">·</span>
                  <a href="/auth/login" className="hover:text-white transition-colors">Sign In</a>
                </nav>
              </div>
              <p className="font-serif italic text-sm text-neutral-600">We Gaze Upon the Same Moon</p>
            </div>
            <div className="mt-6 pt-4 border-t border-white/[0.06] text-xs text-neutral-700">
              <p>&copy; 2026 Gaze</p>
            </div>
          </div>
        </footer>
      </main>
    </div>
  );
}
