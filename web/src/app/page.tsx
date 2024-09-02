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
            <h1 className="text-7xl font-extrabold">
              TrackFlow <span>🏃‍♂️🎯</span>
            </h1>
            <p className="text-2xl font-semibold">
              Hyperpersonalized training recs straight to your inbox
            </p>
          </div>

          <div className="mt-24 max-w-4xl w-full space-y-8 px-4">
            <div className="relative rounded-xl overflow-hidden shadow-lg">
              <Image
                src="/preview.png"
                alt="TrackFlow Feature"
                width={800}
                height={450}
                className="w-full h-auto"
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