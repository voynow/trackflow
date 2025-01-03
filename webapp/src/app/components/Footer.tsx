import Image from 'next/image';
import React from 'react';

const Footer = (): React.ReactElement => {
    return (
        <footer className="mt-16 w-full bg-gray-900 text-gray-320 py-4">
            <div className="container flex items-center justify-between">
                <Image
                    src="/powered_by_strava_light.png"
                    alt="Powered by Strava"
                    width={162}
                    height={30}
                    className="ml-4"
                />
                <p className="text-center flex-grow">
                    © 2025 Crush Your Race. All rights reserved.
                </p>
            </div>
        </footer>
    );
};

export default Footer;
