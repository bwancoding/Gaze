'use client';

import React from 'react';
import Header from '../../components/Header';

export default function AboutPage() {
  return (
    <div className="min-h-screen bg-stone-50">
      <Header />
      <main className="container mx-auto px-6 py-12">
        <div className="max-w-3xl mx-auto">
          {/* Hero */}
          <div className="text-center mb-16">
            <div className="w-20 h-20 bg-gradient-to-br from-amber-400 to-orange-500 rounded-2xl flex items-center justify-center mx-auto mb-6 shadow-lg">
              <span className="text-white font-bold text-3xl">W</span>
            </div>
            <h1 className="text-4xl font-bold text-stone-900 mb-4">
              What&apos;s Really Happening In The World
            </h1>
            <p className="text-lg text-stone-600 leading-relaxed">
              One World, Many Voices, One Conversation
            </p>
          </div>

          {/* Mission */}
          <div className="space-y-12">
            <section>
              <div className="bg-gradient-to-br from-amber-50 to-orange-50 rounded-2xl border border-amber-200 p-8 text-center">
                <h2 className="text-2xl font-bold text-stone-900 mb-4">Our Mission</h2>
                <p className="text-stone-700 leading-relaxed text-lg mb-4">
                  We believe that every person on this planet is a steward of our shared world.
                  Beneath the noise of headlines and the fog of bias, there are real stories &mdash;
                  told by real people, from every corner of the earth.
                </p>
                <p className="text-stone-700 leading-relaxed text-lg">
                  WRHITW exists to bring those voices together: to help humanity understand
                  one another, engage in peaceful dialogue, and continue to grow as one family
                  under the vast sky we all share.
                </p>
              </div>
            </section>

            {/* How it works */}
            <section>
              <h2 className="text-2xl font-bold text-stone-900 mb-4">How It Works</h2>
              <div className="grid md:grid-cols-3 gap-6">
                <div className="bg-white rounded-xl border border-stone-200 p-6">
                  <div className="text-3xl mb-3">{'\u{1F4F0}'}</div>
                  <h3 className="font-semibold text-stone-900 mb-2">Aggregate</h3>
                  <p className="text-stone-600 text-sm">
                    We continuously monitor hundreds of news sources worldwide,
                    clustering related articles into unified events so you see the full picture,
                    not just one outlet&apos;s take.
                  </p>
                </div>
                <div className="bg-white rounded-xl border border-stone-200 p-6">
                  <div className="text-3xl mb-3">{'\u{1F916}'}</div>
                  <h3 className="font-semibold text-stone-900 mb-2">Analyze</h3>
                  <p className="text-stone-600 text-sm">
                    AI identifies the stakeholders affected by each event and generates
                    deep analysis: background, cause chains, impact, timelines, and
                    multiple perspectives side by side.
                  </p>
                </div>
                <div className="bg-white rounded-xl border border-stone-200 p-6">
                  <div className="text-3xl mb-3">{'\u{1F91D}'}</div>
                  <h3 className="font-semibold text-stone-900 mb-2">Dialogue</h3>
                  <p className="text-stone-600 text-sm">
                    Community members share perspectives, listen to each other,
                    and engage in respectful conversation &mdash; because understanding
                    starts with hearing another voice.
                  </p>
                </div>
              </div>
            </section>

            {/* Why Multiple Perspectives */}
            <section>
              <h2 className="text-2xl font-bold text-stone-900 mb-4">Why Multiple Perspectives?</h2>
              <div className="bg-white rounded-xl border border-stone-200 p-6">
                <p className="text-stone-700 leading-relaxed mb-4">
                  Traditional news often presents events from a single editorial viewpoint.
                  But every major event affects many groups differently &mdash;
                  governments, civilians, businesses, communities, future generations &mdash;
                  and each has a story worth hearing.
                </p>
                <p className="text-stone-700 leading-relaxed">
                  By presenting these stakeholder perspectives side by side, we don&apos;t tell you
                  what to think. We give you the information to think for yourself, with empathy
                  for all those involved.
                </p>
              </div>
            </section>

            {/* Personas */}
            <section>
              <h2 className="text-2xl font-bold text-stone-900 mb-4">Personas</h2>
              <div className="bg-white rounded-xl border border-stone-200 p-6">
                <p className="text-stone-700 leading-relaxed mb-4">
                  On WRHITW, you participate through <strong>personas</strong> &mdash;
                  identities that represent your background, expertise, or perspective.
                  A climate scientist, a local farmer, a policy analyst &mdash;
                  each persona brings unique context to discussions.
                </p>
                <p className="text-stone-700 leading-relaxed">
                  Personas can be verified to indicate authentic stakeholder representation,
                  adding credibility and trust to the community conversation.
                </p>
              </div>
            </section>

            {/* Philosophy */}
            <section>
              <div className="bg-stone-900 rounded-2xl p-8 text-center">
                <h2 className="text-2xl font-bold text-white mb-4">We Share This World</h2>
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
            </section>

            <section className="text-center py-8">
              <p className="text-stone-500 text-sm">
                WRHITW &mdash; One World, Many Voices, One Conversation
              </p>
              <p className="text-stone-400 text-xs mt-2">
                &copy; 2026 WRHITW
              </p>
            </section>
          </div>
        </div>
      </main>
    </div>
  );
}
