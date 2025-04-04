import React from "react";
import { BrowserRouter, Route, Routes } from "react-router-dom";
import FileUpload from "./components/FileUpload";
import HeroSection from "./components/HeroSection";

function App() {
    return (
        <>
            <BrowserRouter>
            <Routes>
                <Route path="/" element={<HeroSection />} />
                <Route path="/upload" element={<FileUpload />} />
            </Routes>
            </BrowserRouter>
        </>
    );
}

export default App;
