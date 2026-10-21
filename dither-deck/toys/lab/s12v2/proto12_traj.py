#!/usr/bin/env python3
"""proto12: the warm-start trajectory. one continuous anneal; the charges
(zero-pole singularities) move along the Henry homotopy while the
Swift-Hohenberg field re-equilibrates from its own previous state.
square domain, periodic edges, ink = global 45th percentile (02's law, whole
field — no pad, the pattern does not know about fingers).

charge keyframes (fractions of S, y down; charge identity tracked):
  arch        tented         loop            whorl
  core below  core rises     core in field   core centred
  deltas far  deltas near    delta B leaves  deltas flank
usage: python proto12_traj.py <frame_start> <frame_end>   # e.g. 0 4
"""
import numpy as np
from PIL import Image
import os, sys

OUT = os.path.dirname(os.path.abspath(__file__))
CKPT = f"{OUT}/traj_ckpt.npz"
S = 340
LAM = 7.0
Q0 = 2 * np.pi / LAM
EPS = 0.3
ALPHA = 0.25
DT = 0.02
STEPS_PER_FRAME = 3500
NFRAMES = 12
SEED = 7

y, x = np.mgrid[0:S, 0:S].astype(float)
z = x + 1j * y
TOP = (int(S / 2), int(0.10 * S))

KEY = [  # (core, deltaA, deltaB) per keyframe
    [(0.50, 1.30), (-0.05, 1.75), (1.05, 1.75)],   # arch
    [(0.50, 1.00), (0.32, 0.90), (0.68, 0.90)],    # tented
    [(0.44, 0.58), (0.64, 0.98), (1.50, 2.60)],    # loop (delta B exits)
    [(0.50, 0.46), (0.16, 0.88), (0.84, 0.88)],    # whorl
]

def charges_at(f):
    """charge positions at frame f in [0, NFRAMES-1], keyframes interpolated"""
    t = f / (NFRAMES - 1) * (len(KEY) - 1)
    i = min(int(t), len(KEY) - 2)
    u = t - i
    out = []
    for c in range(3):
        a, b = KEY[i][c], KEY[i + 1][c]
        out.append((a[0] * (1 - u) + b[0] * u, a[1] * (1 - u) + b[1] * u))
    return out[0], [out[1], out[2]]

def director(core, deltas):
    H = np.ones_like(z, dtype=complex)
    H *= (z - core[0] * S - 1j * core[1] * S)
    for dx, dy in deltas:
        H /= (z - dx * S - 1j * dy * S)
    d = H / (np.abs(H) + 1e-12)
    th_top = 0.5 * np.angle(d[TOP[1], TOP[0]])
    return d * np.exp(-2j * th_top)

def tensors(d):
    theta = 0.5 * np.angle(d)
    ct, st = np.cos(theta), np.sin(theta)
    return (ct * ct + ALPHA * st * st,
            st * st + ALPHA * ct * ct,
            (1 - ALPHA) * ct * st)

def anneal(p, axx, ayy, axy, steps):
    def divAgrad(q):
        gx = np.roll(q, -1, 1) - q
        gy = np.roll(q, -1, 0) - q
        fx = axx * gx + axy * gy
        fy = axy * gx + ayy * gy
        return (fx - np.roll(fx, 1, 1)) + (fy - np.roll(fy, 1, 0))
    def B(q):
        return divAgrad(q) + Q0 ** 2 * q
    for _ in range(steps):
        p = p + DT * (EPS * p - B(B(p)) - p ** 3)
        np.clip(p, -5, 5, out=p)
    return p

def finish(p, f):
    thr = np.sort(p.ravel())[int(0.45 * p.size)]
    bits = p < thr
    img = np.full((S, S), 255, np.uint8)
    img[bits] = 0
    Image.fromarray(img).save(f"{OUT}/f{f:02d}.png")

f0, f1 = int(sys.argv[1]), int(sys.argv[2])
if f0 == 0:
    rng = np.random.default_rng(SEED)
    p = (0.25 * np.cos(Q0 * y) + 0.08 * rng.standard_normal((S, S)))
else:
    p = np.load(CKPT)["p"]

for f in range(f0, min(f1, NFRAMES)):
    core, deltas = charges_at(f)
    axx, ayy, axy = tensors(director(core, deltas))
    p = anneal(p, axx, ayy, axy, STEPS_PER_FRAME)
    np.savez(CKPT, p=p)
    finish(p, f)
    print(f"frame {f} done: core={core}, deltas={deltas}", flush=True)
print("segment complete")
