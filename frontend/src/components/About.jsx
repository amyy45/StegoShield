import React from "react";

const About = () => {
    return (
        <section className="bg-white py-16 px-6 sm:px-12 md:px-24 text-center">
            <h2 className="text-3xl font-extrabold text-gray-800 mb-6">About StegoShield</h2>
            <p className="text-gray-600 max-w-3xl mx-auto mb-10 text-justify">
                StegoShield is an advanced cybersecurity tool designed to detect hidden steganographic content inside images, audio, and video files. Using cutting-edge AI models, it ensures that malicious payloads embedded within media files are quickly identified and mitigated.
            </p>

            <div className="mt-12">
                <h3 className="text-2xl font-bold text-gray-800 mb-4">Meet the Developer</h3>
                <div className="max-w-2xl mx-auto bg-gray-50 rounded-xl p-6 shadow-md">
                    <h4 className="text-xl font-semibold text-gray-700 mb-2">Sneha Sah</h4>
                    <p className="text-gray-600 text-justify">
                        Hi! I'm a 3rd-year B.Tech CSE student at IcfaiTech Hyderabad with a strong passion for cybersecurity and ethical hacking. I developed StegoShield as part of my final-year project to tackle the growing threat of steganography-based cyberattacks. I'm deeply invested in building secure systems that protect user data and believe in the power of AI to make that possible.
                    </p>
                </div>
            </div>
        </section>
    );
};

export default About;
