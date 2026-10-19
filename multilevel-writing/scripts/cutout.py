"""Matte a generated 3D hero off its flat background.

The image models return the object on a near-white ground with a soft contact
shadow. A plain colour key either leaves that shadow as a pale halo on the
cover's blue band, or — at a threshold high enough to remove it — leaks into
the object's own white paper. So this does two passes:

  1. flood the background inwards from the border at a safe threshold, which
     protects any white that is enclosed by the artwork;
  2. fade the remaining low-contrast fringe, i.e. opaque pixels that are both
     close to the background colour and close to the cut edge — that is the
     shadow, while interior paper is far from the edge and survives.

Usage: python3 scripts/cutout.py SOURCE.png DEST.png
"""
import sys
from collections import deque
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter

FLOOD_THRESHOLD = 14     # colour distance counted as background
FRINGE_THRESHOLD = 26    # colour distance counted as "nearly background"
FRINGE_RADIUS = 14       # how far the soft shadow reaches from the cut edge


def background_mask(rgb):
    """Pixels reachable from the border without crossing the artwork."""
    h, w, _ = rgb.shape
    bg = rgb[0, 0]
    flat = np.abs(rgb - bg).max(axis=-1) < FLOOD_THRESHOLD
    seen = np.zeros_like(flat, dtype=bool)
    q = deque()
    for x in range(w):
        for y in (0, h - 1):
            if flat[y, x] and not seen[y, x]:
                seen[y, x] = True
                q.append((y, x))
    for y in range(h):
        for x in (0, w - 1):
            if flat[y, x] and not seen[y, x]:
                seen[y, x] = True
                q.append((y, x))
    while q:
        y, x = q.popleft()
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            ny, nx = y + dy, x + dx
            if 0 <= ny < h and 0 <= nx < w and flat[ny, nx] and not seen[ny, nx]:
                seen[ny, nx] = True
                q.append((ny, nx))
    return seen


def edge_distance(mask, radius):
    """Chebyshev distance from `mask`, saturating at `radius` (cheap dilation)."""
    dist = np.where(mask, 0, radius).astype(np.int16)
    cur = mask
    for d in range(1, radius):
        grown = cur.copy()
        grown[1:, :] |= cur[:-1, :]
        grown[:-1, :] |= cur[1:, :]
        grown[:, 1:] |= cur[:, :-1]
        grown[:, :-1] |= cur[:, 1:]
        ring = grown & ~cur
        dist[ring] = d
        cur = grown
    return dist


def main(src, dest):
    im = Image.open(src).convert("RGBA")
    rgb = np.array(im).astype(np.int16)[..., :3]
    bg = rgb[0, 0]

    outside = background_mask(rgb)
    alpha = np.where(outside, 0.0, 1.0)

    near_bg = np.abs(rgb - bg).max(axis=-1) < FRINGE_THRESHOLD
    dist = edge_distance(outside, FRINGE_RADIUS)
    fringe = near_bg & ~outside
    alpha[fringe] = np.clip(dist[fringe] / FRINGE_RADIUS, 0, 1)

    a = Image.fromarray((alpha * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.6))
    out = Image.fromarray(np.dstack([rgb.astype(np.uint8), np.array(a)]), "RGBA")
    out = out.crop(out.getbbox())
    out.save(dest)
    print(f"{Path(dest).name}  {out.size}  ({100 * (np.array(a) == 0).mean():.0f}% clear)")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
