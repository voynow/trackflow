'use client';

import Image from 'next/image';
import { useEffect, useState } from 'react';
import DashboardNavbar from '../components/DashboardNavbar';
import { LoadingSpinner } from '../components/LoadingSpinner';
import { PreferencesForm } from '../components/PreferencesForm';
import { Preferences, ProfileData } from '../types';
import { fetchProfileData, savePreferences } from './api';
import { Day, SessionType } from '../types';

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

    const days: Day[] = ['Mon', 'Tues', 'Wed', 'Thurs', 'Fri', 'Sat', 'Sun'];
    const sessionTypes: SessionType[] = ['easy run', 'long run', 'speed workout', 'rest day', 'moderate run'];

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
        <div className="min-h-screen bg-gray-100 text-gray-800">
            <DashboardNavbar />
            <div className="max-w-4xl mx-auto mt-20 mb-10 p-8 bg-white rounded-3xl shadow-lg">
                <div className="flex items-center mb-8 justify-between">
                    <div className="flex items-center">
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
                    <div>
                        <p className={`inline-block px-3 py-1 rounded-full text-white ${profileData.is_active ? 'bg-green-500' : 'bg-red-500'}`}>
                            {profileData.is_active ? 'Active' : 'Inactive'}
                        </p>
                    </div>
                </div>
                <div className="space-y-10">
                    <div>
                        {isEditing ? (
                            <PreferencesForm
                                preferences={preferences}
                                setPreferences={setPreferences}
                                onSave={handleSavePreferences}
                                onCancel={handleCancelEdit}
                                isSaving={isSaving}
                            />
                        ) : (
                            <div className="bg-gray-50 p-6 max-w-3xl mx-auto text-gray-800 rounded-3xl">
                                <div className="mb-8">
                                    <label className="block text-sm font-medium mb-2 text-gray-600">Race Distance</label>
                                    <div className="w-full bg-gray-50 rounded-xl py-3 px-4 text-gray-800 border border-gray-200">
                                        {preferences.race_distance || 'Not set'}
                                    </div>
                                </div>

                                <div className="mb-8">
                                    <label className="block text-sm font-medium mb-4 text-gray-600">Ideal Training Week</label>
                                    <div className="space-y-2">
                                        {days.map((day) => {
                                            const sessionType = preferences.ideal_training_week?.find(session => session.day === day)?.session_type;
                                            const isPreferenceSet = !!sessionType;
                                            return (
                                                <div key={day} className="flex items-center border rounded-xl overflow-hidden border-gray-300">
                                                    <span className={`w-20 font-medium px-4 py-3 bg-gray-50 ${isPreferenceSet ? 'text-gray-600' : 'text-gray-300'}`}>
                                                        {day}
                                                    </span>
                                                    <span className={`flex-grow py-3 px-4 bg-gray-50 ${isPreferenceSet ? 'text-gray-800' : 'text-gray-300'}`}>
                                                        {sessionType || 'No Preference'}
                                                    </span>
                                                </div>
                                            );
                                        })}
                                    </div>
                                </div>

                                <div className="flex justify-end">
                                    <button
                                        onClick={() => setIsEditing(true)}
                                        className="px-4 py-2 bg-blue-400 text-white rounded-xl hover:bg-blue-300 transition duration-300 ease-in-out"
                                    >
                                        Edit
                                    </button>
                                </div>
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
}