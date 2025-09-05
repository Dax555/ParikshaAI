'use client';

import React, { useState, useEffect, useCallback, useMemo } from 'react';

// --- Configuration ---
const BACKEND_URL = "http://10.1.89.131:10002"; // Your FastAPI backend port
const GENERATE_URL = `${BACKEND_URL}/exam/generate`;
const SUBMIT_CODE_URL = `${BACKEND_URL}/exam/submit_code`;
const EXAM_DURATION_SECONDS = 600; // 10 minutes

// --- Helper Components ---

// Simple SVG Icon for the title
const LightningIcon = () => (
    <svg xmlns="http://www.w3.org/2000/svg" width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="inline-block mr-2 text-yellow-500">
        <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"></polygon>
    </svg>
);

// Confetti component for the success screen
const Confetti = () => {
    const confettiCount = 150;
    const colors = ['#f44336', '#e91e63', '#9c27b0', '#673ab7', '#3f51b5', '#2196f3', '#03a9f4', '#00bcd4', '#009688', '#4caf50', '#8bc34a', '#cddc39', '#ffeb3b', '#ffc107', '#ff9800', '#ff5722'];

    const particles = useMemo(() => {
        const tempParticles = [];
        for (let i = 0; i < confettiCount; i++) {
            tempParticles.push({
                color: colors[Math.floor(Math.random() * colors.length)],
                left: `${Math.random() * 100}%`,
                top: `${-20 + Math.random() * -80}%`, // Start above the screen
                animationDuration: `${2 + Math.random() * 3}s`,
                animationDelay: `${Math.random() * 5}s`,
                transform: `rotate(${Math.random() * 360}deg)`,
                size: `${Math.floor(Math.random() * (12 - 7 + 1)) + 7}px`
            });
        }
        return tempParticles;
    }, []);

    return (
        <div className="absolute top-0 left-0 w-full h-full overflow-hidden pointer-events-none z-50">
            {particles.map((p, i) => (
                <div
                    key={i}
                    className="absolute rounded-full animate-fall"
                    style={{
                        backgroundColor: p.color,
                        left: p.left,
                        top: p.top,
                        width: p.size,
                        height: p.size,
                        transform: p.transform,
                        animationDuration: p.animationDuration,
                        animationDelay: p.animationDelay,
                    }}
                />
            ))}
            <style jsx>{`
                @keyframes fall {
                    to {
                        transform: translateY(100vh) rotate(720deg);
                        opacity: 0;
                    }
                }
                .animate-fall {
                    animation-name: fall;
                    animation-timing-function: linear;
                    animation-iteration-count: infinite;
                }
            `}</style>
        </div>
    );
};


