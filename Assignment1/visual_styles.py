# cars_viz_styles.py
# Generate multiple style variations of the visualization

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
rename_map = {}
if "weigth" in cols:
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

# Coerce numeric columns
for col in ["mpg", "weight", "horsepower", "year", "cylinders"]:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

# Convert years
if df["year"].dropna().between(0, 150).all():
    df["year_full"] = np.where(df["year"] < 100, 1900 + df["year"], df["year"])
else:
    df["year_full"] = df["year"]

# Drop rows missing essentials
df = df.dropna(subset=["mpg", "weight", "horsepower", "cylinders", "origin", "year_full"]).copy()

# ---------- Encodings (same for all styles) ----------
x = df["weight"].values
y = df["mpg"].values

hp = df["horsepower"].values.astype(float)
hp_min, hp_max = float(np.nanmin(hp)), float(np.nanmax(hp))
Amin, Amax = 25.0, 900.0
hp_norm = (hp - hp_min) / (hp_max - hp_min + 1e-9)
sizes = Amin + hp_norm * (Amax - Amin)

cyl_markers = {
    3: "^",  # triangle_up
    4: "o",  # circle
    5: "s",  # square
    6: "D",  # diamond
    8: "X"   # x-filled
}

def marker_for_cyl(c):
    return cyl_markers.get(int(c), "o")

origins = df["origin"].astype(str)
origin_levels = list(pd.Categorical(origins).categories)

yr = df["year_full"].values.astype(float)
yr_min, yr_max = float(yr.min()), float(yr.max())
yr_norm = (yr - yr_min) / (yr_max - yr_min + 1e-9)

# ---------- Define different styles ----------
styles = {
    "default": {
        "name": "Default (Current)",
        "style": "default",
        "origin_colors": {'Europe': '#1f77b4', 'Japan': '#ff7f0e', 'US': '#2ca02c'},
        "year_cmap": "Greys",
        "grid_style": {"linestyle": ":", "linewidth": 0.6, "alpha": 0.5},
        "bg_color": "white",
        "text_color": "black"
    },
    
    "dark": {
        "name": "Dark Theme",
        "style": "dark_background",
        "origin_colors": {'Europe': '#64b5f6', 'Japan': '#ffb74d', 'US': '#81c784'},
        "year_cmap": "Greys_r",  # Reversed for dark bg
        "grid_style": {"linestyle": "-", "linewidth": 0.4, "alpha": 0.3},
        "bg_color": "#1e1e1e",
        "text_color": "white"
    },
    
    "seaborn": {
        "name": "Seaborn Style",
        "style": "ggplot",
        "origin_colors": {'Europe': '#4c72b0', 'Japan': '#dd8452', 'US': '#55a868'},
        "year_cmap": "Greys",
        "grid_style": {"linestyle": "-", "linewidth": 0.8, "alpha": 0.5},
        "bg_color": "#eaeaf2",
        "text_color": "black"
    },
    
    "minimal": {
        "name": "Minimal Clean",
        "style": "bmh",
        "origin_colors": {'Europe': '#348ABD', 'Japan': '#E24A33', 'US': '#8EBA42'},
        "year_cmap": "Greys",
        "grid_style": {"linestyle": "--", "linewidth": 0.5, "alpha": 0.3},
        "bg_color": "white",
        "text_color": "#333333"
    },
    
    "pastel": {
        "name": "Soft Pastel",
        "style": "default",
        "origin_colors": {'Europe': '#92c5de', 'Japan': '#f4a582', 'US': '#b2e2e2'},
        "year_cmap": "Greys",
        "grid_style": {"linestyle": ":", "linewidth": 0.6, "alpha": 0.4},
        "bg_color": "#fafafa",
        "text_color": "#555555"
    },
    
    "vibrant": {
        "name": "Vibrant Colors",
        "style": "default",
        "origin_colors": {'Europe': '#0077bb', 'Japan': '#ee7733', 'US': '#009988'},
        "year_cmap": "Greys",
        "grid_style": {"linestyle": "-", "linewidth": 0.5, "alpha": 0.4},
        "bg_color": "white",
        "text_color": "black"
    }
}

