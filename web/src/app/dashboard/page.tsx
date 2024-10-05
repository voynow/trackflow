'use client';

import { useRouter, useSearchParams } from 'next/navigation';
import React, { Suspense, useCallback, useEffect, useState } from 'react';
import DashboardNavbar from '../components/DashboardNavbar';
import { LoadingSpinner } from '../components/LoadingSpinner';
import TrainingWeek, { TrainingWeekProps } from '../components/TrainingWeek';

React

export default function Dashboard(): JSX.Element {
    return (
        <>
            <DashboardNavbar />
            <Suspense fallback={<LoadingSpinner error={null} />}>
                <DashboardContent />
            </Suspense>
        </>
    );
}

function DashboardContent(): JSX.Element {
    const router = useRouter();
    const searchParams = useSearchParams();
    const [trainingWeekData, setTrainingWeekData] = useState<TrainingWeekProps['data'] | null>(null);
    const [error, setError] = useState<string | null>(null);

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
            } else {
                setError(data.error || 'An error occurred while fetching training data.');
            }
        } catch (error) {
            setError('An unexpected error occurred. Please try again later.');
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
                <LoadingSpinner error={error} />
            )}
        </div>
    );
}
