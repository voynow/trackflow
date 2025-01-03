'use client';

import { motion } from 'framer-motion';
import Footer from '../components/Footer';
import Navbar from '../components/Navbar';

const DashboardPage = () => {
    return (
        <div className="bg-gray-900 text-gray-100 min-h-screen">
            <Navbar />
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
                            <li className="mb-2">Download our mobile app TrackFlowAI from <a href="https://apps.apple.com/us/app/trackflowai/id6737172627" target="_blank" rel="noopener noreferrer" className="text-blue-400 hover:text-blue-300 underline">the App Store</a></li>
                            <li className="mb-2">Contact me at <a href="mailto:voynow99@gmail.com" className="text-blue-400 hover:text-blue-300 underline">voynow99@gmail.com</a> with any feedback</li>
                            <li>And or connect with me on <a href="https://twitter.com/jamievoynow" target="_blank" rel="noopener noreferrer" className="text-blue-400 hover:text-blue-300 underline">X/Twitter</a></li>
                        </ul>
                    </div>
                </motion.div>
            </main>
            <Footer />
        </div>
    );
};

export default DashboardPage;
