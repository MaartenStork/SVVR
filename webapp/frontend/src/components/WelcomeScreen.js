import React, { useState } from 'react';
import { motion } from 'framer-motion';

function WelcomeScreen({ onStart }) {
  const [fraction1, setFraction1] = useState(0.1);
  const [fraction2, setFraction2] = useState(0.2);
  const [fraction3, setFraction3] = useState(0.33);

  const handleSubmit = (e) => {
    e.preventDefault();
    const fractions = [
      parseFloat(fraction1),
      parseFloat(fraction2),
      parseFloat(fraction3)
    ].filter(f => f > 0 && f <= 1);
    
    if (fractions.length > 0) {
      onStart(fractions);
    } else {
      alert('Please enter valid fractions between 0 and 1');
    }
  };

  return (
    <motion.div
      className="welcome-screen"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      transition={{ duration: 0.5 }}
    >
      <motion.h1
        initial={{ scale: 0.9 }}
        animate={{ scale: 1 }}
        transition={{ duration: 0.5, delay: 0.2 }}
      >
        🔥 Jacobi Heat Simulation
      </motion.h1>
      
      <motion.p
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.5, delay: 0.4 }}
      >
        Real-time Temperature Field Solver
      </motion.p>

      <motion.div
        className="input-section"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.6 }}
      >
        <h2>Configure Hot-Square Sizes</h2>
        <p style={{ fontSize: '1rem', marginBottom: '1.5rem', opacity: 0.8 }}>
          Enter the size of the hot square as a fraction of the domain (0 to 1)
        </p>
        
        <form onSubmit={handleSubmit}>
          <div className="fraction-inputs">
            <div className="input-group">
              <label>Simulation 1 (Small):</label>
              <input
                type="number"
                step="0.01"
                min="0.01"
                max="1"
                value={fraction1}
                onChange={(e) => setFraction1(e.target.value)}
                placeholder="e.g., 0.1"
              />
            </div>
            
            <div className="input-group">
              <label>Simulation 2 (Medium):</label>
              <input
                type="number"
                step="0.01"
                min="0.01"
                max="1"
                value={fraction2}
                onChange={(e) => setFraction2(e.target.value)}
                placeholder="e.g., 0.2"
              />
            </div>
            
            <div className="input-group">
              <label>Simulation 3 (Large):</label>
              <input
                type="number"
                step="0.01"
                min="0.01"
                max="1"
                value={fraction3}
                onChange={(e) => setFraction3(e.target.value)}
                placeholder="e.g., 0.33"
              />
            </div>
          </div>

          <motion.button
            type="submit"
            className="start-button"
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            🚀 Run Simulations
          </motion.button>
        </form>

        <p style={{ fontSize: '0.9rem', marginTop: '1.5rem', opacity: 0.7 }}>
          The simulation will run three configurations and compare their convergence behavior in real-time.
        </p>
      </motion.div>
    </motion.div>
  );
}

export default WelcomeScreen;

