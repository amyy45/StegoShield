import React from "react";
import { BrowserRouter, Route, Routes } from "react-router-dom";
import FileUpload from "./components/FileUpload";
import HeroSection from "./components/HeroSection";
import Feature from "./components/Features";
import Customers from "./components/Customers";
import About from "./components/About";
import Contact from "./components/Contact";
import Fotter from "./components/Footer";

function App() {
    return (
        <>
            <BrowserRouter>
                <Routes>
                    <Route
                        path="/"
                        element={
                            <>
                                <HeroSection />
                                <Feature />
                                <Customers />
                                <About />
                                <Contact />
                                <Fotter />
                            </>
                        }
                    />
                    <Route path="/upload" element={<FileUpload />} />
                </Routes>
            </BrowserRouter>
        </>
    );
}

export default App;
