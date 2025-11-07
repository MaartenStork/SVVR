#!/usr/bin/env python3
"""
Controlled sweep over hot-square size to analyze convergence behavior.

Research Question: Does the hot-square size change the difficulty of the solve?

For each hot-square fraction f ∈ (0,1], we:
1. Run the Jacobi solver once (deterministic, no repeats needed)
2. Record iterations to convergence N(f)
3. Record full δ-versus-iteration history
4. Generate plots to visualize convergence behavior
"""

import sys
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import jacobi_solver as js

def run_convergence_sweep(
    fractions=None,
    nx=181,
    ny=181,
    tol=1e-3,
    max_iters=20000,
    output_dir="convergence_analysis"
):
    """
    Run controlled sweep over hot-square sizes.
    
    Parameters:
    -----------
    fractions : list of float
        Hot-square sizes as fraction of domain (0, 1]
    nx, ny : int
        Grid resolution
    tol : float
        Convergence tolerance
    max_iters : int
        Safety cap on iterations
    output_dir : str
        Directory for results
    
    Returns:
    --------
    results : dict
        Dictionary with convergence data for each fraction
    """
    if fractions is None:
        # Default sweep: 10 fractions from 0.05 to 0.8
        fractions = np.linspace(0.05, 0.8, 10)
    
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"\n{'='*70}")
    print(f"CONVERGENCE ANALYSIS: Hot-Square Size Sweep")
    print(f"{'='*70}")
    print(f"Grid: {nx}×{ny}, Tolerance: {tol}, Max iterations: {max_iters}")
    print(f"Hot-square fractions: {len(fractions)} values from {min(fractions):.3f} to {max(fractions):.3f}")
    print(f"{'='*70}\n")
    
    # Physical parameters (fixed across all runs)
    W, H = 9.0, 9.0
    dx = W / (nx - 1)
    dy = H / (ny - 1)
    T_BOTTOM = 32.0
    T_TOP = 100.0
    T_HOT = 212.0
    
    results = {}
    
    for idx, f in enumerate(fractions):
        print(f"[{idx+1}/{len(fractions)}] Running f = {f:.4f}... ", end="", flush=True)
        
        # Allocate fields
        T_old = [[T_BOTTOM for _ in range(nx)] for _ in range(ny)]
        T_new = [[T_BOTTOM for _ in range(nx)] for _ in range(ny)]
        
        # Apply boundary conditions
        js.apply_dirichlet_boundaries(T_old, T_TOP, T_BOTTOM)
        
        # Apply hot square
        i0, i1, j0, j1 = js.build_indices_hot_square(nx, ny, f)
        js.apply_hot_square(T_old, i0, i1, j0, j1, T_HOT)
        
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
        
        # Jacobi iteration
        step = 0
        delta = float("inf")
        iterations = []
        deltas = []
        
        while delta > tol and step < max_iters:
            delta = js.jacobi_step(T_old, T_new, fixed)
            T_old, T_new = T_new, T_old
            step += 1
            
            iterations.append(step)
            deltas.append(delta)
        
        # Store results
        results[f] = {
            'fraction': f,
            'iterations': iterations,
            'deltas': deltas,
            'N': step,  # Total iterations to convergence
            'converged': delta <= tol,
            'final_delta': delta,
            'hot_square_indices': (i0, i1, j0, j1)
        }
        
        status = "✓ Converged" if delta <= tol else "✗ Max iters"
        print(f"{status} in {step} iterations (δ = {delta:.2e})")
    
    print(f"\n{'='*70}")
    print("Sweep complete!")
    print(f"{'='*70}\n")
    
    return results


