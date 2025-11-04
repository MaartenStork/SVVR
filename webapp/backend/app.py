#!/usr/bin/env python3
"""
Flask backend for Jacobi Heat Simulation Web App
Real-time streaming of simulation progress via WebSocket
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import sys
import os
import base64
import io
import numpy as np
from PIL import Image
import threading

# Add parent directory to path to import simulation code
model_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../model'))
print(f"Adding model path: {model_path}")
print(f"Model path exists: {os.path.exists(model_path)}")
if os.path.exists(model_path):
    print(f"Files in model: {os.listdir(model_path)}")
sys.path.insert(0, model_path)

try:
    import code as jacobi_sim
    print(f"Successfully imported code module")
    print(f"Available functions: {[attr for attr in dir(jacobi_sim) if not attr.startswith('_')]}")
except Exception as e:
    print(f"Error importing code module: {e}")
    raise

# Configure Flask to serve React build folder
build_folder = os.path.join(os.path.dirname(__file__), '../frontend/build')
app = Flask(__name__, static_folder=build_folder, static_url_path='')
CORS(app, resources={r"/*": {"origins": "*"}})
socketio = SocketIO(
    app, 
    cors_allowed_origins="*", 
    async_mode='eventlet',
    logger=True,
    engineio_logger=True,
    ping_timeout=60,
    ping_interval=25
)

# Global state for simulation
simulation_state = {
    'running': False,
    'results': []
}

def frame_to_base64(frame_array):
    """Convert numpy array frame to base64 string for transmission"""
    img = Image.fromarray(frame_array)
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    return f"data:image/png;base64,{img_str}"

def run_simulation_with_streaming(hot_fraction, sim_index, total_sims):
    """Run a single simulation and stream progress"""
    # Temporarily modify sys.argv
    original_argv = sys.argv.copy()
    
    output_dir = f"webapp_temp/sim_{hot_fraction:.2f}"
    sys.argv = [
        'code.py',
        '--output-every', '100',
        '--out', output_dir,
        '--hot-fraction', str(hot_fraction),
        '--no-vtk',  # We'll add this flag to skip VTK writing for speed
    ]
    
    # Run simulation with custom callback for streaming
    try:
        result = run_simulation_streaming(hot_fraction, sim_index, total_sims)
        sys.argv = original_argv
        return result
    except Exception as e:
        sys.argv = original_argv
        raise e

def run_simulation_streaming(hot_fraction, sim_index, total_sims):
    """Modified simulation runner that streams data via WebSocket"""
    from pathlib import Path
    
    # Simulation parameters (hardcoded for webapp)
    nx, ny = 181, 181
    tol = 1e-3
    max_iters = 20000
    output_every = 100
    
    W, H = 9.0, 9.0
    dx = W / (nx - 1)
    dy = H / (ny - 1)
    
    T_BOTTOM = 32.0
    T_TOP = 100.0
    T_HOT = 212.0
    
    # Allocate fields
    T_old = [[T_BOTTOM for _ in range(nx)] for _ in range(ny)]
    T_new = [[T_BOTTOM for _ in range(nx)] for _ in range(ny)]
    
    # Apply boundaries and hot square
    jacobi_sim.apply_dirichlet_boundaries(T_old, T_TOP, T_BOTTOM)
    i0, i1, j0, j1 = jacobi_sim.build_indices_hot_square(nx, ny, hot_fraction)
    jacobi_sim.apply_hot_square(T_old, i0, i1, j0, j1, T_HOT)
    
    # Build fixed mask
    fixed = [[False for _ in range(nx)] for _ in range(ny)]
    for i in range(nx):
        fixed[0][i] = True
        fixed[ny - 1][i] = True
    for j in range(ny):
        fixed[j][0] = True
        fixed[j][nx - 1] = True
    for j in range(j0, j1 + 1):
        for i in range(i0, i1 + 1):
            fixed[j][i] = True
    
    # Iteration loop with streaming
    step = 0
    delta = float("inf")
    convergence_history = {"iterations": [], "deltas": []}
    
    # Send initial frame
    frame = jacobi_sim.create_temperature_frame(T_old, step, delta, T_BOTTOM, T_HOT, dpi=60)
    frame_base64 = frame_to_base64(frame)
    
    socketio.emit('simulation_update', {
        'sim_index': sim_index,
        'iteration': step,
        'delta': delta,
        'frame': frame_base64,
        'hot_fraction': hot_fraction,
        'converged': False
    })
    
    while delta > tol and step < max_iters:
        delta = jacobi_sim.jacobi_step(T_old, T_new, fixed)
        T_old, T_new = T_new, T_old
        step += 1
        
        convergence_history["iterations"].append(step)
        convergence_history["deltas"].append(delta)
        
        # Stream progress at intervals
        if step % output_every == 0 or delta <= tol:
            frame = jacobi_sim.create_temperature_frame(T_old, step, delta, T_BOTTOM, T_HOT, dpi=60)
            frame_base64 = frame_to_base64(frame)
            
            socketio.emit('simulation_update', {
                'sim_index': sim_index,
                'iteration': step,
                'delta': delta,
                'frame': frame_base64,
                'hot_fraction': hot_fraction,
                'converged': delta <= tol
            })
            
            # Small sleep to prevent overwhelming the client
            socketio.sleep(0.01)
    
    return {
        'convergence_history': convergence_history,
        'final_iter': step,
        'final_delta': delta,
        'hot_fraction': hot_fraction
    }

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy'}), 200

@app.route('/')
def serve_react_app():
    """Serve React app"""
    return app.send_static_file('index.html')

@app.route('/<path:path>')
def serve_react_routes(path):
    """Serve React app for all routes (for React Router)"""
    # Check if path is a file that exists
    file_path = os.path.join(app.static_folder, path)
    if os.path.exists(file_path) and os.path.isfile(file_path):
        return app.send_static_file(path)
    # Otherwise serve index.html for React Router
    return app.send_static_file('index.html')

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    print('Client connected')
    emit('connected', {'message': 'Connected to simulation server'})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    print('Client disconnected')

@socketio.on('start_simulation')
def handle_start_simulation(data):
    """Start simulation with given parameters"""
    if simulation_state['running']:
        emit('error', {'message': 'Simulation already running'})
        return
    
    hot_fractions = data.get('hot_fractions', [0.1, 0.2, 0.33])
    
    simulation_state['running'] = True
    simulation_state['results'] = []
    
    emit('simulation_started', {
        'message': 'Starting simulations',
        'num_simulations': len(hot_fractions)
    })
    
    # Run simulations in separate thread
    def run_all_simulations():
        try:
            results = []
            for idx, fraction in enumerate(hot_fractions):
                socketio.emit('simulation_status', {
                    'message': f'Running simulation {idx + 1}/{len(hot_fractions)}',
                    'current_sim': idx,
                    'total_sims': len(hot_fractions)
                })
                
                result = run_simulation_streaming(fraction, idx, len(hot_fractions))
                results.append(result)
            
            simulation_state['results'] = results
            simulation_state['running'] = False
            
            socketio.emit('all_simulations_complete', {
                'message': 'All simulations completed',
                'results': [{
                    'hot_fraction': r['hot_fraction'],
                    'final_iter': r['final_iter'],
                    'final_delta': r['final_delta']
                } for r in results]
            })
        except Exception as e:
            simulation_state['running'] = False
            socketio.emit('error', {'message': str(e)})
    
    thread = threading.Thread(target=run_all_simulations)
    thread.daemon = True
    thread.start()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    socketio.run(app, host='0.0.0.0', port=port, debug=True, allow_unsafe_werkzeug=True)

