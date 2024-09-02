import Image from 'next/image';
import { useState } from 'react';


interface SignUpProps {
    onClose: () => void;
}

export default function SignUp({ onClose }: SignUpProps): JSX.Element {
    const [email, setEmail] = useState('');
    const [preferences, setPreferences] = useState('');

    const handleSignUp = (event: React.FormEvent): void => {
        event.preventDefault();
        localStorage.setItem('email', email);
        localStorage.setItem('preferences', preferences);
        const redirectUri = 'http://localhost:3000/';
        const stravaAuthUrl = `https://www.strava.com/oauth/authorize?client_id=95101&redirect_uri=${encodeURIComponent(redirectUri)}&response_type=code&approval_prompt=auto&scope=read_all,profile:read_all,activity:read_all`;
        window.location.href = stravaAuthUrl;
    };


    return (
        <div className="fixed inset-0 bg-black/25 flex items-center justify-center z-50">
            <div className="bg-gray-100 p-8 rounded-lg shadow-2xl max-w-md w-full text-gray-700">
                <h2 className="text-3xl font-semibold mb-4 flex justify-between">
                    Sign Up
                    <button onClick={onClose} className="hover:text-gray-500">x</button>
                </h2>
                <form className="space-y-8" onSubmit={handleSignUp}>
                    <input
                        type="email"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        placeholder="Email"
                        required
                        className="w-full px-3 py-2 border rounded-md"
                    />
                    <textarea
                        value={preferences}
                        onChange={(e) => setPreferences(e.target.value)}
                        placeholder="Preferences (e.g., Training for marathon, prefer Wed workouts, Sat long runs)"
                        className="bg w-full px-3 py-2 border rounded-md focus:ring-2"
                        rows={4}
                    />
                    <button
                        type="submit"
                        className="w-full flex items-center justify-center px-4 py-2 rounded-md hover:bg-white transition duration-300 ease-in-out"
                    >
                        <Image src="/strava-icon.png" alt="Strava Logo" width={20} height={20} className="mr-2" />
                        Sign Up with Strava
                    </button>
                </form>
            </div>
        </div>
    );
}