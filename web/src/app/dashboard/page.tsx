'use client';

import { useRouter, useSearchParams } from 'next/navigation';
import { Suspense, useCallback, useEffect, useState } from 'react';
import DashboardNavbar from '../components/DashboardNavbar';
import TrainingWeek, { TrainingWeekProps } from '../components/TrainingWeek';

export default function Dashboard(): JSX.Element {
    return (
        <>
            <DashboardNavbar />
            <Suspense fallback={<LoadingSpinner />}>
                <DashboardContent />
            </Suspense>
        </>
    );
}

function DashboardContent(): JSX.Element {
    const router = useRouter();
    const searchParams = useSearchParams();
    const [trainingWeekData, setTrainingWeekData] = useState<TrainingWeekProps['data'] | null>(null);

    const fetchTrainingWeekData = useCallback(async (token: string): Promise<void> => {
        try {
            const response = await fetch('https://lwg77yq7dd.execute-api.us-east-1.amazonaws.com/prod/signup', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ jwt_token: token, method: 'get_training_week' })
            });
            const data = await response.json();

            if (response.ok && data.success) {
                data.training_week = JSON.parse(data.training_week);
                setTrainingWeekData(data);
            }
        } catch (error) {
            console.error('Error fetching training data:', error);
        }
    }, []);

    useEffect(() => {
        const token = searchParams.get('token');

        if (token) {
            localStorage.setItem('jwt_token', token);
            router.replace('/dashboard');
            return;
        }

        const storedToken = localStorage.getItem('jwt_token');

        if (!storedToken) {
            router.push('/');
        } else {
            fetchTrainingWeekData(storedToken);
        }
    }, [router, searchParams, fetchTrainingWeekData]);

    return (
        <div className="min-h-screen bg-gray-100 flex flex-col items-center justify-center">
            <h1 className="mb-16"></h1>
            {trainingWeekData ? (
                <TrainingWeek data={trainingWeekData} />
            ) : (
                <LoadingSpinner />
            )}
        </div>
    );
}

function LoadingSpinner(): JSX.Element {
    const [showWaitMessage, setShowWaitMessage] = useState<boolean>(false);

    useEffect(() => {
        const timer = setTimeout(() => {
            setShowWaitMessage(true);
        }, 10000); // 10 seconds

        return () => clearTimeout(timer);
    }, []);

    return (
        <div className="flex flex-col items-center justify-center space-y-4">
            <div className="flex items-center justify-center space-x-2">
                <div className="w-4 h-4 bg-blue-500 rounded-full animate-pulse"></div>
                <div className="w-4 h-4 bg-blue-500 rounded-full animate-pulse delay-75"></div>
                <div className="w-4 h-4 bg-blue-500 rounded-full animate-pulse delay-150"></div>
                <span className="text-sm text-gray-500 ml-2">Loading...</span>
            </div>
            {showWaitMessage && (
                <p className="text-sm text-gray-600 text-center max-w-md">
                    If loading persists, your training schedule may not be available yet.
                    Please check back after 8:30 PM EST when schedules are typically released.
                </p>
            )}
        </div>
    );
}
