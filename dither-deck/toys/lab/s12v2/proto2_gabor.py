#!/usr/bin/env python3
"""S12 v2 prototype 2 — zero-pole orientation + steered-Gabor condensation.

the honest story: ridge POSITIONS are developmental noise (Kücken & Newell:
real prints grow from random initial conditions); ridge DIRECTIONS are the
zero-pole field (Sherlock & Monro: cores = zeros, deltas = poles); the
condensation law is contextual filtering — a Gabor kernel steered by the
local orientation, pitch locked at lam. where orientation regions meet
incompatibly the stripes cannot connect: endings and bifurcations are the
topological residue, not a drawing.
"""
import numpy as np
from PIL import Image
import os

OUT = os.path.dirname(os.path.abspath(__file__))
S = 340
LAM = 10.0                     # ridge pitch, px
BINS = 24
SEED = 12

y, x = np.mgrid[0:S, 0:S].astype(float)
z = x + 1j * y

PAD_RX, PAD_RY, PAD_CY = 0.40 * S, 0.47 * S, 0.52 * S
pad = ((x - S / 2) / PAD_RX) ** 2 + ((y - PAD_CY) / PAD_RY) ** 2 <= 1.0

def director(cores, deltas):
    """d = e^{i 2 theta}: cores zeros (+1/2), deltas poles (-1/2)"""
    H = np.ones_like(z, dtype=complex)
    for cx, cy in cores:
        H *= (z - cx - 1j * cy)
    for dx, dy in deltas:
        H /= (z - dx - 1j * dy)
    return H / (np.abs(H) + 1e-12)

def gabor_kernels(lam=LAM, sig_l=1.1 * LAM, sig_s=0.45 * LAM):
    """BINS oriented Gabor kernels (long along ridge, cos across)"""
    R = int(3 * sig_l) + 1
    yy, xx = np.mgrid[-R:R + 1, -R:R + 1].astype(float)
    ks = []
    for b in range(BINS):
        th = np.pi * b / BINS                    # ridge direction (mod pi)
        u = xx * np.cos(th) + yy * np.sin(th)    # along ridge
        v = -xx * np.sin(th) + yy * np.cos(th)   # across ridge
        g = np.exp(-u ** 2 / (2 * sig_l ** 2) - v ** 2 / (2 * sig_s ** 2)) * np.cos(2 * np.pi * v / lam)
        ks.append(np.fft.fft2(np.fft.ifftshift(g), s=(S, S)))
    return ks

KF = gabor_kernels()

def stripes(cores, deltas, seed=SEED):
    d = director(cores, deltas)
    theta = 0.5 * np.angle(d) % np.pi            # ridge orientation mod pi
    rng = np.random.default_rng(seed)
    noise = rng.standard_normal((S, S))
    NF = np.fft.fft2(noise)
    # soft bin weights: two nearest bins, linear
    fb = theta / np.pi * BINS
    b0 = np.floor(fb).astype(int) % BINS
    frac = fb - np.floor(fb)
    acc = np.zeros((S, S))
    # precompute filtered noise per bin (24 FFTs, cheap)
    resp = [np.real(np.fft.ifft2(NF * KF[b])) for b in range(BINS)]
    for b in range(BINS):
        w = np.where(b0 == b, 1 - frac, 0.0) + np.where((b0 + 1) % BINS == b, frac, 0.0)
        if w.any():
            acc += w * resp[b]
    acc = np.where(pad, acc, np.nan)
    vals = np.sort(acc[pad].ravel())
    thr = vals[int(0.45 * len(vals))]
    bits = (acc < thr) & pad
    return bits

def render(tag, cores, deltas):
    bits = stripes(cores, deltas)
    img = np.full((S, S), 255, np.uint8)
    img[bits] = 0
    Image.fromarray(img).save(f"{OUT}/g_{tag}.png")
    print(f"{tag}: ink={bits.sum()/pad.sum():.4f}")

JOURNEY = [
    ("arch",   [(0.50, 2.40)], [(-0.50, 2.80), (1.50, 2.80)]),
    ("tented", [(0.50, 1.55)], [(0.18, 1.90), (0.82, 1.90)]),
    ("loop",   [(0.44, 0.60)], [(0.62, 1.02), (1.45, 2.60)]),
    ("whorl",  [(0.50, 0.46)], [(0.16, 0.88), (0.84, 0.88)]),
]
for tag, cores, deltas in JOURNEY:
    C = [(cx * S, cy * S) for cx, cy in cores]
    D = [(dx * S, dy * S) for dx, dy in deltas]
    render(tag, C, D)

from PIL import Image as I
ims = [I.open(f"{OUT}/g_{t}.png").convert("L") for t, _, _ in JOURNEY]
M = I.new("L", (S * len(ims), S), 128)
for i, im in enumerate(ims):
    M.paste(im, (i * S, 0))
M.save(f"{OUT}/_mont_g.png")
print("montage done")
