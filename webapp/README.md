# Jacobi Heat Simulation Web App

A beautiful, real-time web application for running and visualizing Jacobi heat simulations.

## Features

- 🔥 Real-time temperature field visualization
- 📊 Live convergence plotting
- 🎨 Beautiful modern UI with animations
- ⚡ WebSocket streaming for instant updates
- 📱 Responsive design

## Project Structure

```
webapp/
├── backend/              # Flask backend with WebSocket support
│   ├── app.py           # Main server application
│   └── requirements.txt # Python dependencies
├── frontend/            # React frontend
│   ├── public/          # Static assets
│   ├── src/             # React components
│   │   ├── components/  # UI components
│   │   ├── App.js       # Main app component
│   │   └── App.css      # Styling
│   └── package.json     # Node dependencies
└── render.yaml          # Render deployment config
```

## Local Development

### Backend Setup

```bash
cd backend
pip install -r requirements.txt
python app.py
```

The backend will run on `http://localhost:5000`

### Frontend Setup

```bash
cd frontend
npm install
npm start
```

The frontend will run on `http://localhost:3000`

## Deployment to Render

### Method 1: Using render.yaml (Recommended)

1. Push this repository to GitHub
2. Go to [Render Dashboard](https://dashboard.render.com/)
3. Click "New" → "Blueprint"
4. Connect your GitHub repository
5. Select the `webapp` directory containing `render.yaml`
6. Click "Apply"

Render will automatically:
- Create both backend and frontend services
- Set up environment variables
- Deploy and link the services

### Method 2: Manual Deployment

#### Backend Deployment

1. Create a new Web Service on Render
2. Connect your GitHub repository
3. Configure:
   - **Name**: `jacobi-simulation-backend`
   - **Root Directory**: `Assignment2/webapp/backend`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn --worker-class eventlet -w 1 app:app --bind 0.0.0.0:$PORT`
   - **Health Check Path**: `/health`
4. Deploy

#### Frontend Deployment

1. Create a new Static Site on Render
2. Connect your GitHub repository
3. Configure:
   - **Name**: `jacobi-simulation-frontend`
   - **Root Directory**: `Assignment2/webapp/frontend`
   - **Build Command**: `npm install && npm run build`
   - **Publish Directory**: `build`
4. Add environment variable:
   - **REACT_APP_BACKEND_URL**: `https://your-backend-url.onrender.com`
5. Deploy

## Environment Variables

### Frontend

- `REACT_APP_BACKEND_URL`: URL of the backend service (automatically set in Blueprint deployment)

### Backend

- `PORT`: Port to run the server on (automatically set by Render)

## Usage

1. Open the web app
2. Configure hot-square sizes (3 different fractions)
3. Click "Run Simulations"
4. Watch the simulations run in real-time!
5. Compare convergence rates on the live graph

## Technical Stack

### Backend
- Flask (Web framework)
- Flask-SocketIO (WebSocket support)
- NumPy (Numerical computations)
- Matplotlib (Visualization)
- Gunicorn + Eventlet (Production server)

### Frontend
- React (UI framework)
- Socket.IO Client (Real-time communication)
- Recharts (Charting library)
- Framer Motion (Animations)

## Research Question

**Does the hot-square size change the difficulty of the solve?**

This application helps answer that question by running multiple simulations simultaneously and comparing their convergence behavior in real-time.

## License

MIT

