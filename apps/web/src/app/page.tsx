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

        {/* Three pillars — clean, no gradients */}
        <section className="container mx-auto px-6 py-16">
          <div className="max-w-4xl mx-auto">
            <div className="grid md:grid-cols-3 gap-8 md:gap-12">
              <div>
                <div className="w-10 h-10 border-2 border-neutral-900 rounded-lg flex items-center justify-center mb-4">
                  <svg className="w-5 h-5 text-neutral-900" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1m2 13a2 2 0 01-2-2V7m2 13a2 2 0 002-2V9a2 2 0 00-2-2h-2m-4-3H9M7 16h6M7 8h6v4H7V8z" />
                  </svg>
                </div>
                <h3 className="font-serif text-lg font-semibold text-neutral-900 mb-2">Aggregate</h3>
                <p className="text-sm text-neutral-600 leading-relaxed">
                  We monitor hundreds of news sources worldwide and cluster
                  related articles into unified events, giving you comprehensive
                  coverage rather than a single outlet&apos;s take.
                </p>
              </div>
              <div>
                <div className="w-10 h-10 border-2 border-neutral-900 rounded-lg flex items-center justify-center mb-4">
                  <svg className="w-5 h-5 text-neutral-900" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                  </svg>
                </div>
                <h3 className="font-serif text-lg font-semibold text-neutral-900 mb-2">Break Down</h3>
                <p className="text-sm text-neutral-600 leading-relaxed">
                  Each event is analyzed for background, root causes, impact,
                  and timeline. Stakeholder perspectives are identified and
                  presented side by side for comparison.
                </p>
              </div>
              <div>
                <div className="w-10 h-10 border-2 border-neutral-900 rounded-lg flex items-center justify-center mb-4">
                  <svg className="w-5 h-5 text-neutral-900" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M17 8h2a2 2 0 012 2v6a2 2 0 01-2 2h-2v4l-4-4H9a1.994 1.994 0 01-1.414-.586m0 0L11 14h4a2 2 0 002-2V6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2v4l.586-.586z" />
                  </svg>
                </div>
                <h3 className="font-serif text-lg font-semibold text-neutral-900 mb-2">Discuss</h3>
                <p className="text-sm text-neutral-600 leading-relaxed">
                  Verified stakeholders can claim their identity and share
                  first-hand perspectives. The broader community can join
                  the conversation, ask questions, and engage directly.
                </p>
              </div>
            </div>
          </div>
        </section>

        <hr className="rule-thick mx-6 md:mx-auto max-w-4xl" />

        {/* Mission */}
        <section className="container mx-auto px-6 py-16">
          <div className="max-w-2xl mx-auto">
            <h2 className="font-serif text-headline text-neutral-900 mb-6 text-center">Our Mission</h2>
            <div className="space-y-4 text-neutral-700 leading-relaxed">
              <p>
                Most news presents one editorial angle. But every major event affects
                different groups in different ways. A trade policy that benefits one
                industry may displace workers in another.
              </p>
              <p>
                Gaze aggregates coverage from hundreds of sources, identifies the
                stakeholders involved, and presents their perspectives side by side.
                Then we let the people affected speak for themselves.
              </p>
            </div>
          </div>
        </section>

        <hr className="rule mx-6 md:mx-auto max-w-4xl" />

        {/* Why Multiple Perspectives */}
        <section className="container mx-auto px-6 py-16">
          <div className="max-w-2xl mx-auto">
            <h2 className="font-serif text-title text-neutral-900 mb-6">Why Multiple Perspectives?</h2>
            <div className="space-y-4 text-neutral-700 leading-relaxed text-sm">
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
        </section>

        <hr className="rule mx-6 md:mx-auto max-w-4xl" />

        {/* Speak as Who You Are */}
        <section className="container mx-auto px-6 py-16">
          <div className="max-w-2xl mx-auto">
            <h2 className="font-serif text-title text-neutral-900 mb-6">Speak as Who You Are</h2>
            <div className="space-y-4 text-neutral-700 leading-relaxed text-sm">
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
        </section>

        {/* Philosophy block — dark */}
        <section className="bg-neutral-900 text-white py-16">
          <div className="container mx-auto px-6">
            <div className="max-w-2xl mx-auto text-center">
              <h2 className="font-serif text-title mb-6">We Share This World</h2>
              <p className="text-neutral-400 leading-relaxed mb-4">
                The defining events of our time cross every border. Understanding
                them requires hearing from the people closest to them, not just the
                loudest commentators.
              </p>
              <p className="text-neutral-400 leading-relaxed mb-6">
                Gaze exists to make that possible: comprehensive coverage,
                transparent analysis, and open conversation. No spin, no paywall,
                no algorithm filtering what matters.
              </p>
              <p className="text-accent-light font-medium text-sm uppercase tracking-wider">
                See what&apos;s really happening.
              </p>
            </div>
          </div>
        </section>

        {/* Footer */}
        <footer className="border-t border-neutral-200 py-10">
          <div className="container mx-auto px-6">
            <div className="flex flex-col md:flex-row justify-between items-center">
              <div className="flex items-center space-x-2 mb-4 md:mb-0">
                <span className="font-serif text-lg font-bold text-neutral-900">Gaze</span>
                <span className="text-xs text-neutral-400">See the Full Story</span>
              </div>

              <div className="flex items-center space-x-6 text-sm text-neutral-500">
                <a href="/stories" className="hover:text-neutral-900 transition-colors">Stories</a>
                <a href="#about" className="hover:text-neutral-900 transition-colors">About</a>
                <a href="/feedback" className="hover:text-neutral-900 transition-colors">Feedback</a>
              </div>
            </div>

            <div className="mt-8 pt-6 border-t border-neutral-200 text-center text-xs text-neutral-400">
              <p>&copy; 2026 Gaze &middot; We Gaze Upon the Same Moon</p>
            </div>
          </div>
        </footer>
      </main>
    </div>
  );
}
