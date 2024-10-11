import Link from 'next/link';

/**
 * Navbar component for the application.
 * @returns JSX.Element
 */
export default function Navbar(): JSX.Element {
    /**
     * Handles the sign-in process.
     */
    const handleSignIn = (): void => {
        const isDevelopment = process.env.NODE_ENV === 'development';
        const redirectUri = `https://www.trackflow.xyz/verify${isDevelopment ? '?env=dev' : ''}`;
        const stravaAuthUrl = `https://www.strava.com/oauth/authorize?client_id=95101&redirect_uri=${encodeURIComponent(redirectUri)}&response_type=code&approval_prompt=auto&scope=read_all,profile:read_all,activity:read_all`;
        window.location.href = stravaAuthUrl;
    };

    return (
        <nav className="fixed top-0 w-full bg-gray-100 text-gray-800 z-10">
            <div className="px-8 flex justify-between items-center h-16">
                <Link href="/" className="text-3xl font-bold hover:text-gray-500 transition duration-300 ease-in-out">
                    Track<span className="text-blue-500">Flow</span>
                </Link>
                <button
                    className="px-4 py-2 text-gray-800 bg-white font-semibold rounded-3xl flex space-x-2 outline outline-2 outline-gray-800 hover:scale-105 hover:shadow-lg transition duration-300 ease-in-out"
                    onClick={handleSignIn}
                >
                    <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                    </svg>
                    <span>Sign in</span>
                </button>
            </div>
        </nav>
    );
}
