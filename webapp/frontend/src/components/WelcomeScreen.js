import React, { useState } from 'react';
import { motion } from 'framer-motion';

function WelcomeScreen({ onStart }) {
  const [fraction1, setFraction1] = useState(0.1);
  const [fraction2, setFraction2] = useState(0.2);
  const [fraction3, setFraction3] = useState(0.33);
  
  // Advanced options
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [gridSize, setGridSize] = useState(51);
  const [tolerance, setTolerance] = useState(0.005);
  const [maxIters, setMaxIters] = useState(5000);
  const [frameEvery, setFrameEvery] = useState(100);

  const handleSubmit = (e) => {
    e.preventDefault();
    const fractions = [
      parseFloat(fraction1),
      parseFloat(fraction2),
      parseFloat(fraction3)
    ].filter(f => f > 0 && f <= 1);
    
    if (fractions.length > 0) {
      onStart({
        hot_fractions: fractions,
        grid_size: parseInt(gridSize),
        tolerance: parseFloat(tolerance),
        max_iters: parseInt(maxIters),
        frame_every: parseInt(frameEvery)
      });
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

          {/* Advanced Options Toggle */}
          <button
            type="button"
            onClick={() => setShowAdvanced(!showAdvanced)}
            style={{
              background: 'rgba(255, 255, 255, 0.2)',
              border: '2px solid rgba(255, 255, 255, 0.3)',
              color: 'white',
              padding: '0.6rem 1.5rem',
              borderRadius: '10px',
              cursor: 'pointer',
              fontSize: '1rem',
              fontWeight: '600',
              marginBottom: '1rem'
            }}
          >
            {showAdvanced ? '▼' : '▶'} Advanced Options
          </button>

          {/* Advanced Options Panel */}
          {showAdvanced && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              style={{
                background: 'rgba(0, 0, 0, 0.2)',
                padding: '1.5rem',
                borderRadius: '10px',
                marginBottom: '1.5rem'
              }}
            >
              <h3 style={{ fontSize: '1.2rem', marginBottom: '1rem', textAlign: 'left' }}>
                Performance Settings
              </h3>
              
              <div className="fraction-inputs">
                <div className="input-group">
                  <label>Grid Size (NxN):</label>
                  <input
                    type="number"
                    min="21"
                    max="181"
                    step="10"
                    value={gridSize}
                    onChange={(e) => setGridSize(e.target.value)}
                  />
                  <span style={{ fontSize: '0.8rem', opacity: 0.7 }}>Smaller = faster</span>
                </div>
                
                <div className="input-group">
                  <label>Tolerance:</label>
                  <input
                    type="number"
                    min="0.001"
                    max="0.01"
                    step="0.001"
                    value={tolerance}
                    onChange={(e) => setTolerance(e.target.value)}
                  />
                  <span style={{ fontSize: '0.8rem', opacity: 0.7 }}>Higher = faster</span>
                </div>
                
                <div className="input-group">
                  <label>Max Iterations:</label>
                  <input
                    type="number"
                    min="1000"
                    max="20000"
                    step="1000"
                    value={maxIters}
                    onChange={(e) => setMaxIters(e.target.value)}
                  />
                  <span style={{ fontSize: '0.8rem', opacity: 0.7 }}>Safety limit</span>
                </div>
                
                <div className="input-group">
                  <label>Frame Every N Iters:</label>
                  <input
                    type="number"
                    min="50"
                    max="500"
                    step="50"
                    value={frameEvery}
                    onChange={(e) => setFrameEvery(e.target.value)}
                  />
                  <span style={{ fontSize: '0.8rem', opacity: 0.7 }}>More frames = smoother GIF</span>
                </div>
              </div>
              
              <p style={{ fontSize: '0.85rem', marginTop: '1rem', opacity: 0.6, textAlign: 'left' }}>
                💡 <strong>Tip:</strong> For fastest results use 51x51 grid and 0.005 tolerance. 
                For best quality use 181x181 grid and 0.001 tolerance (slower!).
              </p>
            </motion.div>
          )}

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
          The simulation will run three configurations in parallel and compare their convergence behavior.
        </p>
      </motion.div>
    </motion.div>
  );
}

export default WelcomeScreen;

