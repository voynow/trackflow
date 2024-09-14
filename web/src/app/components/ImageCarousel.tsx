import Image from 'next/image';
import { useEffect, useState } from 'react';

const images = [
    { src: '/preview1.png', alt: 'TrackFlow Feature 1' },
    { src: '/preview2.png', alt: 'TrackFlow Feature 2' },
    { src: '/preview3.png', alt: 'TrackFlow Feature 3' },
];

export default function ImageCarousel(): JSX.Element {
    const [currentImageIndex, setCurrentImageIndex] = useState<number>(0);

    useEffect(() => {
        const interval = setInterval(() => {
            setCurrentImageIndex((prevIndex) => (prevIndex + 1) % images.length);
        }, 3000);

        return () => clearInterval(interval);
    }, []);

    return (
        <div className="mt-16 max-w-4xl w-full">
            <div className="relative overflow-hidden">
                <div
                    className="flex transition-transform duration-500 ease-in-out"
                    style={{ transform: `translateX(-${currentImageIndex * 100}%)` }}
                >
                    {images.map((image, index) => (
                        <div key={index} className="w-full flex-shrink-0">
                            <div className="relative aspect-[10/10]">
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
                        className={`w-3 h-3 rounded-full ${index === currentImageIndex ? 'bg-blue-400' : 'bg-gray-400'}`}
                        onClick={() => setCurrentImageIndex(index)}
                    />
                ))}
            </div>
        </div>
    );
}
