#!/usr/bin/env python3
"""proto7: SH stripes at 340^2, pitch matched to the reference (~14px at 680
scale), full four-state journey. usage: python proto7_340.py arch tented
"""
import numpy as np
from PIL import Image
import os, sys

OUT = os.path.dirname(os.path.abspath(__file__))
S = 340
LAM = 7.0                      # = 14px at 680 deck scale, like the reference
Q0 = 2 * np.pi / LAM
EPS = 0.3
ALPHA = 0.25
DT = 0.02
STEPS = 26000
SEED = 7

y, x = np.mgrid[0:S, 0:S].astype(float)
z = x + 1j * y
PAD_RX, PAD_RY, PAD_CY = 0.40 * S, 0.47 * S, 0.52 * S
pad = ((x - S / 2) / PAD_RX) ** 2 + ((y - PAD_CY) / PAD_RY) ** 2 <= 1.0
TOP = (int(S / 2), int(PAD_CY - 0.8 * PAD_RY))

def director(cores, deltas):
    H = np.ones_like(z, dtype=complex)
    for cx, cy in cores:
        H *= (z - cx - 1j * cy)
    for dx, dy in deltas:
        H /= (z - dx - 1j * dy)
    return H / (np.abs(H) + 1e-12)

def run(cores, deltas, tag):
    d = director(cores, deltas)
    th_top = 0.5 * np.angle(d[TOP[1], TOP[0]])
    d = d * np.exp(-2j * th_top)
    theta = 0.5 * np.angle(d)
    ct, st = np.cos(theta), np.sin(theta)
    axx = ct * ct + ALPHA * st * st
    ayy = st * st + ALPHA * ct * ct
    axy = (1 - ALPHA) * ct * st
    def divAgrad(p):
        gx = np.roll(p, -1, 1) - p
        gy = np.roll(p, -1, 0) - p
        fx = axx * gx + axy * gy
        fy = axy * gx + ayy * gy
        return (fx - np.roll(fx, 1, 1)) + (fy - np.roll(fy, 1, 0))
    def B(p):
        return divAgrad(p) + Q0 ** 2 * p
    rng = np.random.default_rng(SEED)
    p = 0.01 * rng.standard_normal((S, S)) * pad
    for i in range(STEPS):
        p = p + DT * (EPS * p - B(B(p)) - p ** 3)
        np.clip(p, -5, 5, out=p)
        p = p * pad
    vals = np.sort(p[pad].ravel())
    thr = vals[int(0.45 * len(vals))]
    bits = (p < thr) & pad
    img = np.full((S, S), 255, np.uint8)
    img[bits] = 0
    Image.fromarray(img).save(f"{OUT}/v_{tag}.png")
    print(tag, "ink", round(bits.sum() / pad.sum(), 4))

JOURNEY = {
    "arch":   ([(0.50, 1.45)], [(-0.05, 1.95), (1.05, 1.95)]),
    "tented": ([(0.50, 1.18)], [(0.30, 1.04), (0.70, 1.04)]),
    "loop":   ([(0.44, 0.58)], [(0.64, 0.98), (1.50, 2.60)]),
    "whorl":  ([(0.50, 0.46)], [(0.16, 0.88), (0.84, 0.88)]),
}
tags = sys.argv[1:] or list(JOURNEY)
for tag in tags:
    cores, deltas = JOURNEY[tag]
    C = [(cx * S, cy * S) for cx, cy in cores]
    D = [(dx * S, dy * S) for dx, dy in deltas]
    print("running", tag, flush=True)
    run(C, D, tag)

# montage whatever exists, in canonical order, plus ref
ims = []
for tag in ["arch", "tented", "loop", "whorl"]:
    f = f"{OUT}/v_{tag}.png"
    if os.path.exists(f):
        ims.append(Image.open(f).convert("L"))
if len(ims) == 4:
    ref = Image.open(f"{OUT}/../ref_fingerprint.png").convert("L").resize((S, S))
    ims.append(ref)
M = Image.new("L", (S * len(ims), S), 128)
for i, im in enumerate(ims):
    M.paste(im, (i * S, 0))
M.save(f"{OUT}/_journey340c.png")
print("montage saved:", len(ims), "panels")
