'use client';

import { motion } from 'framer-motion';
import Link from 'next/link';

export default function ResearchPage() {
    return (
        <main className="min-h-screen flex flex-col items-center justify-center p-8 relative z-10 bg-[#0a0a0a] text-white">
            <motion.div
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                className="text-center max-w-2xl"
            >
                <div className="text-6xl mb-6">📚</div>
                <h1 className="text-4xl font-bold mb-4 text-cyan-400">Deep Research Mode</h1>
                <p className="text-xl text-slate-400 mb-8">
                    Multi-source synthesis and comprehensive analysis capabilities coming soon.
                </p>
                <Link href="/">
                    <button className="px-6 py-3 rounded-full border border-white/20 hover:bg-white hover:text-black transition-all">
                        Return Home
                    </button>
                </Link>
            </motion.div>
        </main>
    );
}
