'use client';

import { useRouter, useSearchParams } from 'next/navigation';
import { Suspense, useEffect, useRef, useState, useCallback } from 'react';
import DashboardNavbar from '../components/DashboardNavbar';
import TrainingWeek, { TrainingWeekProps } from '../components/TrainingWeek';

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
    const [trainingWeekData, setTrainingWeekData] = useState<TrainingWeekProps['data'] | null>(null);
    const [isLoading, setIsLoading] = useState<boolean>(true);

    const fetchTrainingData = useCallback(async (token: string) => {
        try {
            const response = await fetch('https://lwg77yq7dd.execute-api.us-east-1.amazonaws.com/prod/signup', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ jwt_token: token })
            });
            const data = await response.json();
            console.log('API response:', data);

            if (response.ok && data.success) {
                data.training_week = JSON.parse(data.training_week);
                console.log('Training week data parsed successfully');
                setTrainingWeekData(data);
            } else if (!response.ok) {
                console.error('Failed to fetch training data. Status:', response.status);
            } else if (!data.success) {
                console.error('Invalid JWT token. Server response:', data);
            }
        } catch (error) {
            console.error('Error fetching training data:', error);
        } finally {
            setIsLoading(false);
        }
    }, []);

    useEffect(() => {
        if (hasRun.current) return;
        hasRun.current = true;

        const token = searchParams.get('token');
        console.log('Token from searchParams:', token ? 'exists' : 'not found');

        if (token) {
            localStorage.setItem('jwt_token', token);
            console.log('Token saved to localStorage, redirecting to dashboard');
            router.replace('/dashboard');
        }

        const storedToken = localStorage.getItem('jwt_token');
        console.log('Stored token:', storedToken ? 'exists' : 'not found');

        if (!storedToken) {
            console.log('User session not found. Redirecting to login page.');
            router.push('/');
        } else {
            console.log('User authenticated. Fetching training data...');
            fetchTrainingData(storedToken);
        }
    }, [router, searchParams, fetchTrainingData]);

    console.log('Rendering DashboardContent, trainingWeekData:', trainingWeekData ? 'exists' : 'null', 'isLoading:', isLoading);

    if (isLoading) {
        return <LoadingSpinner />;
    }

    return (
        <div className="min-h-screen bg-gray-100 flex flex-col items-center justify-center">
            <h1 className="mb-16"></h1>
            {trainingWeekData ? (
                <TrainingWeek data={trainingWeekData} />
            ) : (
                <div>No training data available.</div>
            )}
        </div>
    );
}

function LoadingSpinner(): JSX.Element {
    return (
        <div className="flex items-center justify-center space-x-2">
            <div className="w-4 h-4 bg-blue-500 rounded-full animate-pulse"></div>
            <div className="w-4 h-4 bg-blue-500 rounded-full animate-pulse delay-75"></div>
            <div className="w-4 h-4 bg-blue-500 rounded-full animate-pulse delay-150"></div>
            <span className="text-sm text-gray-500 ml-2">Loading...</span>
        </div>
    );
}
