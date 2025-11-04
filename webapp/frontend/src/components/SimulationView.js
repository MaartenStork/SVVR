import React from 'react';
import { motion } from 'framer-motion';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

function SimulationView({ results, isRunning, statusMessage, onReset }) {
  // Prepare data for convergence chart
  const prepareChartData = () => {
    if (!results) return [];
    
    const maxLength = Math.max(...results.map(r => r.convergence_history.iterations.length));
    
    const chartData = [];
    for (let i = 0; i < maxLength; i++) {
      const dataPoint = { index: i };
      results.forEach((result, simIndex) => {
        if (result.convergence_history.iterations[i]) {
          dataPoint[`sim${simIndex}`] = result.convergence_history.deltas[i];
          dataPoint.iteration = result.convergence_history.iterations[i];
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
        <h1>Simulation Results</h1>
        <div className="status-message">
          {isRunning && (
            <>
              <span className="running-indicator"></span>
              {statusMessage}
            </>
          )}
          {!isRunning && results && (
            <span>✅ {statusMessage}</span>
          )}
        </div>
        {!isRunning && results && (
          <button className="reset-button" onClick={onReset}>
            ↻ New Simulation
          </button>
        )}
      </div>

      {isRunning ? (
        <div style={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          minHeight: '60vh',
          gap: '2rem'
        }}>
          <motion.div
            animate={{ rotate: 360 }}
            transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
            style={{ fontSize: '5rem' }}
          >
            ⏳
          </motion.div>
          <h2 style={{ fontSize: '2rem', opacity: 0.9 }}>
            Running 3 simulations in parallel...
          </h2>
          <p style={{ fontSize: '1.2rem', opacity: 0.7 }}>
            This may take 3-5 minutes. The simulations are computing heat diffusion with Jacobi iteration.
          </p>
        </div>
      ) : results ? (
        <div className="simulation-content">
          {/* Left Panel: GIF Simulations */}
          <div className="simulations-panel">
            {results.map((result, index) => (
              <motion.div
                key={index}
                className="simulation-card"
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.5, delay: index * 0.1 }}
              >
                <h3>
                  <span>Hot-Square {result.hot_fraction.toFixed(2)}</span>
                  <span className="converged-badge">
                    {result.final_iter} iterations
                  </span>
                </h3>
                
                <div className="simulation-info">
                  <span>Converged at iteration: {result.final_iter}</span>
                  <span>Final Delta: {result.final_delta.toExponential(2)}</span>
                </div>

                <img
                  src={result.gif_data}
                  alt={`Simulation ${index + 1}`}
                  className="simulation-frame"
                  style={{ cursor: 'pointer' }}
                  title="Click to view full size"
                />
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
                    formatter={(value) => value?.toExponential(2)}
                  />
                  <Legend />
                  {results.map((result, index) => (
                    <Line
                      key={index}
                      type="monotone"
                      dataKey={`sim${index}`}
                      name={`Size ${result.hot_fraction.toFixed(2)}`}
                      stroke={colors[index % colors.length]}
                      strokeWidth={3}
                      dot={false}
                      isAnimationActive={true}
                    />
                  ))}
                </LineChart>
              </ResponsiveContainer>
            </div>

            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              style={{ 
                marginTop: '1.5rem', 
                padding: '1.5rem', 
                background: 'rgba(74, 222, 128, 0.2)',
                borderRadius: '10px',
                border: '2px solid rgba(74, 222, 128, 0.5)'
              }}
            >
              <h3 style={{ marginBottom: '1rem', fontSize: '1.3rem' }}>
                🔬 Research Finding:
              </h3>
              <p style={{ fontSize: '1.1rem', lineHeight: '1.6' }}>
                <strong>Larger hot squares converge FASTER!</strong>
              </p>
              {results.map((result, index) => (
                <div key={index} style={{ marginTop: '0.5rem', fontSize: '1rem' }}>
                  <strong>Size {result.hot_fraction.toFixed(2)}:</strong> {result.final_iter} iterations
                </div>
              ))}
            </motion.div>
          </motion.div>
        </div>
      ) : null}
    </motion.div>
  );
}

export default SimulationView;
