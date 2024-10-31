'use client';

import { motion } from 'framer-motion';
import Link from 'next/link';
import Footer from '../components/Footer';

const DashboardPage = () => {
    return (
        <div className="bg-gray-900 text-gray-100 min-h-screen">
            {/* Navbar like component */}
            <div className="flex items-center justify-left h-16 px-4 text-2xl font-bold">
                <span className="text-blue-200">Track</span><span className="text-blue-400">Flow</span>
            </div>
            <main className="container mx-auto px-6 py-24 sm:px-8 lg:px-12">
                <motion.div
                    className="text-center mb-24"
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.8 }}
                >
                    <h1 className="text-blue-400 text-6xl sm:text-7xl font-extrabold tracking-tight mb-8 mt-12">
                        Coming Soon 🚧
                    </h1>
                    <p className="text-2xl sm:text-3xl text-gray-100 mb-16">
                        We&apos;re working hard to bring you an amazing web experience!
                    </p>
                    <div className="bg-gray-800 bg-opacity-50 backdrop-blur-sm p-10 rounded-lg max-w-2xl mx-auto">
                        <h3 className="text-3xl font-semibold mb-6 text-center">
                            In the meantime...
                        </h3>
                        <ul className="list-disc list-inside mb-8 text-left sm:text-lg md:text-xl">
                            <li className="mb-2">Download our mobile app TrackFlowAI from <a href="https://apps.apple.com/us/app/trackflowai/id6737172627" target="_blank" rel="noopener noreferrer" className="text-blue-400 hover:text-blue-300 underline">the App Store</a>.</li>
                            <li>Have questions? Reach out to us.</li>
                        </ul>
                        <Link href="mailto:voynow99@gmail.com" className="px-8 py-4 text-xl text-gray-200 bg-blue-600 font-bold rounded-full hover:bg-blue-700 hover:scale-105 transition duration-300 ease-in-out shadow-lg hover:shadow-blue-500/50 inline-block">
                            Contact @jamievoynow
                        </Link>
                    </div>
                </motion.div>
            </main>
            <Footer />
        </div>
    );
};

export default DashboardPage;
