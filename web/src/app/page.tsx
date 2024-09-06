'use client';

import Image from 'next/image';
import Footer from './components/Footer';
import Navbar from './components/Navbar';

export default function Home(): JSX.Element {
  return (
    <>
      <Navbar />
      <main className="min-h-screen bg-gray-100 flex flex-col items-center justify-between text-gray-700">
        <div className="mt-32 flex flex-col items-center justify-center text-center">
          <div className="space-y-8">
            <h1 className="text-5xl font-extrabold">
              TrackFlow <span>🏃‍♂️🎯</span>
            </h1>
            <p className="text-2xl">
              Hyperpersonalized training recs straight to your inbox
            </p>
          </div>

          <div className="mt-24 max-w-4xl w-full space-y-8 px-4">
            <div className="mx-auto mb-6 w-full bg-white rounded-lg shadow-md overflow-hidden lg:w-3/4">
              <Image
                src="/preview.png"
                alt="TrackFlow Feature"
                width={1500}
                height={3000}
                className="w-full h-auto"
                quality={100}
                priority
              />
            </div>
            <p className="text-xl">
              TrackFlow uses AI to analyze your past workouts, preferences, and goals to generate weekly training plans and daily updates.
            </p>
          </div>
        </div>

        <Footer />
      </main>
    </>
  );
}
