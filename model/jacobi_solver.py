from __future__ import annotations
import argparse
import math
import os
from pathlib import Path
from typing import Tuple, List
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.colors import LinearSegmentedColormap
import numpy as np

# -----------------------------
# Utilities
# -----------------------------

def linspace(n: int, start: float, end: float) -> List[float]:
    if n == 1:
        return [start]
    step = (end - start) / (n - 1)
    return [start + i * step for i in range(n)]

def write_vti_image_data(
    filename: str,
    grid: "list[list[float]]",
    dx: float,
    dy: float,
    origin: Tuple[float, float, float] = (0.0, 0.0, 0.0),
    name: str = "Temperature",
):
    """
    Write 2D scalar field as VTK-XML ImageData (.vti), ASCII.
    """
    ny = len(grid)
    nx = len(grid[0])
    nz = 1
    # VTK-XML expects x fastest, then y, then z (same order you already write)
    with open(filename, "w") as f:
        f.write('<?xml version="1.0"?>\n')
        f.write('<VTKFile type="ImageData" version="0.1" byte_order="LittleEndian">\n')
        f.write(f'  <ImageData WholeExtent="0 {nx-1} 0 {ny-1} 0 {nz-1}" '
                f'Origin="{origin[0]} {origin[1]} {origin[2]}" '
                f'Spacing="{dx} {dy} 1">\n')
        f.write(f'    <Piece Extent="0 {nx-1} 0 {ny-1} 0 {nz-1}">\n')
        f.write(f'      <PointData Scalars="{name}">\n')
        f.write(f'        <DataArray type="Float32" Name="{name}" format="ascii">\n')
        for j in range(ny):
            row = grid[j]
            f.write(" ".join(f"{float(row[i]):.6f}" for i in range(nx)) + "\n")
        f.write('        </DataArray>\n')
        f.write('      </PointData>\n')
        f.write('      <CellData/>\n')
        f.write('    </Piece>\n')
        f.write('  </ImageData>\n')
        f.write('</VTKFile>\n')

def write_pvd_collection(pvd_path: str, vtk_filenames: List[str], times: List[float]):
    """
    Write a ParaView Data (PVD) collection file so the sequence loads as a time series.
    """
    assert len(vtk_filenames) == len(times)
    with open(pvd_path, "w") as f:
        f.write('<?xml version="1.0"?>\n')
        f.write('<VTKFile type="Collection" version="0.1" byte_order="LittleEndian">\n')
        f.write("  <Collection>\n")
        for fn, t in zip(vtk_filenames, times):
            f.write(f'    <DataSet timestep="{t:.6f}" file="{Path(fn).name}"/>\n')
        f.write("  </Collection>\n")
        f.write("</VTKFile>\n")

def write_csv_snapshot(path: str, grid: "list[list[float]]"):
    ny = len(grid)
    nx = len(grid[0])
    with open(path, "w") as f:
        f.write("i,j,T\n")
        for j in range(ny):
            for i in range(nx):
                f.write(f"{i},{j},{grid[j][i]:.6f}\n")

def create_temperature_frame(grid: "list[list[float]]", step: int, delta: float, 
                             vmin: float, vmax: float, dpi: int = 100) -> np.ndarray:
    """
    Create a matplotlib figure of the temperature field and return it as an array.
    """
    import matplotlib
    matplotlib.use('Agg')  # Use non-interactive backend
    
    ny = len(grid)
    nx = len(grid[0])
    
    # Convert grid to numpy array (flip y-axis for correct orientation)
    T_array = np.array(grid)
    
    fig, ax = plt.subplots(figsize=(8, 7), dpi=dpi)
    
    # Use rainbow colormap to match ParaView (try: 'jet', 'turbo', 'rainbow', or 'gist_rainbow')
    im = ax.imshow(T_array, origin='lower', cmap='turbo', vmin=vmin, vmax=vmax, 
                   aspect='equal', interpolation='bilinear')
    
    # Add colorbar
    cbar = plt.colorbar(im, ax=ax, label='Temperature (°F)')
    
    # Add title with iteration info
    ax.set_title(f'Temperature Field Evolution\nIteration: {step}, Delta: {delta:.2e}', 
                 fontsize=12, fontweight='bold')
    ax.set_xlabel('X Position')
    ax.set_ylabel('Y Position')
    
    # Convert figure to numpy array (using buffer_rgba for compatibility)
    fig.canvas.draw()
    buf = np.asarray(fig.canvas.buffer_rgba())
    # Convert RGBA to RGB
    frame = buf[:, :, :3].copy()
    
    plt.close(fig)
    return frame

