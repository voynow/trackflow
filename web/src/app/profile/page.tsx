'use client';

import Image from 'next/image';
import { useCallback, useEffect, useState } from 'react';
import { FiEdit2, FiInfo } from 'react-icons/fi';
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

    const fetchProfileData = useCallback(async (token: string): Promise<void> => {
        try {
            const response = await fetch('https://lwg77yq7dd.execute-api.us-east-1.amazonaws.com/prod/signup', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ jwt_token: token, method: 'get_profile' })
            });
            const data = await response.json();

            console.log(data);

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
            window.location.href = '/';
        } else {
            fetchProfileData(storedToken);
        }
    }, [fetchProfileData]);

    if (isLoading) {
        return <div className="flex items-center justify-center min-h-screen">Loading...</div>;
    }

    if (!profileData) {
        return <div className="flex items-center justify-center min-h-screen">Failed to load profile data</div>;
    }

    return (
        <div className="min-h-screen bg-gray-50">
            <DashboardNavbar />
            <div className="container mx-auto px-4 py-16 mt-8">
                <div className="bg-white shadow-sm rounded-lg overflow-hidden">
                    <div className="px-6 py-10">
                        <div className="flex items-center space-x-6">
                            <Image
                                src={profileData.profile}
                                alt={`${profileData.firstname} ${profileData.lastname}`}
                                width={96}
                                height={96}
                                className="rounded-full"
                            />
                            <div>
                                <h1 className="text-2xl font-semibold text-gray-800">
                                    {profileData.firstname} {profileData.lastname}
                                </h1>
                                <p className="text-gray-600 mt-1">{profileData.email}</p>
                            </div>
                        </div>
                        <div className="mt-8 space-y-6">
                            <ProfileSection title="Account Status" icon={<FiInfo />}>
                                <div className="flex items-center mt-2">
                                    <span className={`inline-block w-2 h-2 rounded-full mr-2 ${profileData.is_active ? 'bg-green-500' : 'bg-red-500'}`}></span>
                                    <span className="text-gray-700">
                                        {profileData.is_active ? 'Active' : 'Inactive'}
                                    </span>
                                </div>
                            </ProfileSection>
                            <ProfileSection title="Preferences" icon={<FiEdit2 />}>
                                <p className="text-gray-700 mt-2">{profileData.preferences}</p>
                            </ProfileSection>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}

type ProfileSectionProps = {
    title: string;
    icon: React.ReactNode;
    children: React.ReactNode;
};

function ProfileSection({ title, icon, children }: ProfileSectionProps): JSX.Element {
    return (
        <div>
            <h2 className="text-lg font-semibold text-gray-700 flex items-center">
                {title}
                <span className="ml-2 text-gray-400">{icon}</span>
            </h2>
            {children}
        </div>
    );
}
