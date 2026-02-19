'use client';

import { useState, useRef, useEffect } from 'react';
import { motion } from 'framer-motion';
import { PhotoIcon, XMarkIcon, MicrophoneIcon, SpeakerWaveIcon, StopIcon } from '@heroicons/react/24/outline'; // Use Heroicons
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import rehypeHighlight from 'rehype-highlight';
import 'highlight.js/styles/github-dark.css';

interface ThinkingStep {
    step: number;
    thought: string;
    reasoning: string;
    confidence: number;
}

interface ResearchSource {
    title: string;
    content: string;
    url?: string;
}

interface ResearchResult {
    topic: string;
    summary: string;
    key_findings: string[];
    sources: ResearchSource[];
    research_time: number;
}

interface Message {
    role: 'user' | 'assistant';
    content: string;
    thinking_steps?: ThinkingStep[];
    image?: string; // Add image support to message interface
}

export default function ChatPage() {
    const [messages, setMessages] = useState<Message[]>([]);
    const [input, setInput] = useState('');
    const [selectedImage, setSelectedImage] = useState<string | null>(null); // Image state
    const fileInputRef = useRef<HTMLInputElement>(null); // File input ref
    const [loading, setLoading] = useState(false);
    const [mode, setMode] = useState<'chat' | 'research'>('chat');
    const [researchResult, setResearchResult] = useState<ResearchResult | null>(null);

    // Voice State
    const [isListening, setIsListening] = useState(false);
    const [isSpeaking, setIsSpeaking] = useState(false);
    const recognitionRef = useRef<any>(null); // Keep as any for Web Speech API compatibility

    // Chat State
    const [depth, setDepth] = useState('quick');
    const [selectedModel, setSelectedModel] = useState('auto');
    const messagesEndRef = useRef<HTMLDivElement>(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    const handleImageSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0];
        if (file) {
            const reader = new FileReader();
            reader.onloadend = () => {
                setSelectedImage(reader.result as string);
            };
            reader.readAsDataURL(file);
        }
    };

    const removeImage = () => {
        setSelectedImage(null);
        if (fileInputRef.current) {
            fileInputRef.current.value = '';
        }
    };

    // Voice: Speech to Text
    const startListening = () => {
        if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
            const SpeechRecognition = (window as any).webkitSpeechRecognition || (window as any).SpeechRecognition;
            const recognition = new SpeechRecognition();
            recognition.continuous = false;
            recognition.interimResults = false;
            recognition.lang = 'en-US';

            recognition.onstart = () => setIsListening(true);
            recognition.onend = () => setIsListening(false);
            recognition.onError = (event: any) => {
                console.error('Speech recognition error', event.error);
                setIsListening(false);
            };
            recognition.onresult = (event: any) => {
                const transcript = event.results[0][0].transcript;
                setInput((prev) => prev + (prev ? ' ' : '') + transcript);
            };

            recognitionRef.current = recognition;
            recognition.start();
        } else {
            alert('Speech recognition is not supported in this browser.');
        }
    };

    const stopListening = () => {
        if (recognitionRef.current) {
            recognitionRef.current.stop();
            setIsListening(false);
        }
    };

    // Voice: Text to Speech
    const speak = (text: string) => {
        if ('speechSynthesis' in window) {
            // Cancel any current speech
            window.speechSynthesis.cancel();

            const utterance = new SpeechSynthesisUtterance(text);
            utterance.onstart = () => setIsSpeaking(true);
            utterance.onend = () => setIsSpeaking(false);
            utterance.onerror = () => setIsSpeaking(false);

            // Optional: Select a specific voice if available
            // const voices = window.speechSynthesis.getVoices();
            // utterance.voice = voices.find(v => v.lang === 'en-US') || null;

            window.speechSynthesis.speak(utterance);
        } else {
            alert('Text to speech is not supported in this browser.');
        }
    };

    const stopSpeaking = () => {
        if ('speechSynthesis' in window) {
            window.speechSynthesis.cancel();
            setIsSpeaking(false);
        }
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if ((!input.trim() && !selectedImage) || loading) return;

        const userMessage: Message = {
            role: 'user',
            content: input,
            image: selectedImage || undefined
        };
        setMessages((prev) => [...prev, userMessage]);

        const currentImage = selectedImage;
        const currentInput = input;

        setInput('');
        setSelectedImage(null);
        setLoading(true);

        const assistantMessage: Message = { role: 'assistant', content: '', thinking_steps: [] };
        setMessages((prev) => [...prev, assistantMessage]);

        try {
            // Determine API URL based on environment
            const apiUrl = process.env.NEXT_PUBLIC_API_URL || (process.env.NODE_ENV === 'production' ? '/api' : 'http://localhost:8000');
            const response = await fetch(`${apiUrl}/chat/stream`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    message: currentInput || (currentImage ? "Analyze this image" : ""), // Ensure message exists
                    depth: depth,
                    model: selectedModel,
                    image: currentImage
                }),
            });

            if (!response.ok) throw new Error('Failed to get response');
            if (!response.body) throw new Error('No response body');

            const reader = response.body.getReader();
            const decoder = new TextDecoder();

            while (true) {
                const { value, done } = await reader.read();
                if (done) break;

                const chunk = decoder.decode(value);
                const lines = chunk.split('\n');

                for (const line of lines) {
                    if (!line.trim()) continue;
                    try {
                        const data = JSON.parse(line);

                        setMessages((prev) => {
                            const newMessages = [...prev];
                            const lastIndex = newMessages.length - 1;
                            const lastMessage = {
                                ...newMessages[lastIndex],
                                thinking_steps: [...(newMessages[lastIndex].thinking_steps || [])]
                            };
                            newMessages[lastIndex] = lastMessage;

                            if (data.type === 'content') {
                                lastMessage.content += data.data;
                            } else if (data.type === 'step') {
                                const stepData = data.data as ThinkingStep; // Type assertion
                                if (!lastMessage.thinking_steps) lastMessage.thinking_steps = [];
                                lastMessage.thinking_steps.push(stepData);
                            }

                            return newMessages;
                        });
                    } catch (e) {
                        console.error('Error parsing chunk:', e);
                    }
                }
            }
        } catch (error) {
            console.error('Error:', error);
            setMessages((prev) => {
                const newMessages = [...prev];
                const lastMessage = newMessages[newMessages.length - 1];
                lastMessage.content += '\n[System Error: Failed to complete response]';
                return newMessages;
            });
        } finally {
            setLoading(false);
        }
    };

    const handleResearch = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!input.trim() || loading) return;

        setLoading(true);
        setResearchResult(null);
        setMessages((prev) => [...prev, { role: 'user', content: `Researching: ${input}` }]);

        try {
            // Determine API URL based on environment
            const apiUrl = process.env.NEXT_PUBLIC_API_URL || (process.env.NODE_ENV === 'production' ? '/api' : 'http://localhost:8000');
            const response = await fetch(`${apiUrl}/research`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    topic: input,
                    depth: depth,
                    max_sources: 5
                }),
            });

            if (!response.ok) throw new Error('Research failed');

            const data = await response.json() as ResearchResult; // Type assertion
            setResearchResult(data);
            setMessages((prev) => [...prev, {
                role: 'assistant',
                content: `Here is the research report for "${data.topic}".`,
                thinking_steps: []
            }]);

        } catch (error) {
            console.error('Research error:', error);
            setMessages((prev) => [...prev, {
                role: 'assistant',
                content: 'Failed to complete research task. Please try again.',
                thinking_steps: []
            }]);
        } finally {
            setLoading(false);
            setInput('');
        }
    };

    return (
        <main className="min-h-screen flex flex-col p-4 relative z-10">
            <div className="max-w-4xl mx-auto w-full flex flex-col h-screen">
                {/* Header */}
                <div className="py-6 text-center">
                    <h1 className="text-4xl font-bold glow-text animate-glow mb-2">
                        <span className="font-bold">Z<span className="text-cyan-500">3</span>ube</span> {mode === 'chat' ? 'Chat' : 'Research'}
                    </h1>
                    <p className="text-gray-400">
                        {mode === 'chat' ? 'Powered by advanced AI reasoning' : 'Deep multi-source investigation'}
                    </p>

                    {/* Speaking Indicator / Stop Button */}
                    {isSpeaking && (
                        <motion.div
                            initial={{ opacity: 0, scale: 0.9 }}
                            animate={{ opacity: 1, scale: 1 }}
                            className="fixed top-24 right-4 z-50"
                        >
                            <button
                                onClick={stopSpeaking}
                                className="flex items-center gap-2 bg-red-500/20 border border-red-500 text-red-500 px-4 py-2 rounded-full hover:bg-red-500/30 transition-colors shadow-lg backdrop-blur-md"
                            >
                                <StopIcon className="w-5 h-5 animate-pulse" />
                                <span className="text-sm font-medium">Stop Speaking</span>
                            </button>
                        </motion.div>
                    )}
                </div>

                {/* Messages/Results Container */}
                <div className="flex-1 overflow-y-auto space-y-4 mb-4 px-4 custom-scrollbar">
                    {messages.length === 0 && researchResult === null && (
                        <div className="text-center text-gray-400 mt-20">
                            <p className="text-xl mb-4">Start a {mode} session with <span className="font-bold">Z<span className="text-cyan-500">3</span>ube</span></p>
                            <div className="flex flex-wrap gap-2 justify-center">
                                {mode === 'chat' ? (
                                    <>
                                        <ExampleButton text="Explain quantum computing" onClick={setInput} />
                                        <ExampleButton text="Generate Python code" onClick={setInput} />
                                    </>
                                ) : (
                                    <>
                                        <ExampleButton text="Latest AI trends 2026" onClick={setInput} />
                                        <ExampleButton text="Market analysis of EV batteries" onClick={setInput} />
                                    </>
                                )}
                            </div>
                        </div>
                    )}

                    {/* Chat Messages */}
                    {messages.map((message, index) => (
                        <MessageBubble key={index} message={message} onSpeak={speak} />
                    ))}

                    {/* Research Result View */}
                    {researchResult && (
                        <motion.div
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            className="bg-black/40 backdrop-blur-md border border-cyan-500/30 rounded-lg p-6 space-y-6"
                        >
                            <div className="border-b border-gray-700 pb-4">
                                <h2 className="text-2xl font-bold text-cyan-400 mb-2">{researchResult.topic}</h2>
                                <div className="flex gap-4 text-sm text-gray-400">
                                    <span>⏱️ {researchResult.research_time.toFixed(2)}s</span>
                                    <span>Running on Gemini 3 Flash</span>
                                </div>
                            </div>

                            <div>
                                <h3 className="text-lg font-semibold text-white mb-2">Summary</h3>
                                <div className="text-gray-300 leading-relaxed">
                                    <ReactMarkdown>{researchResult.summary}</ReactMarkdown>
                                </div>
                            </div>

                            <div>
                                <h3 className="text-lg font-semibold text-white mb-2">Key Findings</h3>
                                <ul className="space-y-2">
                                    {researchResult.key_findings.map((finding: string, i: number) => (
                                        <li key={i} className="flex gap-2 text-gray-300">
                                            <span className="text-cyan-500">•</span>
                                            <span>{finding}</span>
                                        </li>
                                    ))}
                                </ul>
                            </div>

                            <div>
                                <h3 className="text-lg font-semibold text-white mb-2">Sources</h3>
                                <div className="grid gap-3">
                                    {researchResult.sources.map((source, i) => (
                                        <div key={i} className="bg-black/50 p-3 rounded border border-gray-800">
                                            <div className="text-cyan-500 text-sm font-medium mb-1">{source.title}</div>
                                            <div className="text-gray-500 text-xs truncate">{source.content}</div>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        </motion.div>
                    )}

                    {loading && (
                        <div className="flex justify-start">
                            <div className="glass p-4 rounded-lg max-w-[80%]">
                                <div className="flex items-center gap-3">
                                    <div className="flex space-x-2">
                                        <div className="w-3 h-3 bg-cyan-500 rounded-full animate-bounce"></div>
                                        <div className="w-3 h-3 bg-cyan-500 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                                        <div className="w-3 h-3 bg-cyan-500 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                                    </div>
                                    <span className="text-cyan-500 text-sm animate-pulse">
                                        {mode === 'research' ? 'Conducting Deep Research...' : 'Thinking...'}
                                    </span>
                                </div>
                            </div>
                        </div>
                    )}

                    <div ref={messagesEndRef} />
                </div>

                {/* Input Form */}
                <form onSubmit={mode === 'chat' ? handleSubmit : handleResearch} className="glass p-4 rounded-lg space-y-3">
                    {/* Controls */}
                    <div className="flex justify-between items-center text-sm mb-2">
                        <div className="flex items-center gap-4">
                            {/* Mode Selector */}
                            <div className="flex bg-black/50 rounded-lg p-1 border border-cyan-500/30">
                                <button
                                    type="button"
                                    onClick={() => setMode('chat')}
                                    className={`px-3 py-1 rounded-md transition-all ${mode === 'chat' ? 'bg-cyan-500 text-black font-bold' : 'text-gray-400 hover:text-white'}`}
                                >
                                    Chat
                                </button>
                                <button
                                    type="button"
                                    onClick={() => setMode('research')}
                                    className={`px-3 py-1 rounded-md transition-all ${mode === 'research' ? 'bg-cyan-500 text-black font-bold' : 'text-gray-400 hover:text-white'}`}
                                >
                                    Research
                                </button>
                            </div>

                            {mode === 'chat' && (
                                <div className="flex items-center gap-2">
                                    <label className="text-gray-400 hidden sm:block">Model:</label>
                                    <select
                                        value={selectedModel}
                                        onChange={(e) => setSelectedModel(e.target.value)}
                                        className="bg-black/50 border border-cyan-500/30 rounded px-2 py-1 text-cyan-400 focus:outline-none focus:border-cyan-500 text-xs sm:text-sm"
                                        disabled={loading}
                                    >
                                        <option value="auto">Auto (CoT)</option>
                                        <option value="gemini">Gemini 3 Flash</option>
                                        <option value="anthropic">Anthropic (Claude 3.5 Sonnet)</option>
                                        <option value="openai">OpenAI (Legacy)</option>
                                        <option value="deepseek">Deepseek (Beta)</option>
                                        <option value="llama">Llama (Local)</option>
                                    </select>
                                </div>
                            )}
                        </div>

                        <div className="flex items-center gap-2">
                            <label className="text-gray-400 hidden sm:block">Depth:</label>
                            <select
                                value={depth}
                                onChange={(e) => setDepth(e.target.value)}
                                className="bg-black/50 border border-cyan-500/30 rounded px-2 py-1 text-cyan-400 focus:outline-none focus:border-cyan-500 text-xs sm:text-sm"
                                disabled={loading}
                            >
                                <option value="quick">Quick</option>
                                <option value="normal">Normal</option>
                                <option value="deep">Deep</option>
                            </select>
                        </div>
                    </div>

                    <div className="flex gap-2 items-end">
                        {/* Image Upload Input */}
                        <input
                            type="file"
                            accept="image/*"
                            onChange={handleImageSelect}
                            ref={fileInputRef}
                            className="hidden"
                        />
                        <button
                            type="button"
                            onClick={() => fileInputRef.current?.click()}
                            className="p-3 bg-black/50 border border-cyan-500/30 rounded-lg text-cyan-500 hover:bg-cyan-500/10 transition-colors mb-[1px]"
                            title="Upload Image"
                        >
                            <PhotoIcon className="w-6 h-6" />
                        </button>

                        {/* Microphone Button */}
                        <button
                            type="button"
                            onClick={isListening ? stopListening : startListening}
                            className={`p-3 rounded-lg border transition-colors mb-[1px] ${isListening
                                ? 'bg-red-500/20 border-red-500 text-red-500 animate-pulse'
                                : 'bg-black/50 border-cyan-500/30 text-cyan-500 hover:bg-cyan-500/10'
                                }`}
                            title={isListening ? "Stop Listening" : "Start Voice Input"}
                        >
                            <MicrophoneIcon className="w-6 h-6" />
                        </button>

                        <div className="flex-1 flex flex-col gap-2">
                            {/* Image Preview */}
                            {selectedImage && (
                                <div className="relative inline-block w-fit">
                                    <img
                                        src={selectedImage}
                                        alt="Preview"
                                        className="h-16 w-auto rounded border border-cyan-500/50"
                                    />
                                    <button
                                        type="button"
                                        onClick={removeImage}
                                        className="absolute -top-2 -right-2 bg-red-500 text-white rounded-full p-0.5 hover:bg-red-600"
                                    >
                                        <XMarkIcon className="w-4 h-4" />
                                    </button>
                                </div>
                            )}

                            <input
                                type="text"
                                value={input}
                                onChange={(e) => setInput(e.target.value)}
                                placeholder={isListening ? "Listening..." : (mode === 'chat' ? "Ask Z3ube anything..." : "Enter a topic to research...")}
                                className="w-full bg-black/50 border border-cyan-500/30 rounded-lg px-4 py-3 text-cyan-400 placeholder-gray-500 focus:outline-none focus:border-cyan-500"
                                disabled={loading}
                            />
                        </div>

                        <button
                            type="submit"
                            disabled={loading || (!input.trim() && !selectedImage)}
                            className="px-6 py-3 bg-cyan-500 text-black font-bold rounded-lg hover-glow disabled:opacity-50 disabled:cursor-not-allowed mb-[1px]"
                        >
                            {mode === 'chat' ? 'Send' : 'Research'}
                        </button>
                    </div>
                </form>
            </div >
        </main >
    );
}

function MessageBubble({ message, onSpeak }: { message: Message; onSpeak: (text: string) => void }) {
    const isUser = message.role === 'user';

    return (
        <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}
        >
            <div
                className={`max-w-[85%] p-4 rounded-lg relative group ${isUser
                    ? 'bg-cyan-500 text-black'
                    : 'glass text-cyan-400 border border-cyan-500/20'
                    }`}
            >
                {/* Speaker Button (AI Only) */}
                {!isUser && (
                    <button
                        onClick={() => onSpeak(message.content)}
                        className="absolute -top-3 -right-3 p-1.5 bg-black/50 border border-cyan-500/30 rounded-full text-cyan-500 opacity-0 group-hover:opacity-100 transition-opacity hover:bg-cyan-500/20"
                        title="Read Aloud"
                    >
                        <SpeakerWaveIcon className="w-4 h-4" />
                    </button>
                )}

                {/* Image Attachment */}
                {message.image && (
                    <div className="mb-4">
                        <img src={message.image} alt="User Upload" className="max-w-full h-auto rounded-lg border border-black/20" />
                    </div>
                )}

                {/* Markdown Content */}
                <div className={`prose ${isUser ? 'prose-sm' : 'prose-invert'} max-w-none`}>
                    <ReactMarkdown
                        remarkPlugins={[remarkGfm]}
                        rehypePlugins={[rehypeHighlight]}
                        components={{
                            // Custom components for styling
                            code({ node, inline, className, children, ...props }: any) {
                                const match = /language-(\w+)/.exec(className || '')
                                return !inline && match ? (
                                    <div className="rounded-md overflow-hidden my-2 border border-gray-700">
                                        <div className="bg-gray-800 px-3 py-1 text-xs text-gray-400 border-b border-gray-700 flex justify-between">
                                            <span>{match[1]}</span>
                                        </div>
                                        <pre className={className}>
                                            <code {...props} className={className}>
                                                {children}
                                            </code>
                                        </pre>
                                    </div>
                                ) : (
                                    <code {...props} className="bg-gray-800 px-1 py-0.5 rounded text-sm text-pink-400">
                                        {children}
                                    </code>
                                )
                            }
                        }}
                    >
                        {message.content}
                    </ReactMarkdown>
                </div>

                {message.thinking_steps && message.thinking_steps.length > 0 && (
                    <details className="mt-4 text-sm opacity-70 border-t border-gray-700 pt-2">
                        <summary className="cursor-pointer hover:text-white transition-colors">
                            View reasoning process ({message.thinking_steps.length} steps)
                        </summary>
                        <div className="mt-2 space-y-2 pl-2 border-l-2 border-gray-700">
                            {message.thinking_steps.map((step, i) => (
                                <div key={i} className="text-xs">
                                    <strong className="text-matrix-green">Step {step.step}:</strong>
                                    <span className="ml-1 text-gray-300">{step.thought}</span>
                                </div>
                            ))}
                        </div>
                    </details>
                )}
            </div>
        </motion.div>
    );
}

function ExampleButton({
    text,
    onClick,
}: {
    text: string;
    onClick: (text: string) => void;
}) {
    return (
        <button
            onClick={() => onClick(text)}
            className="glass px-4 py-2 rounded-lg text-sm text-matrix-green hover-glow transition-all hover:scale-105"
        >
            {text}
        </button>
    );
}
