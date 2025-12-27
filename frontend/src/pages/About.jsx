import { motion } from "framer-motion";
import React from "react";
import {
  FaDatabase,
  FaChartLine,
  FaCode,
  FaReact,
  FaChartArea,
  FaBullseye,
  FaLayerGroup,
} from "react-icons/fa";
import { SiFlask } from "react-icons/si";
import "./About.css";

const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.15,
    },
  },
};

const itemVariants = {
  hidden: { opacity: 0, y: 20 },
  visible: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.6, ease: "easeOut" },
  },
};

const About = () => {
  return (
    <div className="about-page">
      <div className="about-content">
        <motion.header
          className="about-header"
          initial={{ opacity: 0, y: -30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7, ease: "easeOut" }}
        >
          <h1>Tentang Warta Pangan</h1>
          <motion.p
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.3, duration: 0.7 }}
          >
            Warta Pangan adalah sebuah aplikasi web inovatif yang dirancang
            untuk memberikan prediksi harga komoditas pangan di Indonesia.
            Tujuan kami adalah untuk membantu para petani, pedagang, dan
            konsumen dalam membuat keputusan yang lebih baik dengan menyediakan
            informasi tren harga yang akurat dan mudah diakses.
          </motion.p>
        </motion.header>

        <motion.div
          className="cards-container"
          variants={containerVariants}
          initial="hidden"
          animate="visible"
        >
          <motion.div
            className="about-card glass-container"
            variants={itemVariants}
          >
            <div className="card-header">
              <div className="icon-wrapper">
                <FaDatabase className="card-icon" />
              </div>
              <h2>Sumber Data</h2>
            </div>
            <div className="card-body">
              <p>
                Data harga yang kami gunakan bersumber dari Pusat Informasi
                Harga Pangan Strategis Nasional (PIHPS Nasional), mencakup data
                historis dari 2019 hingga 2025 untuk analisis yang komprehensif.
              </p>
            </div>
          </motion.div>

          <motion.div
            className="about-card glass-container"
            variants={itemVariants}
          >
            <div className="card-header">
              <div className="icon-wrapper">
                <FaChartLine className="card-icon" />
              </div>
              <h2>Metodologi</h2>
            </div>
            <div className="card-body">
              <p>
                Untuk memberikan prediksi harga yang akurat, kami menggunakan
                beberapa model machine learning yang telah teruji keandalannya.
              </p>
              <ul>
                <li>
                  <FaLayerGroup />
                  <strong>Ensemble</strong>
                </li>
                <li>
                  <FaChartArea />
                  <strong>SARIMA</strong>
                </li>
                <li>
                  <FaBullseye />
                  <strong>Prophet</strong>
                </li>
                <li>
                  <FaChartLine />
                  <strong>Holt-Winters</strong>
                </li>
              </ul>
            </div>
          </motion.div>

          <motion.div
            className="about-card glass-container"
            variants={itemVariants}
          >
            <div className="card-header">
              <div className="icon-wrapper">
                <FaCode className="card-icon" />
              </div>
              <h2>Teknologi</h2>
            </div>
            <div className="card-body">
              <ul>
                <li>
                  <FaReact />
                  <strong>Frontend:</strong> React.js
                </li>
                <li>
                  <SiFlask />
                  <strong>Backend:</strong> Flask (Python)
                </li>
              </ul>
            </div>
          </motion.div>
        </motion.div>
      </div>
    </div>
  );
};

export default About;
