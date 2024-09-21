'use client';

import Image from 'next/image';
import React, { useState, useEffect } from 'react';
import DashboardNavbar from '../components/DashboardNavbar';
import { PreferencesForm } from '../components/PreferencesForm';
import { ProfileData, Preferences } from '../types';

export default function ProfilePage(): JSX.Element {
    const [profileData, setProfileData] = useState<ProfileData | null>(null);
    const [preferences, setPreferences] = useState<Preferences>({});
    const [isLoading, setIsLoading] = useState<boolean>(true);
    const [isEditing, setIsEditing] = useState<boolean>(false);

    useEffect(() => {
        fetchProfileData();
    }, []);

    const fetchProfileData = async (): Promise<void> => {
        const token = localStorage.getItem('jwt_token');
        if (!token) {
            window.location.href = '/';
            return;
        }

        try {
            const response = await fetch('https://lwg77yq7dd.execute-api.us-east-1.amazonaws.com/prod/signup', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ jwt_token: token, method: 'get_profile' })
            });
            const data = await response.json();

            if (response.ok && data.success) {
                setProfileData(data.profile);
                setPreferences(JSON.parse(data.profile.preferences || '{}'));
            } else {
                throw new Error('Failed to fetch profile data');
            }
        } catch (error) {
            console.error('Error fetching profile data:', error);
        } finally {
            setIsLoading(false);
        }
    };

    const handleSavePreferences = async (): Promise<void> => {
        const token = localStorage.getItem('jwt_token');
        if (!token) {
            window.location.href = '/';
            return;
        }

        try {
            const response = await fetch('https://lwg77yq7dd.execute-api.us-east-1.amazonaws.com/prod/signup', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    jwt_token: token,
                    method: 'update_preferences',
                    preferences: JSON.stringify(preferences)
                })
            });
            const data = await response.json();

            if (response.ok && data.success) {
                await fetchProfileData(); // Refresh profile data after saving
            } else {
                throw new Error('Failed to save preferences');
            }
        } catch (error) {
            console.error('Error saving preferences:', error);
        }
        setIsEditing(false);
    };

    const handleCancelEdit = (): void => {
        // Reset preferences to the last saved state
        if (profileData) {
            setPreferences(JSON.parse(profileData.preferences || '{}'));
        }
        setIsEditing(false);
    };

    if (isLoading) return <div className="flex justify-center items-center h-screen">Loading...</div>;
    if (!profileData) return <div className="flex justify-center items-center h-screen">Failed to load profile data</div>;

    return (
        <div className="bg-gray-100 min-h-screen">
            <DashboardNavbar />
            <div className="max-w-2xl mx-auto mt-10 p-6 bg-white rounded-lg shadow-md">
                <div className="flex items-center mb-6">
                    <Image
                        src={profileData.profile}
                        alt={`${profileData.firstname} ${profileData.lastname}`}
                        width={96}
                        height={96}
                        className="rounded-full mr-4"
                    />
                    <div>
                        <h1 className="text-2xl font-bold">{profileData.firstname} {profileData.lastname}</h1>
                        <p className="text-gray-600">{profileData.email}</p>
                    </div>
                </div>
                <div className="space-y-4">
                    <div>
                        <h2 className="text-lg font-semibold">Status</h2>
                        <p className={`mt-1 ${profileData.is_active ? 'text-green-600' : 'text-red-600'}`}>
                            {profileData.is_active ? 'Active' : 'Inactive'}
                        </p>
                    </div>
                    <div>
                        <h2 className="text-lg font-semibold mb-2">Preferences</h2>
                        {isEditing ? (
                            <PreferencesForm
                                preferences={preferences}
                                setPreferences={setPreferences}
                                onSave={handleSavePreferences}
                                onCancel={handleCancelEdit}
                            />
                        ) : (
                            <div>
                                {/* Display current preferences */}
                                <pre>{JSON.stringify(preferences, null, 2)}</pre>
                                <button
                                    onClick={() => setIsEditing(true)}
                                    className="mt-2 px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
                                >
                                    Edit Preferences
                                </button>
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
}
