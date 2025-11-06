# Scientific Visualization and Virtual Reality

This repository contains two assignments related to numerical methods and visualization. Assignment 1 is in a separate folder, while the rest is assignment 2. Structure like this due to hosting a webservice on assignment 2.

## Project Structure

```
SVVR/
├── SVVR/
│     ├── Assignment1/            # Assignment 1: Data Visualization
│     │   ├── data/               # Data files
│     │   ├── model/              # Visualization models
│     │   └── plots/              # Generated plots
│     ├── model/                  # Assignment 1: Jacobi Solver
│     │   ├── jacobi_solver.py    # Main Jacobi solver implementation
│     │   ├── experiment_hot_square_size.py
│     │   ├── experiment_results/ # Experiment outputs
│     │   ├── out_vtk/            # VTK output files
│     │   └── research_output/    # Research visualizations
│     ├── webapp/                 # Assignment 2: Web Application
│     │   ├── backend/            # Flask backend with WebSocket support
│     │   │   ├── app.py          # Main server application
│     │   │   └── requirements.txt # Python dependencies
│     │   └── frontend/           # React frontend
│     │       ├── public/         # Static assets
│     │       ├── src/            # React components
│     │       │   ├── components/ # UI components
│     │       │   ├── App.js      # Main app component
│     │       │   └── App.css    # Styling
│     │       └── package.json    # Node dependencies
│     └── render.yaml             # Assignment 2: Render deployment config
└── README.md                       # This file
```

## Components

1. **Jacobi Solver** (`Assignment1/SVVR/model/jacobi_solver.py`)

   - Steady-state 2D temperature field solver using Jacobi iteration
   - Generates VTK files for ParaView visualization
   - Supports configurable hot square sizes and convergence parameters
2. **Data Visualization** (`Assignment1/SVVR/Assignment1/`)

   - Data analysis and visualization tools
   - Generates various plot styles

### Usage

```bash
cd Assignment1/SVVR/model
python jacobi_solver.py --nx 181 --ny 181 --tol 0.001
```

### Local Development

#### Backend Setup

```bash
cd Assignment1/SVVR/webapp/backend
pip install -r requirements.txt
python app.py
```

The backend will run on `http://localhost:5000`

#### Frontend Setup

```bash
cd Assignment1/SVVR/webapp/frontend
npm install
npm start
```

The frontend will run on `http://localhost:3000`

### Usage

1. Open the web app
2. Configure hot-square sizes (multiple fractions)
3. Click "Run Simulations"
4. Watch the simulations run in real-time!
5. Compare convergence rates on the live graph

## License

MIT
