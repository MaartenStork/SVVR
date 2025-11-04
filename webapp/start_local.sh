#!/bin/bash

# Quick start script for local development

echo "🔥 Starting Jacobi Heat Simulation Web App"
echo "=========================================="

# Check if in correct directory
if [ ! -d "backend" ] || [ ! -d "frontend" ]; then
    echo "❌ Error: Please run this script from the webapp directory"
    exit 1
fi

# Start backend in background
echo "📡 Starting backend server..."
cd backend
python app.py &
BACKEND_PID=$!
cd ..

# Wait for backend to start
echo "⏳ Waiting for backend to initialize..."
sleep 3

# Start frontend
echo "🎨 Starting frontend..."
cd frontend
npm start

# Cleanup on exit
trap "echo '🛑 Shutting down...'; kill $BACKEND_PID" EXIT