# -----------------------------
# Physics / Discretization
# -----------------------------

def build_indices_hot_square(nx: int, ny: int, hot_fraction: float = 1/3.0) -> Tuple[int, int, int, int]:
    """
    Hot square is hot_fraction of plate width/height, centered.
    We keep it integer-index aligned and inclusive bounds.
    """
    hot_w = int(round(nx * hot_fraction))
    hot_h = int(round(ny * hot_fraction))

    i0 = (nx - hot_w) // 2
    i1 = i0 + hot_w - 1
    j0 = (ny - hot_h) // 2
    j1 = j0 + hot_h - 1
    return i0, i1, j0, j1

def apply_dirichlet_boundaries(T: "list[list[float]]", top: float, bottom: float):
    ny = len(T)
    nx = len(T[0])

    # Top and Bottom
    for i in range(nx):
        T[ny - 1][i] = top
        T[0][i] = bottom

    # Left/Right linear ramps from bottom (32) to top (100)
    for j in range(ny):
        y = j / (ny - 1) if ny > 1 else 0.0
        ramp = bottom + (top - bottom) * y
        T[j][0] = ramp
        T[j][nx - 1] = ramp

def apply_hot_square(T: "list[list[float]]", i0: int, i1: int, j0: int, j1: int, temp: float):
    for j in range(j0, j1 + 1):
        for i in range(i0, i1 + 1):
            T[j][i] = temp

def jacobi_step(T_old: "list[list[float]]", T_new: "list[list[float]]",
                fixed_mask: "list[list[bool]]") -> float:
    """
    Perform one Jacobi sweep; return delta = max |T_new - T_old|
    fixed_mask=True means Dirichlet node (boundary or hot square): copy through.
    """
    ny = len(T_old)
    nx = len(T_old[0])
    delta = 0.0

    for j in range(ny):
        jm1 = max(j - 1, 0)
        jp1 = min(j + 1, ny - 1)
        for i in range(nx):
            if fixed_mask[j][i]:
                T_new[j][i] = T_old[j][i]
            else:
                im1 = max(i - 1, 0)
                ip1 = min(i + 1, nx - 1)
                T_new[j][i] = 0.25 * (T_old[j][im1] + T_old[j][ip1] +
                                      T_old[jm1][i] + T_old[jp1][i])
            d = abs(T_new[j][i] - T_old[j][i])
            if d > delta:
                delta = d
    return delta

# -----------------------------
# Main
# -----------------------------

