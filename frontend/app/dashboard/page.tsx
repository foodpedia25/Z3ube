'use client';

import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';

interface Stats {
    learning?: {
        total_interactions: number;
        success_rate: number;
        patterns_identified: number;
    };
    health?: {
        status: string;
        metrics: {
            total_errors: number;
            recovery_success_rate: number;
        };
    };
}

export default function DashboardPage() {
    const [stats, setStats] = useState<Stats>({});
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchStats();
    }, []);

    const fetchStats = async () => {
        try {
            const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
            const response = await fetch(`${apiUrl}/stats`);
            const data = await response.json();
            setStats(data);
        } catch (error) {
            console.error('Error fetching stats:', error);
        } finally {
            setLoading(false);
        }
    };

    return (
        <main className="min-h-screen p-8 relative z-10">
            <div className="max-w-7xl mx-auto">
                {/* Header */}
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="text-center mb-12"
                >
                    <h1 className="text-5xl font-bold glow-text animate-glow mb-4">
                        System Dashboard
                    </h1>
                    <p className="text-gray-400">Real-time monitoring of Z3ube capabilities</p>
                </motion.div>

                {loading ? (
                    <div className="text-center text-matrix-green">
                        <div className="text-2xl">Loading metrics...</div>
                    </div>
                ) : (
                    <>
                        {/* System Status */}
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                            <StatCard
                                title="System Status"
                                value={stats.health?.status || 'Unknown'}
                                subtitle="Overall Health"
                                color="green"
                            />
                            <StatCard
                                title="Total Interactions"
                                value={stats.learning?.total_interactions || 0}
                                subtitle="Learning from experience"
                                color="blue"
                            />
                            <StatCard
                                title="Success Rate"
                                value={`${((stats.learning?.success_rate || 0) * 100).toFixed(1)}%`}
                                subtitle="Performance metric"
                                color="green"
                            />
                        </div>

                        {/* Capabilities Grid */}
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
                            <CapabilityCard
                                icon="🧠"
                                title="Reasoning Engine"
                                status="Active"
                                description="Multi-step chain-of-thought processing"
                            />
                            <CapabilityCard
                                icon="📚"
                                title="Research Engine"
                                status="Active"
                                description="Deep multi-source research"
                            />
                            <CapabilityCard
                                icon="💻"
                                title="Code Generator"
                                status="Active"
                                description="Multi-language code generation"
                            />
                            <CapabilityCard
                                icon="🔧"
                                title="Auto-Healer"
                                status="Active"
                                description={`${stats.health?.metrics?.total_errors || 0} errors handled`}
                            />
                            <CapabilityCard
                                icon="📈"
                                title="Self-Learning"
                                status="Active"
                                description={`${stats.learning?.patterns_identified || 0} patterns identified`}
                            />
                            <CapabilityCard
                                icon="🕸️"
                                title="Knowledge Graph"
                                status="Active"
                                description="Semantic relationship mapping"
                            />
                        </div>

                        {/* Performance Metrics */}
                        <motion.div
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            transition={{ delay: 0.3 }}
                            className="glass p-6 rounded-lg"
                        >
                            <h2 className="text-2xl font-bold text-matrix-green mb-4">
                                Performance Metrics
                            </h2>
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                <MetricRow
                                    label="Patterns Identified"
                                    value={stats.learning?.patterns_identified || 0}
                                />
                                <MetricRow
                                    label="Success Rate"
                                    value={`${((stats.learning?.success_rate || 0) * 100).toFixed(1)}%`}
                                />
                                <MetricRow
                                    label="Errors Handled"
                                    value={stats.health?.metrics?.total_errors || 0}
                                />
                                <MetricRow
                                    label="Recovery Rate"
                                    value={`${((stats.health?.metrics?.recovery_success_rate || 0) * 100).toFixed(1)}%`}
                                />
                            </div>
                        </motion.div>
                    </>
                )}
            </div>
        </main>
    );
}

function StatCard({
    title,
    value,
    subtitle,
    color,
}: {
    title: string;
    value: string | number;
    subtitle: string;
    color: 'green' | 'blue';
}) {
    const colorClass = color === 'green' ? 'text-matrix-green' : 'text-neon-blue';

    return (
        <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            className="glass p-6 rounded-lg hover-glow"
        >
            <h3 className="text-gray-400 text-sm mb-2">{title}</h3>
            <div className={`text-4xl font-bold ${colorClass} glow-text mb-2`}>
                {value}
            </div>
            <p className="text-gray-500 text-sm">{subtitle}</p>
        </motion.div>
    );
}

function CapabilityCard({
    icon,
    title,
    status,
    description,
}: {
    icon: string;
    title: string;
    status: string;
    description: string;
}) {
    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            whileHover={{ scale: 1.02 }}
            className="glass p-6 rounded-lg hover-glow"
        >
            <div className="flex items-start gap-4">
                <div className="text-4xl">{icon}</div>
                <div className="flex-1">
                    <h3 className="text-xl font-bold text-matrix-green mb-1">{title}</h3>
                    <div className="text-green-400 text-sm mb-2">● {status}</div>
                    <p className="text-gray-400 text-sm">{description}</p>
                </div>
            </div>
        </motion.div>
    );
}

function MetricRow({ label, value }: { label: string; value: string | number }) {
    return (
        <div className="flex justify-between items-center p-3 bg-black/30 rounded">
            <span className="text-gray-400">{label}</span>
            <span className="text-matrix-green font-bold">{value}</span>
        </div>
    );
}
