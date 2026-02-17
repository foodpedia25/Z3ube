'use client';

import { motion } from 'framer-motion';
import Link from 'next/link';

export default function Home() {
    return (
        <main className="min-h-screen flex flex-col items-center justify-center p-8 relative z-10 overflow-hidden">
            {/* Hero Section */}
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.8 }}
                className="text-center max-w-5xl"
            >
                <div className="flex items-center justify-center gap-6 mb-8">
                    <div className="relative w-24 h-24 animate-spin-slow">
                        <img
                            src="/z3ube-logo.svg"
                            alt="Z3ube Logo"
                            className="object-contain w-full h-full"
                        />
                    </div>
                    <h2 className="text-6xl font-bold text-white tracking-tighter"><span className="font-bold">Z<span className="text-cyan-500">3</span>ube</span></h2>
                </div>
                <h1 className="text-5xl lg:text-[76px] font-semibold tracking-tight leading-[1.05] text-white mb-6">
                    <span className="block animate-fade-in-up delay-100">Twentieth Century</span>
                    <span className="block text-cyan-400 animate-fade-in-up delay-200">Synthetic Sentience.</span>
                </h1>
                <p className="text-xl lg:text-2xl text-slate-400 max-w-xl mx-auto font-normal leading-relaxed animate-fade-in-up delay-300 mb-12">
                    Advanced reasoning • Self-learning • Auto-healing • Deep research • Code generation
                </p>

                {/* CTA Buttons */}
                <div className="flex gap-4 justify-center mb-16 animate-fade-in-up delay-400">
                    <Link href="/chat">
                        <motion.button
                            whileHover={{ scale: 1.05 }}
                            whileTap={{ scale: 0.95 }}
                            className="px-8 py-3.5 rounded-full bg-cyan-500 text-black font-bold text-[17px] hover:bg-cyan-400 transition-all hover:shadow-lg hover:shadow-cyan-500/20 active:scale-[0.98]"
                        >
                            Start Chatting
                        </motion.button>
                    </Link>
                    <Link href="/dashboard">
                        <motion.button
                            whileHover={{ scale: 1.05 }}
                            whileTap={{ scale: 0.95 }}
                            className="px-8 py-3.5 rounded-full border border-white/20 text-white font-medium hover:bg-white hover:text-black transition-all duration-300 text-[17px]"
                        >
                            View Dashboard
                        </motion.button>
                    </Link>
                </div>
            </motion.div>

            {/* Capabilities Grid */}
            <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.3, duration: 0.8 }}
                className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 max-w-6xl w-full"
            >
                <CapabilityCard
                    icon="🧠"
                    title="Advanced Reasoning"
                    description="Multi-step chain-of-thought with plan-execute-reflect loops"
                    delay={0.4}
                    href="/chat"
                />
                <CapabilityCard
                    icon="📚"
                    title="Deep Research"
                    description="Multi-source synthesis and comprehensive analysis"
                    delay={0.5}
                    href="/research"
                />
                <CapabilityCard
                    icon="💻"
                    title="Code Generation"
                    description="Python, JavaScript, C++, ROS2, Arduino & more"
                    delay={0.6}
                    href="/code"
                />
                <CapabilityCard
                    icon="🔧"
                    title="Auto-Healing"
                    description="Self-diagnosis and automatic error recovery"
                    delay={0.7}
                    href="/dashboard"
                />
                <CapabilityCard
                    icon="📈"
                    title="Self-Learning"
                    description="Continuous improvement from every interaction"
                    delay={0.8}
                    href="/dashboard"
                />
                <CapabilityCard
                    icon="🤖"
                    title="Robotics Engineering"
                    description="Specialized code for robotic systems"
                    delay={0.9}
                    href="/robotics"
                />
            </motion.div>

            {/* Stats Section */}
            <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 1.0, duration: 0.8 }}
                className="mt-16 grid grid-cols-1 md:grid-cols-3 gap-8 max-w-4xl w-full"
            >
                <StatCard number="99.9%" label="Uptime" />
                <StatCard number="<100ms" label="Response Time" />
                <StatCard number="Infinite" label="Possibilities" />
            </motion.div>
        </main>
    );
}

function CapabilityCard({
    icon,
    title,
    description,
    delay,
    href = '#',
}: {
    icon: string;
    title: string;
    description: string;
    delay: number;
    href?: string;
}) {
    const Card = (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay, duration: 0.5 }}
            whileHover={{ scale: 1.05, boxShadow: '0 0 30px rgba(6, 182, 212, 0.3)' }}
            className="glass p-6 rounded-lg hover-border-cyan cursor-pointer border border-white/10 hover:border-cyan-500/50 transition-all duration-300 h-full"
        >
            <div className="text-4xl mb-3">{icon}</div>
            <h3 className="text-xl font-bold mb-2 text-white">{title}</h3>
            <p className="text-gray-400">{description}</p>
        </motion.div>
    );

    return href ? <Link href={href} className="block h-full">{Card}</Link> : Card;
}

function StatCard({ number, label }: { number: string; label: string }) {
    return (
        <div className="text-center glass p-6 rounded-lg">
            <div className="text-4xl font-bold text-cyan-400 mb-2">
                {number}
            </div>
            <div className="text-gray-300">{label}</div>
        </div>
    );
}
