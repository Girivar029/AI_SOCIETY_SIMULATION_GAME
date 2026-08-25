"""Matplotlib graphs for history — non-invasive, returns surfaces for Pygame or shows external window."""

from pathlib import Path

try:
    import matplotlib
    matplotlib.use("Agg")  # headless / file only, no interactive window
    import matplotlib.pyplot as plt
    HAS_MPL = True
except ImportError:
    HAS_MPL = False

from src.simulation.state import History

# Variables to plot (representative 8)
PLOT_VARS = [
    "productivity",
    "wealth",
    "inequality",
    "social_stability",
    "freedom",
    "trust",
    "research_capacity",
    "technological_progress",
]

COLORS = ["#d7b45f", "#7fb069", "#c96a6a", "#6ac6c0", "#9a7bff", "#ff9a76", "#72a2ff", "#ffd86b"]

def generate_graph_surface(history: History, width=640, height=360, dpi=100):
    """Generate matplotlib figure and return as pygame Surface (RGBA) plus file path."""
    if not HAS_MPL:
        return None, None
    import pygame
    years = [s.year for s in history.all_states]
    fig_w = width / dpi
    fig_h = height / dpi
    fig, ax = plt.subplots(figsize=(fig_w, fig_h), dpi=dpi)
    fig.patch.set_facecolor("#16161e")
    ax.set_facecolor("#16161e")
    for idx, var in enumerate(PLOT_VARS):
        vals = [s.values[var] for s in history.all_states]
        ax.plot(years, vals, label=var, color=COLORS[idx % len(COLORS)], linewidth=1.6, marker="o", markersize=3)
    ax.set_xticks(years)
    ax.set_xlim(-2, 105)
    ax.set_ylim(0, 100)
    ax.set_xlabel("Year", color="#f5f0dc", fontsize=8)
    ax.set_ylabel("Score", color="#f5f0dc", fontsize=8)
    ax.tick_params(colors="#f5f0dc", labelsize=7)
    # legend outside?
    ax.legend(fontsize=6, facecolor="#22222c", edgecolor="#b9a56e", labelcolor="#f5f0dc", loc="upper left", ncol=2)
    ax.grid(True, color="#2a2a34", linewidth=0.5, linestyle="--", alpha=0.6)
    ax.set_title("Century Trajectory — Year 0 to 100", color="#f5f0dc", fontsize=9, pad=10)
    # tighten
    fig.tight_layout(pad=1.0)
    # Render to RGBA buffer
    fig.canvas.draw()
    w, h = fig.canvas.get_width_height()
    buf = fig.canvas.tostring_argb() if hasattr(fig.canvas, "tostring_argb") else fig.canvas.tostring_rgb()
    # Handle ARGB vs RGB difference
    if hasattr(fig.canvas, "tostring_argb"):
        surf = pygame.image.frombuffer(buf, (w, h), "ARGB")
    else:
        surf = pygame.image.frombuffer(buf, (w, h), "RGB")
        surf = surf.convert()
    plt.close(fig)
    return surf, None

def save_graph_png(history: History, out_path: Path):
    if not HAS_MPL:
        raise RuntimeError("matplotlib not available")
    years = [s.year for s in history.all_states]
    fig, ax = plt.subplots(figsize=(8, 4.5), dpi=150)
    fig.patch.set_facecolor("#16161e")
    ax.set_facecolor("#16161e")
    for idx, var in enumerate(PLOT_VARS):
        vals = [s.values[var] for s in history.all_states]
        ax.plot(years, vals, label=var, color=COLORS[idx % len(COLORS)], linewidth=2, marker="o")
    ax.set_xticks(years)
    ax.set_ylim(0, 100)
    ax.set_xlabel("Year", color="#f5f0dc")
    ax.set_ylabel("Score", color="#f5f0dc")
    ax.tick_params(colors="#f5f0dc")
    ax.legend(fontsize=8, facecolor="#22222c", edgecolor="#b9a56e", labelcolor="#f5f0dc")
    ax.grid(True, color="#2a2a34", alpha=0.6)
    ax.set_title("Century Trajectory", color="#f5f0dc")
    fig.tight_layout()
    fig.savefig(str(out_path), facecolor=fig.get_facecolor())
    plt.close(fig)
    return out_path
