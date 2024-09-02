'use client';

import { useRouter, useSearchParams } from 'next/navigation';
import { useEffect, useState } from 'react';

export default function Verify() {
    const [status, setStatus] = useState<'verifying' | 'success' | 'error'>('verifying');
    const router = useRouter();
    const searchParams = useSearchParams();

    useEffect(() => {
        const code = searchParams.get('code');
        const email = localStorage.getItem('email');
        const preferences = localStorage.getItem('preferences');

        if (code && email && preferences) {
            fetch('https://your-api-endpoint.com/signup', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ code, email, preferences }),
            })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        setStatus('success');
                        localStorage.removeItem('email');
                        localStorage.removeItem('preferences');
                        setTimeout(() => router.push('/'), 2000);
                    } else {
                        setStatus('error');
                    }
                })
                .catch(() => {
                    setStatus('error');
                });
        } else {
            setStatus('error');
        }
    }, [searchParams, router]);

    return (
        <div className="flex items-center justify-center min-h-screen bg-gray-100">
            <div className="bg-white p-8 rounded-lg shadow-md">
                {status === 'verifying' && <p>Verifying your account...</p>}
                {status === 'success' && <p>Verification successful! Redirecting...</p>}
                {status === 'error' && <p>An error occurred. Please try again.</p>}
            </div>
        </div>
    );
}