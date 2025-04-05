import React from "react";

const Contact = () => {
    return (
        <section className="bg-white py-16 px-6 sm:px-12 md:px-24">
            <div className="max-w-4xl mx-auto text-center">
                <h2 className="text-3xl font-extrabold text-gray-800 mb-6">Contact Us</h2>
                <p className="text-gray-600 mb-12 text-justify">
                    Have questions, suggestions, or just want to say hi? We'd love to hear from you!
                    Fill out the form below and we’ll get back to you as soon as possible.
                </p>
            </div>

            <form className="max-w-3xl mx-auto bg-gray-50 p-8 rounded-xl shadow-md space-y-6">
                <div>
                    <label className="block text-left text-sm font-medium text-gray-700 mb-1">Name</label>
                    <input
                        type="text"
                        placeholder="Your Name"
                        className="w-full px-4 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-gray-400"
                        required
                    />
                </div>
                <div>
                    <label className="block text-left text-sm font-medium text-gray-700 mb-1">Email</label>
                    <input
                        type="email"
                        placeholder="you@example.com"
                        className="w-full px-4 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-gray-400"
                        required
                    />
                </div>
                <div>
                    <label className="block text-left text-sm font-medium text-gray-700 mb-1">Message</label>
                    <textarea
                        rows="5"
                        placeholder="Your message..."
                        className="w-full px-4 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-gray-400"
                        required
                    ></textarea>
                </div>
                <div className="text-center">
                    <button
                        type="submit"
                        className="px-6 py-2 text-white bg-gray-800 hover:bg-gray-700 rounded-full text-sm"
                    >
                        Send Message
                    </button>
                </div>
            </form>

        </section>
    );
};

export default Contact;
