import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import MatrixRain from '../components/MatrixRain'
import Footer from '../components/Footer'

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
            <body className={`${inter.className} bg-[#0a0a0a] text-white min-h-screen overflow-x-hidden`}>
                <MatrixRain />
                <div className="flex flex-col min-h-screen">
                    <main className="flex-grow">
                        {children}
                    </main>
                    <Footer />
                </div>
            </body>
        </html>
    )
}
