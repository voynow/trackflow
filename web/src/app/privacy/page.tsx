'use client';

import Link from 'next/link';
import React from 'react';

const PrivacyPolicy: React.FC = () => {
    return (
        <div className="min-h-screen bg-gray-100 flex flex-col items-center justify-center px-4 py-16 sm:px-6 lg:px-8">
            <div className="max-w-3xl w-full space-y-8 bg-white p-10 rounded-xl shadow-md">
                <div>
                    <Link href="/" className="block">
                        <h1 className="text-4xl font-bold text-center text-gray-800">
                            Track<span className="text-blue-500">Flow</span>
                        </h1>
                    </Link>
                    <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">Privacy Policy</h2>
                </div>

                <div className="space-y-6 text-gray-700">
                    <p>
                        At TrackFlow, we value your privacy and are committed to protecting your personal information.
                        This privacy policy outlines our practices concerning the handling of your data.
                    </p>

                    <div>
                        <h3 className="text-xl font-semibold mb-2">Data Storage</h3>
                        <p>
                            <strong>We do not save your data.</strong> TrackFlow is designed to process your information
                            in real-time without storing it on our servers. This approach ensures that your personal
                            training data remains under your control.
                        </p>
                    </div>

                    <div>
                        <h3 className="text-xl font-semibold mb-2">Data Sharing</h3>
                        <p>
                            <strong>We do not send your data externally.</strong> Your information is processed within
                            our secure environment and is not shared with third parties. We believe in keeping your
                            training data private and confidential.
                        </p>
                    </div>

                    <div>
                        <h3 className="text-xl font-semibold mb-2">Strava Integration</h3>
                        <p>
                            TrackFlow integrates with Strava to provide you with personalized training recommendations.
                            We only access the data necessary for this purpose and do so securely through Strava's API.
                        </p>
                    </div>

                    <p>
                        By using TrackFlow, you agree to the terms outlined in this privacy policy. If you have any
                        questions or concerns, please don't hesitate to contact us.
                    </p>
                </div>

                <div className="text-center text-sm text-gray-500">
                    <p>Last updated: {new Date().toLocaleDateString()}</p>
                </div>
            </div>
        </div>
    );
};

export default PrivacyPolicy;
