
import React from 'react';

export default function CookiesPage() {
    return (
        <div className="min-h-screen bg-black text-white p-8 pt-24">
            <div className="max-w-4xl mx-auto">
                <h1 className="text-4xl font-bold mb-8 text-cyan-500">Cookies Policy</h1>

                <div className="space-y-6 text-gray-300">
                    <section>
                        <h2 className="text-2xl font-semibold mb-4 text-white">1. What Are Cookies?</h2>
                        <p>Cookies are small text files that are stored on your computer or mobile device when you visit a website. They are widely used to make websites work more efficiently and to provide information to the owners of the site.</p>
                    </section>

                    <section>
                        <h2 className="text-2xl font-semibold mb-4 text-white">2. How We Use Cookies</h2>
                        <p>We use cookies to understand how you interact with our website, to personalize your experience, and to remember your preferences.</p>
                    </section>

                    <section>
                        <h2 className="text-2xl font-semibold mb-4 text-white">3. Types of Cookies</h2>
                        <ul className="list-disc pl-5 mt-2 space-y-2">
                            <li><strong>Essential Cookies:</strong> Necessary for the website to function correctly.</li>
                            <li><strong>Analytics Cookies:</strong> Help us understand how visitors interact with the website.</li>
                            <li><strong>Functionality Cookies:</strong> Allow the website to remember choices you make.</li>
                        </ul>
                    </section>

                    <section>
                        <h2 className="text-2xl font-semibold mb-4 text-white">4. Managing Cookies</h2>
                        <p>You can control and/or delete cookies as you wish. You can delete all cookies that are already on your computer and you can set most browsers to prevent them from being placed.</p>
                    </section>

                    <p className="mt-8 text-sm text-gray-500">Last updated: 2026</p>
                </div>
            </div>
        </div>
    );
}
