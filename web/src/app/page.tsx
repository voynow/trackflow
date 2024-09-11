'use client';

import Image from 'next/image';
import { useEffect, useState } from 'react';
import Footer from './components/Footer';
import Navbar from './components/Navbar';

const images = [
  { src: '/preview1.png', alt: 'TrackFlow Feature 1' },
  { src: '/preview2.png', alt: 'TrackFlow Feature 2' },
  { src: '/preview3.png', alt: 'TrackFlow Feature 3' },
];

export default function Home(): JSX.Element {
  const [currentImageIndex, setCurrentImageIndex] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentImageIndex((prevIndex) => (prevIndex + 1) % images.length);
    }, 3000);

    return () => clearInterval(interval);
  }, []);

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
          <button className="bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-6 rounded-full text-lg transition duration-300 ease-in-out">
            Get Started
          </button>
        </div>

        <div className="mt-16 max-w-4xl w-full">
          <div className="relative overflow-hidden">
            <div className="flex transition-transform duration-500 ease-in-out"
              style={{ transform: `translateX(-${currentImageIndex * 100}%)` }}>
              {images.map((image, index) => (
                <div key={index} className="w-full flex-shrink-0">
                  <div className="relative aspect-[17/10]">
                    <Image
                      src={image.src}
                      alt={image.alt}
                      fill
                      className="object-cover object-top rounded-lg"
                      quality={100}
                      priority={index === 0}
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="mt-4 flex justify-center space-x-2">
            {images.map((_, index) => (
              <button
                key={index}
                className={`w-3 h-3 rounded-full ${index === currentImageIndex ? 'bg-blue-400' : 'bg-gray-400'
                  }`}
                onClick={() => setCurrentImageIndex(index)}
              />
            ))}
          </div>
        </div>

        <div className="text-white mt-16 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-8">
          {[
            { icon: '📊', title: 'Data-Driven Insights' },
            { icon: '🎯', title: 'Goal-Oriented Plans' },
            { icon: '🔄', title: 'Adaptive Training' },
          ].map((feature, index) => (
            <div key={index} className="bg-gray-800 p-6 rounded-lg text-center">
              <div className="text-4xl mb-4">{feature.icon}</div>
              <h3 className="text-xl font-semibold">{feature.title}</h3>
            </div>
          ))}
        </div>
      </main>
      <Footer />
    </div>
  );
}