# ---------- Function to create visualization with a given style ----------
def create_visualization(style_name, style_config):
    """Create visualization with specified style"""
    
    # Set matplotlib style
    try:
        plt.style.use(style_config["style"])
    except:
        plt.style.use("default")
    
    # Create figure
    fig = plt.figure(figsize=(20, 7), dpi=150)
    fig.patch.set_facecolor(style_config["bg_color"])
    
    ax = plt.gca()
    ax.set_facecolor(style_config["bg_color"])
    
    # Get style-specific settings
    origin_palette = style_config["origin_colors"]
    year_cmap = mpl.colormaps.get_cmap(style_config["year_cmap"])
    
    # Store scatter objects for hover
    all_scatter_objects = []
    model_names = []
    
    # Plot by origin
    for orig in origin_levels:
        subset = df[origins == orig]
        if subset.empty:
            continue
        idx = subset.index
        
        ms = [marker_for_cyl(c) for c in subset["cylinders"].values]
        ss = sizes[idx]
        ec = [year_cmap(v) for v in ((subset["year_full"].values.astype(float) - yr_min) / (yr_max - yr_min + 1e-9))]
        fc = origin_palette[orig]
        
        # Group by marker type
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
            model_names.append(sub_models.tolist())
    
    # Add hover tooltips
    def make_annotation_func(scatter_objs, model_lists):
        def annotate(sel):
            point_idx = sel.index
            for scatter_obj, models in zip(scatter_objs, model_lists):
                if sel.artist == scatter_obj:
                    if point_idx < len(models):
                        model = models[point_idx]
                        x, y = sel.target[0], sel.target[1]
                        sel.annotation.set_text(f"{model}\n({x:.0f} lbs, {y:.1f} MPG)")
                        sel.annotation.get_bbox_patch().set_boxstyle("round,pad=0.5")
                    break
        return annotate
    
    cursor = mplcursors.cursor(all_scatter_objects, hover=True)
    cursor.connect("add", make_annotation_func(all_scatter_objects, model_names))
    
    # Axes labels & title
    ax.set_xlabel("Vehicle weight", labelpad=6, color=style_config["text_color"])
    ax.set_ylabel("Fuel efficiency (MPG)", labelpad=6, color=style_config["text_color"])
    ax.set_title(f"MPG vs Weight - {style_config['name']}\n(Horsepower=size, Origin=hue, Year=edge, Cylinders=shape)",
                color=style_config["text_color"])
    
    # Grid
    ax.grid(True, **style_config["grid_style"])
    ax.tick_params(colors=style_config["text_color"])
    
    # Legends
    origin_handles = [Patch(facecolor=origin_palette[o], edgecolor="none", label=o) for o in origin_levels]
    origin_legend = ax.legend(handles=origin_handles, title="Origin (hue)", 
                             loc="upper right", frameon=True)
    origin_legend.get_frame().set_facecolor(style_config["bg_color"])
    for text in origin_legend.get_texts():
        text.set_color(style_config["text_color"])
    origin_legend.get_title().set_color(style_config["text_color"])
    ax.add_artist(origin_legend)
    
    # Cylinders legend
    unique_cyl = sorted(df["cylinders"].dropna().astype(int).unique())
    shape_handles = [Line2D([0], [0], marker=marker_for_cyl(c), color="none",
                            markerfacecolor='grey', markeredgecolor='grey',
                            markersize=8, linewidth=0, label=f"{c} cyl")
                     for c in unique_cyl]
    shape_legend = ax.legend(handles=shape_handles, title="Cylinders (shape)", 
                            loc="lower left", frameon=True)
    shape_legend.get_frame().set_facecolor(style_config["bg_color"])
    for text in shape_legend.get_texts():
        text.set_color(style_config["text_color"])
    shape_legend.get_title().set_color(style_config["text_color"])
    ax.add_artist(shape_legend)
    
    # Horsepower legend
    hp_ticks = np.linspace(hp_min, hp_max, 4)
    hp_sizes = Amin + (hp_ticks - hp_min) / (hp_max - hp_min + 1e-9) * (Amax - Amin)
    size_handles = [plt.scatter([], [], s=s, facecolor="none", edgecolor="grey", 
                               linewidth=1.5, label=f"{int(v)} HP")
                    for s, v in zip(hp_sizes, hp_ticks)]
    size_legend = ax.legend(handles=size_handles, title="Horsepower (size)", 
                           loc="upper right", frameon=True, scatterpoints=1,
                           handletextpad=3.5, labelspacing=2.2, borderpad=1.2,
                           bbox_to_anchor=(1.0, 0.82))
    size_legend.get_frame().set_facecolor(style_config["bg_color"])
    for text in size_legend.get_texts():
        text.set_color(style_config["text_color"])
    size_legend.get_title().set_color(style_config["text_color"])
    ax.add_artist(size_legend)
    
    # Year colorbar
    norm = mpl.colors.Normalize(vmin=yr_min, vmax=yr_max)
    sm = mpl.cm.ScalarMappable(cmap=year_cmap, norm=norm)
    sm.set_array([])
    cbar = plt.colorbar(sm, ax=ax, pad=0.015)
    cbar.set_label("Model year (edge lightness)", color=style_config["text_color"])
    cbar.ax.tick_params(colors=style_config["text_color"])
    
    if yr_max - yr_min <= 20:
        cbar.set_ticks(np.arange(math.floor(yr_min), math.ceil(yr_max)+1, 2))
    
    plt.tight_layout()
    
    # Save
    filename = f"cars_viz_{style_name}.png"
    plt.savefig(filename, bbox_inches="tight", facecolor=style_config["bg_color"])
    print(f"✓ Saved: {filename}")
    
    plt.close()

# ---------- Generate all style variations ----------
print("Generating multiple style variations...")
print("=" * 60)

for style_name, style_config in styles.items():
    print(f"Creating: {style_config['name']}...")
    create_visualization(style_name, style_config)

print("=" * 60)
print(f"✓ Generated {len(styles)} style variations!")
print("\nFiles created:")
for style_name in styles.keys():
    print(f"  - cars_viz_{style_name}.png")

