# cars_viz.py
# One-figure, seven-dimension visualization per Bertin & Mackinlay mapping.

import math
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
import matplotlib as mpl
import mplcursors

# ---------- Load & clean ----------
df = pd.read_csv("cars.csv")

# Normalize column names (handle misspelling "weigth")
cols = {c.lower().strip(): c for c in df.columns}
# rename to consistent lower-case names
rename_map = {}
if "weigth" in cols:   # original misspelling
    rename_map[cols["weigth"]] = "weight"
if "mpg" in cols:
    rename_map[cols["mpg"]] = "mpg"
if "cylinders" in cols:
    rename_map[cols["cylinders"]] = "cylinders"
if "horsepower" in cols:
    rename_map[cols["horsepower"]] = "horsepower"
if "year" in cols:
    rename_map[cols["year"]] = "year"
if "model" in cols:
    rename_map[cols["model"]] = "model"
if "origin" in cols:
    rename_map[cols["origin"]] = "origin"

df = df.rename(columns=rename_map)

# Coerce numeric columns; some datasets store '?' for horsepower.
for col in ["mpg", "weight", "horsepower", "year", "cylinders"]:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

# If years are 70..82, convert to full years 1970..1982 for labeling; keep numeric continuity.
if df["year"].dropna().between(0, 150).all():  # heuristic for model-year encoding
    df["year_full"] = np.where(df["year"] < 100, 1900 + df["year"], df["year"])
else:
    df["year_full"] = df["year"]

# Drop rows missing essentials for the mark
df = df.dropna(subset=["mpg", "weight", "horsepower", "cylinders", "origin", "year_full"]).copy()

# ---------- Encodings ----------
# Position -> (weight, mpg)
x = df["weight"].values
y = df["mpg"].values

# Size (area) -> horsepower (use perceptual area scaling)
hp = df["horsepower"].values.astype(float)
hp_min, hp_max = float(np.nanmin(hp)), float(np.nanmax(hp))
# Map horsepower to area in [Amin, Amax]; choose radii so small values are still visible.
Amin, Amax = 25.0, 900.0  # scatter 's' argument is area in points^2
hp_norm = (hp - hp_min) / (hp_max - hp_min + 1e-9)
sizes = Amin + hp_norm * (Amax - Amin)

# Shape -> cylinders (nominal/ordered)
# Map distinct cylinder counts to distinct markers (separable with color & size).
cyl_markers = {
    3: "^",  # triangle_up
    4: "o",  # circle
    5: "s",  # square
    6: "D",  # diamond
    8: "X"   # x-filled
}
# Default fallback
def marker_for_cyl(c):
    return cyl_markers.get(int(c), "o")

markers = [marker_for_cyl(c) for c in df["cylinders"].values]

# Hue (facecolor) -> origin (nominal). Use Matplotlib's default color cycle per origin group.
origins = df["origin"].astype(str)
origin_levels = list(pd.Categorical(origins).categories)
# assign a base color per origin from the current cycler
cycler_colors = plt.rcParams['axes.prop_cycle'].by_key().get('color', ["C0", "C1", "C2", "C3"])
origin_palette = {orig: cycler_colors[i % len(cycler_colors)] for i, orig in enumerate(origin_levels)}

# Year (ordered) -> lightness on the marker EDGE using a grayscale ramp
yr = df["year_full"].values.astype(float)
yr_min, yr_max = float(yr.min()), float(yr.max())
yr_norm = (yr - yr_min) / (yr_max - yr_min + 1e-9)

# Build a grayscale mapper for edges (0 -> dark, 1 -> light)
year_cmap = mpl.colormaps.get_cmap("Greys")
edge_colors = [year_cmap(val) for val in yr_norm]

# ---------- Figure ----------
plt.figure(figsize=(20, 7), dpi=150)

ax = plt.gca()

# Store all points and their model names for hover functionality
all_scatter_objects = []
model_names = []

# Plot by origin (for legend color patches) while preserving per-point shape/size/edge lightness
for orig in origin_levels:
    subset = df[origins == orig]
    if subset.empty:
        continue
    idx = subset.index
    # Build arrays for this subset
    ms = [marker_for_cyl(c) for c in subset["cylinders"].values]
    ss = sizes[idx]
    ec = [year_cmap(v) for v in ((subset["year_full"].values.astype(float) - yr_min) / (yr_max - yr_min + 1e-9))]
    # Facecolor fixed by origin (hue); edge color carries year (lightness)
    fc = origin_palette[orig]
    
    # Group by marker type to reduce number of scatter calls
    for marker_type in set(ms):
        mask = [m == marker_type for m in ms]
        if not any(mask):
            continue
        
        sub_x = subset["weight"].values[mask]
        sub_y = subset["mpg"].values[mask]
        sub_s = ss[mask]
        sub_ec = np.array([ec[i] for i in range(len(ec)) if mask[i]])
        sub_models = subset["model"].astype(str).values[mask]
        
        sc = ax.scatter(sub_x, sub_y, s=sub_s, marker=marker_type, 
                       facecolor=fc, edgecolor=sub_ec, linewidth=0.9, alpha=0.9)
        all_scatter_objects.append(sc)
        # Store model names for this scatter object
        model_names.append(sub_models.tolist())

