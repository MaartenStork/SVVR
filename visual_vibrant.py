# cars_viz_vibrant.py

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

# Hue (facecolor) -> origin (VIBRANT COLOR PALETTE)
origins = df["origin"].astype(str)
origin_levels = list(pd.Categorical(origins).categories)
# Vibrant color palette
origin_palette = {
    'Europe': '#0077bb',  # Vibrant blue
    'Japan': '#ee7733',   # Vibrant orange
    'US': '#009988'       # Vibrant teal
}

# Year (ordered) -> lightness on the marker EDGE using a grayscale ramp
yr = df["year_full"].values.astype(float)
yr_min, yr_max = float(yr.min()), float(yr.max())
yr_norm = (yr - yr_min) / (yr_max - yr_min + 1e-9)

# Build a grayscale mapper for edges (0 -> dark, 1 -> light)
year_cmap = mpl.colormaps.get_cmap("Greys")
edge_colors = [year_cmap(val) for val in yr_norm]

# ---------- Figure ----------
# Create figure with more space for legends and margins
fig = plt.figure(figsize=(16, 10), dpi=150)

# Set default font size larger
plt.rcParams.update({'font.size': 12})

# Create main plot area with specific position to leave room for legends
ax = plt.axes([0.06, 0.15, 0.70, 0.70])  # [left, bottom, width, height]

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

# Add hover tooltips using mplcursors with beautiful styling
def make_annotation_func(scatter_objs, model_lists):
    """Create annotation function that shows model name on hover"""
    def annotate(sel):
        # Find which scatter object this point belongs to
        point_idx = sel.index
        for scatter_obj, models in zip(scatter_objs, model_lists):
            if sel.artist == scatter_obj:
                if point_idx < len(models):
                    model = models[point_idx]
                    # Normalize model name - capitalize properly
                    model_clean = model.strip().title()
                    # Show only the model name
                    sel.annotation.set_text(model_clean)
                    sel.annotation.set_fontsize(13)
                    sel.annotation.set_fontweight('600')  # Semi-bold
                    
                    # Style the box beautifully
                    bbox = sel.annotation.get_bbox_patch()
                    bbox.set_boxstyle("round,pad=0.7")
                    bbox.set_facecolor('#2c3e50')  # Dark blue-gray
                    bbox.set_edgecolor('#3498db')  # Bright blue border
                    bbox.set_linewidth(2)
                    bbox.set_alpha(0.95)
                    
                    # Style the text
                    sel.annotation.set_color('white')
                    
                    # Style the arrow
                    sel.annotation.arrow_patch.set_color('#3498db')
                    sel.annotation.arrow_patch.set_linewidth(1.5)
                break
    return annotate

# Create cursor with hover functionality
cursor = mplcursors.cursor(all_scatter_objects, hover=True)
cursor.connect("add", make_annotation_func(all_scatter_objects, model_names))

# Axes labels & title
ax.set_xlabel("Vehicle weight", labelpad=6, fontsize=15, fontweight='bold')
ax.set_ylabel("Fuel efficiency (MPG)", labelpad=6, fontsize=15, fontweight='bold')

# Make tick labels bigger
ax.tick_params(axis='both', which='major', labelsize=14)
ax.set_title("MPG vs Weight", 
             fontsize=18, pad=15, fontweight='bold')

# Make grid subtle to support reading by position
ax.grid(True, linestyle="-", linewidth=0.5, alpha=0.4)

# ---------- Legends (Unified Professional Layout) ----------

# Create unified legend area on the right
legend_x = 0.78  # X position for all legends
legend_width = 0.20  # Width for legends
legend_height = 0.16  # Height for each legend box
legend_gap = 0.09  # Consistent gap between all legends
legend_gap_large = 0.178  # Larger gap before Horsepower

# Style settings for consistency
legend_style = {
    'frameon': True,
    'framealpha': 1.0,
    'edgecolor': '#d0d0d0',
    'fancybox': True,
    'fontsize': 13,
    'title_fontsize': 14,
    'borderpad': 1.5,
    'columnspacing': 1.0,
    'handletextpad': 1.5
}

# Calculate positions with proper spacing
legend_top = 0.69  # Top position for first legend

# 1. Origin legend - Top
origin_handles = [Patch(facecolor=origin_palette[o], edgecolor="#333333", linewidth=0.5) 
                  for o in origin_levels]
origin_y = legend_top
origin_ax = fig.add_axes([legend_x, origin_y, legend_width, legend_height])
origin_ax.axis('off')
leg1 = origin_ax.legend(origin_handles, origin_levels, title="Origin (hue)", 
                        loc='lower left', mode='expand', ncol=1,
                        bbox_to_anchor=(0, 0, 1, 1),
                        **legend_style)
leg1.get_title().set_fontweight('bold')

