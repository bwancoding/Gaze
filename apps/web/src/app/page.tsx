'use client';

import React from 'react';
import { useRouter } from 'next/navigation';
import Header from '../components/Header';
import { isAuthenticated } from '../lib/auth';

export default function Home() {
  const router = useRouter();
  const [loggedIn, setLoggedIn] = React.useState(false);

  React.useEffect(() => {
    setLoggedIn(isAuthenticated());
  }, []);

  return (
    <div className="min-h-screen bg-neutral-50">
      <Header />

      <main>
        {/* Hero — editorial, typography-driven */}
        <section className="relative bg-neutral-900 text-white overflow-hidden">
          {/* Subtle texture overlay */}
          <div className="absolute inset-0 opacity-[0.03]" style={{
            backgroundImage: `url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='1'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")`,
          }} />
          <div className="relative container mx-auto px-6 py-20 md:py-28">
            <div className="max-w-3xl">
              <p className="text-sm uppercase tracking-[0.2em] text-neutral-400 mb-6">Global News Platform</p>
              <h1 className="font-serif text-display text-white mb-6" style={{ fontFamily: 'var(--font-dancing)' }}>
                We Gaze Upon the Same Moon.
              </h1>
              <p className="text-body-lg text-neutral-300 mb-10 max-w-xl leading-relaxed">
                Every global event carries multiple perspectives.
                We bring them together so you can see the full picture.
              </p>
              <div className="flex items-center gap-4">
                <button
                  onClick={() => router.push('/trending')}
                  className="bg-white text-neutral-900 px-6 py-2.5 rounded-md font-medium text-sm hover:bg-neutral-100 transition-colors"
                >
                  Explore Trending
                </button>
                {!loggedIn && (
                  <button
                    onClick={() => router.push('/auth/login')}
                    className="text-sm text-neutral-300 hover:text-white transition-colors underline underline-offset-4 decoration-neutral-600 hover:decoration-white"
                  >
                    Join the Conversation
                  </button>
                )}
              </div>
            </div>
          </div>
          {/* Bottom rule */}
          <div className="absolute bottom-0 left-0 right-0 h-px bg-neutral-700" />
        </section>

        {/* How It Works — numbered steps with editorial feel */}
        <section className="container mx-auto px-6 py-20">
          <div className="max-w-4xl mx-auto">
            <p className="text-xs uppercase tracking-[0.2em] text-neutral-400 mb-2">How It Works</p>
            <h2 className="font-serif text-headline text-neutral-900 mb-12">From noise to clarity, in three steps.</h2>
            <div className="grid md:grid-cols-3 gap-6 md:gap-10">
              <div className="relative border-t-2 border-neutral-900 pt-6">
                <span className="font-serif text-4xl font-light text-neutral-200 absolute -top-1 right-0 leading-none select-none">01</span>
                <h3 className="font-serif text-lg font-semibold text-neutral-900 mb-3">Aggregate</h3>
                <p className="text-sm text-neutral-600 leading-relaxed">
                  We monitor hundreds of news sources worldwide and cluster
                  related articles into unified events — comprehensive
                  coverage, not a single outlet&apos;s take.
                </p>
              </div>
              <div className="relative border-t-2 border-neutral-900 pt-6">
                <span className="font-serif text-4xl font-light text-neutral-200 absolute -top-1 right-0 leading-none select-none">02</span>
                <h3 className="font-serif text-lg font-semibold text-neutral-900 mb-3">Break Down</h3>
                <p className="text-sm text-neutral-600 leading-relaxed">
                  Each event is analyzed for background, root causes, impact,
                  and timeline. Stakeholder perspectives are identified and
                  presented side by side.
                </p>
              </div>
              <div className="relative border-t-2 border-neutral-900 pt-6">
                <span className="font-serif text-4xl font-light text-neutral-200 absolute -top-1 right-0 leading-none select-none">03</span>
                <h3 className="font-serif text-lg font-semibold text-neutral-900 mb-3">Discuss</h3>
                <p className="text-sm text-neutral-600 leading-relaxed">
                  Verified stakeholders claim their identity and share
                  first-hand perspectives. The broader community joins
                  the conversation directly.
                </p>
              </div>
            </div>
          </div>
        </section>

        {/* Mission — pull-quote style */}
        <section className="bg-neutral-100 border-y border-neutral-200">
          <div className="container mx-auto px-6 py-20">
            <div className="max-w-3xl mx-auto">
              <blockquote className="font-serif text-title text-neutral-900 leading-snug mb-6 border-l-4 border-accent pl-6">
                Most news presents one editorial angle. But every major event affects
                different groups in different ways.
              </blockquote>
              <p className="text-neutral-600 leading-relaxed max-w-2xl">
                Gaze aggregates coverage from hundreds of sources, identifies the
                stakeholders involved, and presents their perspectives side by side.
                Then we let the people affected speak for themselves.
              </p>
            </div>
          </div>
        </section>

        {/* Two-column feature blocks */}
        <section className="container mx-auto px-6 py-20">
          <div className="max-w-4xl mx-auto space-y-16">
            {/* Multiple Perspectives */}
            <div className="grid md:grid-cols-5 gap-8 items-start">
              <div className="md:col-span-2">
                <h2 className="font-serif text-title text-neutral-900 mb-2">Why Multiple Perspectives?</h2>
                <div className="w-12 h-0.5 bg-accent" />
              </div>
              <div className="md:col-span-3 space-y-4 text-neutral-600 leading-relaxed text-sm">
                <p>
                  A military conflict is experienced very differently by a soldier, a refugee,
                  and a diplomat. A policy change carries different weight for those who shaped it
                  and those who live with the consequences.
                </p>
                <p>
                  By presenting these perspectives side by side, we give you the context
                  to form your own understanding rather than adopting a single narrative.
                </p>
              </div>
            </div>

            <hr className="rule" />

            {/* Speak as Who You Are */}
            <div className="grid md:grid-cols-5 gap-8 items-start">
              <div className="md:col-span-2">
                <h2 className="font-serif text-title text-neutral-900 mb-2">Speak as Who You Are</h2>
                <div className="w-12 h-0.5 bg-accent" />
              </div>
              <div className="md:col-span-3 space-y-4 text-neutral-600 leading-relaxed text-sm">
                <p>
                  On Gaze, you can claim your connection to an event. A healthcare worker
                  commenting on medical policy, or a local resident discussing a disaster
                  in their community, brings context that outside observers cannot.
                </p>
                <p>
                  Declare your stakeholder identity with one click, or submit documentation
                  for a verified badge. Readers can distinguish first-hand accounts
                  from general commentary.
                </p>
              </div>
            </div>
          </div>
        </section>

        {/* Philosophy block — dark */}
        <section className="bg-neutral-900 text-white py-20">
          <div className="container mx-auto px-6">
            <div className="max-w-3xl mx-auto text-center">
              <p className="text-xs uppercase tracking-[0.2em] text-neutral-500 mb-4">Our Philosophy</p>
              <h2 className="font-serif text-headline mb-8">We Share This World</h2>
              <p className="text-neutral-400 leading-relaxed mb-4 text-lg">
                The defining events of our time cross every border. Understanding
                them requires hearing from the people closest to them, not just the
                loudest commentators.
              </p>
              <p className="text-neutral-500 leading-relaxed mb-10">
                Gaze exists to make that possible: comprehensive coverage,
                transparent analysis, and open conversation. No spin, no paywall,
                no algorithm filtering what matters.
              </p>
              <button
                onClick={() => router.push('/trending')}
                className="border border-white/30 text-white px-8 py-2.5 rounded-md text-sm font-medium hover:bg-white hover:text-neutral-900 transition-colors"
              >
                See What&apos;s Really Happening
              </button>
            </div>
          </div>
        </section>

        {/* Footer */}
        <footer className="bg-neutral-900 text-neutral-400 border-t border-neutral-800">
          <div className="container mx-auto px-6 py-12">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
              {/* Brand */}
              <div className="col-span-2 md:col-span-1">
                <span className="font-serif text-xl font-bold text-white">Gaze</span>
                <p className="text-xs text-neutral-500 mt-1 leading-relaxed">
                  See the Full Story
                </p>
              </div>

              {/* Explore */}
              <div>
                <p className="text-xs uppercase tracking-wider text-neutral-500 mb-3">Explore</p>
                <nav className="space-y-2 text-sm">
                  <a href="/trending" className="block hover:text-white transition-colors">Trending</a>
                  <a href="/stories" className="block hover:text-white transition-colors">Stories</a>
                </nav>
              </div>

              {/* Platform */}
              <div>
                <p className="text-xs uppercase tracking-wider text-neutral-500 mb-3">Platform</p>
                <nav className="space-y-2 text-sm">
                  <a href="/feedback" className="block hover:text-white transition-colors">Feedback</a>
                  <a href="/auth/login" className="block hover:text-white transition-colors">Sign In</a>
                </nav>
              </div>
            </div>

            <div className="mt-10 pt-6 border-t border-neutral-800 flex flex-col md:flex-row justify-between items-center text-xs text-neutral-600">
              <p>&copy; 2026 Gaze</p>
              <p className="mt-2 md:mt-0 font-serif italic">We Gaze Upon the Same Moon</p>
            </div>
          </div>
        </footer>
      </main>
    </div>
  );
}