# Add hover tooltips using mplcursors
def make_annotation_func(scatter_objs, model_lists):
    """Create annotation function that shows model name on hover"""
    def annotate(sel):
        # Find which scatter object this point belongs to
        point_idx = sel.index
        for scatter_obj, models in zip(scatter_objs, model_lists):
            if sel.artist == scatter_obj:
                if point_idx < len(models):
                    model = models[point_idx]
                    # Get point coordinates
                    x, y = sel.target[0], sel.target[1]
                    # Show model name and coordinates
                    sel.annotation.set_text(f"{model}\n({x:.0f} lbs, {y:.1f} MPG)")
                    sel.annotation.get_bbox_patch().set_boxstyle("round,pad=0.5")
                break
    return annotate

# Create cursor with hover functionality
cursor = mplcursors.cursor(all_scatter_objects, hover=True)
cursor.connect("add", make_annotation_func(all_scatter_objects, model_names))

# Axes labels & title
ax.set_xlabel("Vehicle weight", labelpad=6)
ax.set_ylabel("Fuel efficiency (MPG)", labelpad=6)
ax.set_title("MPG vs Weight, with Horsepower (size), Origin (hue), Year (edge lightness), Cylinders (shape)")

# Make grid subtle to support reading by position
ax.grid(True, linestyle=":", linewidth=0.6, alpha=0.5)

# ---------- Legends ----------
# Origin legend (color patches)
origin_handles = [Patch(facecolor=origin_palette[o], edgecolor="none", label=o) for o in origin_levels]
origin_legend = ax.legend(handles=origin_handles, title="Origin (hue)", loc="upper right", frameon=True)
ax.add_artist(origin_legend)

# Cylinders legend (shapes)
unique_cyl = sorted(df["cylinders"].dropna().astype(int).unique())
shape_handles = [Line2D([0], [0], marker=marker_for_cyl(c), color="none",
                        markerfacecolor="grey", markeredgecolor="grey",
                        markersize=8, linewidth=0, label=f"{c} cyl")
                 for c in unique_cyl]
shape_legend = ax.legend(handles=shape_handles, title="Cylinders (shape)", loc="lower left", frameon=True)
ax.add_artist(shape_legend)

# Horsepower legend (size): pick representative values with better spacing
hp_ticks = np.linspace(hp_min, hp_max, 4)
hp_sizes = Amin + (hp_ticks - hp_min) / (hp_max - hp_min + 1e-9) * (Amax - Amin)
size_handles = [plt.scatter([], [], s=s, facecolor="none", edgecolor="grey", linewidth=1.5, label=f"{int(v)} HP")
                for s, v in zip(hp_sizes, hp_ticks)]
# Position directly below the Origin legend in the upper right corner
size_legend = ax.legend(handles=size_handles, title="Horsepower (size)", 
                        loc="upper right", frameon=True, scatterpoints=1,
                        handletextpad=3.5,  # Space between circle and text
                        labelspacing=2.2,   # Balanced vertical space between entries
                        borderpad=1.2,      # Padding around legend
                        bbox_to_anchor=(1.0, 0.82))  # Positioned directly below origin legend with small gap
ax.add_artist(size_legend)

# Year colorbar (edge lightness)
norm = mpl.colors.Normalize(vmin=yr_min, vmax=yr_max)
sm = mpl.cm.ScalarMappable(cmap=year_cmap, norm=norm)
sm.set_array([])  # required for older MPL
cbar = plt.colorbar(sm, ax=ax, pad=0.015)
cbar.set_label("Model year (edge lightness)")

# ---------- Nice ticks ----------
# If year_full was 1970..1982, ensure the colorbar shows integers
if yr_max - yr_min <= 20:
    cbar.set_ticks(np.arange(math.floor(yr_min), math.ceil(yr_max)+1, 2))

# Layout
plt.tight_layout()

# Save both PNG and SVG (SVG keeps per-point metadata for basic hover in some viewers)
plt.savefig("cars_viz.png", bbox_inches="tight")
plt.savefig("cars_viz.svg", bbox_inches="tight")

plt.show()
