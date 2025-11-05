#!/usr/bin/env python3
"""
Flask backend for Jacobi Heat Simulation Web App
Real-time streaming of simulation progress via WebSocket
"""

# Monkey patch for eventlet to enable true threading
import eventlet
eventlet.monkey_patch()

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
    import jacobi_solver as jacobi_sim
    print(f"Successfully imported jacobi_solver module")
    print(f"Available functions: {[attr for attr in dir(jacobi_sim) if not attr.startswith('_')][:10]}")  # Show first 10
except Exception as e:
    print(f"Error importing jacobi_solver module: {e}")
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
    ping_timeout=120,  # 2 minutes
    ping_interval=30   # Ping every 30 seconds
)

# Global state for simulation
simulation_state = {
    'running': False,
    'results': [],
    'progress': []  # Track progress for each simulation (dynamic size)
}

def frame_to_base64(frame_array):
    """Convert numpy array frame to base64 string for transmission"""
    img = Image.fromarray(frame_array)
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    return f"data:image/png;base64,{img_str}"

def generate_gif(frames, fps=10):
    """Generate GIF from list of frames"""
    pil_frames = [Image.fromarray(frame) for frame in frames]
    duration_ms = int(1000 / fps)
    
    # Save to bytes buffer
    buffered = io.BytesIO()
    pil_frames[0].save(
        buffered,
        format='GIF',
        save_all=True,
        append_images=pil_frames[1:],
        duration=duration_ms,
        loop=0
    )
    return buffered.getvalue()

def run_simulation_with_streaming(hot_fraction, sim_index, total_sims):
    """Run a single simulation and stream progress - NO FILE WRITING!"""
    # Run simulation directly in memory - NO VTK FILES
    try:
        result = run_simulation_streaming(hot_fraction, sim_index, total_sims)
        return result
    except Exception as e:
        print(f"Error in simulation {sim_index}: {e}")
        raise e

