'use client';

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';

export default function DashboardPage() {
    const [status, setStatus] = useState<any>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchStatus = async () => {
            try {
                // Determine API URL based on environment
                const apiUrl = process.env.NEXT_PUBLIC_API_URL || (process.env.NODE_ENV === 'production' ? '/api' : 'http://localhost:8000');
                const res = await fetch(`${apiUrl}/system/status`);
                if (!res.ok) throw new Error('Failed to fetch status');
                const data = await res.json();
                setStatus(data);
            } catch (e) {
                console.error("Failed to fetch status", e);
            } finally {
                setLoading(false);
            }
        };

        fetchStatus();
        const interval = setInterval(fetchStatus, 3000); // Poll every 3 seconds
        return () => clearInterval(interval);
    }, []);

    if (loading && !status) {
        return (
            <div className="min-h-screen flex items-center justify-center bg-black text-cyan-500">
                <div className="animate-pulse">Initializing Neural Interface...</div>
            </div>
        );
    }

    const { health, learning, reasoning, system } = status || {};

    return (
        <main className="min-h-screen bg-black text-cyan-500 p-8 font-mono relative overflow-hidden">
            {/* Background Matrix Effect (Simplified) */}
            <div className="absolute inset-0 pointer-events-none opacity-10 bg-[url('/matrix-bg.png')]"></div>

            <div className="max-w-7xl mx-auto relative z-10">
                <header className="mb-12 border-b border-cyan-900 pb-4 flex justify-between items-end">
                    <div>
                        <h1 className="text-4xl font-bold mb-2 text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-blue-600">
                            Z3UBE NEURAL DASHBOARD
                        </h1>
                        <p className="text-sm text-cyan-700">SYSTEM STATUS: {health?.status?.toUpperCase() || 'UNKNOWN'}</p>
                    </div>
                    <div className="text-right text-xs text-gray-500">
                        <p>UPTIME: {system?.uptime || '0%'}</p>
                        <p>LATENCY: {system?.latency || '0ms'}</p>
                    </div>
                </header>

                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
                    {/* Health Card */}
                    <DashboardCard title="SYSTEM HEALTH" delay={0.1}>
                        <div className="flex items-center justify-between mb-4">
                            <div className={`w-4 h-4 rounded-full ${health?.status === 'healthy' ? 'bg-green-500 shadow-[0_0_10px_#00ff00]' : 'bg-red-500 animate-pulse'}`}></div>
                            <span className="text-xl font-bold">{health?.metrics?.recovery_success_rate ? (health.metrics.recovery_success_rate * 100).toFixed(1) : 0}%</span>
                        </div>
                        <div className="text-xs text-gray-400 space-y-1">
                            <p>Recovered Errors: {health?.metrics?.recovered_errors || 0}</p>
                            <p>Total Errors: {health?.metrics?.total_errors || 0}</p>
                        </div>
                    </DashboardCard>

                    {/* Reasoning Card */}
                    <DashboardCard title="CORTEX ACTIVITY" delay={0.2}>
                        <div className="mb-4">
                            <div className="text-2xl font-bold text-white mb-1">{reasoning?.short_term_memory_size || 0}</div>
                            <div className="text-xs text-cyan-600">Active Thoughts</div>
                        </div>
                        <div className="text-xs space-y-1 border-t border-cyan-900/50 pt-2">
                            <p>Model: <span className="text-white">{reasoning?.active_model}</span></p>
                            <p>Long Term Memory: {reasoning?.long_term_memory_size || 0}</p>
                        </div>
                    </DashboardCard>

                    {/* Learning Card */}
                    <DashboardCard title="NEURAL PLASTICITY" delay={0.3}>
                        <div className="mb-4">
                            <div className="text-2xl font-bold text-pink-500 mb-1">{learning?.patterns_identified || 0}</div>
                            <div className="text-xs text-pink-700">Patterns Learned</div>
                        </div>
                        <div className="text-xs space-y-1 border-t border-cyan-900/50 pt-2">
                            <p>Success Rate: {learning?.success_rate ? (learning.success_rate * 100).toFixed(1) : 0}%</p>
                            <p>Improvements: {learning?.improvements_applied || 0}</p>
                        </div>
                    </DashboardCard>

                    {/* Network Card */}
                    <DashboardCard title="NETWORK BRIDGE" delay={0.4}>
                        <div className="mb-4">
                            <div className="text-2xl font-bold text-yellow-500 mb-1">{system?.active_connections || 0}</div>
                            <div className="text-xs text-yellow-700">Active Nodes</div>
                        </div>
                        <div className="text-xs space-y-1 border-t border-cyan-900/50 pt-2">
                            <p>Protocol: REST/WebSocket</p>
                            <p>Encryption: TLS 1.3</p>
                        </div>
                    </DashboardCard>
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    {/* Recent Errors Log */}
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.5 }}
                        className="bg-black/40 border border-red-900/30 p-4 rounded-lg backdrop-blur-sm"
                    >
                        <h3 className="text-red-500 font-bold mb-4 text-sm tracking-wider">⚠️ ANOMALY LOG</h3>
                        <div className="space-y-2 max-h-60 overflow-y-auto custom-scrollbar">
                            {health?.recent_errors && health.recent_errors.length > 0 ? (
                                health.recent_errors.map((err: any, i: number) => (
                                    <div key={i} className="text-xs border-l-2 border-red-800 pl-2 py-1">
                                        <div className="flex justify-between text-gray-500 mb-1">
                                            <span>{new Date(err.timestamp).toLocaleTimeString()}</span>
                                            <span className="text-red-400">{err.type}</span>
                                        </div>
                                        <div className="text-gray-300">{err.message}</div>
                                    </div>
                                ))
                            ) : (
                                <div className="text-gray-600 text-center py-8">System Nominal. No Anomalies Detected.</div>
                            )}
                        </div>
                    </motion.div>

                    {/* Learned Patterns Log */}
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.6 }}
                        className="bg-black/40 border border-pink-900/30 p-4 rounded-lg backdrop-blur-sm"
                    >
                        <h3 className="text-pink-500 font-bold mb-4 text-sm tracking-wider">🧠 SYNAPTIC PATTERNS</h3>
                        <div className="space-y-2 max-h-60 overflow-y-auto custom-scrollbar">
                            {learning?.top_success_strategies ? (
                                Object.entries(learning.top_success_strategies).map(([tag, strategies]: any, i: number) => (
                                    <div key={i} className="text-xs border-l-2 border-pink-800 pl-2 py-1">
                                        <div className="text-pink-400 font-bold mb-1">Context: {tag}</div>
                                        <div className="text-gray-400 italic">"Strategy identified from {strategies.length} successful interactions"</div>
                                    </div>
                                ))
                            ) : (
                                <div className="text-gray-600 text-center py-8">Awaiting Neural Data...</div>
                            )}
                        </div>
                    </motion.div>
                </div>
            </div>
        </main>
    );
}

function DashboardCard({ title, children, delay }: { title: string, children: React.ReactNode, delay: number }) {
    return (
        <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay }}
            className="bg-black/60 border border-cyan-500/20 p-6 rounded-lg hover:border-cyan-500/50 transition-colors group"
        >
            <h3 className="text-xs font-bold text-gray-500 mb-4 tracking-widest group-hover:text-cyan-400 transition-colors">{title}</h3>
            {children}
        </motion.div>
    );
}
