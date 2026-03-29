import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'HyperTrace - Trading Signal Dashboard',
  description: 'Real-time trading signals and portfolio allocation using HyperLiquid data',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}
