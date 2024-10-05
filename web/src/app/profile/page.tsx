'use client';

import Image from 'next/image';
import { useEffect, useState } from 'react';
import DashboardNavbar from '../components/DashboardNavbar';
import { LoadingSpinner } from '../components/LoadingSpinner';
import { PreferencesForm } from '../components/PreferencesForm';
import { Preferences, ProfileData } from '../types';
import { fetchProfileData, savePreferences } from './api';

export default function ProfilePage(): JSX.Element {
    const [profileData, setProfileData] = useState<ProfileData | null>(null);
    const [preferences, setPreferences] = useState<Preferences>({});
    const [isLoading, setIsLoading] = useState<boolean>(true);
    const [isEditing, setIsEditing] = useState<boolean>(false);
    const [isSaving, setIsSaving] = useState<boolean>(false);

    useEffect(() => {
        loadProfileData();
    }, []);

    const loadProfileData = async (): Promise<void> => {
        try {
            const data = await fetchProfileData();
            setProfileData(data);
            setPreferences(JSON.parse(data.preferences || '{}'));
        } catch (error) {
            console.error('Error fetching profile data:', error);
        } finally {
            setIsLoading(false);
        }
    };

    const handleSavePreferences = async (): Promise<void> => {
        setIsSaving(true);
        try {
            await savePreferences(preferences);
            await loadProfileData();
        } catch (error) {
            console.error('Error saving preferences:', error);
        } finally {
            setIsSaving(false);
            setIsEditing(false);
        }
    };

    const handleCancelEdit = (): void => {
        if (profileData) {
            setPreferences(JSON.parse(profileData.preferences || '{}'));
        }
        setIsEditing(false);
    };

    if (isLoading) {
        return (
            <div className="min-h-screen bg-gray-50 flex flex-col items-center justify-center">
                <LoadingSpinner error={null} />
            </div>
        );
    }

    if (!profileData) {
        return (
            <div className="min-h-screen bg-gray-50 flex flex-col items-center justify-center">
                <LoadingSpinner error="Failed to load profile data" />
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-gray-50 text-gray-800">
            <DashboardNavbar />
            <div className="max-w-4xl mx-auto mt-20 p-8 bg-white rounded-3xl shadow-lg">
                <div className="flex items-center mb-8">
                    <Image
                        src={profileData.profile}
                        alt={`${profileData.firstname} ${profileData.lastname}`}
                        width={96}
                        height={96}
                        className="rounded-full mr-6 border-2 border-blue-500"
                    />
                    <div>
                        <h1 className="text-3xl font-bold bg-clip-text text-transparent bg-blue-400">
                            {profileData.firstname} {profileData.lastname}
                        </h1>
                        <p className="text-gray-600">{profileData.email}</p>
                    </div>
                </div>
                <div className="space-y-10">
                    <div>
                        <h2 className="text-xl font-semibold mb-2">Status</h2>
                        <p className={`inline-block px-3 py-1 rounded-full text-white ${profileData.is_active ? 'bg-green-500' : 'bg-red-500'}`}>
                            {profileData.is_active ? 'Active' : 'Inactive'}
                        </p>
                    </div>
                    <div>
                        <h2 className="text-xl font-semibold mb-4">Training Preferences</h2>
                        {isEditing ? (
                            <PreferencesForm
                                preferences={preferences}
                                setPreferences={setPreferences}
                                onSave={handleSavePreferences}
                                onCancel={handleCancelEdit}
                                isSaving={isSaving}
                            />
                        ) : (
                            <div>
                                <pre className="bg-gray-50 p-4 rounded-xl overflow-x-auto text-gray-800">
                                    {JSON.stringify(preferences, null, 2)}
                                    <button
                                        onClick={() => setIsEditing(true)}
                                        className="mt-4 px-4 py-2 bg-blue-400 text-white rounded-xl hover:bg-blue-300 transition duration-300 ease-in-out float-right"
                                    >
                                        Edit
                                    </button>
                                </pre>
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
}