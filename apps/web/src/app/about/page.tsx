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
              A platform that helps you understand global events through
              multiple stakeholder perspectives, powered by AI analysis
              and community discussion.
            </p>
          </div>

          {/* How it works */}
          <div className="space-y-12">
            <section>
              <h2 className="text-2xl font-bold text-stone-900 mb-4">How It Works</h2>
              <div className="grid md:grid-cols-3 gap-6">
                <div className="bg-white rounded-xl border border-stone-200 p-6">
                  <div className="text-3xl mb-3">{'\u{1F4F0}'}</div>
                  <h3 className="font-semibold text-stone-900 mb-2">Aggregate</h3>
                  <p className="text-stone-600 text-sm">
                    We continuously monitor hundreds of news sources worldwide,
                    clustering related articles into unified events.
                  </p>
                </div>
                <div className="bg-white rounded-xl border border-stone-200 p-6">
                  <div className="text-3xl mb-3">{'\u{1F916}'}</div>
                  <h3 className="font-semibold text-stone-900 mb-2">Analyze</h3>
                  <p className="text-stone-600 text-sm">
                    AI identifies key stakeholders for each event and generates
                    deep analysis: background, cause chains, impact, and timelines.
                  </p>
                </div>
                <div className="bg-white rounded-xl border border-stone-200 p-6">
                  <div className="text-3xl mb-3">{'\u{1F4AC}'}</div>
                  <h3 className="font-semibold text-stone-900 mb-2">Discuss</h3>
                  <p className="text-stone-600 text-sm">
                    Community members create discussion threads, share perspectives,
                    and engage in informed debate about global events.
                  </p>
                </div>
              </div>
            </section>

            <section>
              <h2 className="text-2xl font-bold text-stone-900 mb-4">Why Stakeholder Perspectives?</h2>
              <div className="bg-white rounded-xl border border-stone-200 p-6">
                <p className="text-stone-700 leading-relaxed mb-4">
                  Traditional news often presents events from a single editorial viewpoint.
                  We believe every major event affects multiple groups differently &mdash;
                  governments, civilians, businesses, activists &mdash; and each has a valid story to tell.
                </p>
                <p className="text-stone-700 leading-relaxed">
                  By identifying and presenting these stakeholder perspectives side by side,
                  we help you build a more complete understanding of complex global events,
                  rather than seeing just one angle.
                </p>
              </div>
            </section>

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
                  adding credibility to your contributions in the community.
                </p>
              </div>
            </section>

            <section className="text-center py-8">
              <p className="text-stone-500 text-sm">
                WRHITW is an open platform for informed global discourse.
              </p>
              <p className="text-stone-400 text-xs mt-2">
                &copy; 2026 WRHITW &middot; See the Full Story
              </p>
            </section>
          </div>
        </div>
      </main>
    </div>
  );
}
