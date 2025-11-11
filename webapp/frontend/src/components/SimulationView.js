import React from 'react';
import { motion } from 'framer-motion';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

function SimulationView({ results, isRunning, statusMessage, progress, onReset }) {
  // Prepare data for convergence chart
  const prepareChartData = () => {
    if (!results) return [];
    
    // Filter out undefined/null results (not completed yet)
    const completedResults = results.filter(r => r && r.convergence_history);
    if (completedResults.length === 0) return [];
    
    const maxLength = Math.max(...completedResults.map(r => r.convergence_history.iterations.length));
    
    const chartData = [];
    for (let i = 0; i < maxLength; i++) {
      const dataPoint = { index: i };
      results.forEach((result, simIndex) => {
        if (result && result.convergence_history && result.convergence_history.iterations[i]) {
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
              Running Simulations
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
            
          </div>

          {/* Right: PDF Viewer */}
          <div style={{
            background: 'rgba(255, 255, 255, 0.1)',
            borderRadius: '15px',
            padding: '2rem',
            backdropFilter: 'blur(10px)'
          }}>
            <h2 style={{ fontSize: '1.8rem', marginBottom: '1rem' }}>
              Read My Research Report
            </h2>
            <p style={{ fontSize: '1.1rem', marginBottom: '1.5rem', opacity: 0.9 }}>
              While you wait, learn about the research question:
              <br/><strong>"How does the size of the central hot square affect the number of iterations a Jacobi solver needs to reach a given tolerance?"</strong>
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
            {results.map((result, index) => result ? (
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
            ) : null)}
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
                <LineChart 
                  data={chartData}
                  margin={{ top: 20, right: 30, left: 60, bottom: 40 }}
                >
                  <CartesianGrid strokeDasharray="3 3" stroke="#ccc" strokeWidth={0.5} />
                  <XAxis 
                    dataKey="iteration" 
                    stroke="#000"
                    strokeWidth={1.5}
                    label={{ 
                      value: 'Iteration', 
                      position: 'insideBottom', 
                      offset: -10, 
                      style: { fontSize: 18, fontWeight: 'bold', fill: '#000' } 
                    }}
                    tick={{ fill: '#000', fontSize: 14 }}
                    tickLine={{ stroke: '#000' }}
                    type="number"
                  />
                  <YAxis 
                    scale="log"
                    domain={['auto', 'auto']}
                    stroke="#000"
                    strokeWidth={1.5}
                    label={{ 
                      value: 'Max Change δ (log scale)', 
                      angle: -90, 
                      position: 'insideLeft', 
                      offset: 10,
                      style: { fontSize: 18, fontWeight: 'bold', fill: '#000' } 
                    }}
                    tick={{ fill: '#000', fontSize: 14 }}
                    tickFormatter={(value) => {
                      const exponent = Math.round(Math.log10(value));
                      const superscripts = {
                        '0': '⁰', '1': '¹', '2': '²', '3': '³', '4': '⁴',
                        '5': '⁵', '6': '⁶', '7': '⁷', '8': '⁸', '9': '⁹',
                        '-': '⁻'
                      };
                      const expStr = String(exponent);
                      const superscript = expStr.split('').map(c => superscripts[c] || c).join('');
                      return `10${superscript}`;
                    }}
                    tickLine={{ stroke: '#000' }}
                  />
                  <Tooltip 
                    contentStyle={{ background: 'rgba(255, 255, 255, 0.95)', borderRadius: '8px', border: '1px solid #ccc' }}
                    formatter={(value) => value?.toExponential(2)}
                    labelFormatter={(label) => `Iteration: ${label}`}
                  />
                  <Legend 
                    wrapperStyle={{ paddingTop: '20px' }}
                    iconType="line"
                  />
                  {results.map((result, index) => result ? (
                    <Line
                      key={index}
                      type="monotone"
                      dataKey={`sim${index}`}
                      name={`f=${result.hot_fraction.toFixed(2)}`}
                      stroke={colors[index % colors.length]}
                      strokeWidth={2}
                      dot={false}
                      isAnimationActive={true}
                    />
                  ) : null)}
                </LineChart>
              </ResponsiveContainer>
            </div>
          </motion.div>
        </div>
      ) : null}
    </motion.div>
  );
}

export default SimulationView;
