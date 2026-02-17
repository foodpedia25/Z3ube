import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import MatrixRain from '../components/MatrixRain'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
    title: 'Z3ube - Next-Generation AI Agent',
    description: 'Revolutionary AI agent with advanced reasoning, self-learning, and code generation',
}

export default function RootLayout({
    children,
}: {
    children: React.ReactNode
}) {
    return (
        <html lang="en">
            <body className={inter.className}>
                <MatrixRain />
                {children}
            </body>
        </html>
    )
}
