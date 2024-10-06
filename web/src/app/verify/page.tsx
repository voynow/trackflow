'use client';

import { useRouter, useSearchParams } from 'next/navigation';
import { Suspense, useEffect, useRef, useState } from 'react';

export default function Verify(): JSX.Element {
    return (
        <Suspense fallback={<div>Loading...</div>}>
            <VerifyContent />
        </Suspense>
    );
}

function VerifyContent(): JSX.Element {
    const [status, setStatus] = useState<'verifying' | 'success' | 'error'>('verifying');
    const router = useRouter();
    const searchParams = useSearchParams();
    const code = searchParams.get('code');
    const hasRun = useRef(false);

    useEffect(() => {
        if (hasRun.current) return;
        hasRun.current = true;

        const email = localStorage.getItem('email');

        const verifyAccount = async (payload: Record<string, string>) => {
            console.log('Verifying with payload:', payload);
            try {
                const response = await fetch('https://lwg77yq7dd.execute-api.us-east-1.amazonaws.com/prod/signup', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });
                const data = await response.json();
                console.log('Verification response:', data);
                if (data.success) {
                    setStatus('success');
                    localStorage.removeItem('email');
                    localStorage.setItem('jwt_token', data.jwt_token);
                    const isDevelopment = searchParams.get('env') === 'dev';
                    const dashboardUrl = isDevelopment
                        ? `http://localhost:3000/dashboard?token=${encodeURIComponent(data.jwt_token)}`
                        : 'https://www.trackflow.xyz/dashboard';
                    setTimeout(() => {
                        router.push(dashboardUrl);
                    }, 1000);
                } else {
                    console.error('Verification failed:', data);
                    throw new Error(`Verification failed: ${JSON.stringify(data)}`);
                }
            } catch (error) {
                console.error('Error during verification:', error);
                setStatus('error');
                setTimeout(() => router.push('/'), 1500);
            }
        };

        if (code) {
            if (email) {
                verifyAccount({ email, code });
            } else {
                verifyAccount({ code });
            }
        } else {
            console.error('No verification code found in URL');
            setStatus('error');
            setTimeout(() => router.push('/'), 1500);
        }
    }, [code, router]);

    return (
        <div className="flex items-center justify-center min-h-screen bg-gray-100">
            <div className="bg-white p-8 rounded-lg shadow-md text-center max-w-md w-full">
                {status === 'verifying' && (
                    <>
                        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-gray-900 mx-auto mb-4"></div>
                        <p className="text-lg font-semibold">Verifying your account...</p>
                    </>
                )}
                {status === 'success' && (
                    <>
                        <svg className="h-16 w-16 text-green-500 mx-auto mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                        </svg>
                        <p className="text-lg font-semibold">Verification successful!</p>
                    </>
                )}
                {status === 'error' && (
                    <>
                        <svg className="h-16 w-16 text-red-500 mx-auto mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                        </svg>
                        <p className="text-lg font-semibold">Verification failed. Redirecting...</p>
                    </>
                )}
            </div>
        </div>
    );
}
