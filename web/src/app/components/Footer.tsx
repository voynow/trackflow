import Image from 'next/image';

const Footer = (): JSX.Element => {
    return (
        <footer className="mt-32 w-full bg-gray-100 text-gray-400 py-4">
            <div className="container flex items-center justify-between">
                <Image
                    src="/powered_by_strava.png"
                    alt="Powered by Strava"
                    width={162}
                    height={30}
                    className="ml-4"
                />
                <p className="text-center flex-grow">
                    © 2024 TrackFlow. All rights reserved.
                </p>
            </div>
        </footer>
    );
};

export default Footer;
