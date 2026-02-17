/** @type {import('tailwindcss').Config} */
module.exports = {
    content: [
        './pages/**/*.{js,ts,jsx,tsx,mdx}',
        './components/**/*.{js,ts,jsx,tsx,mdx}',
        './app/**/*.{js,ts,jsx,tsx,mdx}',
    ],
    theme: {
        extend: {
            colors: {
                'matrix-green': '#00ff41',
                'matrix-dark': '#0d0208',
                'neon-blue': '#00d9ff',
                'neon-pink': '#ff006e',
                'cyan-400': '#22d3ee',
                'cyan-500': '#06b6d4',
            },
            animation: {
                'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
                'glow': 'glow 2s ease-in-out infinite alternate',
                'spin-slow': 'spin 10s linear infinite',
                'fade-in-up': 'fadeInUp 0.8s ease-out forwards',
            },
            keyframes: {
                glow: {
                    '0%': { textShadow: '0 0 10px #22d3ee, 0 0 20px #22d3ee' },
                    '100%': { textShadow: '0 0 20px #22d3ee, 0 0 30px #22d3ee, 0 0 40px #22d3ee' },
                },
                fadeInUp: {
                    '0%': { opacity: '0', transform: 'translateY(20px)' },
                    '100%': { opacity: '1', transform: 'translateY(0)' },
                }
            }
        },
    },
    plugins: [],
}
