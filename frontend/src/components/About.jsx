import React from 'react';

const About = () => {
    return (
        <div className="py-20 px-6 md:px-20 bg-white text-gray-800">
            <h2 className="text-4xl font-extrabold text-center mb-6">About StegoShield</h2>
            <p className="max-w-4xl mx-auto text-lg leading-relaxed text-justify">
                StegoShield is an advanced cybersecurity tool designed to detect hidden steganographic
                content inside images, audio, and video files. Using cutting-edge AI models, it ensures that
                malicious payloads embedded within media files are quickly identified and mitigated.
            </p>

            {/* Developer Card */}
            <div className="mt-20 text-center">
                <h3 className="text-3xl font-bold mb-6">Meet the Developer</h3>
                <div className="bg-gray-100 max-w-3xl mx-auto p-10 rounded-2xl shadow-lg">
                    <h4 className="text-xl font-semibold mb-4">Sneha Sah</h4>
                    <p className="text-justify text-base leading-relaxed">
                        Hi! I'm a 3rd-year B.Tech CSE student at IcfaiTech Hyderabad with a strong passion for
                        cybersecurity and ethical hacking. I developed StegoShield as part of my academic
                        project to tackle the growing threat of steganography-based cyberattacks. I'm deeply
                        invested in building secure systems that protect user data and believe in the power of
                        AI to make that possible.
                    </p>
                </div>
            </div>
        </div>
    );
};

export default About;
