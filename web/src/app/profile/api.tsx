import { Preferences, ProfileData } from '../types';

const API_URL = 'https://lwg77yq7dd.execute-api.us-east-1.amazonaws.com/prod/signup';

export async function fetchProfileData(): Promise<ProfileData> {
    const token = localStorage.getItem('jwt_token');
    if (!token) {
        throw new Error('No token found');
    }

    const response = await fetch(API_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ jwt_token: token, method: 'get_profile' })
    });
    const data = await response.json();

    if (response.ok && data.success) {
        return data.profile;
    } else {
        throw new Error(data.error || 'Failed to fetch profile data');
    }
}

export async function savePreferences(preferences: Preferences): Promise<void> {
    const token = localStorage.getItem('jwt_token');
    if (!token) {
        throw new Error('No token found');
    }
    console.log("Saving preferences:", preferences);
    const response = await fetch(API_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            jwt_token: token,
            method: 'update_preferences',
            payload: { preferences: preferences }
        })
    });
    const data = await response.json();
    console.log("Response received:", data);
    if (!response.ok || !data.success) {
        if (data.error) {
            throw new Error(data.error)
        } else {
            throw new Error('Failed to save preferences: ' + JSON.stringify(data))
        }
    }
}