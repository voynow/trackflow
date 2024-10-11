'use client';

import { useRouter } from 'next/navigation';
import FeaturesList from './components/FeaturesList';
import Footer from './components/Footer';
import ImageCarousel from './components/ImageCarousel';
import Navbar from './components/Navbar';

export default function Home(): JSX.Element {
  const router = useRouter();

  return (
    <div className="bg-gray-100 text-gray-800 pt-8 min-h-screen">
      <Navbar />
      <main className="flex flex-col items-center justify-center px-4 py-16 sm:px-6 lg:px-8">
        <div className="text-center">
          <h1 className="text-5xl sm:text-6xl font-extrabold tracking-tight mb-4 mt-12">
            Track<span className="text-blue-400">Flow</span> 🏃‍♂️🎯
          </h1>
          <p className="text-xl sm:text-2xl text-gray-400 mb-8">
            Step into the Next Generation of Training
          </p>
          <div className="space-y-4">
            <button
              className="px-6 py-3 text-white bg-gradient-to-r from-blue-400 to-indigo-600 font-bold rounded-full text-2xl hover:scale-105 hover:shadow-lg transition duration-300 ease-in-out transform hover:-translate-y-1"
              onClick={() => router.push('/signup')}
            >
              Join the Community
            </button>
          </div>
        </div>

        <ImageCarousel />
        <FeaturesList />
      </main>
      <Footer />
    </div>
  );
}
