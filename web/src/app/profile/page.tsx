'use client';

import Image from 'next/image';
import { useCallback, useEffect, useState } from 'react';
import { FiCheck, FiEdit2, FiInfo, FiX } from 'react-icons/fi';
import DashboardNavbar from '../components/DashboardNavbar';

interface ProfileData {
    firstname: string;
    lastname: string;
    email: string;
    preferences: string;
    profile: string;
    is_active: boolean;
}

export default function ProfilePage(): JSX.Element {
    const [profileData, setProfileData] = useState<ProfileData | null>(null);
    const [isLoading, setIsLoading] = useState<boolean>(true);
    const [isEditing, setIsEditing] = useState<boolean>(false);
    const [editedPreferences, setEditedPreferences] = useState<string>('');

    const fetchProfileData = useCallback(async (token: string): Promise<void> => {
        try {
            const response = await fetch('https://lwg77yq7dd.execute-api.us-east-1.amazonaws.com/prod/signup', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ jwt_token: token, method: 'get_profile' })
            });
            const data = await response.json();

            if (response.ok && data.success) {
                setProfileData(data.profile);
            } else {
                throw new Error('Failed to fetch profile data');
            }
        } catch (error) {
            console.error('Error fetching profile data:', error);
        } finally {
            setIsLoading(false);
        }
    }, []);

    useEffect(() => {
        const storedToken = localStorage.getItem('jwt_token');

        if (!storedToken) {
            // Redirect to login page if no token is found
            window.location.href = '/';
        } else {
            fetchProfileData(storedToken);
        }
    }, [fetchProfileData]);


    const handlePreferencesCancel = () => {
        setIsEditing(false);
    };

    const handleActiveToggle = async () => {
        if (!profileData) return;
        // Implement API call to update active status
        setProfileData({ ...profileData, is_active: !profileData.is_active });
    };

    if (isLoading) {
        return <div className="flex items-center justify-center min-h-screen">Loading...</div>;
    }

    if (!profileData) {
        return <div className="flex items-center justify-center min-h-screen">Failed to load profile data</div>;
    }

    return (
        <div className="min-h-screen bg-gray-100">
            <DashboardNavbar />
            <div className="container mx-auto px-4 py-16 mt-8">
                <div className="bg-white shadow-xl rounded-lg overflow-hidden">
                    <div className="bg-gradient-to-l from-indigo-600 to-blue-300 h-48"></div>
                    <div className="relative px-6 py-10">
                        <div className="absolute -top-16 left-6">
                            <Image
                                src={profileData.profile}
                                alt={`${profileData.firstname} ${profileData.lastname}`}
                                width={128}
                                height={128}
                                className="rounded-full border-4 border-white shadow-lg"
                            />
                        </div>
                        <div className="mt-16">
                            <h1 className="text-3xl font-bold text-gray-800">
                                {profileData.firstname} {profileData.lastname}
                            </h1>
                            <p className="text-gray-600 mt-2">{profileData.email}</p>
                            <div className="mt-6 relative">
                                <h2 className="text-xl font-semibold text-gray-700 flex items-center">
                                    Account Status
                                    <div className="group relative ml-2">
                                        <FiInfo className="text-gray-400 cursor-help" />
                                        <span className="absolute ml-2 w-48 p-2 bg-gray-800 text-white text-xs rounded opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                                            Everyone needs a training break from time to time. Go inactive to turn off TrackFlow recommendations.
                                        </span>
                                    </div>
                                </h2>
                                <div className="mt-2 flex items-center">
                                    <span className={`inline-block w-3 h-3 rounded-full mr-2 ${profileData.is_active ? 'bg-green-500' : 'bg-red-500'}`}></span>
                                    <span className="text-gray-700 w-16">
                                        {profileData.is_active ? 'Active' : 'Inactive'}
                                    </span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
