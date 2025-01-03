'use client';

import { motion } from 'framer-motion';
import { Inter, Montserrat } from 'next/font/google';
import { useRouter } from 'next/navigation';
import React from 'react';

const inter = Inter({ subsets: ['latin'] });
const montserrat = Montserrat({ subsets: ['latin'] });

export default function Home(): React.ReactElement {
  const router = useRouter();

  return (
    <div className="bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 text-gray-100 min-h-screen">
      <main className="container mx-auto px-6 py-24 sm:px-8 lg:px-12">
        <motion.div
          className="text-center mb-24"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 1 }}
        >
          <h1 className={`text-6xl sm:text-7xl md:text-8xl font-extrabold tracking-tight mb-8 mt-12 ${montserrat.className}`}>
            <span className="text-blue-300">Crush</span>{' '}
            <span className="text-blue-500">Your Race</span>
          </h1>
          <p className={`text-2xl sm:text-3xl text-gray-100 mb-16 ${inter.className}`}>
            AI-Powered Training Plans for Runners
          </p>

          <motion.button
            className="px-8 py-4 text-xl text-gray-200 bg-blue-600 font-bold rounded-full hover:bg-blue-700 transition duration-300 ease-in-out shadow-lg hover:shadow-blue-500/50 mb-24"
            onClick={() => router.push('/dashboard')}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            Get Started
          </motion.button>

          <div className="bg-gray-700 bg-opacity-50 backdrop-blur-sm p-10 rounded-lg max-w-2xl mx-auto">
            <h3 className="text-3xl font-semibold mb-6 text-center">
              <span className="line-through">$5 per month</span>{" "}
              <span className="text-green-400">Free for a limited time!</span>
            </h3>
            <ul className="list-disc list-inside mb-8 text-left sm:text-lg md:text-xl">
              <li className="mb-2">Unlimited personalized training plans</li>
              <li className="mb-2">Real-time performance tracking</li>
              <li>Goal-oriented performance optimization</li>
            </ul>
            <button
              className="px-8 py-4 text-xl text-gray-200 bg-blue-600 font-bold rounded-full hover:bg-blue-700 hover:scale-105 transition duration-300 ease-in-out shadow-lg hover:shadow-blue-500/50"
              onClick={() => router.push('/dashboard')}
            >
              Get Started for Free
            </button>
          </div>
        </motion.div>
      </main>
    </div>
  );
}
