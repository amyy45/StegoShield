import React from "react";
import { Link } from "react-router-dom";

const Footer = () => {
    return (
        <footer className="bg-gray-900 text-gray-300 py-10 mt-20">
            <div className="max-w-7xl mx-auto px-6 grid grid-cols-1 md:grid-cols-3 gap-8">
                {/* About Section */}
                <div>
                    <h3 className="text-lg font-semibold mb-3">About StegoShield</h3>
                    <p className="text-sm text-justify">
                        StegoShield is an AI-powered platform that detects hidden steganographic payloads in
                        images, audio, and video files. Designed for security enthusiasts and researchers.
                    </p>
                </div>

                {/* Navigation */}
                <div>
                    <h3 className="text-lg font-semibold mb-3">Quick Links</h3>
                    <ul className="space-y-2 text-sm">
                        <li><Link to="/" className="hover:text-white">Home</Link></li>
                        <li><Link to="/features" className="hover:text-white">Features</Link></li>
                        <li><Link to="/customers" className="hover:text-white">Customers</Link></li>
                        <li><Link to="/about" className="hover:text-white">About</Link></li>
                        <li><Link to="/contact" className="hover:text-white">Contact</Link></li>
                    </ul>
                </div>

                {/* Developer Info */}
                <div>
                    <h3 className="text-lg font-semibold mb-3">Developer</h3>
                    <p className="text-sm">
                        Built with ❤️ by Sneha<br />
                        B.Tech CSE | Cybersecurity Enthusiast<br />
                        ICFAItech, Hyderabad
                    </p>
                </div>
            </div>

            <div className="mt-10 text-center text-sm text-gray-500">
                © {new Date().getFullYear()} StegoShield. All rights reserved.
            </div>
        </footer>
    );
};

export default Footer;
