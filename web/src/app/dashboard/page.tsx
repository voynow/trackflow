'use client';

import { useRouter, useSearchParams } from 'next/navigation';
import { Suspense, useEffect, useRef } from 'react';
import DashboardNavbar from '../components/DashboardNavbar';

export default function Dashboard(): JSX.Element {
    return (
        <>
            <DashboardNavbar />
            <Suspense fallback={<div>Loading...</div>}>
                <DashboardContent />
            </Suspense>
        </>
    );
}

function DashboardContent(): JSX.Element {
    const router = useRouter();
    const searchParams = useSearchParams();
    const hasRun = useRef(false);

    useEffect(() => {
        if (hasRun.current) return;
        hasRun.current = true;

        const token = searchParams.get('token');
        if (token) {
            localStorage.setItem('jwt_token', token);
            router.replace('/dashboard'); // Remove the token from the URL
        } else {
            const storedToken = localStorage.getItem('jwt_token');
            if (!storedToken) {
                console.log('User session not found. Redirecting to login page.');
                router.push('/');
            } else {
                console.log('User authenticated. Displaying dashboard.');
            }
        }
    }, [router, searchParams]);

    return (
        <div className="min-h-screen bg-gray-100 flex flex-col items-center justify-center">
            <h1 className="text-3xl font-bold">Dashboard</h1>
            <p className="text-sm text-gray-500 mt-4">In development...</p>
        </div>
    );
}
