import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import MatrixRain from '../components/MatrixRain'
import Footer from '../components/Footer'
import Navbar from '../components/Navbar'
import { ClerkProvider } from '@clerk/nextjs'
import { dark } from '@clerk/themes'

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
        <ClerkProvider
            appearance={{
                baseTheme: dark,
                variables: {
                    colorPrimary: '#06b6d4',
                    colorBackground: '#0a0a0a',
                },
            }}
        >
            <html lang="en">
                <body className={`${inter.className} bg-[#0a0a0a] text-white min-h-screen overflow-x-hidden`}>
                    <MatrixRain />
                    <div className="flex flex-col min-h-screen">
                        <Navbar />
                        <main className="flex-grow pt-20">
                            {children}
                        </main>
                        <Footer />
                    </div>
                </body>
            </html>
        </ClerkProvider>
    )
}
