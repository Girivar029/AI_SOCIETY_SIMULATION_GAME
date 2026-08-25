"""Asset discovery — faces and backgrounds, deterministic mapping."""

import random
from pathlib import Path
import pygame

from src.config.roles import Role, ROLES

# Paths relative to project root (parent of src) — also handles PyInstaller frozen bundle
import sys

def _get_project_root() -> Path:
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        # PyInstaller onefile: assets are at _MEIPASS/
        return Path(sys._MEIPASS)
    # Try normal layout: file at <root>/src/ui/assets.py -> parents[2] is <root>
    p = Path(__file__).resolve().parents[2]
    # If Images_Faces not found (e.g. onedir with _internal), try searching upwards and _MEIPASS fallback
    if (p / "Images_Faces").exists():
        return p
    # Fallback: executable directory (onedir layout)
    exe_dir = Path(sys.executable).resolve().parent if getattr(sys, 'frozen', False) else p
    if (exe_dir / "Images_Faces").exists():
        return exe_dir
    if (exe_dir / "_internal" / "Images_Faces").exists():
        return exe_dir / "_internal"
    return p

PROJECT_ROOT = _get_project_root()
FACES_DIR = PROJECT_ROOT / "Images_Faces"
BG_DIR = PROJECT_ROOT / "Images_BG"

# Background to year — deterministic sorted order
YEAR_ORDER = [0, 10, 25, 50, 100]

def discover_backgrounds() -> dict[int, Path]:
    files = sorted([p for p in BG_DIR.iterdir() if p.suffix.lower() in (".jpg", ".jpeg", ".png")], key=lambda x: x.name)
    # Need exactly 5
    if len(files) < 5:
        raise RuntimeError(f"Expected 5 backgrounds, found {len(files)} in {BG_DIR}")
    # Take first 5 sorted
    files = files[:5]
    mapping = {}
    for year, path in zip(YEAR_ORDER, files):
        mapping[year] = path
    return mapping

def discover_faces() -> list[Path]:
    files = sorted([p for p in FACES_DIR.iterdir() if p.suffix.lower() == ".png"], key=lambda x: x.name)
    if len(files) != 16:
        raise RuntimeError(f"Expected 16 faces, found {len(files)}")
    return files

def shuffle_portraits() -> dict[Role, Path]:
    """Shuffle 16 faces, assign first 10 to roles. Isolated random — not used by simulation."""
    faces = discover_faces()
    # Use system random (time-seeded) — cosmetic only
    shuffled = list(faces)
    random.shuffle(shuffled)
    assignment = {}
    for role, path in zip(ROLES, shuffled):
        assignment[role] = path
    return assignment

# Cache loaded surfaces
_bg_cache: dict[Path, pygame.Surface] = {}
_face_cache: dict[Path, pygame.Surface] = {}

def load_background_surface(path: Path) -> pygame.Surface:
    if path in _bg_cache:
        return _bg_cache[path]
    surf = pygame.image.load(str(path)).convert()
    _bg_cache[path] = surf
    return surf

def load_face_surface(path: Path) -> pygame.Surface:
    if path in _face_cache:
        return _face_cache[path]
    surf = pygame.image.load(str(path)).convert_alpha()
    _face_cache[path] = surf
    return surf

# For headless tests we expose mapping without pygame init
def get_background_mapping_without_load() -> dict[int, Path]:
    return discover_backgrounds()