// --- Main Application Component ---
export default function ExamPage() {
    // --- State Management ---
    const [page, setPage] = useState('start'); // 'start', 'exam', 'submitted'
    const [fullName, setFullName] = useState('');
    const [question, setQuestion] = useState('Loading question...');
    const [answer, setAnswer] = useState('');
    const [timeLeft, setTimeLeft] = useState(EXAM_DURATION_SECONDS);
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [error, setError] = useState('');

    // --- Submission Logic ---
    const submitAnswer = useCallback(async (reason = "") => {
        if (isSubmitting) return;

        setIsSubmitting(true);
        if (reason === "tab_switch") {
            setError("Tab switched! To prevent cheating, your answer is being automatically submitted.");
        } else if (reason === "time_up") {
            setError("Time is up! Auto-submitting your answer...");
        }

        try {
            const payload = {
                full_name: fullName,
                code_answer: answer,
                question: question,
            };
            const response = await fetch(SUBMIT_CODE_URL, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            if (!response.ok) {
                throw new Error(`Server responded with status: ${response.status}`);
            }
            setPage('submitted');
        } catch (err) {
            setError(`Submission failed: ${err.message}. Please try again.`);
            setIsSubmitting(false); // Re-enable button on failure
        }
    }, [answer, fullName, question, isSubmitting]);

    // --- Timer Logic ---
    useEffect(() => {
        if (page !== 'exam') return;

        if (timeLeft <= 0) {
            submitAnswer("time_up");
            return;
        }

        const timerId = setInterval(() => {
            setTimeLeft(prevTime => prevTime - 1);
        }, 1000);

        return () => clearInterval(timerId);
    }, [page, timeLeft, submitAnswer]);

    // --- Anti-Cheating: Tab Switch Detection ---
    useEffect(() => {
        if (page !== 'exam') return;

        const handleVisibilityChange = () => {
            if (document.visibilityState === 'hidden') {
                submitAnswer("tab_switch");
            }
        };

        document.addEventListener('visibilitychange', handleVisibilityChange);

        return () => {
            document.removeEventListener('visibilitychange', handleVisibilityChange);
        };
    }, [page, submitAnswer]);

    // --- Event Handlers ---
    const handleStartExam = async () => {
        if (!fullName.trim()) {
            setError("Please enter your name before starting.");
            return;
        }
        setError('');
        setIsSubmitting(true);

        try {
            const response = await fetch(GENERATE_URL, { method: 'POST' });
            if (!response.ok) throw new Error(`Server returned status: ${response.status}`);

            const data = await response.json();
            setQuestion(data.code_question || "⚠️ No question received.");
            setPage('exam');
        } catch (err) {
            setError(`⚠️ Connection Error: Could not start the exam. ${err.message}`);
        } finally {
            setIsSubmitting(false);
        }
    };

    const formatTime = (seconds) => {
        const mins = Math.floor(seconds / 60);
        const secs = seconds % 60;
        return `${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;
    };

    // --- Render Logic ---
    const renderPage = () => {
        switch (page) {
            case 'start':
                return (
                    <div className="w-full max-w-lg mx-auto">
                        <div className="bg-white p-8 rounded-lg shadow-md border border-gray-200">
                            <h2 className="text-2xl font-bold text-center text-gray-800 mb-4">Welcome to the Exam</h2>
                            <p className="text-center text-gray-600 mb-6">Please enter your full name to begin. You will have 10 minutes to complete the challenge.</p>
                            <input
                                type="text"
                                value={fullName}
                                onChange={(e) => setFullName(e.target.value)}
                                placeholder="e.g., Ada Lovelace"
                                className="w-full px-4 py-2 mb-4 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-teal-500"
                            />
                            {error && <p className="text-red-500 text-sm mb-4 text-center">{error}</p>}
                            <button
                                onClick={handleStartExam}
                                disabled={isSubmitting}
                                className="w-full bg-slate-800 text-white font-bold py-3 px-4 rounded-lg hover:bg-teal-500 transition-colors duration-300 disabled:bg-gray-400"
                            >
                                {isSubmitting ? 'Generating...' : 'Start Exam'}
                            </button>
                        </div>
                    </div>
                );
            case 'exam':
                return (
                    <div className="grid grid-cols-1 md:grid-cols-5 gap-8 w-full max-w-7xl mx-auto">
                        {/* Left Column: Solution */}
                        <div className="md:col-span-3 bg-white p-6 rounded-lg shadow-md border border-gray-200">
                             <h3 className="text-xl font-bold text-gray-800 mb-2">📝 Your Solution</h3>
                             <p className="text-sm text-gray-500 mb-4">Candidate: <strong>{fullName}</strong></p>
                             <textarea
                                 value={answer}
                                 onChange={(e) => setAnswer(e.target.value)}
                                 placeholder="Enter your shell script code here..."
                                 className="w-full h-96 p-4 border border-gray-300 rounded-md font-mono text-sm focus:outline-none focus:ring-2 focus:ring-teal-500"
                             />
                             {error && <p className="text-red-500 text-sm mt-4 text-center">{error}</p>}
                             <button
                                 onClick={() => submitAnswer('manual')}
                                 disabled={isSubmitting}
                                 className="mt-4 w-full bg-slate-800 text-white font-bold py-3 px-4 rounded-lg hover:bg-teal-500 transition-colors duration-300 disabled:bg-gray-400"
                             >
                                 {isSubmitting ? 'Submitting...' : 'Submit Final Answer'}
                             </button>
                        </div>
                        {/* Right Column: Status & Question */}
                        <div className="md:col-span-2 space-y-8">
                             <div className="bg-white p-6 rounded-lg shadow-md border border-gray-200">
                                 <h3 className="text-xl font-bold text-gray-800 mb-2">⏳ Status & Timer</h3>
                                 <p className="text-5xl font-bold text-teal-500 text-center my-4">{formatTime(timeLeft)}</p>
                                 <div className="w-full bg-gray-200 rounded-full h-2.5">
                                    <div className="bg-teal-500 h-2.5 rounded-full" style={{ width: `${(1 - timeLeft / EXAM_DURATION_SECONDS) * 100}%` }}></div>
                                 </div>
                             </div>
                             <div className="bg-white p-6 rounded-lg shadow-md border border-gray-200">
                                 <h3 className="text-xl font-bold text-gray-800 mb-4">🎯 Problem Description</h3>
                                 <div className="bg-teal-50 border border-teal-200 text-teal-800 p-4 rounded-md text-sm">
                                    <span className="font-bold">📌 Note:</span> {question}
                                 </div>
                             </div>
                        </div>
                    </div>
                );
            case 'submitted':
                return (
                     <div className="w-full max-w-2xl mx-auto text-center">
                        <Confetti />
                        <div className="bg-white p-10 rounded-lg shadow-xl border border-gray-200">
                           <p className="text-2xl font-bold text-green-600 mb-4">🎉 Thank You!</p>
                           <p className="text-gray-700 text-lg mb-2">Your submission has been recorded successfully.</p>
                           <h2 className="text-xl text-gray-800 font-semibold mt-6">The exam is now complete. You may close this window.</h2>
                        </div>
                     </div>
                );
            default:
                return null;
        }
    };

    return (
        <main className="flex min-h-screen flex-col items-center justify-center p-4 sm:p-8 md:p-12 bg-gray-100 font-sans">
            <div className="text-center mb-8">
                <h1 className="text-4xl font-bold text-gray-800 flex items-center justify-center">
                    <LightningIcon />
                    CodeCraft Online Exam
                </h1>
                <p className="text-lg text-gray-600 mt-2">Assess Your Shell Scripting Skills</p>
            </div>
            <div className="w-full flex items-center justify-center">
                {renderPage()}
            </div>
        </main>
    );
}
