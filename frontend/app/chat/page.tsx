'use client';

import { useState, useRef, useEffect } from 'react';
import { motion } from 'framer-motion';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import rehypeHighlight from 'rehype-highlight';
import 'highlight.js/styles/github-dark.css';

interface Message {
    role: 'user' | 'assistant';
    content: string;
    thinking_steps?: any[];
}

export default function ChatPage() {
    const [messages, setMessages] = useState<Message[]>([]);
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);
    const [mode, setMode] = useState<'chat' | 'research'>('chat');
    const [researchResult, setResearchResult] = useState<any>(null);

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

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!input.trim() || loading) return;

        const userMessage: Message = { role: 'user', content: input };
        setMessages((prev) => [...prev, userMessage]);
        setInput('');
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
                    message: input,
                    depth: depth,
                    model: selectedModel
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
                                lastMessage.thinking_steps.push(data.data);
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

            const data = await response.json();
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
                        <MessageBubble key={index} message={message} />
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
                                    {researchResult.sources.map((source: any, i: number) => (
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

                    <div className="flex gap-2">
                        <input
                            type="text"
                            value={input}
                            onChange={(e) => setInput(e.target.value)}
                            placeholder={mode === 'chat' ? "Ask Z3ube anything..." : "Enter a topic to research..."}
                            className="flex-1 bg-black/50 border border-cyan-500/30 rounded-lg px-4 py-3 text-cyan-400 placeholder-gray-500 focus:outline-none focus:border-cyan-500"
                            disabled={loading}
                        />
                        <button
                            type="submit"
                            disabled={loading || !input.trim()}
                            className="px-6 py-3 bg-cyan-500 text-black font-bold rounded-lg hover-glow disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                            {mode === 'chat' ? 'Send' : 'Research'}
                        </button>
                    </div>
                </form>
            </div >
        </main >
    );
}

function MessageBubble({ message }: { message: Message }) {
    const isUser = message.role === 'user';

    return (
        <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}
        >
            <div
                className={`max-w-[85%] p-4 rounded-lg ${isUser
                    ? 'bg-cyan-500 text-black'
                    : 'glass text-cyan-400 border border-cyan-500/20'
                    }`}
            >
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
