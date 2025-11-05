import React, { useState } from 'react';
import { motion } from 'framer-motion';

function WelcomeScreen({ onStart }) {
  // Dynamic simulations (start with 1)
  const [simulations, setSimulations] = useState([
    { id: 1, fraction: 0.2 }
  ]);
  
  // Advanced options
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [gridSize, setGridSize] = useState(51);
  const [tolerance, setTolerance] = useState(0.001);
  const [maxIters, setMaxIters] = useState(15000);
  const [frameEvery, setFrameEvery] = useState(20);

  const addSimulation = () => {
    if (simulations.length < 5) {  // Max 5 simulations
      const newId = Math.max(...simulations.map(s => s.id)) + 1;
      setSimulations([...simulations, { id: newId, fraction: 0.2 }]);
    }
  };

  const removeSimulation = (id) => {
    if (simulations.length > 1) {  // Keep at least 1
      setSimulations(simulations.filter(s => s.id !== id));
    }
  };

  const updateFraction = (id, value) => {
    setSimulations(simulations.map(s => 
      s.id === id ? { ...s, fraction: parseFloat(value) } : s
    ));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    const fractions = simulations
      .map(s => s.fraction)
      .filter(f => f > 0 && f <= 1);
    
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
        Jacobi Heat Simulation
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
            {simulations.map((sim, index) => (
              <div key={sim.id} className="input-group">
                <label htmlFor={`fraction${sim.id}`}>
                  Hot-Square Size {index + 1}:
                </label>
                <input
                  id={`fraction${sim.id}`}
                  name={`fraction${sim.id}`}
                  type="number"
                  step="0.01"
                  min="0.01"
                  max="1"
                  value={sim.fraction}
                  onChange={(e) => updateFraction(sim.id, e.target.value)}
                  placeholder="e.g., 0.2"
                />
                {simulations.length > 1 && (
                  <button
                    type="button"
                    onClick={() => removeSimulation(sim.id)}
                    style={{
                      background: '#ef4444',
                      color: 'white',
                      border: 'none',
                      borderRadius: '8px',
                      padding: '0.5rem 1rem',
                      cursor: 'pointer',
                      fontSize: '1rem',
                      fontWeight: 'bold'
                    }}
                  >
                    ✕
                  </button>
                )}
              </div>
            ))}
            
            {/* Add Simulation Button */}
            {simulations.length < 5 && (
              <button
                type="button"
                onClick={addSimulation}
                style={{
                  background: 'rgba(139, 92, 246, 0.3)',
                  border: '2px dashed rgba(167, 139, 250, 0.6)',
                  color: 'white',
                  padding: '0.8rem',
                  borderRadius: '10px',
                  cursor: 'pointer',
                  fontSize: '1.1rem',
                  fontWeight: '600',
                  width: '100%',
                  marginTop: '0.5rem'
                }}
              >
                ➕ Add Another Simulation (max 5)
              </button>
            )}
          </div>

          <motion.button
            type="submit"
            className="start-button"
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            style={{ marginBottom: '0rem' }}
          >
            Run Simulations
          </motion.button>

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
              marginTop: '1rem',
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
                  <label htmlFor="gridSize">Grid Size (NxN):</label>
                  <input
                    id="gridSize"
                    name="gridSize"
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
                  <label htmlFor="tolerance">Tolerance:</label>
                  <input
                    id="tolerance"
                    name="tolerance"
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
                  <label htmlFor="maxIters">Max Iterations:</label>
                  <input
                    id="maxIters"
                    name="maxIters"
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
                  <label htmlFor="frameEvery">Frame Every N Iters:</label>
                  <input
                    id="frameEvery"
                    name="frameEvery"
                    type="number"
                    min="1"
                    max="500"
                    step="1"
                    value={frameEvery}
                    onChange={(e) => setFrameEvery(e.target.value)}
                  />
                  <span style={{ fontSize: '0.8rem', opacity: 0.7 }}>More frames = smoother GIF</span>
                </div>
              </div>
              
              <p style={{ fontSize: '0.85rem', marginTop: '1rem', opacity: 0.6, textAlign: 'left' }}>
                💡 <strong>Tip:</strong> Defaults (51x51, tol=0.001) run until proper convergence (~1-2 min). 
                For quality: 91x91 + tol=0.001 (~3-4 min). For research: 181x181 + tol=0.001 (~8-10 min).
              </p>
            </motion.div>
          )}
        </form>

        <p style={{ fontSize: '0.9rem', marginTop: '1.5rem', opacity: 0.7 }}>
          The simulations will run in parallel and compare their convergence behavior.
        </p>
      </motion.div>
    </motion.div>
  );
}

export default WelcomeScreen;