def run_simulation_streaming(hot_fraction, sim_index, total_sims, grid_size=51, tolerance=0.001, max_iters=15000, frame_every=100):
    """Modified simulation runner that streams data via WebSocket"""
    from pathlib import Path
    
    # Simulation parameters from user input
    nx = ny = grid_size
    tol = tolerance
    max_iters = max_iters
    frame_every = frame_every
    
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
    
    # Iteration loop - NO STREAMING, just collect frames
    step = 0
    delta = float("inf")
    initial_delta = None
    convergence_history = {"iterations": [], "deltas": []}
    frames = []
    
    # Initial frame
    frames.append(jacobi_sim.create_temperature_frame(T_old, 0, delta, T_BOTTOM, T_HOT, dpi=100))
    
    print(f"Sim {sim_index}: Starting with {nx}x{ny} grid, hot_fraction={hot_fraction}")
    
    while delta > tol and step < max_iters:
        delta = jacobi_sim.jacobi_step(T_old, T_new, fixed)
        T_old, T_new = T_new, T_old
        step += 1
        
        # Capture initial delta after first iteration
        if step == 1:
            initial_delta = delta
        
        convergence_history["iterations"].append(step)
        convergence_history["deltas"].append(delta)
        
        # CRITICAL: Yield to other greenlets every 10 iterations for true parallelism
        if step % 10 == 0:
            eventlet.sleep(0)  # Cooperative yield
        
        # Capture frames and send progress
        if step % frame_every == 0 or delta <= tol:
            frames.append(jacobi_sim.create_temperature_frame(T_old, step, delta, T_BOTTOM, T_HOT, dpi=100))
            
            # Calculate progress based on convergence (logarithmic scale for exponential decay)
            if initial_delta and initial_delta > tol and delta > tol:
                import math
                # Use log scale: progress increases as delta decreases exponentially
                log_initial = math.log10(initial_delta)
                log_current = math.log10(delta)
                log_target = math.log10(tol)
                progress = int(((log_initial - log_current) / (log_initial - log_target)) * 100)
                progress = max(0, min(99, progress))  # Cap at 99% until converged
            elif delta <= tol:
                progress = 100  # Converged!
            else:
                progress = int((step / max_iters) * 100)
            
            # Update global progress state (will be broadcast by monitoring thread)
            simulation_state['progress'][sim_index] = progress
            
            if step % 500 == 0:  # Progress log every 500 iterations
                print(f"Sim {sim_index}: Iteration {step}, Delta {delta:.2e}, Progress {progress}%")
    
    # Return frames (GIF will be generated after synchronization)
    print(f"Sim {sim_index}: Complete! {step} iterations, {len(frames)} frames collected")
    
    return {
        'convergence_history': convergence_history,
        'final_iter': step,
        'final_delta': delta,
        'hot_fraction': hot_fraction,
        'frames': frames  # Return frames, not GIF yet
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
    
    # Extract parameters from client
    hot_fractions = data.get('hot_fractions', [0.1, 0.2, 0.33])
    grid_size = data.get('grid_size', 51)
    tolerance = data.get('tolerance', 0.001)
    max_iters = data.get('max_iters', 15000)
    frame_every = data.get('frame_every', 100)
    
    print(f"Starting simulations with grid={grid_size}x{grid_size}, tol={tolerance}, max_iters={max_iters}")
    
    simulation_state['running'] = True
    simulation_state['results'] = []
    simulation_state['progress'] = [0] * len(hot_fractions)  # Dynamic size based on number of simulations
    
    emit('simulation_started', {
        'message': 'Starting simulations',
        'num_simulations': len(hot_fractions)
    })
    
    # Progress monitoring - broadcasts progress frequently for smooth updates
    def monitor_progress():
        while simulation_state['running']:
            socketio.emit('simulation_progress', {
                'progress': simulation_state['progress']
            }, namespace='/')
            eventlet.sleep(0.3)  # Update 3x per second for smoother bars
    
    # Start monitor in eventlet greenlet
    eventlet.spawn(monitor_progress)
    
    # Run ALL simulations in PARALLEL!
    results = [None] * len(hot_fractions)
    lock = threading.Lock()
    
    def run_single_simulation(fraction, idx):
        try:
            print(f"Starting simulation {idx + 1}/{len(hot_fractions)}: fraction={fraction}")
            result = run_simulation_streaming(fraction, idx, len(hot_fractions), 
                                             grid_size, tolerance, max_iters, frame_every)
            
            with lock:
                results[idx] = result
                # Check if all simulations are done
                if all(r is not None for r in results):
                    # Synchronize GIF lengths - pad shorter ones with last frame
                    max_frames = max(len(r['frames']) for r in results)
                    print(f"Synchronizing GIFs to {max_frames} frames each")
                    
                    for r in results:
                        frames_needed = max_frames - len(r['frames'])
                        if frames_needed > 0:
                            print(f"  Sim {results.index(r)}: Adding {frames_needed} frames (was {len(r['frames'])})")
                            # Add frames BEFORE and AFTER for smooth looping
                            padding_start = frames_needed // 2
                            padding_end = frames_needed - padding_start
                            # Pad start with first frame
                            r['frames'] = [r['frames'][0]] * padding_start + r['frames']
                            # Pad end with last frame
                            r['frames'] = r['frames'] + [r['frames'][-1]] * padding_end
                    
                    # Generate synchronized GIFs with EXACT same settings
                    duration_ms = 200  # 200ms per frame = 5 FPS
                    for i, r in enumerate(results):
                        print(f"  Generating GIF for Sim {i}: {len(r['frames'])} frames @ {duration_ms}ms/frame")
                        gif_bytes = generate_gif(r['frames'], fps=5)
                        r['gif_data'] = f"data:image/gif;base64,{base64.b64encode(gif_bytes).decode()}"
                        del r['frames']  # Free memory
                    
                    print(f"All GIFs generated with {max_frames} frames each")
                    
                    simulation_state['results'] = results
                    simulation_state['running'] = False
                    
                    # Send ALL results at once!
                    socketio.emit('all_simulations_complete', {
                        'message': 'All simulations completed!',
                        'results': [{
                            'hot_fraction': r['hot_fraction'],
                            'final_iter': r['final_iter'],
                            'final_delta': r['final_delta'],
                            'gif_data': r['gif_data'],
                            'convergence_history': r['convergence_history']
                        } for r in results]
                    }, namespace='/')
                    print("All simulations complete! Synchronized GIFs sent to client.")
        except Exception as e:
            simulation_state['running'] = False
            socketio.emit('error', {'message': str(e)}, namespace='/')
            print(f"Error in simulation {idx}: {e}")
    
    # Start ALL simulations in PARALLEL using eventlet
    greenlets = []
    for idx, fraction in enumerate(hot_fractions):
        greenlet = eventlet.spawn(run_single_simulation, fraction, idx)
        greenlets.append(greenlet)
    
    print(f"Started {len(greenlets)} simulations in parallel with eventlet")

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    socketio.run(app, host='0.0.0.0', port=port, debug=True, allow_unsafe_werkzeug=True)

