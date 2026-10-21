#!/usr/bin/env python3
"""proto5: longer ridges + second contextual pass (Cappelli-style iteration),
arch flattened, tented given a visible delta fan."""
import numpy as np
from PIL import Image
import os

OUT = os.path.dirname(os.path.abspath(__file__))
S = 340
LAM = 10.0
BINS = 24
SEED = 12
SIG_L = 2.6 * LAM
SIG_S = 0.5 * LAM

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

def kern(th, sig_l, sig_s, cos=True):
    R = int(3 * sig_l) + 1
    yy, xx = np.mgrid[-R:R + 1, -R:R + 1].astype(float)
    u = xx * np.cos(th) + yy * np.sin(th)
    v = -xx * np.sin(th) + yy * np.cos(th)
    g = np.exp(-u ** 2 / (2 * sig_l ** 2) - v ** 2 / (2 * sig_s ** 2))
    if cos:
        g = g * np.cos(2 * np.pi * v / LAM)
    else:
        g = g / g.sum()
    return g

def steer(field_in, theta, sig_l, sig_s, cos):
    FF = np.fft.fft2(field_in)
    acc = np.zeros((S, S))
    fb = theta / np.pi * BINS
    b0 = np.floor(fb).astype(int) % BINS
    frac = fb - np.floor(fb)
    for b in range(BINS):
        w = np.where(b0 == b, 1 - frac, 0.0) + np.where((b0 + 1) % BINS == b, frac, 0.0)
        if not w.any():
            continue
        K = np.fft.fft2(np.fft.ifftshift(kern(np.pi * b / BINS, sig_l, sig_s, cos)), s=(S, S))
        acc += w * np.real(np.fft.ifft2(FF * K))
    return acc

def stripes(cores, deltas, seed=SEED):
    d = director(cores, deltas)
    th_top = 0.5 * np.angle(d[TOP[1], TOP[0]])
    d = d * np.exp(-2j * th_top)
    theta = 0.5 * np.angle(d) % np.pi
    rng = np.random.default_rng(seed)
    a1 = steer(rng.standard_normal((S, S)), theta, SIG_L, SIG_S, cos=True)
    a2 = steer(a1, theta, 2.0 * LAM, 0.6 * LAM, cos=False)   # second contextual pass
    vals = np.sort(a2[pad].ravel())
    thr = vals[int(0.45 * len(vals))]
    return (a2 < thr) & pad

def img_of(bits):
    img = np.full((S, S), 255, np.uint8)
    img[bits] = 0
    return Image.fromarray(img)

JOURNEY = [
    ("arch",   [(0.50, 2.30)], [(-0.30, 2.70), (1.30, 2.70)]),
    ("tented", [(0.50, 1.35)], [(0.30, 1.30), (0.70, 1.30)]),
    ("loop",   [(0.44, 0.58)], [(0.64, 0.98), (1.50, 2.60)]),
    ("whorl",  [(0.50, 0.46)], [(0.16, 0.88), (0.84, 0.88)]),
]
ims = []
for tag, cores, deltas in JOURNEY:
    C = [(cx * S, cy * S) for cx, cy in cores]
    D = [(dx * S, dy * S) for dx, dy in deltas]
    bits = stripes(C, D)
    img_of(bits).save(f"{OUT}/k_{tag}.png")
    print(tag, "ink", round(bits.sum() / pad.sum(), 4))
    ims.append(img_of(bits))

ref = Image.open(f"{OUT}/../ref_fingerprint.png").convert("L").resize((S, S))
M = Image.new("L", (S * 5, S), 128)
for i, im in enumerate(ims + [ref]):
    M.paste(im, (i * S, 0))
M.save(f"{OUT}/_journey5.png")
print("montage: arch tented loop whorl REF")
