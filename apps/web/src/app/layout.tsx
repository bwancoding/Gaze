import type { Metadata } from 'next'
import { Inter, Dancing_Script } from 'next/font/google'
import '../styles/globals.css'

const inter = Inter({ subsets: ['latin'] })
const dancingScript = Dancing_Script({ subsets: ['latin'], variable: '--font-dancing' })

export const metadata: Metadata = {
  title: 'WRHITW - What\'s Really Happening In The World',
  description: 'Multi-perspective news aggregation platform. See every side of the story through diverse global voices.',
  openGraph: {
    title: 'WRHITW - What\'s Really Happening In The World',
    description: 'Multi-perspective news aggregation platform. See every side of the story through diverse global voices.',
    type: 'website',
    siteName: 'WRHITW',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'WRHITW - What\'s Really Happening In The World',
    description: 'Multi-perspective news aggregation platform.',
  },
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={`${inter.className} ${dancingScript.variable}`}>{children}</body>
    </html>
  )
}
