'use client';

import { motion } from 'framer-motion';
import Link from 'next/link';

export default function Home() {
    return (
        <main className="min-h-screen flex flex-col items-center justify-center p-8 relative z-10">
            {/* Hero Section */}
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.8 }}
                className="text-center max-w-5xl"
            >
                <h1 className="text-7xl font-bold mb-6 glow-text animate-glow">
                    Z3ube
                </h1>
                <p className="text-2xl mb-4 text-matrix-green">
                    Next-Generation AI Agent Platform
                </p>
                <p className="text-xl mb-12 text-gray-300 max-w-3xl mx-auto">
                    Advanced reasoning • Self-learning • Auto-healing • Deep research • Code generation
                </p>

                {/* CTA Buttons */}
                <div className="flex gap-4 justify-center mb-16">
                    <Link href="/chat">
                        <motion.button
                            whileHover={{ scale: 1.05 }}
                            whileTap={{ scale: 0.95 }}
                            className="px-8 py-4 bg-matrix-green text-black font-bold rounded-lg hover-glow text-lg"
                        >
                            Start Chatting
                        </motion.button>
                    </Link>
                    <Link href="/dashboard">
                        <motion.button
                            whileHover={{ scale: 1.05 }}
                            whileTap={{ scale: 0.95 }}
                            className="px-8 py-4 glass border border-matrix-green text-matrix-green font-bold rounded-lg hover-glow text-lg"
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
                />
                <CapabilityCard
                    icon="📚"
                    title="Deep Research"
                    description="Multi-source synthesis and comprehensive analysis"
                    delay={0.5}
                />
                <CapabilityCard
                    icon="💻"
                    title="Code Generation"
                    description="Python, JavaScript, C++, ROS2, Arduino & more"
                    delay={0.6}
                />
                <CapabilityCard
                    icon="🔧"
                    title="Auto-Healing"
                    description="Self-diagnosis and automatic error recovery"
                    delay={0.7}
                />
                <CapabilityCard
                    icon="📈"
                    title="Self-Learning"
                    description="Continuous improvement from every interaction"
                    delay={0.8}
                />
                <CapabilityCard
                    icon="🤖"
                    title="Robotics Engineering"
                    description="Specialized code for robotic systems"
                    delay={0.9}
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
}: {
    icon: string;
    title: string;
    description: string;
    delay: number;
}) {
    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay, duration: 0.5 }}
            whileHover={{ scale: 1.05, boxShadow: '0 0 30px rgba(0, 255, 65, 0.3)' }}
            className="glass p-6 rounded-lg hover-glow cursor-pointer"
        >
            <div className="text-4xl mb-3">{icon}</div>
            <h3 className="text-xl font-bold mb-2 text-matrix-green">{title}</h3>
            <p className="text-gray-300">{description}</p>
        </motion.div>
    );
}

function StatCard({ number, label }: { number: string; label: string }) {
    return (
        <div className="text-center glass p-6 rounded-lg">
            <div className="text-4xl font-bold text-matrix-green glow-text mb-2">
                {number}
            </div>
            <div className="text-gray-300">{label}</div>
        </div>
    );
}
