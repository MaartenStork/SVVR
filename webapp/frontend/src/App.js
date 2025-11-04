import React, { useState, useEffect } from 'react';
import { AnimatePresence } from 'framer-motion';
import io from 'socket.io-client';
import WelcomeScreen from './components/WelcomeScreen';
import SimulationView from './components/SimulationView';
import './App.css';

// Connect to same origin (backend serves the frontend)
const BACKEND_URL = window.location.origin;

function App() {
  const [socket, setSocket] = useState(null);
  const [started, setStarted] = useState(false);
  const [results, setResults] = useState(null);
  const [isRunning, setIsRunning] = useState(false);
  const [statusMessage, setStatusMessage] = useState('');
  const [progress, setProgress] = useState([0, 0, 0]);

  useEffect(() => {
    // Connect to WebSocket
    const newSocket = io(BACKEND_URL, {
      transports: ['polling', 'websocket'],
      reconnection: true,
      reconnectionAttempts: 5,
      reconnectionDelay: 1000,
      timeout: 10000
    });

    newSocket.on('connect', () => {
      console.log('✅ Connected to server');
      setStatusMessage('Connected to simulation server');
    });

    newSocket.on('disconnect', (reason) => {
      console.log('🔌 Disconnected:', reason);
      setStatusMessage('⚠️ Connection lost. Reconnecting...');
      setIsRunning(false);
    });

    newSocket.on('connect_error', (error) => {
      console.error('❌ Connection error:', error);
      setStatusMessage('Connection error. Retrying...');
    });

    newSocket.on('simulation_started', (data) => {
      console.log('Simulations started!');
      setIsRunning(true);
      setStatusMessage('Running simulations in parallel... Please wait.');
      setResults(null);
      setProgress([0, 0, 0]);
    });

    newSocket.on('simulation_progress', (data) => {
      console.log(`📊 Progress - Sim ${data.sim_index}: ${data.progress}% (Iteration ${data.iteration}/${data.max_iters})`);
      setProgress(prev => {
        const newProgress = [...prev];
        newProgress[data.sim_index] = data.progress;
        return newProgress;
      });
    });

    newSocket.on('all_simulations_complete', (data) => {
      console.log('All simulations complete!', data.results);
      setIsRunning(false);
      setStatusMessage('All simulations completed!');
      setResults(data.results);
    });

    newSocket.on('error', (data) => {
      console.error('Error:', data.message);
      setStatusMessage(`Error: ${data.message}`);
      setIsRunning(false);
    });

    setSocket(newSocket);

    return () => newSocket.close();
  }, []);

  const handleStart = (params) => {
    if (socket) {
      setStarted(true);
      socket.emit('start_simulation', params);
    }
  };

  const handleReset = () => {
    setStarted(false);
    setResults(null);
    setIsRunning(false);
    setStatusMessage('');
    setProgress([0, 0, 0]);
  };

  return (
    <div className="App">
      <AnimatePresence mode="wait">
        {!started ? (
          <WelcomeScreen key="welcome" onStart={handleStart} />
        ) : (
          <SimulationView
            key="simulation"
            results={results}
            isRunning={isRunning}
            statusMessage={statusMessage}
            progress={progress}
            onReset={handleReset}
          />
        )}
      </AnimatePresence>
    </div>
  );
}

export default App;

