import { AnimatePresence } from "framer-motion";
import React from "react";
import { BrowserRouter as Router, Route, Routes } from "react-router-dom";
import Navbar from "./components/Navbar";
import AuroraBackground from "./components/AuroraBackground";
import Home from "./pages/Home";
import About from "./pages/About";
import "./App.css";

const App = () => {
  return (
    <Router>
      <div className="App">
        <AuroraBackground />
        <Navbar />
        <AnimatePresence mode="wait">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/about" element={<About />} />
          </Routes>
        </AnimatePresence>
        <footer className="App-footer">
          <p>© 2025 Warta Pangan. All rights reserved.</p>
        </footer>
      </div>
    </Router>
  );
};

export default App;
