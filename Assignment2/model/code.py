#!/usr/bin/env python3
"""
Steady-state 2D temperature (Laplace) with Jacobi updates — slide-faithful.

Geometry (meters):
- Plate: 9 m x 9 m
- Hot square: 3 m x 3 m centered, fixed at 212°
Boundary conditions:
- Bottom edge: 32°
- Top edge: 100°
- Left & Right edges: linear ramp from 32° (bottom) to 100° (top)
- Interior hot square: 212°, kept fixed every sweep

Outputs:
- Legacy VTK STRUCTURED_POINTS files: step_00000.vtk, step_00020.vtk, ...
- A ParaView .pvd collection file to treat the steps as a time series
- (Optional) CSV snapshots for quick inspection

This matches the lecture slides' pseudocode and delta stopping rule.
"""

from __future__ import annotations
import argparse
import math
import os
from pathlib import Path
from typing import Tuple, List

# -----------------------------
# Utilities
# -----------------------------

def linspace(n: int, start: float, end: float) -> List[float]:
    if n == 1:
        return [start]
    step = (end - start) / (n - 1)
    return [start + i * step for i in range(n)]

def write_legacy_vtk_structured_points(
    filename: str,
    grid: "list[list[float]]",
    dx: float,
    dy: float,
    origin: Tuple[float, float, float] = (0.0, 0.0, 0.0),
    name: str = "Temperature",
):
    """
    Write a 2D scalar field as a VTK legacy STRUCTURED_POINTS dataset (ASCII).
    ParaView will read this without extra Python packages.

    Data ordering for STRUCTURED_POINTS is x fastest, then y, then z.
    We have a single z-plane (NZ=1).
    """
    ny = len(grid)
    nx = len(grid[0])
    nz = 1

    with open(filename, "w") as f:
        f.write("# vtk DataFile Version 3.0\n")
        f.write("Steady-state temperature (Jacobi)\n")
        f.write("ASCII\n")
        f.write("DATASET STRUCTURED_POINTS\n")
        f.write(f"DIMENSIONS {nx} {ny} {nz}\n")
        f.write(f"ORIGIN {origin[0]} {origin[1]} {origin[2]}\n")
        f.write(f"SPACING {dx} {dy} 1.0\n")
        f.write(f"POINT_DATA {nx * ny * nz}\n")
        f.write(f"SCALARS {name} float 1\n")
        f.write("LOOKUP_TABLE default\n")

        # VTK expects x varying fastest, then y
        for j in range(ny):
            row = grid[j]
            # Write numbers in chunks per line for readability
            line = []
            for i in range(nx):
                line.append(f"{float(row[i]):.6f}")
                if len(line) >= 8:
                    f.write(" ".join(line) + "\n")
                    line = []
            if line:
                f.write(" ".join(line) + "\n")

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

# -----------------------------
# Physics / Discretization
# -----------------------------

def build_indices_hot_square(nx: int, ny: int) -> Tuple[int, int, int, int]:
    """
    Hot square is 1/3 of plate width/height, centered.
    We keep it integer-index aligned and inclusive bounds.
    """
    w_frac = 1 / 3.0
    hot_w = int(round(nx * w_frac))
    hot_h = int(round(ny * w_frac))

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

def main():
    ap = argparse.ArgumentParser(description="Laplace (Jacobi) with ParaView-ready outputs.")
    ap.add_argument("--nx", type=int, default=181, help="Grid points in x (columns).")
    ap.add_argument("--ny", type=int, default=181, help="Grid points in y (rows).")
    ap.add_argument("--tol", type=float, default=1e-3, help="Convergence tolerance on delta.")
    ap.add_argument("--max-iters", type=int, default=20000, help="Safety cap on iterations.")
    ap.add_argument("--output-every", type=int, default=50, help="Write VTK every N iterations.")
    ap.add_argument("--out", type=str, default="out_vtk", help="Output directory.")
    ap.add_argument("--also-csv", action="store_true", help="Write CSV snapshots too.")
    args = ap.parse_args()

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

    i0, i1, j0, j1 = build_indices_hot_square(args.nx, args.ny)
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
    step = 0
    vtk0 = out_dir / f"step_{step:05d}.vtk"
    write_legacy_vtk_structured_points(str(vtk0), T_old, dx, dy, name="Temperature")
    vtk_paths.append(str(vtk0))
    times.append(float(step))
    if args.also_csv:
        write_csv_snapshot(str(out_dir / f"step_{step:05d}.csv"), T_old)

    # Jacobi iteration loop (slide: do { ... } while (delta > tolerance))
    delta = float("inf")
    while delta > args.tol and step < args.max_iters:
        delta = jacobi_step(T_old, T_new, fixed)
        T_old, T_new = T_new, T_old  # swap buffers
        step += 1

        # Output cadence like the slides' “t=0,5,10,20,...”
        if step % args.output_every == 0 or delta <= args.tol:
            vtk_path = out_dir / f"step_{step:05d}.vtk"
            write_legacy_vtk_structured_points(str(vtk_path), T_old, dx, dy, name="Temperature")
            vtk_paths.append(str(vtk_path))
            times.append(float(step))
            if args.also_csv:
                write_csv_snapshot(str(out_dir / f"step_{step:05d}.csv"), T_old)
            print(f"[iter {step:6d}] delta={delta:.6e} -> wrote {vtk_path.name}")

    # PVD collection for ParaView time series
    write_pvd_collection(str(out_dir / "series.pvd"), vtk_paths, times)
    print(f"\nDone. Final iter={step}, delta={delta:.6e}")
    print(f"Open in ParaView: {out_dir/'series.pvd'} (time series)")
    print("Tip: add 'Annotate Time' for the iteration number, and show the scalar bar.")

if __name__ == "__main__":
    main()
