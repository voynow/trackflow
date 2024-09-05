import Link from 'next/link';
import { useState } from 'react';
import SignUp from './SignUp';

export default function Navbar(): JSX.Element {
    const [showSignup, setShowSignup] = useState<boolean>(false);
    const [isMenuOpen, setIsMenuOpen] = useState<boolean>(false);

    const handleSignIn = (): void => {
        const redirectUri = 'https://trackflowai.vercel.app/verify';
        const stravaAuthUrl = `https://www.strava.com/oauth/authorize?client_id=95101&redirect_uri=${encodeURIComponent(redirectUri)}&response_type=code&approval_prompt=auto&scope=read_all,profile:read_all,activity:read_all`;
        window.location.href = stravaAuthUrl;
    };

    return (
        <>
            <nav className="fixed top-0 w-full bg-gray-100 bg-opacity-75 text-gray-700 z-10">
                <div className="px-4 sm:px-6">
                    <div className="flex justify-between h-16">
                        <div className="flex-shrink-0 flex items-center">
                            <Link href="/" className="text-2xl sm:text-4xl font-bold hover:text-gray-500 transition duration-300 ease-in-out">
                                TrackFlow
                            </Link>
                        </div>
                        <div className="hidden sm:flex items-center space-x-4">
                            <button className="bg-gray-800 text-gray-200 text-xl px-6 py-2 rounded-lg hover:bg-gray-700 transition duration-300 ease-in-out"
                                onClick={() => setShowSignup(true)}>
                                <div className="flex items-center">
                                    <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-2" viewBox="0 0 20 20" fill="currentColor">
                                        <path d="M8 9a3 3 0 100-6 3 3 0 000 6zM8 11a6 6 0 016 6H2a6 6 0 016-6zM16 7a1 1 0 10-2 0v1h-1a1 1 0 100 2h1v1a1 1 0 102 0v-1h1a1 1 0 100-2h-1V7z" />
                                    </svg>
                                    Sign Up
                                </div>
                            </button>
                            <button className="bg-gray-800 text-gray-200 text-xl px-6 py-2 rounded-lg hover:bg-gray-700 transition duration-300 ease-in-out"
                                onClick={handleSignIn}>
                                <div className="flex items-center">
                                    <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-2" viewBox="0 0 20 20" fill="currentColor">
                                        <path fillRule="evenodd" d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z" clipRule="evenodd" />
                                    </svg>
                                    Sign In
                                </div>
                            </button>
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
                    <div className="pt-16 px-4 space-y-4">
                        <button
                            onClick={() => setIsMenuOpen(false)}
                            className="absolute top-4 right-4 text-gray-700 hover:text-gray-500 focus:outline-none"
                        >
                            <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                            </svg>
                        </button>
                        <button className="w-full bg-gray-800 text-gray-200 text-xl px-6 py-2 rounded-lg hover:bg-gray-700 transition duration-300 ease-in-out"
                            onClick={() => { setShowSignup(true); setIsMenuOpen(false); }}>
                            Sign Up
                        </button>
                        <button className="w-full bg-gray-800 text-gray-200 text-xl px-6 py-2 rounded-lg hover:bg-gray-700 transition duration-300 ease-in-out"
                            onClick={() => { handleSignIn(); setIsMenuOpen(false); }}>
                            Sign In
                        </button>
                    </div>
                </div>
            )}
            {showSignup && <SignUp onClose={() => setShowSignup(false)} />}
        </>
    );
}
