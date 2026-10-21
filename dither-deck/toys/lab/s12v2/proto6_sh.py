#!/usr/bin/env python3
"""proto6: anisotropic Swift-Hohenberg stripes on a zero-pole director.

d psi/dt = eps*psi - B(B(psi)) - psi^3,   B(psi) = div(A grad psi) + q0^2 psi
A = R diag(a_across=1, a_along=alpha) R^T  — stripes lock their wavevector
ACROSS the director, so ridges run ALONG it. dislocations (endings) appear
where the director field makes a consistent stripe field impossible.
deterministic: structure from the PDE, only the seed is noise.
"""
import numpy as np
from PIL import Image
import os

OUT = os.path.dirname(os.path.abspath(__file__))
S = 170
LAM = 7.0
Q0 = 2 * np.pi / LAM
EPS = 0.3
ALPHA = 0.25          # along-ridge diffusivity penalty -> stripes follow director
DT = 0.02
STEPS = 30000
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
    theta = 0.5 * np.angle(d)                      # ridge direction mod pi (signed ok)
    ct, st = np.cos(theta), np.sin(theta)
    # diffusion tensor: across = 1, along = ALPHA
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
        p = p * pad                                # stripes live only in the pad
        if i % 10000 == 0:
            print(f"  {tag} step {i}, max|p|={np.abs(p).max():.3f}")
    return p

def finish(p, tag):
    vals = np.sort(p[pad].ravel())
    thr = vals[int(0.45 * len(vals))]
    bits = (p < thr) & pad
    img = np.full((S, S), 255, np.uint8)
    img[bits] = 0
    Image.fromarray(img).save(f"{OUT}/sh_{tag}.png")
    print(tag, "ink", round(bits.sum() / pad.sum(), 4))
    return Image.fromarray(img)

CONFIGS = [
    ("loop",  [(0.44 * S, 0.58 * S)], [(0.64 * S, 0.98 * S), (1.50 * S, 2.60 * S)]),
    ("whorl", [(0.50 * S, 0.46 * S)], [(0.16 * S, 0.88 * S), (0.84 * S, 0.88 * S)]),
]
ims = []
for tag, C, D in CONFIGS:
    p = run(C, D, tag)
    ims.append(finish(p, tag))

ref = Image.open(f"{OUT}/../ref_fingerprint.png").convert("L").resize((S, S))
M = Image.new("L", (S * 3, S), 128)
for i, im in enumerate(ims + [ref]):
    M.paste(im, (i * S, 0))
M.save(f"{OUT}/_sh.png")
print("montage: loop whorl REF")
