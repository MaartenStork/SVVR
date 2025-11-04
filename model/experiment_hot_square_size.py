#!/usr/bin/env python3
"""
Experiment: Does hot-square size change the difficulty of the solve?

This script runs the Jacobi solver with different hot-square sizes,
compares convergence rates, and generates visualization outputs.
"""

import sys
import os
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from PIL import Image

# Import the main simulation from code.py
import code as jacobi_sim

def run_experiment(hot_fractions, output_dir="experiment_results"):
    """
    Run simulations for different hot-square sizes and collect results.
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    results = []
    
    for fraction in hot_fractions:
        print(f"\n{'='*60}")
        print(f"Running simulation with hot-square size = {fraction:.2f} of domain")
        print(f"{'='*60}\n")
        
        # Temporarily modify sys.argv to pass arguments to code.py
        original_argv = sys.argv.copy()
        sys.argv = [
            'code.py',
            '--gif',
            '--output-every', '200',
            '--out', str(output_path / f'sim_fraction_{fraction:.2f}'),
            '--hot-fraction', str(fraction)
        ]
        
        # Run the simulation
        result = jacobi_sim.main(hot_fraction=fraction, return_data=True)
        
        # Restore original argv
        sys.argv = original_argv
        
        results.append(result)
        print(f"\nCompleted: Hot fraction {fraction:.2f} - {result['final_iter']} iterations")
    
    return results

def create_convergence_plot(results, output_path):
    """
    Create a convergence plot comparing different hot-square sizes.
    """
    plt.figure(figsize=(12, 8))
    
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
    
    for i, result in enumerate(results):
        iterations = result['convergence_history']['iterations']
        deltas = result['convergence_history']['deltas']
        fraction = result['hot_fraction']
        
        plt.semilogy(iterations, deltas, label=f'Hot fraction = {fraction:.2f}', 
                     linewidth=2, color=colors[i % len(colors)])
        
        # Mark final convergence point
        plt.scatter(result['final_iter'], result['final_delta'], 
                   s=100, marker='o', color=colors[i % len(colors)], 
                   zorder=5, edgecolors='black', linewidth=1.5)
    
    plt.xlabel('Iteration Number', fontsize=14, fontweight='bold')
    plt.ylabel('Maximum Temperature Change (Delta)', fontsize=14, fontweight='bold')
    plt.title('Convergence Rate vs Hot-Square Size\nJacobi Solver for 2D Laplace Equation', 
              fontsize=16, fontweight='bold', pad=20)
    plt.grid(True, which='both', alpha=0.3, linestyle='--')
    plt.legend(fontsize=12, loc='best', framealpha=0.9)
    plt.tight_layout()
    
    plot_path = output_path / 'convergence_comparison.png'
    plt.savefig(str(plot_path), dpi=150, bbox_inches='tight')
    print(f"\nConvergence plot saved to: {plot_path}")
    plt.close()

def create_iterations_bar_chart(results, output_path):
    """
    Create a bar chart showing iterations to convergence.
    """
    plt.figure(figsize=(10, 6))
    
    fractions = [r['hot_fraction'] for r in results]
    iterations = [r['final_iter'] for r in results]
    
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
    bars = plt.bar(range(len(fractions)), iterations, 
                   color=colors[:len(fractions)], edgecolor='black', linewidth=1.5)
    
    # Add value labels on bars
    for i, (bar, iters) in enumerate(zip(bars, iterations)):
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(iters)}',
                ha='center', va='bottom', fontsize=12, fontweight='bold')
    
    plt.xlabel('Hot-Square Fraction', fontsize=14, fontweight='bold')
    plt.ylabel('Iterations to Convergence', fontsize=14, fontweight='bold')
    plt.title('Solver Difficulty vs Hot-Square Size', fontsize=16, fontweight='bold', pad=20)
    plt.xticks(range(len(fractions)), [f'{f:.2f}' for f in fractions], fontsize=12)
    plt.grid(True, axis='y', alpha=0.3, linestyle='--')
    plt.tight_layout()
    
    chart_path = output_path / 'iterations_comparison.png'
    plt.savefig(str(chart_path), dpi=150, bbox_inches='tight')
    print(f"Iterations bar chart saved to: {chart_path}")
    plt.close()

def create_side_by_side_gif(results, output_path, fps=10):
    """
    Create a side-by-side GIF comparing simulations.
    """
    print("\nCreating side-by-side comparison GIF...")
    
    # Get frames from all results
    all_frames = [r['frames'] for r in results]
    
    if any(frames is None for frames in all_frames):
        print("Warning: Some simulations don't have frames. Skipping GIF creation.")
        return
    
    # Find the minimum number of frames across all simulations
    min_frames = min(len(frames) for frames in all_frames)
    
    # Create side-by-side frames
    combined_frames = []
    for frame_idx in range(min_frames):
        # Get corresponding frames from each simulation
        current_frames = [frames[frame_idx] for frames in all_frames]
        
        # Combine horizontally
        combined = np.hstack(current_frames)
        combined_frames.append(combined)
    
    print(f"Creating GIF with {len(combined_frames)} frames...")
    
    # Convert to PIL images and save as GIF
    pil_frames = [Image.fromarray(frame) for frame in combined_frames]
    duration_ms = int(1000 / fps)
    
    gif_path = output_path / 'side_by_side_comparison.gif'
    pil_frames[0].save(
        str(gif_path),
        save_all=True,
        append_images=pil_frames[1:],
        duration=duration_ms,
        loop=0
    )
    
    print(f"Side-by-side GIF saved to: {gif_path}")
    print(f"GIF dimensions: {combined_frames[0].shape}")

def main():
    print("="*60)
    print("EXPERIMENT: Hot-Square Size vs Solver Difficulty")
    print("="*60)
    
    # Define hot-square sizes to test (as fraction of domain)
    hot_fractions = [0.1, 0.2, 0.33]  # Small, medium, large (1/3)
    
    output_dir = Path("experiment_results")
    
    # Run simulations
    results = run_experiment(hot_fractions, output_dir)
    
    # Create analysis plots
    print("\n" + "="*60)
    print("GENERATING ANALYSIS PLOTS")
    print("="*60)
    
    create_convergence_plot(results, output_dir)
    create_iterations_bar_chart(results, output_dir)
    create_side_by_side_gif(results, output_dir, fps=10)
    
    # Print summary
    print("\n" + "="*60)
    print("EXPERIMENT SUMMARY")
    print("="*60)
    for result in results:
        print(f"\nHot-Square Fraction: {result['hot_fraction']:.2f}")
        print(f"  Iterations to convergence: {result['final_iter']}")
        print(f"  Final delta: {result['final_delta']:.6e}")
    
    print(f"\n{'='*60}")
    print(f"All results saved to: {output_dir.absolute()}")
    print(f"{'='*60}\n")

if __name__ == "__main__":
    main()

