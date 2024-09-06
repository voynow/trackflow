'use client';

import { useRouter } from 'next/navigation';
import { useEffect } from 'react';


export default function Dashboard(): JSX.Element {
    const router = useRouter();

    useEffect(() => {
        const token = localStorage.getItem('jwt_token');
        if (!token) {
            console.log('User session not found. Redirecting to login page.');
            router.push('/');
        } else {
            console.log('User authenticated. Displaying dashboard.');
        }
    }, [router]);

    return (
        <div className="min-h-screen bg-gray-100 flex flex-col items-center justify-center">
            <h1 className="text-3xl font-bold">Dashboard</h1>
            <p className="text-sm text-gray-500 mt-4">In development...</p>
        </div>
    );
}
