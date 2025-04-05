import { useEffect, useState } from "react";
import logo from "../assets/logo.png";
import "./landing.css";

const HeroSection = () => {
  const [isOpen, setIsOpen] = useState(false);

  const navigation = [
    { title: "Home", path: "#" },
    { title: "Features", path: "#" },
    { title: "Customers", path: "#" },
    { title: "Contact", path: "#" },
  ];

  useEffect(() => {
    const handleClickOutside = (e) => {
      if (!e.target.closest(".menu-btn")) setIsOpen(false);
    };
    document.addEventListener("click", handleClickOutside);
    return () => document.removeEventListener("click", handleClickOutside);
  }, []);

  const Brand = () => (
    <div className="flex items-center justify-between py-4 md:block">
      <a href="#">
        <img src={logo} alt="StegoShield logo" className="w-32 h-auto" />
      </a>
      <div className="md:hidden">
        <button
          className="menu-btn text-gray-600 hover:text-gray-800"
          onClick={() => setIsOpen(!isOpen)}
        >
          {isOpen ? (
            <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" viewBox="0 0 20 20" fill="currentColor">
              <path
                fillRule="evenodd"
                d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z"
                clipRule="evenodd"
              />
            </svg>
          ) : (
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" className="h-6 w-6">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M4 6h16M4 12h16m-7 6h7" />
            </svg>
          )}
        </button>
      </div>
    </div>
  );

  return (
    <div className="relative">
      <div className="absolute inset-0 blur-xl h-[580px] -z-10"
        style={{
          background:
            "linear-gradient(143.6deg, rgba(192, 132, 252, 0) 20.79%, rgba(232, 121, 249, 0.26) 40.92%, rgba(204, 171, 238, 0) 70.35%)",
        }}
      ></div>

<header className="relative z-10">
  {/* Mobile Brand (Only shown when menu is open) */}
  <div className={`md:hidden ${isOpen ? "mx-2 pb-5" : "hidden"}`}>
    <Brand />
  </div>

  {/* Navigation */}
  <nav
    className={`pb-5 md:text-sm ${
      isOpen
        ? "absolute top-0 inset-x-0 bg-white shadow-lg rounded-xl border mx-2 mt-2 md:static md:shadow-none md:border-none md:mx-0"
        : ""
    }`}
  >
    <div className="max-w-screen-xl mx-auto px-4 sm:px-6 md:flex md:items-center md:justify-between md:px-8">
      <Brand />

      {/* Nav Links */}
      <div
        className={`md:flex items-center space-y-6 md:space-y-0 md:space-x-6 ${
          isOpen
            ? "flex flex-col items-center justify-center mt-6"
            : "hidden md:block"
        }`}
      >
        <ul className="flex flex-col items-center space-y-6 md:flex-row md:space-y-0 md:space-x-6">
          {navigation.map((item, idx) => (
            <li key={idx}>
              <a
                href={item.path}
                className="block text-gray-700 hover:text-gray-900 text-center"
              >
                {item.title}
              </a>
            </li>
          ))}
        </ul>

        {/* Sign In Button */}
        <a
          href="#"
          className="inline-flex items-center justify-center px-4 py-2 text-white bg-gray-800 hover:bg-gray-700 rounded-full text-sm mt-4 md:mt-0"
        >
          Sign in
        </a>
      </div>
    </div>
  </nav>
</header>


      <section>
        <div className="max-w-screen-xl mx-auto px-4 sm:px-6 md:px-8 py-16 sm:py-24 flex flex-col-reverse md:flex-row items-center gap-12 text-center md:text-left">
          <div className="w-full max-w-xl space-y-6">
            <a
              href="#"
              className="inline-flex gap-x-2 items-center text-sm font-medium border px-3 py-1.5 rounded-full hover:bg-white transition"
            >
              Stego Shield 
              <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                <path d="M7.21 14.77a.75.75 0 01.02-1.06L11.17 10 7.23 6.29a.75.75 0 111.04-1.08l4.5 4.25a.75.75 0 010 1.08l-4.5 4.25a.75.75 0 01-1.06-.02z" />
              </svg>
            </a>
            <h1 className="text-4xl sm:text-5xl font-extrabold text-gray-800">
              Protecting Your Data, One Pixel at a Time
            </h1>
            <p className="text-gray-600">
            StegoShield detects hidden payloads inside everyday media files — images, audio, and video — using cutting-edge AI.
            </p>
            <div className="flex flex-col sm:flex-row justify-center md:justify-start gap-3 sm:gap-4">
              <a
                href="#"
                className="inline-flex items-center justify-center gap-x-2 px-5 py-2 text-white bg-gray-800 hover:bg-gray-700 rounded-full text-sm"
              >
                Get started
              </a>
              <a
                href="#"
                className="inline-flex items-center justify-center gap-x-2 px-5 py-2 text-gray-700 hover:text-gray-900 rounded-full text-sm"
              >
                Learn more
              </a>
            </div>
          </div>

          <div className="w-full md:w-1/2 flex justify-center">
            <img
              src="https://raw.githubusercontent.com/sidiDev/remote-assets/c86a7ae02ac188442548f510b5393c04140515d7/undraw_progressive_app_m-9-ms_oftfv5.svg"
              alt="Hero illustration"
              className="w-full max-w-md sm:max-w-xl"
            />
          </div>
        </div>
      </section>
    </div>
  );
};

export default HeroSection;
