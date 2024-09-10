import React from 'react';

export default function ProfilePage(): React.ReactElement {
    return (
        <div className="flex flex-col items-center justify-center min-h-screen bg-gradient-to-r from-purple-400 to-pink-500 text-white p-4">
            <h1 className="text-4xl font-bold mb-4">
                404: Profile Not Found
            </h1>
            <p className="text-xl mb-8">
                Oops! This page is under construction.
            </p>
        </div>
    );
}
