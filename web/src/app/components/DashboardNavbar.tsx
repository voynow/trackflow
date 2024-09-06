// src/app/components/DashboardNavbar.tsx
import Link from 'next/link';
import { useState } from 'react';


export default function DashboardNavbar(): JSX.Element {
    const [isDropdownOpen, setIsDropdownOpen] = useState<boolean>(false);

    const handleLogout = (): void => {
        localStorage.removeItem('jwt_token');
        window.location.href = '/';
    };

    return (
        <nav className="fixed top-0 w-full bg-white shadow-sm text-gray-700 z-10">
            <div className="px-4 sm:px-6">
                <div className="flex justify-between h-16">
                    <div className="flex-shrink-0 flex items-center">
                        <Link href="/dashboard" className="text-2xl sm:text-3xl font-bold hover:text-gray-500 transition duration-300">
                            TrackFlow
                        </Link>
                    </div>
                    <div className="flex items-center">
                        <button
                            onClick={() => setIsDropdownOpen(!isDropdownOpen)}
                            className="p-2 rounded-full hover:bg-gray-100 transition duration-300 focus:outline-none"
                        >
                            <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                            </svg>
                        </button>
                        {isDropdownOpen && (
                            <div className="absolute right-0 mt-16 w-48 bg-white rounded-md shadow-lg py-1">
                                <Link href="/profile" className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100">Profile</Link>
                                <Link href="/settings" className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100">Settings</Link>
                                <button onClick={handleLogout} className="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100">Logout</button>
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </nav>
    );
}
