// src/app/components/DashboardNavbar.tsx
import Link from 'next/link';
import { useEffect, useRef, useState } from 'react';


export default function DashboardNavbar(): JSX.Element {
    const [isDropdownOpen, setIsDropdownOpen] = useState<boolean>(false);
    const dropdownRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        function handleClickOutside(event: MouseEvent): void {
            if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
                setIsDropdownOpen(false);
            }
        }

        document.addEventListener('mousedown', handleClickOutside);
        return () => {
            document.removeEventListener('mousedown', handleClickOutside);
        };
    }, []);

    const handleLogout = (): void => {
        localStorage.removeItem('jwt_token');
        window.location.href = '/';
    };

    return (
        <nav className="fixed top-0 w-full bg-white shadow-sm text-gray-800 z-10">
            <div className="mx-auto px-4 sm:px-6 lg:px-8">
                <div className="flex justify-between items-center h-16">
                    <Link href="/dashboard" className="text-2xl font-semibold hover:text-gray-600 transition duration-300">
                        Track<span className="text-blue-400">Flow</span>
                    </Link>
                    <div className="flex items-center space-x-4">
                        <div className="relative" ref={dropdownRef}>
                            <button
                                onClick={() => setIsDropdownOpen(!isDropdownOpen)}
                                className="flex items-center space-x-2 text-lg hover:text-gray-600 transition duration-300 focus:outline-none"
                                aria-label="User menu"
                            >
                                <svg className="h-12 w-12 hover:text-gray-600 hover:bg-gray-50 transition duration-300 rounded-full p-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                                </svg>
                            </button>
                            {isDropdownOpen && (
                                <div className="absolute right-0 w-48 text-lg bg-gray-100 rounded-md outline outline-gray-200 shadow-lg py-2">
                                    <Link href="/dashboard" className="block px-4 py-2 hover:bg-white transition duration-300 rounded-md text-center">Dashboard</Link>
                                    <Link href="/profile" className="block px-4 py-2 hover:bg-white transition duration-300 rounded-md text-center">Profile</Link>
                                    <button onClick={handleLogout} className="block w-full px-4 py-2 hover:bg-white transition duration-300 rounded-md text-center">Logout</button>
                                </div>
                            )}
                        </div>
                    </div>
                </div>
            </div>
        </nav>
    );
}
