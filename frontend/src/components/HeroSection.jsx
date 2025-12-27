import React from "react";
import { motion } from "framer-motion";
import "./HeroSection.css";

const HeroSection = () => {
  return (
    <motion.section
      className="hero-section"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.8 }}
    >
      <div className="hero-content">
        <motion.div
          className="hero-text"
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.2 }}
        >
          <motion.div
            className="hero-badge"
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.5, delay: 0.3 }}
          >
            <span>🌾</span>
            <span>Prediksi Akurat Berbasis AI</span>
          </motion.div>

          <h1 className="hero-title">
            Pantau Harga Pangan
            <span className="gradient-text"> Jakarta</span>
          </h1>

          <p className="hero-description">
            Dapatkan prediksi harga komoditas pangan yang akurat di wilayah
            Jakarta. Membantu pedagang dan konsumen membuat keputusan yang lebih
            baik dengan data yang dapat dipercaya.
          </p>

          <div className="hero-stats">
            <motion.div
              className="stat-item"
              whileHover={{ scale: 1.05 }}
              transition={{ type: "spring", stiffness: 300 }}
            >
              <div className="stat-number">31</div>
              <div className="stat-label">Komoditas</div>
            </motion.div>
            <motion.div
              className="stat-item"
              whileHover={{ scale: 1.05 }}
              transition={{ type: "spring", stiffness: 300 }}
            >
              <div className="stat-number">92%</div>
              <div className="stat-label">Akurasi</div>
            </motion.div>
            <motion.div
              className="stat-item"
              whileHover={{ scale: 1.05 }}
              transition={{ type: "spring", stiffness: 300 }}
            >
              <div className="stat-number">7</div>
              <div className="stat-label">Tahun Data</div>
            </motion.div>
          </div>
        </motion.div>

        <motion.div
          className="hero-visual"
          initial={{ opacity: 0, x: 30 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.8, delay: 0.4 }}
        >
          <div className="visual-container">
            <motion.div
              className="floating-illustration"
              animate={{
                y: [0, -20, 0],
                rotate: [0, 5, 0],
              }}
              transition={{
                duration: 6,
                repeat: Infinity,
                ease: "easeInOut",
              }}
            >
              <img
                src="/illustrations/charts-analytics.svg"
                alt="Data Analytics Visualization"
                style={{ width: "100%", height: "auto" }}
              />
            </motion.div>

            <motion.div
              className="floating-icon icon-1"
              animate={{
                y: [0, -15, 0],
                x: [0, 10, 0],
              }}
              transition={{
                duration: 4,
                repeat: Infinity,
                ease: "easeInOut",
              }}
            >
              <img
                src="/illustrations/network-avatar.svg"
                alt="Network Icon"
                style={{ width: "80px", height: "80px" }}
              />
            </motion.div>

            <motion.div
              className="floating-icon icon-2"
              animate={{
                y: [0, 20, 0],
                x: [0, -10, 0],
              }}
              transition={{
                duration: 5,
                repeat: Infinity,
                ease: "easeInOut",
                delay: 1,
              }}
            >
              <img
                src="/illustrations/network-connection.svg"
                alt="Connection Icon"
                style={{ width: "70px", height: "70px" }}
              />
            </motion.div>
          </div>
        </motion.div>
      </div>
    </motion.section>
  );
};

export default HeroSection;
