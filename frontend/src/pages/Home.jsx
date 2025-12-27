import { motion } from "framer-motion";
import { FaChartLine, FaInfoCircle } from "react-icons/fa";
import React, { useState, useEffect } from "react";
import axios from "axios";
import { Line, Bar } from "react-chartjs-2";
import "chart.js/auto";
import HeroSection from "../components/HeroSection";
import "../App.css";

const Home = () => {
  const [commodities, setCommodities] = useState([]);
  const [selectedCommodity, setSelectedCommodity] = useState("");
  const [monthsToPredict, setMonthsToPredict] = useState(1);
  const [prediction, setPrediction] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [showBounds, setShowBounds] = useState(true);

  useEffect(() => {
    const fetchCommodities = async () => {
      try {
        const response = await axios.get(
          `${import.meta.env.VITE_API_URL}/api/commodities`
        );
        setCommodities(response.data);
      } catch (err) {
        setError("Failed to fetch commodities.");
        console.error(err);
      }
    };

    fetchCommodities();
  }, []);

  const handlePredict = async () => {
    if (!selectedCommodity) {
      setError("Please select a commodity.");
      return;
    }

    setLoading(true);
    setError(null);
    setPrediction(null);

    try {
      const response = await axios.post(
        `${import.meta.env.VITE_API_URL}/api/predict`,
        {
          commodity: selectedCommodity,
          months: monthsToPredict,
        }
      );
      const result = response.data;
      if (result && result.predictions && !Array.isArray(result.predictions)) {
        result.predictions = [result.predictions];
      }
      setPrediction(result);
    } catch (err) {
      setError("Failed to get prediction.");
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const chartType =
    prediction &&
    prediction.predictions &&
    Array.isArray(prediction.predictions) &&
    prediction.predictions.length === 1
      ? "bar"
      : "line";

  const ChartComponent = chartType === "bar" ? Bar : Line;

  const chartData = {
    labels: (prediction?.predictions || []).map((p) =>
      new Date(p.ds).toLocaleDateString()
    ),
    datasets: [
      {
        label: "Prediksi Harga",
        data: (prediction?.predictions || []).map((p) => p.yhat),
        borderColor: "#3e95cd",
        backgroundColor: "#3e95cd",
        fill: false,
        borderWidth: 3,
      },
      {
        label: "Batas Atas",
        data: showBounds
          ? (prediction?.predictions || []).map((p) => p.yhat_upper)
          : [],
        borderColor: "#8e5ea2",
        backgroundColor: "#8e5ea2",
        fill: false,
        borderDash: [5, 5],
      },
      {
        label: "Batas Bawah",
        data: showBounds
          ? (prediction?.predictions || []).map((p) => p.yhat_lower)
          : [],
        borderColor: "#c45850",
        backgroundColor: "#c45850",
        fill: false,
        borderDash: [5, 5],
      },
    ],
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: "top",
      },
      title: {
        display: true,
        text: `Prediksi Harga untuk ${selectedCommodity}`,
        font: {
          size: 16,
        },
      },
    },
    scales: {
      y: {
        title: {
          display: true,
          text: "Harga (IDR)",
          font: {
            size: 12,
            weight: "bold",
          },
          padding: { bottom: 10 },
        },
        ticks: {
          font: {
            size: 10,
          },
        },
      },
      x: {
        title: {
          display: true,
          text: "Tanggal",
          font: {
            size: 12,
            weight: "bold",
          },
          padding: { top: 10 },
        },
        ticks: {
          font: {
            size: 10,
          },
          autoSkip: true,
          maxTicksLimit: 12,
          maxRotation: 90,
          minRotation: 90,
        },
      },
    },
  };

  const PredictionSummary = ({ summary }) => {
    if (!summary) return null;

    return (
      <div className="prediction-summary">
        <h3>
          <FaInfoCircle /> Ringkasan Prediksi
        </h3>
        <p>{summary}</p>
      </div>
    );
  };

  const generateSummary = (predictions) => {
    if (!predictions || predictions.length === 0) {
      return "";
    }

    const firstPred = predictions[0];
    const lastPred = predictions[predictions.length - 1];
    const trend =
      lastPred.yhat > firstPred.yhat
        ? "cenderung naik"
        : lastPred.yhat < firstPred.yhat
        ? "cenderung turun"
        : "tetap stabil";

    const startDate = new Date(firstPred.ds).toLocaleDateString("id-ID", {
      month: "long",
      year: "numeric",
    });
    const endDate = new Date(lastPred.ds).toLocaleDateString("id-ID", {
      month: "long",
      year: "numeric",
    });

    return `Ringkasan prediksi untuk ${selectedCommodity} selama ${monthsToPredict} bulan dari ${startDate} hingga ${endDate}. Harga awal diperkirakan sekitar Rp ${Math.round(
      firstPred.yhat
    ).toLocaleString()}. Secara umum, harga ${trend}. Pada akhir periode (${endDate}), harga diprediksi mencapai sekitar Rp ${Math.round(
      lastPred.yhat
    ).toLocaleString()}. Rentang kepercayaan terluas untuk periode ini berada antara Rp ${Math.round(
      predictions.reduce((min, p) => Math.min(min, p.yhat_lower), Infinity)
    ).toLocaleString()} dan Rp ${Math.round(
      predictions.reduce((max, p) => Math.max(max, p.yhat_upper), -Infinity)
    ).toLocaleString()}.`;
  };

  return (
    <motion.main
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      transition={{ duration: 0.5 }}
    >
      <HeroSection />

      <div className="controls glass-container">
        <div className="form-main-controls">
          <div className="input-group">
            <label htmlFor="commodity-select">Pilih Komoditas:</label>
            <select
              id="commodity-select"
              value={selectedCommodity}
              onChange={(e) => setSelectedCommodity(e.target.value)}
            >
              {commodities.map((c) => (
                <option key={c} value={c}>
                  {c}
                </option>
              ))}
            </select>
          </div>
          <div class="input-group">
            <label htmlFor="months-input">Jangka Waktu (Bulan):</label>
            <input
              id="months-input"
              type="number"
              value={monthsToPredict}
              onChange={(e) => setMonthsToPredict(parseInt(e.target.value, 10))}
              min="1"
            />
          </div>
          <button onClick={handlePredict} disabled={loading}>
            {loading ? "Memprediksi..." : "Prediksi"}
          </button>
        </div>
        <div class="chart-options">
          <label>
            <input
              type="checkbox"
              checked={showBounds}
              onChange={() => setShowBounds(!showBounds)}
            />
            Tampilkan Rentang Keyakinan
          </label>
        </div>
      </div>
      {error && <p className="error-message">{error}</p>}
      {loading && <div className="spinner"></div>}
      {prediction && (
        <>
          <motion.div
            className="chart-container glass-container"
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.5 }}
          >
            <ChartComponent data={chartData} options={chartOptions} />
          </motion.div>
          <motion.div
            className="info-container-wrapper glass-container"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.2 }}
          >
            <div className="info-container">
              <div className="info-card">
                <h3>
                  <FaChartLine /> Cara Membaca Grafik Ini
                </h3>
                <p>
                  <strong>Prediksi Harga:</strong> Ini adalah perkiraan terbaik
                  model untuk harga komoditas di masa depan.
                </p>
                {showBounds && (
                  <p>
                    <strong>Rentang Keyakinan:</strong> Garis-garis ini (atas
                    dan bawah) mewakili rentang di mana harga sebenarnya
                    kemungkinan akan berada. Pita yang lebih lebar menunjukkan
                    lebih banyak ketidakpastian dalam prediksi.
                  </p>
                )}
              </div>
              <div className="info-card">
                <PredictionSummary
                  summary={generateSummary(prediction.predictions)}
                />
              </div>
            </div>
          </motion.div>
        </>
      )}
    </motion.main>
  );
};

export default Home;
