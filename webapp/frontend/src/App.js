import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import io from 'socket.io-client';
import WelcomeScreen from './components/WelcomeScreen';
import SimulationView from './components/SimulationView';
import './App.css';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:5000';

function App() {
  const [socket, setSocket] = useState(null);
  const [started, setStarted] = useState(false);
  const [simulations, setSimulations] = useState([]);
  const [convergenceData, setConvergenceData] = useState({});
  const [isRunning, setIsRunning] = useState(false);
  const [statusMessage, setStatusMessage] = useState('');

  useEffect(() => {
    // Connect to WebSocket
    const newSocket = io(BACKEND_URL, {
      transports: ['websocket', 'polling'],
      reconnection: true
    });

    newSocket.on('connect', () => {
      console.log('Connected to server');
      setStatusMessage('Connected to simulation server');
    });

    newSocket.on('simulation_update', (data) => {
      const { sim_index, iteration, delta, frame, hot_fraction, converged } = data;
      
      // Update simulation frame
      setSimulations(prev => {
        const newSims = [...prev];
        newSims[sim_index] = {
          ...newSims[sim_index],
          frame,
          iteration,
          delta,
          hot_fraction,
          converged
        };
        return newSims;
      });

      // Update convergence data
      setConvergenceData(prev => ({
        ...prev,
        [sim_index]: [
          ...(prev[sim_index] || []),
          { iteration, delta, hot_fraction }
        ]
      }));
    });

    newSocket.on('simulation_started', (data) => {
      setIsRunning(true);
      setStatusMessage(data.message);
      // Initialize simulation states
      const numSims = data.num_simulations;
      setSimulations(Array(numSims).fill(null).map(() => ({
        frame: null,
        iteration: 0,
        delta: 0,
        hot_fraction: 0,
        converged: false
      })));
      setConvergenceData({});
    });

    newSocket.on('all_simulations_complete', (data) => {
      setIsRunning(false);
      setStatusMessage('All simulations completed!');
      console.log('Results:', data.results);
    });

    newSocket.on('error', (data) => {
      console.error('Error:', data.message);
      setStatusMessage(`Error: ${data.message}`);
      setIsRunning(false);
    });

    setSocket(newSocket);

    return () => newSocket.close();
  }, []);

  const handleStart = (hotFractions) => {
    if (socket) {
      setStarted(true);
      socket.emit('start_simulation', { hot_fractions: hotFractions });
    }
  };

  const handleReset = () => {
    setStarted(false);
    setSimulations([]);
    setConvergenceData({});
    setIsRunning(false);
    setStatusMessage('');
  };

  return (
    <div className="App">
      <AnimatePresence mode="wait">
        {!started ? (
          <WelcomeScreen key="welcome" onStart={handleStart} />
        ) : (
          <SimulationView
            key="simulation"
            simulations={simulations}
            convergenceData={convergenceData}
            isRunning={isRunning}
            statusMessage={statusMessage}
            onReset={handleReset}
          />
        )}
      </AnimatePresence>
    </div>
  );
}

export default App;

