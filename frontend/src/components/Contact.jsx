import React from 'react';

const Contact = () => {
    return (
        <div className="pt-20 pb-10 px-6 md:px-20 bg-gray-50 text-gray-800">
            <h2 className="text-4xl font-extrabold text-center mb-6">Contact Us</h2>
            <p className="max-w-4xl mx-auto text-lg text-justify leading-relaxed mb-10">
                We’re here to help! Whether you have a question about our services, need assistance with a file upload, or want to provide feedback, our team is ready to assist you.
                Have questions, suggestions, or just want to say hi? We'd love to hear from you! Fill out the form below and we’ll get back to you as soon as possible.
            </p>

            <form className="max-w-2xl mx-auto bg-white p-10 rounded-2xl shadow-lg space-y-6"
                action={"https://getform.io/f/bnlqzgjb"} method='POST'>
                <div>
                    <label className="block text-sm font-medium mb-1" htmlFor="name">Name</label>
                    <input
                        id="name"
                        name="name"
                        type="text"
                        placeholder="Your name"
                        className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                </div>
                <div>
                    <label className="block text-sm font-medium mb-1" htmlFor="email">Email</label>
                    <input
                        id="email"
                        name="email"
                        type="email"
                        placeholder="you@example.com"
                        className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                </div>
                <div>
                    <label className="block text-sm font-medium mb-1" htmlFor="message">Message</label>
                    <textarea
                        id="message"
                        name="message"
                        rows="5"
                        placeholder="Write your message..."
                        className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    ></textarea>
                </div>
                <button
                    type="submit"
                    className="px-6 py-2 text-white bg-gray-800 hover:bg-gray-700 rounded-full text-sm block mx-auto"
                >
                    Send Message
                </button>
            </form>
        </div>
    );
};

export default Contact;
