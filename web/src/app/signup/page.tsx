'use client';

import Image from 'next/image';
import Link from 'next/link';
import { useState } from 'react';
import { motion } from 'framer-motion';
import Navbar from '../components/Navbar';

/**
 * SignUpPage component for user registration
 * @returns JSX.Element
 */
export default function SignUpPage(): JSX.Element {
    const [email, setEmail] = useState<string>('');

    const handleSignUp = (event: React.FormEvent): void => {
        event.preventDefault();
        localStorage.setItem('email', email);
        const isDevelopment = process.env.NODE_ENV === 'development';
        const redirectUri = `https://www.trackflow.xyz/verify${isDevelopment ? '?env=dev' : ''}`;
        const stravaAuthUrl = `https://www.strava.com/oauth/authorize?client_id=95101&redirect_uri=${encodeURIComponent(redirectUri)}&response_type=code&approval_prompt=auto&scope=read_all,profile:read_all,activity:read_all`;
        window.location.href = stravaAuthUrl;
    };

    const fadeInUp = {
        initial: { opacity: 0, y: 20 },
        animate: { opacity: 1, y: 0 },
        transition: { duration: 0.6 }
    };

    return (
        <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 text-gray-100 flex flex-col">
            <Navbar />
            <div className="flex-grow flex items-center justify-center px-4 py-12 sm:px-6 lg:px-8">
                <motion.div 
                    className="max-w-md w-full space-y-8 bg-gray-800 p-10 rounded-xl shadow-2xl"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ duration: 1 }}
                >
                    <div>
                        <Link href="/" className="block">
                            <h1 className="text-6xl font-extrabold text-center tracking-tight">
                                <span className="text-blue-300">Track</span><span className="text-blue-500">Flow</span>
                            </h1>
                        </Link>
                        <h2 className="mt-6 text-center text-2xl font-semibold text-gray-100">
                            Elevate Your Running Game
                        </h2>
                    </div>
                    <form className="mt-8 space-y-6" onSubmit={handleSignUp}>
                        <input
                            type="email"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            placeholder="Enter your email"
                            required
                            className="appearance-none rounded-lg relative block w-full px-3 py-2 border border-gray-600 bg-gray-700 placeholder-gray-400 text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 focus:z-10 sm:text-sm"
                        />
                        <div className="flex justify-center">
                            <motion.button
                                type="submit"
                                className="w-full flex justify-center py-3 px-4 text-xl font-bold rounded-full text-gray-200 bg-blue-600 hover:bg-blue-700 transition duration-300 ease-in-out shadow-lg hover:shadow-blue-500/50"
                                whileHover={{ scale: 1.05 }}
                                whileTap={{ scale: 0.95 }}
                            >
                                Sign Up with Strava
                                <span className="ml-2 my-auto">
                                    <Image src="/strava-icon.png" alt="Strava Logo" width={20} height={20} />
                                </span>
                            </motion.button>
                        </div>
                    </form>
                </motion.div>
            </div>
        </div>
    );
}
