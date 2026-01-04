import type { Metadata } from 'next'
import { Inter, Noto_Sans_JP } from 'next/font/google'
import './globals.css'
import { Providers } from './providers'

const inter = Inter({
  subsets: ['latin'],
  variable: '--font-inter',
})

const notoSansJP = Noto_Sans_JP({
  subsets: ['latin'],
  variable: '--font-noto-sans-jp',
  weight: ['400', '500', '600', '700'],
})

export const metadata: Metadata = {
  title: 'UNS Rirekisho Pro | 人材派遣管理システム',
  description: 'Human Resource Dispatch Management System for Universal Kikaku Co., Ltd.',
  keywords: ['HR', 'dispatch', 'rirekisho', 'employee management', 'Japan'],
  authors: [{ name: 'UNS Kikaku' }],
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="ja" suppressHydrationWarning>
      <body className={`${inter.variable} ${notoSansJP.variable} font-sans antialiased`}>
        <Providers>{children}</Providers>
      </body>
    </html>
  )
}
