'use client';

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

export default function RoboticsStudio() {
    const [config, setConfig] = useState({
        robotType: 'mobile_robot',
        framework: 'ros2', // ros2 or arduino
        language: 'ros2_cpp', // ros2_cpp, ros2_python, arduino
        sensors: [] as string[],
        description: ''
    });

    const [generating, setGenerating] = useState(false);
    const [projectFiles, setProjectFiles] = useState<Record<string, string> | null>(null);
    const [selectedFile, setSelectedFile] = useState<string | null>(null);

    const handleSensorToggle = (sensor: string) => {
        setConfig(prev => ({
            ...prev,
            sensors: prev.sensors.includes(sensor)
                ? prev.sensors.filter(s => s !== sensor)
                : [...prev.sensors, sensor]
        }));
    };

    const generateProject = async () => {
        setGenerating(true);
        setProjectFiles(null);
        setSelectedFile(null);

        try {
            const apiUrl = process.env.NEXT_PUBLIC_API_URL || (process.env.NODE_ENV === 'production' ? '/api' : 'http://localhost:8000');

            const prompt = `Create a ${config.framework} project for a ${config.robotType}.
Sensors: ${config.sensors.join(', ') || 'None'}.
Description: ${config.description || 'Standard setup'}.
Target Language: ${config.language}.
`;

            const res = await fetch(`${apiUrl}/code/project`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    description: prompt,
                    language: config.language // utilizing the language field for project type/language
                })
            });

            if (!res.ok) throw new Error('Generation failed');

            const data = await res.json();
            setProjectFiles(data.files);
            // Select first file
            if (data.files && Object.keys(data.files).length > 0) {
                setSelectedFile(Object.keys(data.files)[0]);
            }
        } catch (e) {
            console.error(e);
            alert("Failed to generate project. Please try again.");
        } finally {
            setGenerating(false);
        }
    };

    return (
        <main className="min-h-screen bg-[#050505] text-gray-300 font-mono flex flex-col md:flex-row">
            {/* Sidebar / Configuration */}
            <div className="w-full md:w-80 border-r border-gray-800 bg-[#0a0a0a] p-6 flex flex-col h-screen overflow-y-auto">
                <div className="mb-8 flex items-center gap-3">
                    <div className="w-8 h-8 rounded bg-cyan-600 flex items-center justify-center text-black font-bold text-xl">R</div>
                    <h1 className="text-xl font-bold tracking-wider text-white">ROBOTICS<br /><span className="text-cyan-500 text-sm">STUDIO</span></h1>
                </div>

                <div className="space-y-6 flex-grow">
                    {/* Robot Type */}
                    <div className="space-y-2">
                        <label className="text-xs font-bold text-gray-500 uppercase tracking-widest">Platform</label>
                        <select
                            className="w-full bg-black border border-gray-700 rounded p-2 text-sm focus:border-cyan-500 outline-none transition-colors"
                            value={config.robotType}
                            onChange={(e) => setConfig({ ...config, robotType: e.target.value })}
                        >
                            <option value="mobile_robot">Mobile Rover</option>
                            <option value="robotic_arm">Robotic Arm (6-DOF)</option>
                            <option value="drone">Quadrotor Drone</option>
                            <option value="humanoid">Humanoid Biped</option>
                            <option value="custom">Custom Platform</option>
                        </select>
                    </div>

                    {/* Framework */}
                    <div className="space-y-2">
                        <label className="text-xs font-bold text-gray-500 uppercase tracking-widest">Framework</label>
                        <div className="grid grid-cols-2 gap-2">
                            <button
                                onClick={() => setConfig({ ...config, framework: 'ros2', language: 'ros2_cpp' })}
                                className={`p-2 text-xs border rounded transition-all ${config.framework === 'ros2' ? 'bg-cyan-900/30 border-cyan-500 text-cyan-400' : 'border-gray-700 hover:border-gray-500'}`}
                            >
                                ROS 2
                            </button>
                            <button
                                onClick={() => setConfig({ ...config, framework: 'arduino', language: 'arduino' })}
                                className={`p-2 text-xs border rounded transition-all ${config.framework === 'arduino' ? 'bg-cyan-900/30 border-cyan-500 text-cyan-400' : 'border-gray-700 hover:border-gray-500'}`}
                            >
                                Arduino
                            </button>
                        </div>
                    </div>

                    {/* Language (if ROS2) */}
                    {config.framework === 'ros2' && (
                        <div className="space-y-2">
                            <label className="text-xs font-bold text-gray-500 uppercase tracking-widest">Language</label>
                            <select
                                className="w-full bg-black border border-gray-700 rounded p-2 text-sm focus:border-cyan-500 outline-none transition-colors"
                                value={config.language}
                                onChange={(e) => setConfig({ ...config, language: e.target.value })}
                            >
                                <option value="ros2_cpp">C++ (rclcpp)</option>
                                <option value="ros2_python">Python (rclpy)</option>
                            </select>
                        </div>
                    )}

                    {/* Sensors */}
                    <div className="space-y-2">
                        <label className="text-xs font-bold text-gray-500 uppercase tracking-widest">Sensors</label>
                        <div className="grid grid-cols-2 gap-2">
                            {['Lidar', 'Camera', 'IMU', 'GPS', 'Ultrasonic', 'Encoder'].map(sensor => (
                                <button
                                    key={sensor}
                                    onClick={() => handleSensorToggle(sensor)}
                                    className={`p-2 text-xs border rounded text-left transition-all ${config.sensors.includes(sensor) ? 'bg-cyan-500 text-black border-cyan-500 font-bold' : 'border-gray-700 text-gray-400 hover:border-gray-500'}`}
                                >
                                    {sensor}
                                </button>
                            ))}
                        </div>
                    </div>

                    {/* Description */}
                    <div className="space-y-2">
                        <label className="text-xs font-bold text-gray-500 uppercase tracking-widest">Requirements</label>
                        <textarea
                            className="w-full bg-black border border-gray-700 rounded p-2 text-sm focus:border-cyan-500 outline-none min-h-[100px] resize-none"
                            placeholder="Describe behavior (e.g., 'Navigate to waypoint and avoid obstacles')..."
                            value={config.description}
                            onChange={(e) => setConfig({ ...config, description: e.target.value })}
                        />
                    </div>
                </div>

                <div className="mt-6">
                    <button
                        onClick={generateProject}
                        disabled={generating}
                        className={`w-full py-4 rounded font-bold uppercase tracking-wider transition-all
                            ${generating
                                ? 'bg-gray-800 text-gray-500 cursor-not-allowed'
                                : 'bg-gradient-to-r from-cyan-600 to-blue-600 text-white hover:shadow-[0_0_20px_rgba(6,182,212,0.4)]'
                            }`}
                    >
                        {generating ? 'Engineering...' : 'Initialize Project'}
                    </button>
                    {generating && (
                        <div className="w-full bg-gray-900 h-1 mt-2 rounded overflow-hidden">
                            <motion.div
                                className="h-full bg-cyan-500"
                                initial={{ width: "0%" }}
                                animate={{ width: "100%" }}
                                transition={{ duration: 2, repeat: Infinity }}
                            />
                        </div>
                    )}
                </div>
            </div>

            {/* Main Content / File Viewer */}
            <div className="flex-grow flex flex-col h-screen overflow-hidden bg-[#050505] relative">
                {/* Background Grid */}
                <div className="absolute inset-0 bg-[linear-gradient(rgba(18,18,18,0.5)_1px,transparent_1px),linear-gradient(90deg,rgba(18,18,18,0.5)_1px,transparent_1px)] bg-[size:40px_40px] pointer-events-none"></div>

                {!projectFiles ? (
                    <div className="flex-grow flex flex-col items-center justify-center opacity-30 pointer-events-none">
                        <div className="text-6xl text-cyan-900 mb-4 animate-pulse">⚡</div>
                        <h2 className="text-2xl font-bold tracking-widest">AWAITING BLUEPRINTS</h2>
                        <p className="mt-2 text-sm">Configure system parameters to initiate generation.</p>
                    </div>
                ) : (
                    <div className="flex flex-grow h-full z-10">
                        {/* File Explorer */}
                        <div className="w-64 bg-[#0a0a0a] border-r border-gray-800 flex flex-col">
                            <div className="p-3 border-b border-gray-800 text-xs font-bold text-gray-500 uppercase">Project Files</div>
                            <div className="flex-grow overflow-y-auto p-2 space-y-1">
                                {Object.keys(projectFiles).map(filename => (
                                    <button
                                        key={filename}
                                        onClick={() => setSelectedFile(filename)}
                                        className={`w-full text-left px-3 py-2 rounded text-sm font-mono truncate transition-colors
                                            ${selectedFile === filename
                                                ? 'bg-cyan-900/30 text-cyan-400 border-l-2 border-cyan-500'
                                                : 'text-gray-400 hover:bg-gray-900 hover:text-white'
                                            }`}
                                    >
                                        {filename}
                                    </button>
                                ))}
                            </div>
                        </div>

                        {/* Code Editor View */}
                        <div className="flex-grow flex flex-col bg-[#050505]">
                            <div className="h-10 border-b border-gray-800 bg-[#0a0a0a] flex items-center px-4 justify-between">
                                <span className="text-sm text-gray-300 font-mono">{selectedFile}</span>
                                <div className="flex gap-2">
                                    <button className="text-xs px-2 py-1 rounded bg-gray-800 hover:bg-gray-700 text-gray-300">Copy</button>
                                    <button className="text-xs px-2 py-1 rounded bg-cyan-900/30 text-cyan-400 border border-cyan-500/30 hover:bg-cyan-900/50">Download</button>
                                </div>
                            </div>
                            <div className="flex-grow overflow-auto p-4 custom-scrollbar">
                                <pre className="font-mono text-sm text-gray-300">
                                    <code>
                                        {selectedFile && projectFiles[selectedFile]}
                                    </code>
                                </pre>
                            </div>
                        </div>
                    </div>
                )}
            </div>
        </main>
    );
}
