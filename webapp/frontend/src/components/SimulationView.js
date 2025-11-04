import React from 'react';
import { motion } from 'framer-motion';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

function SimulationView({ simulations, convergenceData, isRunning, statusMessage, onReset }) {
  // Prepare data for convergence chart
  const prepareChartData = () => {
    const maxLength = Math.max(
      ...Object.values(convergenceData).map(data => data?.length || 0)
    );
    
    const chartData = [];
    for (let i = 0; i < maxLength; i++) {
      const dataPoint = { iteration: i };
      Object.keys(convergenceData).forEach(simIndex => {
        if (convergenceData[simIndex] && convergenceData[simIndex][i]) {
          dataPoint[`sim${simIndex}`] = convergenceData[simIndex][i].delta;
        }
      });
      chartData.push(dataPoint);
    }
    return chartData;
  };

  const chartData = prepareChartData();
  const colors = ['#3b82f6', '#f59e0b', '#10b981'];

  return (
    <motion.div
      className="simulation-view"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      transition={{ duration: 0.5 }}
    >
      <div className="simulation-header">
        <h1>Live Simulation Dashboard</h1>
        <div className="status-message">
          {isRunning && <span className="running-indicator"></span>}
          {statusMessage}
        </div>
        <button className="reset-button" onClick={onReset}>
          ↻ New Simulation
        </button>
      </div>

      <div className="simulation-content">
        {/* Left Panel: Simulations */}
        <div className="simulations-panel">
          {simulations.map((sim, index) => (
            <motion.div
              key={index}
              className="simulation-card"
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.5, delay: index * 0.1 }}
            >
              <h3>
                <span>Hot-Square {(sim?.hot_fraction || 0).toFixed(2)}</span>
                {sim?.converged && <span className="converged-badge">✓ Converged</span>}
              </h3>
              
              <div className="simulation-info">
                <span>Iteration: {sim?.iteration || 0}</span>
                <span>Delta: {(sim?.delta || 0).toExponential(2)}</span>
              </div>

              {sim?.frame ? (
                <img
                  src={sim.frame}
                  alt={`Simulation ${index + 1}`}
                  className="simulation-frame"
                />
              ) : (
                <div className="simulation-frame loading">
                  <motion.div
                    animate={{ rotate: 360 }}
                    transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                    style={{ fontSize: '2rem' }}
                  >
                    ⏳
                  </motion.div>
                </div>
              )}
            </motion.div>
          ))}
        </div>

        {/* Right Panel: Convergence Plot */}
        <motion.div
          className="convergence-panel"
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.5, delay: 0.3 }}
        >
          <h2>Convergence Comparison</h2>
          
          {chartData.length > 0 ? (
            <div className="chart-container">
              <ResponsiveContainer width="100%" height={600}>
                <LineChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis 
                    dataKey="iteration" 
                    label={{ value: 'Iteration', position: 'insideBottom', offset: -5 }}
                  />
                  <YAxis 
                    scale="log"
                    domain={['auto', 'auto']}
                    label={{ value: 'Delta (log scale)', angle: -90, position: 'insideLeft' }}
                  />
                  <Tooltip 
                    contentStyle={{ background: 'rgba(255, 255, 255, 0.95)', borderRadius: '8px' }}
                    formatter={(value) => value.toExponential(2)}
                  />
                  <Legend />
                  {simulations.map((sim, index) => (
                    <Line
                      key={index}
                      type="monotone"
                      dataKey={`sim${index}`}
                      name={`Size ${(sim?.hot_fraction || 0).toFixed(2)}`}
                      stroke={colors[index % colors.length]}
                      strokeWidth={2}
                      dot={false}
                      isAnimationActive={false}
                    />
                  ))}
                </LineChart>
              </ResponsiveContainer>
            </div>
          ) : (
            <div style={{ 
              background: 'rgba(255, 255, 255, 0.1)', 
              height: '600px', 
              borderRadius: '10px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: '1.2rem'
            }}>
              Waiting for simulation data...
            </div>
          )}

          {simulations.length > 0 && simulations.some(s => s?.converged) && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              style={{ 
                marginTop: '1.5rem', 
                padding: '1rem', 
                background: 'rgba(74, 222, 128, 0.2)',
                borderRadius: '10px',
                border: '2px solid rgba(74, 222, 128, 0.5)'
              }}
            >
              <h3 style={{ marginBottom: '0.5rem' }}>Results Summary:</h3>
              {simulations.map((sim, index) => 
                sim?.converged && (
                  <div key={index} style={{ marginBottom: '0.3rem' }}>
                    <strong>Size {(sim.hot_fraction || 0).toFixed(2)}:</strong> {sim.iteration} iterations
                  </div>
                )
              )}
            </motion.div>
          )}
        </motion.div>
      </div>
    </motion.div>
  );
}

export default SimulationView;

