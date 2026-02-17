'use client';

import { useState, useRef, useEffect } from 'react';
import { motion } from 'framer-motion';

interface Message {
    role: 'user' | 'assistant';
    content: string;
    thinking_steps?: any[];
}

export default function ChatPage() {
    const [messages, setMessages] = useState<Message[]>([]);
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);
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

        try {
            const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
            const response = await fetch(`${apiUrl}/chat`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: input,
                }),
            });

            if (!response.ok) throw new Error('Failed to get response');

            const data = await response.json();
            const assistantMessage: Message = {
                role: 'assistant',
                content: data.response,
                thinking_steps: data.thinking_steps,
            };

            setMessages((prev) => [...prev, assistantMessage]);
        } catch (error) {
            console.error('Error:', error);
            const errorMessage: Message = {
                role: 'assistant',
                content: 'Sorry, I encountered an error. Please try again.',
            };
            setMessages((prev) => [...prev, errorMessage]);
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
                        Z3ube Chat
                    </h1>
                    <p className="text-gray-400">Powered by advanced AI reasoning</p>
                </div>

                {/* Messages Container */}
                <div className="flex-1 overflow-y-auto space-y-4 mb-4 px-4">
                    {messages.length === 0 && (
                        <div className="text-center text-gray-400 mt-20">
                            <p className="text-xl mb-4">Start a conversation with Z3ube</p>
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
                                    <div className="w-3 h-3 bg-matrix-green rounded-full animate-bounce"></div>
                                    <div
                                        className="w-3 h-3 bg-matrix-green rounded-full animate-bounce"
                                        style={{ animationDelay: '0.1s' }}
                                    ></div>
                                    <div
                                        className="w-3 h-3 bg-matrix-green rounded-full animate-bounce"
                                        style={{ animationDelay: '0.2s' }}
                                    ></div>
                                </div>
                            </div>
                        </div>
                    )}

                    <div ref={messagesEndRef} />
                </div>

                {/* Input Form */}
                <form onSubmit={handleSubmit} className="glass p-4 rounded-lg">
                    <div className="flex gap-2">
                        <input
                            type="text"
                            value={input}
                            onChange={(e) => setInput(e.target.value)}
                            placeholder="Ask Z3ube anything..."
                            className="flex-1 bg-black/50 border border-matrix-green/30 rounded-lg px-4 py-3 text-matrix-green placeholder-gray-500 focus:outline-none focus:border-matrix-green"
                            disabled={loading}
                        />
                        <button
                            type="submit"
                            disabled={loading || !input.trim()}
                            className="px-6 py-3 bg-matrix-green text-black font-bold rounded-lg hover-glow disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                            Send
                        </button>
                    </div>
                </form>
            </div>
        </main>
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
                className={`max-w-[80%] p-4 rounded-lg ${isUser
                        ? 'bg-matrix-green text-black'
                        : 'glass text-matrix-green border border-matrix-green/20'
                    }`}
            >
                <p className="whitespace-pre-wrap">{message.content}</p>

                {message.thinking_steps && message.thinking_steps.length > 0 && (
                    <details className="mt-2 text-sm opacity-70">
                        <summary className="cursor-pointer">View reasoning steps</summary>
                        <div className="mt-2 space-y-1">
                            {message.thinking_steps.map((step, i) => (
                                <div key={i} className="text-xs">
                                    <strong>Step {step.step}:</strong> {step.thought}
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
            className="glass px-4 py-2 rounded-lg text-sm text-matrix-green hover-glow"
        >
            {text}
        </button>
    );
}
