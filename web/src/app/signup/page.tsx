'use client';

import Image from 'next/image';
import Link from 'next/link';
import { useState } from 'react';

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

    return (
        <div className="min-h-screen bg-gradient-to-br from-blue-500 to-purple-700 flex flex-col items-center justify-center px-4 py-12 sm:px-6 lg:px-8">
            <div className="max-w-md w-full space-y-8 bg-white p-10 rounded-xl shadow-2xl">
                <div>
                    <Link href="/" className="block">
                        <h1 className="text-4xl font-bold text-center text-gray-800">
                            Track<span className="text-blue-500">Flow</span>
                        </h1>
                    </Link>
                    <h2 className="mt-6 text-center text-2xl font-semibold text-gray-800">
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
                        className="appearance-none rounded-lg relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 focus:z-10 sm:text-sm"
                    />
                    <button
                        type="submit"
                        className="group relative w-full flex justify-center py-3 px-4 border border-transparent text-sm font-medium rounded-lg text-white bg-blue-500 hover:bg-blue-400 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition duration-150 ease-in-out"
                    >
                        <span className="absolute left-0 inset-y-0 flex items-center pl-3">
                            <Image src="/strava-icon.png" alt="Strava Logo" width={20} height={20} />
                        </span>
                        Sign up with Strava
                    </button>
                </form>
            </div>
        </div>
    );
}
