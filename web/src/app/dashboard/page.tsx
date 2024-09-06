'use client';

import { useRouter, useSearchParams } from 'next/navigation';
import { Suspense, useEffect, useRef, useState } from 'react';
import DashboardNavbar from '../components/DashboardNavbar';
import TrainingWeekUpdate from '../components/TrainingWeekUpdate';

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
    const [trainingData, setTrainingData] = useState<any>(null);

    useEffect(() => {
        if (hasRun.current) return;
        hasRun.current = true;

        const token = searchParams.get('token');
        if (token) {
            localStorage.setItem('jwt_token', token);
            router.replace('/dashboard');
        } else {
            const storedToken = localStorage.getItem('jwt_token');
            if (!storedToken) {
                console.log('User session not found. Redirecting to login page.');
                router.push('/');
            } else {
                console.log('User authenticated. Displaying dashboard.');

                const fetchTrainingData = async () => {
                    try {
                        const response = await fetch('https://lwg77yq7dd.execute-api.us-east-1.amazonaws.com/prod/signup', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({ jwt_token: storedToken })
                        });
                        const data = await response.json();
                        if (response.ok && data.success) {
                            setTrainingData(data);
                        } else if (!response.ok) {
                            console.error('Failed to fetch training data');
                        } else if (!data.success) {
                            console.error('Invalid JWT token');
                        }
                    } catch (error) {
                        console.error('Error fetching training data:', error);
                    }
                };

                fetchTrainingData();
            }
        }
    }, [router, searchParams]);

    return (
        <div className="min-h-screen bg-gray-100 flex flex-col items-center justify-center">
            <h1 className="text-3xl font-bold mb-8">Dashboard</h1>
            {trainingData ? (
                <TrainingWeekUpdate data={trainingData} />
            ) : (
                <p className="text-sm text-gray-500">Loading training data...</p>
            )}
        </div>
    );
}
