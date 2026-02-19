"use client";

import Link from "next/link";
import { SignInButton, SignedIn, SignedOut, UserButton } from "@clerk/nextjs";

export default function Navbar() {
    return (
        <nav className="fixed top-0 left-0 right-0 z-50 border-b border-white/10 bg-black/50 backdrop-blur-md">
            <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
                {/* Logo */}
                <Link href="/" className="flex items-center space-x-2">
                    <span className="text-2xl font-bold tracking-tighter text-white">
                        Z<span className="text-cyan-500">3</span>ube
                    </span>
                </Link>

                {/* Navigation Links */}
                <div className="hidden md:flex items-center space-x-6">
                    <Link href="/chat" className="text-sm font-medium text-gray-300 hover:text-cyan-400 transition-colors">
                        Chat
                    </Link>
                    <Link href="/dashboard" className="text-sm font-medium text-gray-300 hover:text-cyan-400 transition-colors">
                        Dashboard
                    </Link>
                    <Link href="/robotics" className="text-sm font-medium text-gray-300 hover:text-cyan-400 transition-colors">
                        Robotics
                    </Link>
                </div>

                {/* Auth Buttons */}
                <div className="flex items-center gap-4">
                    <SignedOut>
                        <SignInButton mode="modal">
                            <button className="rounded-full bg-white/10 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-white/20">
                                Sign In
                            </button>
                        </SignInButton>
                    </SignedOut>
                    <SignedIn>
                        <UserButton
                            appearance={{
                                elements: {
                                    avatarBox: "h-9 w-9 border-2 border-cyan-500/50"
                                }
                            }}
                        />
                    </SignedIn>
                </div>
            </div>
        </nav>
    );
}
