import React from 'react';
import { motion } from 'framer-motion';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

function SimulationView({ results, isRunning, statusMessage, progress, onReset }) {
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
          display: 'grid',
          gridTemplateColumns: '1fr 1fr',
          gap: '2rem',
          maxWidth: '1400px',
          margin: '0 auto',
          padding: '2rem'
        }}>
          {/* Left: Progress Bars */}
          <div>
            <h2 style={{ fontSize: '1.8rem', marginBottom: '2rem' }}>
              🔄 Running Simulations
            </h2>
            
            {progress.map((prog, idx) => (
              <div key={idx} style={{ marginBottom: '2rem' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                  <span style={{ fontSize: '1.1rem', fontWeight: 'bold' }}>
                    Simulation {idx + 1}
                  </span>
                  <span style={{ fontSize: '1rem', opacity: 0.8 }}>{prog}%</span>
                </div>
                <div style={{
                  width: '100%',
                  height: '30px',
                  background: 'rgba(255, 255, 255, 0.2)',
                  borderRadius: '15px',
                  overflow: 'hidden',
                  boxShadow: '0 2px 10px rgba(0,0,0,0.2)'
                }}>
                  <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: `${progress[idx]}%` }}
                    transition={{ 
                      duration: 0.3,  // Match update frequency exactly
                      ease: "linear"  // Linear for continuous flow
                    }}
                    style={{
                      height: '100%',
                      background: `linear-gradient(90deg, #4ade80, #22c55e)`,
                      borderRadius: '15px',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      color: 'white',
                      fontWeight: 'bold',
                      fontSize: '0.9rem'
                    }}
                  >
                    {progress[idx] > 10 && `${progress[idx]}%`}
                  </motion.div>
                </div>
              </div>
            ))}
            
            <p style={{ fontSize: '1rem', marginTop: '2rem', opacity: 0.8, lineHeight: '1.6' }}>
              ⚡ All three simulations are running in parallel.<br/>
              ⏱️ Default settings: ~1-2 minutes. High quality: ~3-10 minutes.<br/>
              📊 Progress shows convergence (delta → tolerance). Updates 3x/second!
            </p>
          </div>

          {/* Right: PDF Viewer */}
          <div style={{
            background: 'rgba(255, 255, 255, 0.1)',
            borderRadius: '15px',
            padding: '2rem',
            backdropFilter: 'blur(10px)'
          }}>
            <h2 style={{ fontSize: '1.8rem', marginBottom: '1rem' }}>
              📄 Read My Research Report
            </h2>
            <p style={{ fontSize: '1.1rem', marginBottom: '1.5rem', opacity: 0.9 }}>
              While you wait, learn about the research question:
              <br/><strong>"Does hot-square size affect solve difficulty?"</strong>
            </p>
            
            <iframe 
              src="/report.pdf" 
              width="100%" 
              height="500px"
              style={{
                borderRadius: '10px',
                border: 'none',
                boxShadow: '0 4px 15px rgba(0,0,0,0.3)'
              }}
              title="Research Report"
            />
          </div>
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
                  key={`gif-${index}-${Date.now()}`}  // Force reload with unique key
                  src={result.gif_data}
                  alt={`Simulation ${index + 1}`}
                  className="simulation-frame"
                  style={{ 
                    cursor: 'pointer',
                    imageRendering: 'auto',
                    display: 'block',
                    width: '100%'
                  }}
                  title="Click to view full size"
                  onLoad={(e) => {
                    // Force all GIFs to restart together
                    console.log(`GIF ${index} loaded`);
                  }}
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
