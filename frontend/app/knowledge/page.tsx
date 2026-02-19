'use client';

import { useEffect, useRef, useState } from 'react';
import { motion } from 'framer-motion';

interface Node {
    id: string;
    type: string;
    x: number;
    y: number;
    z: number;
    vx: number;
    vy: number;
    vz: number;
}

interface Link {
    source: string;
    target: string;
    relationship: string;
}

export default function KnowledgeGraph() {
    const canvasRef = useRef<HTMLCanvasElement>(null);
    const [graphData, setGraphData] = useState<{ nodes: any[], edges: any[] } | null>(null);
    const [loading, setLoading] = useState(true);
    const [rotation, setRotation] = useState({ x: 0, y: 0 });
    const isDragging = useRef(false);
    const lastMousePos = useRef({ x: 0, y: 0 });
    const nodesRef = useRef<Node[]>([]);

    useEffect(() => {
        const fetchData = async () => {
            try {
                const apiUrl = process.env.NEXT_PUBLIC_API_URL || (process.env.NODE_ENV === 'production' ? '/api' : 'http://localhost:8000');
                const res = await fetch(`${apiUrl}/knowledge/graph`);
                const data = await res.json();
                setGraphData(data);

                // Initialize 3D positions
                nodesRef.current = data.nodes.map((n: any) => ({
                    ...n,
                    x: (Math.random() - 0.5) * 800,
                    y: (Math.random() - 0.5) * 800,
                    z: (Math.random() - 0.5) * 800,
                    vx: 0, vy: 0, vz: 0
                }));
            } catch (e) {
                console.error("Failed to fetch graph data", e);
            } finally {
                setLoading(false);
            }
        };
        fetchData();
    }, []);

    useEffect(() => {
        if (!canvasRef.current || !graphData) return;

        const canvas = canvasRef.current;
        const ctx = canvas.getContext('2d');
        if (!ctx) return;

        let animationFrameId: number;
        let angle = 0;

        const render = () => {
            if (!ctx || !canvas) return;

            // Resize canvas
            if (canvas.width !== window.innerWidth || canvas.height !== window.innerHeight) {
                canvas.width = window.innerWidth;
                canvas.height = window.innerHeight;
            }

            const width = canvas.width;
            const height = canvas.height;
            const cx = width / 2;
            const cy = height / 2;

            // Clear canvas
            ctx.fillStyle = '#050505';
            ctx.fillRect(0, 0, width, height);

            // Auto rotate
            if (!isDragging.current) {
                angle += 0.002;
                setRotation(r => ({ ...r, y: r.y + 0.002 }));
            }

            const nodes = nodesRef.current;
            const edges = graphData.edges;

            // Sort nodes by Z for depth sorting
            const projectedNodes = nodes.map(node => {
                // Apply rotation
                let x = node.x;
                let y = node.y;
                let z = node.z;

                // Rotate Y
                const cosY = Math.cos(rotation.y);
                const sinY = Math.sin(rotation.y);
                const x1 = x * cosY - z * sinY;
                const z1 = z * cosY + x * sinY;
                x = x1;
                z = z1;

                // Rotate X
                const cosX = Math.cos(rotation.x);
                const sinX = Math.sin(rotation.x);
                const y1 = y * cosX - z * sinX;
                const z2 = z * cosX + y * sinX;
                y = y1;
                z = z2;

                // Project 3D to 2D
                const scale = 1000 / (1000 + z);
                const x2d = x * scale + cx;
                const y2d = y * scale + cy;

                return { ...node, x2d, y2d, scale, z };
            });

            projectedNodes.sort((a, b) => a.z - b.z); // Draw back to front

            // Draw Edges
            ctx.strokeStyle = 'rgba(6, 182, 212, 0.15)'; // Cyan with low opacity
            ctx.lineWidth = 1;

            edges.forEach(edge => {
                const source = projectedNodes.find(n => n.id === edge.source);
                const target = projectedNodes.find(n => n.id === edge.target);

                if (source && target) {
                    ctx.beginPath();
                    ctx.moveTo(source.x2d, source.y2d);
                    ctx.lineTo(target.x2d, target.y2d);
                    ctx.stroke();
                }
            });

            // Draw Nodes
            projectedNodes.forEach(node => {
                const size = Math.max(2, 6 * node.scale);
                const alpha = Math.min(1, Math.max(0.2, (node.z + 500) / 1000));

                // Node glow
                const gradient = ctx.createRadialGradient(node.x2d, node.y2d, 0, node.x2d, node.y2d, size * 4);
                gradient.addColorStop(0, 'rgba(6, 182, 212, 0.8)');
                gradient.addColorStop(1, 'rgba(6, 182, 212, 0)');

                ctx.fillStyle = gradient;
                ctx.beginPath();
                ctx.arc(node.x2d, node.y2d, size * 4, 0, Math.PI * 2);
                ctx.fill();

                // Core node
                ctx.fillStyle = `rgba(255, 255, 255, ${alpha})`;
                ctx.beginPath();
                ctx.arc(node.x2d, node.y2d, size, 0, Math.PI * 2);
                ctx.fill();

                // Label
                if (node.scale > 0.6) {
                    ctx.fillStyle = `rgba(6, 182, 212, ${alpha})`;
                    ctx.font = `${Math.floor(10 * node.scale)}px monospace`;
                    ctx.fillText(node.id, node.x2d + size + 5, node.y2d + 3);
                }
            });

            animationFrameId = requestAnimationFrame(render);
        };

        render();

        return () => cancelAnimationFrame(animationFrameId);
    }, [graphData, rotation]);

    // Mouse handlers for rotation
    const handleMouseDown = (e: React.MouseEvent) => {
        isDragging.current = true;
        lastMousePos.current = { x: e.clientX, y: e.clientY };
    };

    const handleMouseMove = (e: React.MouseEvent) => {
        if (!isDragging.current) return;
        const deltaX = e.clientX - lastMousePos.current.x;
        const deltaY = e.clientY - lastMousePos.current.y;

        setRotation(r => ({
            x: r.x - deltaY * 0.005,
            y: r.y + deltaX * 0.005
        }));

        lastMousePos.current = { x: e.clientX, y: e.clientY };
    };

    const handleMouseUp = () => {
        isDragging.current = false;
    };

    return (
        <main className="w-full h-screen bg-[#050505] overflow-hidden relative cursor-move">
            <canvas
                ref={canvasRef}
                onMouseDown={handleMouseDown}
                onMouseMove={handleMouseMove}
                onMouseUp={handleMouseUp}
                onMouseLeave={handleMouseUp}
                className="absolute inset-0 z-0"
            />

            <div className="absolute top-8 left-8 z-10 pointer-events-none">
                <motion.div
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ duration: 1 }}
                >
                    <h1 className="text-4xl font-bold text-white tracking-widest mb-2">
                        KNOWLEDGE<span className="text-cyan-500">GRAPH</span>
                    </h1>
                    <p className="text-cyan-700 text-sm font-mono">
                        SEMANTIC VISUALIZATION OF AI MEMORY
                    </p>
                </motion.div>
            </div>

            {loading && (
                <div className="absolute inset-0 flex items-center justify-center z-20 bg-black/80">
                    <div className="text-cyan-500 animate-pulse font-mono">Loading Semantic Network...</div>
                </div>
            )}

            {/* Control hints */}
            <div className="absolute bottom-8 right-8 z-10 text-right pointer-events-none">
                <p className="text-xs text-gray-500 font-mono">DRAG TO ROTATE VIEW</p>
                <div className="text-cyan-900 text-[10px] mt-1">NODES: {graphData?.nodes.length || 0} | EDGES: {graphData?.edges.length || 0}</div>
            </div>
        </main>
    );
}
