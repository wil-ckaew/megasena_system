import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import Link from 'next/link'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'Mega-Sena System',
  description: 'Sistema inteligente para análise e geração de jogos da Mega-Sena',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="pt-BR">
      <body className={inter.className}>
        <nav style={navStyles}>
          <Link href="/" style={navLinkStyles}>🏠 Home</Link>
          <Link href="/bolao" style={navLinkStyles}>🎯 Bolão</Link>
          <Link href="/chatbot" style={navLinkStyles}>🤖 ChatBot</Link>
        </nav>
        <main>
          {children}
        </main>
      </body>
    </html>
  )
}

const navStyles = {
  backgroundColor: '#1a237e',
  padding: '15px 30px',
  display: 'flex',
  gap: '20px',
}

const navLinkStyles = {
  color: 'white',
  textDecoration: 'none',
  fontWeight: 'bold',
  padding: '10px 20px',
  borderRadius: '5px',
  transition: 'background-color 0.3s',
}