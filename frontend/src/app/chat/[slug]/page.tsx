"use client";

import { useState, useRef, useEffect, useCallback, useMemo } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Send, Sparkles, Bot, User, Moon, Sun } from "lucide-react";
import QRCode from "@/components/qr/qrcode";
import IframeExportButton from "@/components/iframe/iframe";

type Message = {
    id: number;
    role: "user" | "assistant";
    content: string;
    timestamp: Date;
    conversation_id?: string,
    agent_set_id?: string,
};

const initialMessages: Message[] = [
    {
        id: 1,
        role: "assistant",
        content: "Hey there! ✨ I'm here to help with anything you need. What's on your mind?",
        timestamp: new Date(Date.now() - 60000)
    },
    {
        id: 2,
        role: "user",
        content: "Can you tell me a joke?",
        timestamp: new Date(Date.now() - 30000)
    },
    {
        id: 3,
        role: "assistant",
        content: "Here's one for you: Why don't skeletons fight each other? They don't have the guts! 💀😂",
        timestamp: new Date()
    },
];

// Memoized message component for better performance
const MessageBubble = ({ msg, formatTime }: any) => {
    const isUser = msg.role === "user";

    return (
        <div className={`flex items-start gap-3 animate-fadeIn ${isUser ? "flex-row-reverse" : "flex-row"}`}>
            {/* Avatar */}
            <div className={`flex-shrink-0 w-9 h-9 rounded-xl flex items-center justify-center shadow-md transition-transform hover:scale-110 ${
                isUser
                    ? "bg-gradient-to-br from-violet-500 to-purple-600 text-white"
                    : "bg-gradient-to-br from-gray-100 to-gray-200 dark:from-gray-700 dark:to-gray-800 text-gray-600 dark:text-gray-300"
            }`}>
                {isUser ? <User className="w-4 h-4" /> : <Bot className="w-4 h-4" />}
            </div>

            {/* Message bubble */}
            <div className={`flex flex-col max-w-[70%] ${isUser ? "items-end" : "items-start"}`}>
                <div
                    className={`px-4 py-2.5 shadow-sm transition-all duration-200 hover:shadow-md ${
                        isUser
                            ? "bg-gradient-to-r from-violet-500 to-purple-600 text-white rounded-2xl rounded-tr-sm"
                            : "bg-white dark:bg-gray-800 text-gray-800 dark:text-gray-200 border border-gray-200 dark:border-gray-700 rounded-2xl rounded-tl-sm"
                    }`}
                >
                    <p className="text-[15px] leading-relaxed break-words">{msg.content}</p>
                </div>
                <span className="text-[11px] text-gray-500 dark:text-gray-400 mt-1 px-1">
                    {formatTime(msg.timestamp)}
                </span>
            </div>
        </div>
    );
};

