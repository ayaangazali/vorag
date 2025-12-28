import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'Vorag - Voice RAG Assistant',
  description: 'Voice-powered RAG assistant for website content',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className="antialiased">
        {children}
      </body>
    </html>
  )
}
