"""
0piaceos heart - animated heart made of repeated words (matplotlib).
Just run it. Missing packages are installed automatically.
"""

import subprocess
import sys


def ensure(package, module=None):
    try:
        __import__(module or package)
    except ImportError:
        print(f"Installing {package}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])


ensure("numpy")
ensure("matplotlib")
ensure("pillow", "PIL")

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.path import Path

# ---------------- SETTINGS ----------------
NAME = "0piaceos"
BACKGROUND = "#000000"
COLORS = ["#ffb3d1"]       # all words use the same light pink
SPACING_X = 4.3            # minimum horizontal distance between words
SPACING_Y = 1.15           # minimum vertical distance between words
REVEAL_FRAMES = 130        # frames it takes for the heart to form
BEAT_FRAMES = 55           # frames per heartbeat
SAVE_GIF = False           # True also saves "preview.gif"
# ------------------------------------------

rng = np.random.default_rng(7)

# Classic heart curve
t = np.linspace(0, 2 * np.pi, 600)
hx = 16 * np.sin(t) ** 3
hy = 13 * np.cos(t) - 5 * np.cos(2 * t) - 2 * np.cos(3 * t) - np.cos(4 * t)
outline = Path(np.column_stack([hx, hy]))

# Scatter words inside the heart without overlapping
candidates = np.column_stack([rng.uniform(-16.5, 16.5, 40000),
                              rng.uniform(-17, 13, 40000)])
candidates = candidates[outline.contains_points(candidates, radius=-1.2)]

points = []
for p in candidates:
    if not points:
        points.append(p)
        continue
    d = (np.array(points) - p) / [SPACING_X, SPACING_Y]
    if np.all(np.max(np.abs(d), axis=1) >= 1):
        points.append(p)
points = np.array(points)
N = len(points)

# Reveal order: from the center outwards
center = np.array([0, 1])
order = np.argsort(np.linalg.norm((points - center) / [1, 1.1], axis=1))
start = np.empty(N)
start[order] = np.linspace(0, REVEAL_FRAMES, N)

# Figure
fig, ax = plt.subplots(figsize=(8, 8), facecolor=BACKGROUND)
ax.set_facecolor(BACKGROUND)
ax.set_xlim(-22, 22)
ax.set_ylim(-22, 19)
ax.set_aspect("equal")
ax.axis("off")

# Soft glow around the heart outline
glows = []
for lw, a in [(10, 0.05), (6, 0.08), (2.5, 0.35)]:
    (ln,) = ax.plot(hx, hy, color=COLORS[0], lw=lw, alpha=0, solid_capstyle="round")
    glows.append((ln, a))

# Words
base_size = rng.uniform(7.5, 8.5, N)
rotation = rng.uniform(-14, 14, N)
texts = []
for i, (x, y) in enumerate(points):
    tx = ax.text(x, y, NAME, color=COLORS[i % len(COLORS)], fontsize=base_size[i],
                 fontweight="bold", fontstyle="italic", rotation=rotation[i],
                 ha="center", va="center", alpha=0)
    texts.append(tx)

title = ax.text(0, -19.5, f"{NAME}  \u2665", color=COLORS[0], fontsize=22,
                ha="center", va="center", alpha=0, fontstyle="italic")


def beat(f):
    """Heartbeat pulse (a double 'thump')."""
    ph = (f % BEAT_FRAMES) / BEAT_FRAMES
    return 0.05 * np.exp(-((ph - 0.10) / 0.06) ** 2) + 0.035 * np.exp(-((ph - 0.28) / 0.07) ** 2)


def update(f):
    s = 1 + (beat(f - REVEAL_FRAMES) if f > REVEAL_FRAMES else 0)

    for i, tx in enumerate(texts):
        prog = np.clip((f - start[i]) / 18, 0, 1)
        prog = prog * prog * (3 - 2 * prog)  # smooth fade-in
        tx.set_alpha(prog)
        x, y = points[i] * s
        tx.set_position((x, y - (1 - prog) * 1.5))  # floats up while appearing
        tx.set_fontsize(base_size[i] * s * (0.6 + 0.4 * prog))

    done = np.clip((f - REVEAL_FRAMES + 20) / 40, 0, 1)
    for ln, a in glows:
        ln.set_data(hx * s, hy * s)
        ln.set_alpha(a * done)
    title.set_alpha(done)
    return texts


total = REVEAL_FRAMES + BEAT_FRAMES * 8
anim = FuncAnimation(fig, update, frames=total, interval=30, blit=False, repeat=True)

if SAVE_GIF:
    anim.save("preview.gif", writer="pillow", fps=30)
    print("Saved preview.gif")

plt.tight_layout()
plt.show()