# 2. Cylinders legend - Middle  
unique_cyl = sorted(df["cylinders"].dropna().astype(int).unique())
shape_handles = [Line2D([0], [0], marker=marker_for_cyl(c), color="none",
                        markerfacecolor="#666666", markeredgecolor="#333333",
                        markersize=12, linewidth=0)
                 for c in unique_cyl]
cylinders_y = origin_y - legend_height - legend_gap
cylinders_ax = fig.add_axes([legend_x, cylinders_y, legend_width, legend_height])
cylinders_ax.axis('off')
leg2 = cylinders_ax.legend(shape_handles, [f"{c} cylinders" for c in unique_cyl], 
                           title="Cylinders (shape)", loc='lower left', mode='expand', ncol=1,
                           bbox_to_anchor=(0, 0, 1, 1),
                           **legend_style)
leg2.get_title().set_fontweight('bold')

# 3. Horsepower legend - Bottom
hp_ticks = np.linspace(hp_min, hp_max, 4)
hp_sizes = Amin + (hp_ticks - hp_min) / (hp_max - hp_min + 1e-9) * (Amax - Amin)
size_handles = [plt.scatter([], [], s=s, facecolor="white", edgecolor="#333333", 
                           linewidth=2.0)
                for s in hp_sizes]
hp_y = cylinders_y - legend_height - legend_gap_large
hp_ax = fig.add_axes([legend_x, hp_y, legend_width, legend_height])
hp_ax.axis('off')
leg3 = hp_ax.legend(size_handles, [f"{int(v)} HP" for v in hp_ticks], 
                    title="Horsepower (size)", loc='lower left', mode='expand', ncol=1,
                    bbox_to_anchor=(0, 0, 1, 1),
                    scatterpoints=1, labelspacing=2.0,
                    **legend_style)
leg3.get_title().set_fontweight('bold')

# 4. Model legend (hover info) - Below Horsepower
from matplotlib.patches import Rectangle
model_gap = -0.01  # Smaller gap for Model legend
model_y = hp_y - legend_height - model_gap
model_ax = fig.add_axes([legend_x, model_y, legend_width, legend_height])
model_ax.axis('off')

# Create invisible handles for the text
invisible_handle = Rectangle((0, 0), 0, 0, alpha=0)
legend_style_no_handle = {k: v for k, v in legend_style.items() 
                          if k not in ['handletextpad', 'handlelength']}
leg4 = model_ax.legend([invisible_handle], 
                       ['Hover to reveal model name'], 
                       title="Model (pop-up)", 
                       loc='lower left', mode='expand', ncol=1,
                       bbox_to_anchor=(0, 0, 1, 1),
                       handlelength=0,
                       handletextpad=0,
                       **legend_style_no_handle)
leg4.get_title().set_fontweight('bold')

# Year colorbar - with proper box styling
norm = mpl.colors.Normalize(vmin=yr_min, vmax=yr_max)
sm = mpl.cm.ScalarMappable(cmap=year_cmap, norm=norm)
sm.set_array([])

# First create the box background - slightly taller and moved down more
box_ax = fig.add_axes([0.07, -0.04, 0.68, 0.10])
box_ax.set_xlim(0, 1)
box_ax.set_ylim(0, 1)
box_ax.axis('off')

# Draw a rectangle with rounded corners matching the legend style
from matplotlib.patches import FancyBboxPatch
rect = FancyBboxPatch(
    (0, 0), 1, 1,
    boxstyle="round,pad=0.02",
    facecolor='white',
    edgecolor='#d0d0d0',
    linewidth=1,
    transform=box_ax.transAxes,
    clip_on=False,
    zorder=1  # Behind colorbar
)
box_ax.add_patch(rect)

# Add the title
box_ax.text(0.5, 0.87, 'Year (edge lightness)', fontsize=14, fontweight='bold',
            ha='center', va='top', transform=box_ax.transAxes, zorder=3)

# Now create the colorbar ON TOP of the box - adjusted for new box position
cbar_ax = fig.add_axes([0.12, -0.01, 0.56, 0.02])
cbar = plt.colorbar(sm, cax=cbar_ax, orientation='horizontal')
cbar.ax.tick_params(labelsize=12)
cbar.ax.set_zorder(2)  # On top of box

# ---------- Nice ticks ----------
# If year_full was 1970..1982, ensure the colorbar shows integers
if yr_max - yr_min <= 20:
    cbar.set_ticks(np.arange(math.floor(yr_min), math.ceil(yr_max)+1, 2))

# No need for tight_layout since we're manually positioning everything

# Save both PNG and SVG with margins to ensure nothing is cut off
plt.savefig("cars_viz_vibrant_final.png", dpi=150, bbox_inches='tight', pad_inches=0.5)
plt.savefig("cars_viz_vibrant_final.svg", bbox_inches='tight', pad_inches=0.5)

print("✓ Saved: cars_viz_vibrant_final.png")
print("✓ Saved: cars_viz_vibrant_final.svg")

plt.show()


