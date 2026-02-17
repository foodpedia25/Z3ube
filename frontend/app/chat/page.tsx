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
            const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
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
                            // Creating a copy of the last message to avoid direct mutation of state
                            // which causes duplication in React Strict Mode
                            const lastIndex = newMessages.length - 1;
                            const lastMessage = {
                                ...newMessages[lastIndex],
                                thinking_steps: [...(newMessages[lastIndex].thinking_steps || [])]
                            };
                            newMessages[lastIndex] = lastMessage;

                            if (data.type === 'content') {
                                lastMessage.content += data.data;
                            } else if (data.type === 'thought') {
                                // Add generic thought
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

    return (
        <main className="min-h-screen flex flex-col p-4 relative z-10">
            <div className="max-w-4xl mx-auto w-full flex flex-col h-screen">
                {/* Header */}
                <div className="py-6 text-center">
                    <h1 className="text-4xl font-bold glow-text animate-glow mb-2">
                        <span className="font-bold">Z<span className="text-cyan-500">3</span>ube</span> Chat
                    </h1>
                    <p className="text-gray-400">Powered by advanced AI reasoning</p>
                </div>

                {/* Messages Container */}
                <div className="flex-1 overflow-y-auto space-y-4 mb-4 px-4 custom-scrollbar">
                    {messages.length === 0 && (
                        <div className="text-center text-gray-400 mt-20">
                            <p className="text-xl mb-4">Start a conversation with <span className="font-bold">Z<span className="text-cyan-500">3</span>ube</span></p>
                            <div className="flex flex-wrap gap-2 justify-center">
                                <ExampleButton text="Explain quantum computing" onClick={setInput} />
                                <ExampleButton
                                    text="Generate Python code for a binary tree"
                                    onClick={setInput}
                                />
                                <ExampleButton
                                    text="Research the latest in AI"
                                    onClick={setInput}
                                />
                            </div>
                        </div>
                    )}

                    {messages.map((message, index) => (
                        <MessageBubble key={index} message={message} />
                    ))}

                    {loading && (
                        <div className="flex justify-start">
                            <div className="glass p-4 rounded-lg max-w-[80%]">
                                <div className="flex space-x-2">
                                    <div className="w-3 h-3 bg-cyan-500 rounded-full animate-bounce"></div>
                                    <div
                                        className="w-3 h-3 bg-cyan-500 rounded-full animate-bounce"
                                        style={{ animationDelay: '0.1s' }}
                                    ></div>
                                    <div
                                        className="w-3 h-3 bg-cyan-500 rounded-full animate-bounce"
                                        style={{ animationDelay: '0.2s' }}
                                    ></div>
                                </div>
                            </div>
                        </div>
                    )}

                    <div ref={messagesEndRef} />
                </div>

                {/* Input Form */}
                <form onSubmit={handleSubmit} className="glass p-4 rounded-lg space-y-3">
                    {/* Controls */}
                    <div className="flex justify-end items-center gap-4 text-sm mb-2">
                        <div className="flex items-center gap-2">
                            <label className="text-gray-400">Model:</label>
                            <select
                                value={selectedModel}
                                onChange={(e) => setSelectedModel(e.target.value)}
                                className="bg-black/50 border border-cyan-500/30 rounded px-2 py-1 text-cyan-400 focus:outline-none focus:border-cyan-500"
                                disabled={loading}
                            >
                                <option value="auto">Auto (Chain of Thought)</option>
                                <option value="openai">OpenAI (GPT-4o)</option>
                                <option value="anthropic">Anthropic (Claude 3.5)</option>
                                <option value="gemini">Gemini (Pro 1.5)</option>
                                <option value="llama">Llama 3.1 (Local)</option>
                            </select>
                        </div>
                        <div className="flex items-center gap-2">
                            <label className="text-gray-400">Reasoning Depth:</label>
                            <select
                                value={depth}
                                onChange={(e) => setDepth(e.target.value)}
                                className="bg-black/50 border border-cyan-500/30 rounded px-2 py-1 text-cyan-400 focus:outline-none focus:border-cyan-500"
                                disabled={loading}
                            >
                                <option value="quick">Quick (Fast)</option>
                                <option value="normal">Normal (Balanced)</option>
                                <option value="deep">Deep (Detailed)</option>
                            </select>
                        </div>
                    </div>

                    <div className="flex gap-2">
                        <input
                            type="text"
                            value={input}
                            onChange={(e) => setInput(e.target.value)}
                            placeholder="Ask Z3ube anything..."
                            className="flex-1 bg-black/50 border border-cyan-500/30 rounded-lg px-4 py-3 text-cyan-400 placeholder-gray-500 focus:outline-none focus:border-cyan-500"
                            disabled={loading}
                        />
                        <button
                            type="submit"
                            disabled={loading || !input.trim()}
                            className="px-6 py-3 bg-cyan-500 text-black font-bold rounded-lg hover-glow disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                            Send
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