def plot_convergence_analysis(results, output_dir="convergence_analysis"):
    """
    Generate publication-quality plots for convergence analysis.
    
    Creates:
    1. N(f) plot: Iterations to convergence vs hot-square size
    2. δ-versus-iteration curves for all fractions
    """
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    
    fractions = sorted(results.keys())
    N_values = [results[f]['N'] for f in fractions]
    
    # ========================================================================
    # PLOT 1: N(f) - Iterations to Convergence vs Hot-Square Size
    # ========================================================================
    fig, ax = plt.subplots(figsize=(10, 6))
    
    ax.plot(fractions, N_values, 'o', markersize=10, 
            color='#2E86AB', markerfacecolor='#2E86AB', markeredgewidth=2, 
            markeredgecolor='#2E86AB')
    
    ax.set_xlabel('Hot-Square Fraction $f$', fontsize=14, fontweight='bold')
    ax.set_ylabel('Iterations to Convergence $N(f)$', fontsize=14, fontweight='bold')
    ax.set_title('Convergence Speed vs Hot-Square Size', fontsize=16, fontweight='bold', pad=20)
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.set_xlim(min(fractions) - 0.05, max(fractions) + 0.05)
    
    plt.tight_layout()
    plot1_path = out_dir / 'N_vs_fraction.png'
    plt.savefig(plot1_path, dpi=300, bbox_inches='tight')
    print(f"✓ Saved: {plot1_path}")
    plt.close()
    
    # ========================================================================
    # PLOT 2: δ-versus-iteration curves (log scale)
    # ========================================================================
    fig, ax = plt.subplots(figsize=(12, 7))
    
    # Use a colormap to distinguish different fractions
    colors = plt.cm.viridis(np.linspace(0, 1, len(fractions)))
    
    for idx, f in enumerate(fractions):
        iters = results[f]['iterations']
        deltas = results[f]['deltas']
        
        ax.semilogy(iters, deltas, linewidth=2, color=colors[idx], 
                    label=f'$f={f:.2f}$')  # Removed N={N} for cleaner legend
    
    ax.set_xlabel('Iteration', fontsize=14, fontweight='bold')
    ax.set_ylabel('Max Change $\\delta$', fontsize=14, fontweight='bold')
    ax.set_title('Convergence Behavior: $\\delta$-versus-Iteration', 
                 fontsize=16, fontweight='bold', pad=20)
    ax.grid(True, alpha=0.3, linestyle='--', which='both')
    ax.legend(loc='upper right', fontsize=13, ncol=2, framealpha=0.9)  # Increased from 11 to 13
    
    # Set y-axis limits to show down to 0.0001
    ax.set_ylim(1e-4, None)  # Lower limit at 0.0001
    
    # Add horizontal line for tolerance (subtle)
    tol = 1e-4
    ax.axhline(y=tol, color='red', linestyle='--', linewidth=1, 
               label=f'Tolerance $\\varepsilon={tol}$', alpha=0.5)
    
    plt.tight_layout()
    plot2_path = out_dir / 'delta_vs_iteration.png'
    plt.savefig(plot2_path, dpi=300, bbox_inches='tight')
    print(f"✓ Saved: {plot2_path}")
    plt.close()
    
    # ========================================================================
    # PLOT 3: Combined view (side by side)
    # ========================================================================
    fig = plt.figure(figsize=(16, 6))
    
    # Left: N(f)
    ax1 = plt.subplot(1, 2, 1)
    ax1.plot(fractions, N_values, 'o-', linewidth=2, markersize=8, 
             color='#2E86AB', markerfacecolor='#A23B72', markeredgewidth=2, 
             markeredgecolor='#2E86AB')
    ax1.set_xlabel('Hot-Square Fraction $f$', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Iterations $N(f)$', fontsize=12, fontweight='bold')
    ax1.set_title('(a) Convergence Speed', fontsize=14, fontweight='bold')
    ax1.grid(True, alpha=0.3, linestyle='--')
    
    # Right: δ curves
    ax2 = plt.subplot(1, 2, 2)
    tol = 1e-4  # Define tolerance
    for idx, f in enumerate(fractions):
        iters = results[f]['iterations']
        deltas = results[f]['deltas']
        ax2.semilogy(iters, deltas, linewidth=2, color=colors[idx], 
                     label=f'$f={f:.2f}$')
    ax2.axhline(y=tol, color='red', linestyle='--', linewidth=1, alpha=0.5)
    ax2.set_xlabel('Iteration', fontsize=12, fontweight='bold')
    ax2.set_ylabel('Max Change $\\delta$', fontsize=12, fontweight='bold')
    ax2.set_title('(b) Convergence History', fontsize=14, fontweight='bold')
    ax2.grid(True, alpha=0.3, linestyle='--', which='both')
    ax2.set_ylim(1e-4, None)  # Lower limit at 0.0001
    ax2.legend(loc='upper right', fontsize=12, ncol=2, framealpha=0.9)  # Increased from 10 to 12
    
    plt.suptitle('Convergence Analysis: Hot-Square Size Impact', 
                 fontsize=16, fontweight='bold', y=1.02)
    plt.tight_layout()
    plot3_path = out_dir / 'combined_analysis.png'
    plt.savefig(plot3_path, dpi=300, bbox_inches='tight')
    print(f"✓ Saved: {plot3_path}")
    plt.close()
    
    print(f"\n{'='*70}")
    print("All plots generated successfully!")
    print(f"{'='*70}\n")


def print_summary(results):
    """Print summary statistics of the convergence sweep."""
    fractions = sorted(results.keys())
    N_values = [results[f]['N'] for f in fractions]
    
    print(f"\n{'='*70}")
    print("SUMMARY STATISTICS")
    print(f"{'='*70}")
    print(f"{'Fraction f':<15} {'Iterations N':<15} {'Final δ':<15} {'Status'}")
    print(f"{'-'*70}")
    
    for f in fractions:
        r = results[f]
        status = "✓" if r['converged'] else "✗"
        print(f"{f:<15.4f} {r['N']:<15d} {r['final_delta']:<15.2e} {status}")
    
    print(f"{'-'*70}")
    print(f"Min iterations: {min(N_values)} (at f={fractions[np.argmin(N_values)]:.4f})")
    print(f"Max iterations: {max(N_values)} (at f={fractions[np.argmax(N_values)]:.4f})")
    print(f"Mean iterations: {np.mean(N_values):.1f}")
    print(f"Std iterations: {np.std(N_values):.1f}")
    print(f"{'='*70}\n")


if __name__ == "__main__":
    # Configuration - sweep every 0.05 from 0.05 to 0.95
    fractions = np.arange(0.05, 1.0, 0.05)  # 19 fractions from 0.05 to 0.95
    
    # Run the sweep
    results = run_convergence_sweep(
        fractions=fractions,
        nx=181,
        ny=181,
        tol=1e-4,  # Tolerance set to 0.0001
        max_iters=30000,  # Increased safety cap for smaller fractions
        output_dir="convergence_analysis"
    )
    
    # Generate plots
    plot_convergence_analysis(results, output_dir="convergence_analysis")
    
    # Print summary
    print_summary(results)
    
    print("\n✓ Analysis complete! Check the 'convergence_analysis' directory for results.")

