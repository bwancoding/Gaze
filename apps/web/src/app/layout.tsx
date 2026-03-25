import type { Metadata, Viewport } from 'next'
import { Inter, Dancing_Script } from 'next/font/google'
import '../styles/globals.css'
import AnalyticsTracker from '../components/AnalyticsTracker'

const inter = Inter({
  subsets: ['latin'],
  display: 'swap',
})
const dancingScript = Dancing_Script({
  subsets: ['latin'],
  variable: '--font-dancing',
  display: 'swap',
})

export const viewport: Viewport = {
  themeColor: '#1c1917',
  width: 'device-width',
  initialScale: 1,
  maximumScale: 5,
}

export const metadata: Metadata = {
  title: {
    default: 'WRHITW - What\'s Really Happening In The World',
    template: '%s',
  },
  description: 'Multi-perspective news aggregation platform. See every side of the story through diverse global voices.',
  keywords: ['news', 'global news', 'multi-perspective', 'world events', 'stakeholder analysis', 'news aggregation'],
  authors: [{ name: 'WRHITW' }],
  manifest: '/manifest.json',
  appleWebApp: {
    capable: true,
    statusBarStyle: 'black-translucent',
    title: 'WRHITW',
  },
  openGraph: {
    title: 'WRHITW - What\'s Really Happening In The World',
    description: 'Multi-perspective news aggregation platform. See every side of the story through diverse global voices.',
    type: 'website',
    siteName: 'WRHITW',
    locale: 'en_US',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'WRHITW - What\'s Really Happening In The World',
    description: 'Multi-perspective news aggregation platform.',
  },
  metadataBase: new URL(process.env.NEXT_PUBLIC_SITE_URL || 'https://wrhitw.com'),
  robots: {
    index: true,
    follow: true,
  },
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <head>
        <link rel="apple-touch-icon" href="/icons/icon-192.png" />
      </head>
      <body className={`${inter.className} ${dancingScript.variable}`}>
        <AnalyticsTracker />
        {children}
      </body>
    </html>
  )
}
