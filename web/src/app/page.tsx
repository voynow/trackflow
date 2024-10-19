'use client';

import { motion } from 'framer-motion';
import { useRouter } from 'next/navigation';
import Footer from './components/Footer';
import Navbar from './components/Navbar';
import Image from 'next/image';

export default function Home(): JSX.Element {
  const router = useRouter();

  const features: Array<{ title: string; description: string }> = [
    { title: "Hyper-Personalized Training", description: "Tailored to your training history, fitness level, preferences, and goals." },
    { title: "Strava Integration", description: "Using the Strava API we are able to personalize your training in real-time." },
    { title: "Live Adjustments", description: "As soon as you upload your activities to Strava, we update your training plan accordingly." },
    { title: "Goal Oriented", description: "Whether you are running an Ultra Marathon or a 5K, we got you covered." },
  ];

  const testimonials: Array<{ name: string; quote: string; image: string }> = [
    { 
      name: "Danny Lio", 
      quote: "The training plan I found online was good, but it was missing the level of personalization that TrackFlow provides.",
      image: "/danny-lio.png"
    },
    { 
      name: "Jared Palek", 
      quote: "I used to pay $50.00 per month to work with my coach, but TrackFlow is just as good and a whole lot cheaper!",
      image: "/jared-palek.png"
    },
    { 
      name: "Rachel Decker", 
      quote: "I love that my TrackFlow training plan is always up to date. It's like having a coach by my side for every activity!",
      image: "/rachel-decker.png"
    },
  ];

  const fadeInUp = {
    initial: { opacity: 0, y: 20 },
    animate: { opacity: 1, y: 0 },
    transition: { duration: 0.6 }
  };

  const renderFeatures = (): JSX.Element => {
    if (features.length === 1) {
      return (
        <div className="max-w-2xl mx-auto">
          <FeatureItem feature={features[0]} />
        </div>
      );
    } else if (features.length === 2) {
      return (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 max-w-4xl mx-auto">
          {features.map((feature, index) => (
            <FeatureItem key={index} feature={feature} />
          ))}
        </div>
      );
    } else if (features.length === 4) {
      return (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-8 max-w-7xl mx-auto">
          {features.map((feature, index) => (
            <FeatureItem key={index} feature={feature} />
          ))}
        </div>
      );
    } else {
      return (
        <div className="flex flex-col gap-8 max-w-2xl mx-auto">
          {features.map((feature, index) => (
            <FeatureItem key={index} feature={feature} />
          ))}
        </div>
      );
    }
  };

  const FeatureItem = ({ feature }: { feature: { title: string; description: string } }): JSX.Element => (
    <motion.div
      className="bg-gray-800 p-8 rounded-lg"
      {...fadeInUp}
    >
      <h3 className="text-2xl font-semibold mb-4 bg-gradient-to-r from-blue-300 to-indigo-600 bg-clip-text text-transparent">{feature.title}</h3>
      <p className="text-lg">{feature.description}</p>
    </motion.div>
  );

  return (
    <div className="bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 text-gray-100 min-h-screen">
      <Navbar />
      <main className="container mx-auto px-6 py-24 sm:px-8 lg:px-12">
        <motion.div
          className="text-center mb-24"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 1 }}
        >
          <h1 className="text-6xl sm:text-7xl md:text-8xl font-extrabold tracking-tight mb-8 mt-12">
            <span className="text-blue-300">Track</span><span className="text-blue-500">Flow</span> 🏃‍♂️🎯
          </h1>
          <p className="text-2xl sm:text-3xl text-gray-100 mb-16">
            Step into the Next Generation of Training
          </p>
          <div className="bg-gray-700 bg-opacity-50 backdrop-blur-sm p-10 rounded-lg max-w-2xl mx-auto">
            <h3 className="text-3xl font-semibold mb-6 text-center">
              <span className="line-through">$9.99/month</span>{" "}
              <span className="text-green-400">Free for a limited time!</span>
            </h3>
            <ul className="list-disc list-inside mb-8 text-left sm:text-lg md:text-xl">
              <li className="mb-2">Unlimited personalized training plans</li>
              <li className="mb-2">Real-time performance tracking</li>
              <li>Goal-oriented performance optimization</li>
            </ul>
            <button
              className="px-8 py-4 text-xl text-gray-200 bg-blue-600 font-bold rounded-full hover:bg-blue-700 hover:scale-105 transition duration-300 ease-in-out shadow-lg hover:shadow-blue-500/50"
              onClick={() => router.push('/signup')}
            >
              Get Started for Free
            </button>
          </div>
        </motion.div>

        <motion.section
          className="mb-24"
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          transition={{ duration: 0.8 }}
          viewport={{ once: true }}
        >
          <h2 className="text-4xl font-bold mb-12 text-center">Key Features</h2>
          {renderFeatures()}
        </motion.section>

        <motion.section
          className="mb-24"
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          transition={{ duration: 0.8 }}
          viewport={{ once: true }}
        >
          <h2 className="text-4xl font-bold mb-12 text-center">What Our Users Say</h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-12 max-w-7xl mx-auto">
            {testimonials.map((testimonial, index) => (
              <motion.div
                key={index}
                className="bg-gray-800 p-8 rounded-lg flex flex-col items-center text-center"
                {...fadeInUp}
                transition={{ delay: index * 0.1 }}
              >
                <div className="mb-6 relative w-36 h-36 overflow-hidden rounded-full border-4 border-blue-500">
                  <Image
                    src={testimonial.image}
                    alt={testimonial.name}
                    width={144}
                    height={144}
                    quality={100}
                    priority
                  />
                </div>
                <p className="italic mb-6 text-xl">&ldquo;{testimonial.quote}&rdquo;</p>
                <p className="font-semibold text-lg text-blue-300">- {testimonial.name}</p>
              </motion.div>
            ))}
          </div>
        </motion.section>

        <motion.div
          className="text-center mb-24 max-w-4xl mx-auto"
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          viewport={{ once: true }}
        >
          <h2 className="text-4xl font-bold mb-8">Ready to Transform Your Training?</h2>
          <motion.button
            className="px-10 py-5 text-2xl text-gray-200 bg-blue-600 font-bold rounded-full hover:bg-blue-700 transition duration-300 ease-in-out shadow-lg hover:shadow-blue-500/50"
            onClick={() => router.push('/signup')}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            Join TrackFlow Today
          </motion.button>
        </motion.div>
      </main>
      <Footer />
    </div>
  );
}
