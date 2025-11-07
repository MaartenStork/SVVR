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
  const [progress, setProgress] = useState([]);

  useEffect(() => {
    // Connect to WebSocket
    const newSocket = io(BACKEND_URL, {
      transports: ['polling', 'websocket'],
      reconnection: true,
      reconnectionAttempts: 10,
      reconnectionDelay: 2000,
      timeout: 60000,  // 60 seconds timeout
      pingTimeout: 120000,  // 2 minutes before considering connection dead
      pingInterval: 30000  // Ping every 30 seconds
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
      console.log(`Simulations started! Running ${data.num_simulations} simulations`);
      setIsRunning(true);
      setStatusMessage(`Running ${data.num_simulations} simulation${data.num_simulations > 1 ? 's' : ''} in parallel...`);
      setResults(null);
      setProgress(new Array(data.num_simulations).fill(0));
    });

    newSocket.on('simulation_progress', (data) => {
      // Receive all progress values at once
      if (data.progress && Array.isArray(data.progress)) {
        console.log(`📊 Progress: [${data.progress.join('%, ')}%]`);
        setProgress(data.progress);
      }
    });

    // Handle individual simulation completion (as they finish)
    newSocket.on('simulation_complete', (data) => {
      console.log(`✓ Simulation ${data.index} complete!`, data.result);
      setResults(prevResults => {
        const newResults = prevResults ? [...prevResults] : [];
        newResults[data.index] = data.result;
        return newResults;
      });
    });

    newSocket.on('all_simulations_complete', (data) => {
      console.log('All simulations complete!', data.results);
      setIsRunning(false);
      setStatusMessage('All simulations completed!');
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
    setProgress([]);
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

