import Image from 'next/image';
import Link from 'next/link';
export default function Navbar(): JSX.Element {
    return (
        <nav className="fixed top-0 w-full bg-opacity-0 text-gray-700">
            <div className="px-6">
                <div className="flex justify-between h-16">
                    <div className="flex-shrink-0 flex items-center">
                        <Link href="/" className="text-2xl font-bold hover:text-gray-500 transition duration-300 ease-in-out">
                            TrackFlow
                        </Link>
                    </div>
                    <div className="flex items-center">
                        <button className="text-xl px-6 py-2 rounded-lg hover:bg-white transition duration-300 ease-in-out">
                            <div className="flex items-center">
                                <Image
                                    src="/strava-icon.png"
                                    alt="Strava Logo"
                                    width={20}
                                    height={20}
                                    className="mr-2"
                                />
                                Sign Up
                            </div>
                        </button>
                    </div>
                </div>
            </div>
        </nav>
    );
}