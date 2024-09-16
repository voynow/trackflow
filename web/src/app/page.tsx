'use client';

import { useRouter } from 'next/navigation';
import FeaturesList from './components/FeaturesList';
import Footer from './components/Footer';
import ImageCarousel from './components/ImageCarousel';
import Navbar from './components/Navbar';

export default function Home(): JSX.Element {
  const router = useRouter();

  return (
    <div className="bg-gray-100 text-gray-800 min-h-screen">
      <Navbar />
      <main className="flex flex-col items-center justify-center px-4 py-16 sm:px-6 lg:px-8">
        <div className="text-center">
          <h1 className="text-5xl sm:text-6xl font-extrabold tracking-tight mb-4 mt-12">
            Track<span className="text-blue-400">Flow</span> 🏃‍♂️🎯
          </h1>
          <p className="text-xl sm:text-2xl text-gray-400 mb-8">
            AI-Powered Training Plans, Tailored Just for You
          </p>
          <button
            className="bg-red-600 hover:bg-red-500 text-white font-bold py-3 px-6 rounded-full text-lg transition duration-300 ease-in-out"
            onClick={() => router.push('/signup')}
          >
            Get Started
          </button>
        </div>

        <ImageCarousel />
        <FeaturesList />
      </main>
      <Footer />
    </div>
  );
}