export default function ChatPage(
    {
        params,
    }: {
        params: Promise<{ slug: string }>
    }
) {
    const [messages, setMessages] = useState<Message[]>(initialMessages);
    const [input, setInput] = useState("");
    const [isTyping, setIsTyping] = useState(false);
    const [isDark, setIsDark] = useState(false);
    const messagesEndRef = useRef<HTMLDivElement>(null);
    const scrollContainerRef = useRef<HTMLDivElement>(null);
    const inputRef = useRef<HTMLInputElement>(null);
    const [slug , setSlug] = useState("")
    const [conversationId , setConversationId] = useState("")

    useEffect(() => {
        const getSlug = async () => {
            const resolvedParams = await params;
            setSlug(resolvedParams.slug);
        };
        getSlug().then();
    }, [params]);

    console.log(slug)

    // Auto-scroll to bottom with smooth behavior
    const scrollToBottom = useCallback(() => {
        if (scrollContainerRef.current) {
            const { scrollHeight, clientHeight } = scrollContainerRef.current;
            scrollContainerRef.current.scrollTo({
                top: scrollHeight - clientHeight,
                behavior: 'smooth'
            });
        }
    }, []);

    useEffect(() => {
        scrollToBottom();
    }, [messages, scrollToBottom]);

    const sendMessage = useCallback(async () => {
        if (!input.trim()) return;

        const newMessage: Message = {
            id: Date.now(),
            role: "user",
            content: input.trim(),
            timestamp: new Date(),
        };

        setMessages(prev => [...prev, newMessage]);
        setInput("");
        setIsTyping(true);

        // Keep focus on input
        inputRef.current?.focus();

        // Send message to API
        const response = await fetch('/api/send', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                agent_set_id: slug,
                message: input.trim(),
                conversation_id: conversationId || undefined
            }),
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || 'Failed to send message');
        }

        // Update conversation_id if this is a new conversation
        if (data.conversation_id && !conversationId) {
            setConversationId(data.conversation_id);
        }

        const aiResponse: Message = {
            id: Date.now() + 1,
            role: "assistant",
            content: data.content,
            timestamp: new Date(),
        };

        setMessages(prev => [...prev, aiResponse]);
        setIsTyping(false);

    }, [input]);

    const formatTime = useCallback((date: Date) => {
        return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    }, []);

    const handleKeyDown = useCallback((e: React.KeyboardEvent) => {
        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            sendMessage().then();
        }
    }, [sendMessage]);

    // Memoize typing indicator component
    const TypingIndicator = useMemo(() => (
        isTyping ? (
            <div className="flex items-start gap-3 animate-fadeIn">
                <div className="flex-shrink-0 w-9 h-9 rounded-xl bg-gradient-to-br from-gray-100 to-gray-200 dark:from-gray-700 dark:to-gray-800 text-gray-600 dark:text-gray-300 flex items-center justify-center shadow-md">
                    <Bot className="w-4 h-4" />
                </div>
                <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-2xl rounded-tl-sm px-4 py-3 shadow-sm">
                    <div className="flex space-x-1.5">
                        <div className="w-2 h-2 bg-gray-400 dark:bg-gray-500 rounded-full animate-typing"></div>
                        <div className="w-2 h-2 bg-gray-400 dark:bg-gray-500 rounded-full animate-typing animation-delay-200"></div>
                        <div className="w-2 h-2 bg-gray-400 dark:bg-gray-500 rounded-full animate-typing animation-delay-400"></div>
                    </div>
                </div>
            </div>
        ) : null
    ), [isTyping]);

    return (
        <div
            className={`min-h-screen transition-colors duration-300 ${isDark ? 'dark bg-gray-950' : 'bg-gradient-to-br from-gray-50 via-purple-50 to-pink-50'}`}>
            <div className="fixed bottom-4 right-4 z-50">
                <div
                    className="p-2 bg-white dark:bg-gray-900 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700">
                    <QRCode data={`https://ai-agent-builder-one.vercel.app/chat/${slug}`}/>
                </div>
            </div>

            <div className="min-h-screen flex items-center justify-center p-4">
                {/* Animated background gradients */}
                <div className="fixed inset-0 overflow-hidden pointer-events-none">
                <div
                        className="absolute top-1/4 -left-1/4 w-96 h-96 bg-purple-400/10 rounded-full blur-3xl animate-float"></div>
                    <div
                        className="absolute bottom-1/4 -right-1/4 w-96 h-96 bg-pink-400/10 rounded-full blur-3xl animate-float animation-delay-2000"></div>
                    <div
                        className="absolute top-3/4 left-1/2 w-64 h-64 bg-violet-400/10 rounded-full blur-3xl animate-float animation-delay-4000"></div>
                </div>

                <Card
                    className="w-full max-w-4xl h-[85vh] flex flex-col backdrop-blur-xl bg-white/90 dark:bg-gray-900/90 border-0 shadow-2xl rounded-3xl overflow-hidden relative">
                    {/* Header */}
                    <div
                        className="bg-gradient-to-r from-red-500 to-purple-500 p-4 sm:p-5 text-white relative overflow-hidden">
                        {/* Animated gradient overlay */}
                        <div
                            className="absolute inset-0 bg-gradient-to-r from-transparent via-white/10 to-transparent animate-shimmer"></div>

                        <div className="flex items-center justify-between relative z-10">
                            <div className="flex items-center gap-3">
                                <div className="relative">
                                    <div
                                        className="w-12 h-12 bg-white/20 backdrop-blur-md rounded-2xl flex items-center justify-center shadow-lg">
                                        <Sparkles className="w-6 h-6 text-white"/>
                                    </div>
                                    <div
                                        className="absolute -bottom-1 -right-1 w-4 h-4 bg-green-400 rounded-full border-2 border-white animate-pulse shadow-lg"></div>
                                </div>
                                <div>
                                    <h1 className="text-xl sm:text-2xl font-bold tracking-tight">AI Assistant</h1>
                                    <p className="text-purple-100 text-xs sm:text-sm opacity-90">Always here to help</p>
                                </div>
                            </div>

                            <div className="flex flex-row gap-2 items-center">
                            <IframeExportButton
                                slug={slug}
                                baseUrl={process.env.NEXT_PUBLIC_BASE_URL || "https://ai-agent-builder-one.vercel.app"}
                            />

                            {/* Dark mode toggle */}
                            <Button
                                onClick={() => setIsDark(!isDark)}
                                className="w-10 h-10 rounded-xl bg-white/20 backdrop-blur-md hover:bg-white/30 transition-all duration-200"
                                aria-label="Toggle dark mode"
                            >
                                {isDark ? <Sun className="w-5 h-5"/> : <Moon className="w-5 h-5"/>}
                            </Button>
                            </div>
                        </div>
                    </div>

                    {/* Messages container with fixed height */}
                    <CardContent
                        ref={scrollContainerRef}
                        className="flex-1 overflow-y-auto overflow-x-hidden p-4 sm:p-6 space-y-4 scrollbar-thin scrollbar-thumb-gray-300 dark:scrollbar-thumb-gray-700 scrollbar-track-transparent"
                        style={{height: 'calc(100% - 140px)'}}
                    >
                        {messages.map((msg) => (
                            <MessageBubble key={msg.id} msg={msg} formatTime={formatTime}/>
                        ))}

                        {TypingIndicator}

                        <div ref={messagesEndRef} className="h-1"/>
                    </CardContent>

                    {/* Input area with fixed position */}
                    <div
                        className="p-4 sm:p-5 border-t border-gray-200 dark:border-gray-800 bg-white/80 dark:bg-gray-900/80 backdrop-blur-lg">
                        <div className="flex gap-2 sm:gap-3 items-end">
                            <Input
                                ref={inputRef}
                                placeholder="Type your message..."
                                value={input}
                                onChange={(e) => setInput(e.target.value)}
                                onKeyDown={handleKeyDown}
                                className="flex-1 min-h-[48px] px-4 py-3 text-[15px] border-gray-200 dark:border-gray-700 rounded-2xl bg-white/90 dark:bg-gray-800/90 backdrop-blur-sm focus:ring-2 focus:ring-purple-500/30 focus:border-purple-400 transition-all duration-200 placeholder:text-gray-400 dark:placeholder:text-gray-500 resize-none"
                                disabled={isTyping}
                                autoFocus
                            />
                            <Button
                                onClick={sendMessage}
                                disabled={!input.trim() || isTyping}
                                className="h-12 w-12 rounded-2xl bg-gradient-to-r from-violet-600 to-purple-600 hover:from-violet-700 hover:to-purple-700 shadow-lg transition-all duration-200 hover:scale-105 hover:shadow-xl disabled:opacity-50 disabled:hover:scale-100 disabled:hover:shadow-lg"
                                aria-label="Send message"
                            >
                                <Send className="w-5 h-5"/>
                            </Button>
                        </div>
                    </div>
                </Card>
            </div>

            <style jsx global>{`
                @keyframes fadeIn {
                    from {
                        opacity: 0;
                        transform: translateY(10px);
                    }
                    to {
                        opacity: 1;
                        transform: translateY(0);
                    }
                }

                @keyframes typing {
                    0%, 60%, 100% {
                        transform: translateY(0);
                        opacity: 0.5;
                    }
                    30% {
                        transform: translateY(-10px);
                        opacity: 1;
                    }
                }

                @keyframes float {
                    0%, 100% {
                        transform: translate(0, 0) scale(1);
                    }
                    25% {
                        transform: translate(30px, -30px) scale(1.05);
                    }
                    50% {
                        transform: translate(-20px, 20px) scale(0.95);
                    }
                    75% {
                        transform: translate(20px, -10px) scale(1.02);
                    }
                }

                @keyframes shimmer {
                    0% {
                        transform: translateX(-100%);
                    }
                    100% {
                        transform: translateX(200%);
                    }
                }

                .animate-fadeIn {
                    animation: fadeIn 0.3s ease-out;
                }

                .animate-typing {
                    animation: typing 1.4s infinite;
                }

                .animate-float {
                    animation: float 20s infinite ease-in-out;
                }

                .animate-shimmer {
                    animation: shimmer 3s infinite;
                }

                .animation-delay-200 {
                    animation-delay: 200ms;
                }

                .animation-delay-400 {
                    animation-delay: 400ms;
                }

                .animation-delay-2000 {
                    animation-delay: 2s;
                }

                .animation-delay-4000 {
                    animation-delay: 4s;
                }

                /* Custom scrollbar styles */
                .scrollbar-thin::-webkit-scrollbar {
                    width: 6px;
                }

                .scrollbar-thumb-gray-300::-webkit-scrollbar-thumb {
                    background-color: rgb(209 213 219);
                    border-radius: 3px;
                }

                .dark .scrollbar-thumb-gray-700::-webkit-scrollbar-thumb {
                    background-color: rgb(55 65 81);
                }

                .scrollbar-track-transparent::-webkit-scrollbar-track {
                    background-color: transparent;
                }

                /* Smooth scrolling */
                * {
                    scroll-behavior: smooth;
                }
            `}</style>

        </div>
    );
}