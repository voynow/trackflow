import { motion } from 'framer-motion';

interface Feature {
    icon: string;
    title: string;
    description: string;
}

const features: Feature[] = [
    {
        icon: '🎯',
        title: 'Personalized Plans',
        description: 'AI powered hyper-personalized training recommendations tailored to your preferences.'
    },
    {
        icon: '📊',
        title: 'Strava Integration',
        description: 'Go for a run, upload it to Strava, and TrackFlow will update your progress accordingly.'
    },
    {
        icon: '🏆',
        title: 'Goal Oriented',
        description: 'Our weekly plans are designed to help you achieve your goals, whether you want to run a marathon, or recover from an injury.'
    },
];

export default function FeaturesList(): JSX.Element {
    return (
        <section className="mt-12 py-24 bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 text-white w-full rounded-3xl">
            <div className="container mx-auto px-4">
                <h2 className="text-5xl font-bold text-center mb-4">Why TrackFlow?</h2>
                <p className="text-xl text-center text-gray-300 mb-16 max-w-2xl mx-auto">Revolutionizing your training with cutting-edge AI and data-driven insights.</p>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                    {features.map((feature, index) => (
                        <motion.div
                            key={index}
                            className="bg-gradient-to-br from-gray-800 to-gray-700 rounded-2xl p-8 shadow-lg hover:shadow-2xl transition-all duration-300 border border-gray-700 hover:border-blue-500"
                            initial={{ opacity: 0, y: 50 }}
                            whileInView={{ opacity: 1, y: 0 }}
                            transition={{ duration: 0.5, delay: index * 0.1 }}
                            viewport={{ once: true }}
                        >
                            <div className="text-5xl mb-6 bg-blue-500 rounded-full w-16 h-16 flex items-center justify-center">{feature.icon}</div>
                            <h3 className="text-2xl font-semibold mb-4">{feature.title}</h3>
                            <p className="text-gray-300">{feature.description}</p>
                        </motion.div>
                    ))}
                </div>
            </div>
        </section>
    );
}
