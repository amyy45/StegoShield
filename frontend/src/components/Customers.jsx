import React from "react";

const testimonials = [
    {
        name: "Neha Patel",
        role: "Security Engineer",
        review:
            "StegoShield is an innovative tool that helped me detect hidden payloads in image files with impressive accuracy. Loved the intuitive UI!",
        avatar: "https://randomuser.me/api/portraits/women/68.jpg",
    },
    {
        name: "Karan Mehta",
        role: "Penetration Tester",
        review:
            "Finally a steganography detection tool that actually works and is easy to use. It’s now a part of my go-to toolkit for CTFs and audits.",
        avatar: "https://randomuser.me/api/portraits/men/52.jpg",
    },
    {
        name: "Ayesha Iqbal",
        role: "Cybersecurity Intern",
        review:
            "Used StegoShield during my internship and was amazed by how fast and accurate it was. It really helped me validate suspicious media files.",
        avatar: "https://randomuser.me/api/portraits/women/91.jpg",
    },
];

const Customers = () => {
    return (
        <section className="bg-white py-16 px-4">
            <div className="max-w-screen-xl mx-auto text-center">
                <h2 className="text-3xl font-bold text-gray-800 mb-4">What Our Early Users Say</h2>
                <p className="text-gray-600 mb-12 max-w-2xl mx-auto">
                    Feedback from cybersecurity professionals and researchers who’ve tried StegoShield.
                </p>

                <div className="grid gap-8 md:grid-cols-3">
                    {testimonials.map((user, idx) => (
                        <div
                            key={idx}
                            className="bg-gray-50 shadow-md rounded-2xl p-6 text-left hover:shadow-xl transition"
                        >
                            <div className="flex items-center gap-4 mb-4">
                                <img
                                    src={user.avatar}
                                    alt={user.name}
                                    className="w-12 h-12 rounded-full object-cover"
                                />
                                <div>
                                    <h4 className="font-semibold text-gray-800">{user.name}</h4>
                                    <p className="text-sm text-gray-500">{user.role}</p>
                                </div>
                            </div>
                            <p className="text-gray-700 text-sm">"{user.review}"</p>
                        </div>
                    ))}
                </div>
            </div>
        </section>
    );
};

export default Customers;
