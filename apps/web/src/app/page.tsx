'use client';

import React from 'react';
import { useRouter } from 'next/navigation';
import Header from '../components/Header';

// Icons
const Icons = {
  BookOpen: () => (
    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
    </svg>
  ),
ArrowRight: () => (
    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 8l4 4m0 0l-4 4m4-4H3" />
    </svg>
  ),
};


export default function Home() {
  const router = useRouter();

  return (
    <div className="min-h-screen bg-stone-900">
      <Header />

      <main>
        {/* Hero + About share same outer background */}
        <div className="relative overflow-hidden">
          {/* Outer background image - spans hero + about sections */}
          <div
            className="absolute inset-0 bg-cover bg-center bg-no-repeat scale-110 blur-md"
            style={{ backgroundImage: `url('/hero-bg.png')` }}
          ></div>
          {/* Dark overlay on outer background */}
          <div className="absolute inset-0 bg-black/70"></div>

          {/* Hero card */}
          <section className="relative z-10 text-white pt-6 pb-8">
            <div className="mx-auto flex flex-col items-center">
              {/* Card with feathered mask */}
              <div
                className="relative w-[70%] rounded-3xl overflow-hidden"
                style={{
                  maskImage: 'radial-gradient(ellipse 85% 80% at center, black 50%, transparent 100%)',
                  WebkitMaskImage: 'radial-gradient(ellipse 85% 80% at center, black 50%, transparent 100%)',
                }}
              >
                {/* Card background image */}
                <div
                  className="absolute inset-0 bg-cover bg-center bg-no-repeat"
                  style={{ backgroundImage: `url('/hero-bg.png')` }}
                ></div>
                {/* Dark overlay for text readability */}
                <div className="absolute inset-0 bg-black/25"></div>

                {/* Content */}
                <div className="relative z-10 py-14 px-8 text-center">
                  <h2 className="text-4xl md:text-5xl lg:text-6xl font-bold mb-6 leading-tight whitespace-nowrap" style={{ fontFamily: 'var(--font-dancing)' }}>
                    <span className="text-transparent bg-clip-text bg-gradient-to-r from-amber-200 via-orange-200 to-amber-200">
                      We Gaze Upon the Same Moon.
                    </span>
                  </h2>

                  <p className="text-base md:text-lg text-slate-300 mb-8 leading-relaxed max-w-xl mx-auto">
                    We see all of humanity as stewards of this world,
                    sailing together through the same vast cosmos.
                    Now, let us resolve what we face together — through peaceful dialogue.
                  </p>

                  <div className="flex flex-wrap justify-center gap-3 mb-8">
                    <div className="flex items-center space-x-2 bg-white/10 px-4 py-2 rounded-full backdrop-blur-sm border border-white/20">
                      <div className="w-2 h-2 bg-gradient-to-r from-blue-400 to-indigo-500 rounded-full"></div>
                      <span className="text-xs font-medium">AI Deep Analysis</span>
                    </div>
                    <div className="flex items-center space-x-2 bg-white/10 px-4 py-2 rounded-full backdrop-blur-sm border border-white/20">
                      <div className="w-2 h-2 bg-gradient-to-r from-amber-400 to-orange-500 rounded-full"></div>
                      <span className="text-xs font-medium">Stakeholder Perspectives</span>
                    </div>
                    <div className="flex items-center space-x-2 bg-white/10 px-4 py-2 rounded-full backdrop-blur-sm border border-white/20">
                      <div className="w-2 h-2 bg-gradient-to-r from-emerald-400 to-teal-500 rounded-full"></div>
                      <span className="text-xs font-medium">Community Discussion</span>
                    </div>
                  </div>

                  <div className="flex flex-wrap justify-center gap-4">
                    <button
                      onClick={() => router.push('/trending')}
                      className="inline-flex items-center space-x-2 bg-amber-500 text-stone-900 px-7 py-3 rounded-full font-semibold hover:bg-amber-400 transition-colors shadow-lg hover:shadow-xl text-sm"
                    >
                      <span>Explore Trending</span>
                      <Icons.ArrowRight />
                    </button>
                    <button
                      onClick={() => router.push('/auth/login')}
                      className="inline-flex items-center space-x-2 bg-white/10 text-white px-7 py-3 rounded-full font-semibold hover:bg-white/20 transition-colors backdrop-blur-sm border border-white/30 text-sm"
                    >
                      <span>Join to Communicate</span>
                      <Icons.ArrowRight />
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </section>

          {/* About - Mission (same outer background) */}
          <section id="about" className="relative z-10 text-stone-100 py-16">
          <div className="mx-auto px-[15%]">
            <div className="mx-auto text-center">
              <div className="w-20 h-20 bg-gradient-to-br from-amber-400 to-orange-500 rounded-2xl flex items-center justify-center mx-auto mb-6 shadow-lg">
                <span className="text-white font-bold text-3xl">W</span>
              </div>
              <h3 className="text-3xl md:text-4xl font-bold mb-4">
                What&apos;s Really Happening In The World
              </h3>
              <p className="text-lg text-stone-400 mb-8">
                One World, Many Voices, One Conversation
              </p>

              <div className="bg-stone-700/50 rounded-2xl border border-stone-600 p-8 text-center mb-12">
                <h4 className="text-2xl font-bold mb-4">Our Mission</h4>
                <p className="text-stone-300 leading-relaxed text-lg mb-4">
                  We believe that every person on this planet is a steward of our shared world.
                  Beneath the noise of headlines and the fog of bias, there are real stories &mdash;
                  told by real people, from every corner of the earth.
                </p>
                <p className="text-stone-300 leading-relaxed text-lg">
                  WRHITW exists to bring those voices together: to help humanity understand
                  one another, engage in peaceful dialogue, and continue to grow as one family
                  under the vast sky we all share.
                </p>
              </div>
            </div>
          </div>
        </section>

        {/* About - How It Works */}
        <section className="relative z-10 text-stone-100 py-16">
          <div className="mx-auto px-[15%]">
            <div className="mx-auto">
              <h3 className="text-2xl md:text-3xl font-bold mb-8 text-center">How It Works</h3>
              <div className="grid md:grid-cols-3 gap-6">
                <div className="bg-stone-800 rounded-xl border border-stone-700 p-6">
                  <div className="text-3xl mb-3">{'\u{1F4F0}'}</div>
                  <h4 className="font-semibold mb-2">Aggregate</h4>
                  <p className="text-stone-400 text-sm">
                    We continuously monitor hundreds of news sources worldwide,
                    clustering related articles into unified events so you see the full picture,
                    not just one outlet&apos;s take.
                  </p>
                </div>
                <div className="bg-stone-800 rounded-xl border border-stone-700 p-6">
                  <div className="text-3xl mb-3">{'\u{1F916}'}</div>
                  <h4 className="font-semibold mb-2">Analyze</h4>
                  <p className="text-stone-400 text-sm">
                    AI identifies the stakeholders affected by each event and generates
                    deep analysis: background, cause chains, impact, timelines, and
                    multiple perspectives side by side.
                  </p>
                </div>
                <div className="bg-stone-800 rounded-xl border border-stone-700 p-6">
                  <div className="text-3xl mb-3">{'\u{1F91D}'}</div>
                  <h4 className="font-semibold mb-2">Dialogue</h4>
                  <p className="text-stone-400 text-sm">
                    Community members share perspectives, listen to each other,
                    and engage in respectful conversation &mdash; because understanding
                    starts with hearing another voice.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* About - Why Multiple Perspectives + Personas */}
        <section className="relative z-10 text-stone-100 py-16">
          <div className="mx-auto px-[15%]">
            <div className="mx-auto space-y-12">
              <div>
                <h3 className="text-2xl md:text-3xl font-bold mb-4 text-center">Why Multiple Perspectives?</h3>
                <div className="bg-stone-700/50 rounded-xl border border-stone-600 p-6">
                  <p className="text-stone-300 leading-relaxed mb-4">
                    Traditional news often presents events from a single editorial viewpoint.
                    But every major event affects many groups differently &mdash;
                    governments, civilians, businesses, communities, future generations &mdash;
                    and each has a story worth hearing.
                  </p>
                  <p className="text-stone-300 leading-relaxed">
                    By presenting these stakeholder perspectives side by side, we don&apos;t tell you
                    what to think. We give you the information to think for yourself, with empathy
                    for all those involved.
                  </p>
                </div>
              </div>

              <div>
                <h3 className="text-2xl md:text-3xl font-bold mb-4 text-center">Personas</h3>
                <div className="bg-stone-700/50 rounded-xl border border-stone-600 p-6">
                  <p className="text-stone-300 leading-relaxed mb-4">
                    On WRHITW, you participate through <strong className="text-stone-100">personas</strong> &mdash;
                    identities that represent your background, expertise, or perspective.
                    A climate scientist, a local farmer, a policy analyst &mdash;
                    each persona brings unique context to discussions.
                  </p>
                  <p className="text-stone-300 leading-relaxed">
                    Personas can be verified to indicate authentic stakeholder representation,
                    adding credibility and trust to the community conversation.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* About - Philosophy */}
        <section className="relative z-10 text-stone-100 py-16">
          <div className="mx-auto px-[15%]">
            <div className="mx-auto">
              <div className="bg-gradient-to-br from-stone-800 to-stone-800/80 rounded-2xl border border-stone-700 p-8 text-center">
                <h3 className="text-2xl md:text-3xl font-bold mb-4">We Share This World</h3>
                <p className="text-stone-300 leading-relaxed mb-4">
                  We are all stewards of this planet. Regardless of where we were born,
                  what language we speak, or what we believe &mdash; we share the same sky,
                  the same earth, and the same future.
                </p>
                <p className="text-stone-300 leading-relaxed mb-4">
                  WRHITW is built on a simple conviction: that when people truly understand
                  each other&apos;s experiences, peaceful dialogue becomes possible &mdash;
                  and with dialogue comes progress.
                </p>
                <p className="text-amber-300 leading-relaxed font-medium">
                  Join us in building a world where every voice is heard,
                  every perspective is valued, and humanity moves forward together.
                </p>
              </div>
            </div>
          </div>
        </section>

        </div>
        {/* end of shared outer background wrapper */}

        {/* Footer */}
        <footer className="bg-stone-900 border-t border-stone-700 py-12">
          <div className="container mx-auto px-6">
            <div className="flex flex-col md:flex-row justify-between items-center">
              <div className="flex items-center space-x-3 mb-4 md:mb-0">
                <div className="w-10 h-10 bg-gradient-to-br from-amber-400 to-orange-500 rounded-lg flex items-center justify-center text-white shadow">
                  <Icons.BookOpen />
                </div>
                <div>
                  <p className="font-semibold text-stone-100">WRHITW</p>
                  <p className="text-xs text-stone-400">See the Full Story</p>
                </div>
              </div>

              <div className="flex items-center space-x-6 text-sm text-stone-400">
                <a href="/stories" className="hover:text-stone-200 transition-colors">Stories</a>
                <a href="#about" className="hover:text-stone-200 transition-colors">About</a>
                <a href="/feedback" className="hover:text-stone-200 transition-colors">Feedback</a>
              </div>
            </div>

            <div className="mt-8 pt-8 border-t border-stone-700 text-center text-sm text-stone-500">
              <p>&copy; 2026 WRHITW &middot; We Gaze Upon the Same Moon</p>
            </div>
          </div>
        </footer>
      </main>
    </div>
  );
}
