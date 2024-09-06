// src/app/components/DashboardNavbar.tsx
import Link from 'next/link';
import { useState } from 'react';

export default function DashboardNavbar(): JSX.Element {
    const [isMenuOpen, setIsMenuOpen] = useState<boolean>(false);

    return (
        <>
            <nav className="fixed top-0 w-full bg-gray-100 bg-opacity-75 text-gray-700 z-10">
                <div className="px-4 sm:px-6">
                    <div className="flex justify-between h-16">
                        <div className="flex-shrink-0 flex items-center">
                            <Link href="/dashboard" className="text-2xl sm:text-4xl font-bold hover:text-gray-500 transition duration-300 ease-in-out">
                                Dashboard
                            </Link>
                        </div>
                        <div className="hidden sm:flex items-center justify-end flex-grow">
                            <div className="flex space-x-4">
                                <button
                                    onClick={() => window.location.href = '/profile'}
                                    className="bg-gray-100 text-xl px-2 py-2 rounded-lg hover:bg-gray-50 transition duration-300 ease-in-out"
                                >
                                    Profile
                                </button>
                                <button
                                    onClick={() => window.location.href = '/settings'}
                                    className="bg-gray-100 text-xl px-2 py-2 rounded-lg hover:bg-gray-50 transition duration-300 ease-in-out"
                                >
                                    Settings
                                </button>
                                <button
                                    onClick={() => {
                                        localStorage.removeItem('jwt_token');
                                        window.location.href = '/';
                                    }}
                                    className="bg-gray-100 text-xl px-2 py-2 rounded-lg hover:bg-gray-50 transition duration-300 ease-in-out"
                                >
                                    Logout
                                </button>
                            </div>
                        </div>
                        <div className="sm:hidden flex items-center">
                            <button onClick={() => setIsMenuOpen(!isMenuOpen)} className="text-gray-700 hover:text-gray-500 focus:outline-none">
                                <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                                </svg>
                            </button>
                        </div>
                    </div>
                </div>
            </nav>
            {isMenuOpen && (
                <div className="sm:hidden fixed inset-0 z-20 bg-white bg-opacity-90">
                    <div className="pt-16 px-4 space-y-4 flex flex-col items-center relative">
                        <button
                            onClick={() => setIsMenuOpen(false)}
                            className="absolute top-4 right-4 text-gray-700 hover:text-gray-500 focus:outline-none"
                        >
                            <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                            </svg>
                        </button>
                        <Link href="/profile" className="text-xl hover:text-gray-500" onClick={() => setIsMenuOpen(false)}>
                            Profile
                        </Link>
                        <Link href="/settings" className="text-xl hover:text-gray-500" onClick={() => setIsMenuOpen(false)}>
                            Settings
                        </Link>
                        <button
                            className="text-gray-700 bg-gray-100 text-xl py-2 px-4 hover:bg-gray-50 transition duration-300 ease-in-out flex items-center justify-center border border-gray-300 rounded-lg w-80"
                            onClick={() => {
                                localStorage.removeItem('jwt_token');
                                window.location.href = '/';
                            }}
                        >
                            Logout
                        </button>
                    </div>
                </div>
            )}
        </>
    );
}
