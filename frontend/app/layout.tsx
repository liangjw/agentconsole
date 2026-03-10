import './globals.css'
import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'AgentConsole - 智能代理系统',
  description: '基于OpenSandbox的智能代理系统',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="zh">
      <body>{children}</body>
    </html>
  )
}