def main(hot_fraction=None, return_data=False):
    ap = argparse.ArgumentParser(description="Laplace (Jacobi) with ParaView-ready outputs.")
    ap.add_argument("--nx", type=int, default=181, help="Grid points in x (columns).")
    ap.add_argument("--ny", type=int, default=181, help="Grid points in y (rows).")
    ap.add_argument("--tol", type=float, default=1e-3, help="Convergence tolerance on delta.")
    ap.add_argument("--max-iters", type=int, default=20000, help="Safety cap on iterations.")
    ap.add_argument("--output-every", type=int, default=20, help="Write VTK every N iterations.")
    ap.add_argument("--out", type=str, default="out_vtk", help="Output directory.")
    ap.add_argument("--also-csv", action="store_true", help="Write CSV snapshots too.")
    ap.add_argument("--gif", action="store_true", help="Generate animated GIF of temperature evolution.")
    ap.add_argument("--gif-fps", type=int, default=10, help="Frames per second for GIF.")
    ap.add_argument("--hot-fraction", type=float, default=1/3.0, help="Hot square size as fraction of domain (default: 1/3)")
    ap.add_argument("--no-vtk", action="store_true", help="Skip VTK file writing (for webapp use)")
    args = ap.parse_args()
    
    # Override with programmatic argument if provided
    if hot_fraction is not None:
        args.hot_fraction = hot_fraction

    # Physical sizes (meters)
    W = 9.0
    H = 9.0
    dx = W / (args.nx - 1)
    dy = H / (args.ny - 1)

    # Temperatures (degrees)
    T_BOTTOM = 32.0
    T_TOP = 100.0
    T_HOT = 212.0

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    # Allocate fields
    T_old = [[T_BOTTOM for _ in range(args.nx)] for _ in range(args.ny)]
    T_new = [[T_BOTTOM for _ in range(args.nx)] for _ in range(args.ny)]

    # Apply boundaries and hot square to initial field
    apply_dirichlet_boundaries(T_old, T_TOP, T_BOTTOM)

    i0, i1, j0, j1 = build_indices_hot_square(args.nx, args.ny, args.hot_fraction)
    apply_hot_square(T_old, i0, i1, j0, j1, T_HOT)

    # Build fixed mask (Dirichlet everywhere that must not change)
    fixed = [[False for _ in range(args.nx)] for _ in range(args.ny)]
    # Outer boundaries:
    for i in range(args.nx):
        fixed[0][i] = True
        fixed[args.ny - 1][i] = True
    for j in range(args.ny):
        fixed[j][0] = True
        fixed[j][args.nx - 1] = True
    # Hot square region:
    for j in range(j0, j1 + 1):
        for i in range(i0, i1 + 1):
            fixed[j][i] = True

    # Save step 0
    vtk_paths = []
    times = []
    frames = [] if args.gif else None
    step = 0
    
    if not args.no_vtk:
        vti0 = out_dir / f"step_{step:05d}.vti"
        write_vti_image_data(str(vti0), T_old, dx, dy, name="Temperature")
        vtk_paths.append(str(vti0))
        times.append(float(step))
        if args.also_csv:
            write_csv_snapshot(str(out_dir / f"step_{step:05d}.csv"), T_old)
    if args.gif:
        frames.append(create_temperature_frame(T_old, step, 0.0, T_BOTTOM, T_HOT))

    # Jacobi iteration loop (slide: do { ... } while (delta > tolerance))
    delta = float("inf")
    convergence_history = {"iterations": [], "deltas": []}
    
    while delta > args.tol and step < args.max_iters:
        delta = jacobi_step(T_old, T_new, fixed)
        T_old, T_new = T_new, T_old  # swap buffers
        step += 1
        
        # Track convergence history
        convergence_history["iterations"].append(step)
        convergence_history["deltas"].append(delta)

        # Output cadence like the slides' "t=0,5,10,20,..."
        if step % args.output_every == 0 or delta <= args.tol:
            if not args.no_vtk:
                vti_path = out_dir / f"step_{step:05d}.vti"
                write_vti_image_data(str(vti_path), T_old, dx, dy, name="Temperature")
                vtk_paths.append(str(vti_path))  # keep the list; it now holds .vti files
                times.append(float(step))
                if args.also_csv:
                    write_csv_snapshot(str(out_dir / f"step_{step:05d}.csv"), T_old)
                print(f"[iter {step:6d}] delta={delta:.6e} -> wrote {vti_path.name}")
            else:
                print(f"[iter {step:6d}] delta={delta:.6e}")
            if args.gif:
                frames.append(create_temperature_frame(T_old, step, delta, T_BOTTOM, T_HOT))

    # PVD collection for ParaView time series
    if not args.no_vtk and len(vtk_paths) > 0:
        write_pvd_collection(str(out_dir / "series.pvd"), vtk_paths, times)
    
    # Save GIF if requested
    if args.gif and len(frames) > 0:
        gif_path = out_dir / "temperature_evolution.gif"
        print(f"\nSaving GIF animation with {len(frames)} frames...")
        
        # Use PIL to save GIF
        from PIL import Image
        pil_frames = [Image.fromarray(frame) for frame in frames]
        duration_ms = int(1000 / args.gif_fps)
        pil_frames[0].save(
            str(gif_path),
            save_all=True,
            append_images=pil_frames[1:],
            duration=duration_ms,
            loop=0
        )
        print(f"GIF saved to: {gif_path}")
    
    print(f"\nDone. Final iter={step}, delta={delta:.6e}")
    if not args.no_vtk:
        print(f"Open in ParaView: {out_dir/'series.pvd'} (time series)")
        print("Tip: add 'Annotate Time' for the iteration number, and show the scalar bar.")
    if args.gif:
        print(f"View animation: {out_dir/'temperature_evolution.gif'}")
    
    # Return data if called programmatically
    if return_data:
        return {
            "convergence_history": convergence_history,
            "final_grid": T_old,
            "final_iter": step,
            "final_delta": delta,
            "hot_fraction": args.hot_fraction,
            "nx": args.nx,
            "ny": args.ny,
            "frames": frames if args.gif else None
        }

if __name__ == "__main__":
    main()
