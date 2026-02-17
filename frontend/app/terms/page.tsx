
import React from 'react';

export default function TermsPage() {
    return (
        <div className="min-h-screen bg-black text-white p-8 pt-24">
            <div className="max-w-4xl mx-auto">
                <h1 className="text-4xl font-bold mb-8 text-cyan-500">Terms and Conditions</h1>

                <div className="space-y-6 text-gray-300">
                    <section>
                        <h2 className="text-2xl font-semibold mb-4 text-white">1. Introduction</h2>
                        <p>Welcome to Z3ube. By accessing our website and using our AI services, you agree to bound by these Terms and Conditions. Please read them carefully.</p>
                    </section>

                    <section>
                        <h2 className="text-2xl font-semibold mb-4 text-white">2. Use of Service</h2>
                        <p>Z3ube provides advanced AI reasoning capabilities. You agree to use these services only for lawful purposes and in accordance with these Terms.</p>
                    </section>

                    <section>
                        <h2 className="text-2xl font-semibold mb-4 text-white">3. Intellectual Property</h2>
                        <p>The content, features, and functionality of Z3ube are owned by Z3ube and are protected by international copyright, trademark, and other intellectual property laws.</p>
                    </section>

                    <section>
                        <h2 className="text-2xl font-semibold mb-4 text-white">4. User Content</h2>
                        <p>You retain rights to any content you submit to our AI services. However, by submitting content, you grant Z3ube a license to use, store, and process such content for the purpose of providing the service.</p>
                    </section>

                    <section>
                        <h2 className="text-2xl font-semibold mb-4 text-white">5. Limitation of Liability</h2>
                        <p>Z3ube shall not be liable for any indirect, incidental, special, consequential or punitive damages resulting from your use of the service.</p>
                    </section>

                    <p className="mt-8 text-sm text-gray-500">Last updated: 2026</p>
                </div>
            </div>
        </div>
    );
}
