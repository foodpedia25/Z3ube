
import React from 'react';

export default function PrivacyPage() {
    return (
        <div className="min-h-screen bg-black text-white p-8 pt-24">
            <div className="max-w-4xl mx-auto">
                <h1 className="text-4xl font-bold mb-8 text-cyan-500">Privacy Policy</h1>

                <div className="space-y-6 text-gray-300">
                    <section>
                        <h2 className="text-2xl font-semibold mb-4 text-white">1. Data Collection</h2>
                        <p>We collect information you provide directly to us, such as when you create an account, use our chat services, or contact us for support. This may include your email address and chat history.</p>
                    </section>

                    <section>
                        <h2 className="text-2xl font-semibold mb-4 text-white">2. How We Use Your Data</h2>
                        <p>We use the collected data to provide, maintain, and improve our services, to develop new features, and to protect Z3ube and our users.</p>
                    </section>

                    <section>
                        <h2 className="text-2xl font-semibold mb-4 text-white">3. AI Processing</h2>
                        <p>User inputs to our AI models are processed to generate responses. We may use anonymized data to improve our model performance.</p>
                    </section>

                    <section>
                        <h2 className="text-2xl font-semibold mb-4 text-white">4. Data Sharing</h2>
                        <p>We do not share your personal information with third parties except as described in this policy or with your consent.</p>
                    </section>

                    <section>
                        <h2 className="text-2xl font-semibold mb-4 text-white">5. Security</h2>
                        <p>We take reasonable measures to help protect information about you from loss, theft, misuse and unauthorized access.</p>
                    </section>

                    <p className="mt-8 text-sm text-gray-500">Last updated: 2026</p>
                </div>
            </div>
        </div>
    );
}
