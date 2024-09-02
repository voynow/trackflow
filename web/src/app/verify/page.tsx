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
    const [countdown, setCountdown] = useState<number>(5);
    const router = useRouter();
    const { push } = router;
    const searchParams = useSearchParams();
    const code = searchParams.get('code');
    const isInitialMount = useRef(true);

    useEffect(() => {
        if (isInitialMount.current) {
            isInitialMount.current = false; // Prevent re-triggering after the first render

            const email = localStorage.getItem('email');
            const preferences = localStorage.getItem('preferences');

            console.log('useEffect triggered');
            console.log('Retrieved email:', email);
            console.log('Retrieved preferences:', preferences);
            console.log('Retrieved code:', code);

            if (code && email && preferences) {
                console.log('All required data is present. Proceeding with fetch request.');
                fetch('https://lwg77yq7dd.execute-api.us-east-1.amazonaws.com/prod/signup', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ email, preferences, code })
                })
                    .then(response => {
                        console.log('Fetch response received:', response);
                        return response.json();
                    })
                    .then(data => {
                        console.log('Parsed response data:', data);
                        if (data.success) {
                            console.log('Verification successful');
                            setStatus('success');
                            localStorage.removeItem('email');
                            localStorage.removeItem('preferences');
                            setTimeout(() => {
                                console.log('Redirecting to home page');
                                push('/');
                            }, 5000);
                        } else {
                            console.log('Verification failed');
                            setStatus('error');
                        }
                    })
                    .catch(error => {
                        console.error('Fetch error:', error);
                        setStatus('error');
                    });
            } else {
                console.log('Missing required data. Setting status to error.');
                setStatus('error');
            }
        }
    }, [code, push]); // depend on `code` to ensure updates on URL changes

    return (
        <div className="flex items-center justify-center min-h-screen bg-gray-100">
            <div className="bg-white p-8 rounded-lg shadow-md text-center">
                {status === 'verifying' && (
                    <p className="text-lg">Verifying...</p>
                )}
                {status === 'success' && (
                    <>
                        <p className="text-lg mb-2">Verified successfully! ✅</p>
                        <p className="text-sm text-gray-500">
                            Redirecting in {countdown}
                        </p>
                    </>
                )}
                {status === 'error' && (
                    <p className="text-lg">Verification failed</p>
                )}
            </div>
        </div>
    );
}
