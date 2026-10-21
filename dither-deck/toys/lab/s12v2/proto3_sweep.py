#!/usr/bin/env python3
"""sweep: ridge-length (sig_l) x journey config, to pick parameters."""
import numpy as np
from PIL import Image
import os

OUT = os.path.dirname(os.path.abspath(__file__))
S = 340
LAM = 10.0
BINS = 24
SEED = 12

y, x = np.mgrid[0:S, 0:S].astype(float)
z = x + 1j * y
PAD_RX, PAD_RY, PAD_CY = 0.40 * S, 0.47 * S, 0.52 * S
pad = ((x - S / 2) / PAD_RX) ** 2 + ((y - PAD_CY) / PAD_RY) ** 2 <= 1.0

def director(cores, deltas, rot=0.0):
    H = np.ones_like(z, dtype=complex)
    for cx, cy in cores:
        H *= (z - cx - 1j * cy)
    for dx, dy in deltas:
        H /= (z - dx - 1j * dy)
    d = H / (np.abs(H) + 1e-12)
    return d * np.exp(2j * rot)          # global orientation bias

def gabor(lam, sig_l, sig_s, th):
    R = int(3 * sig_l) + 1
    yy, xx = np.mgrid[-R:R + 1, -R:R + 1].astype(float)
    u = xx * np.cos(th) + yy * np.sin(th)
    v = -xx * np.sin(th) + yy * np.cos(th)
    return np.exp(-u ** 2 / (2 * sig_l ** 2) - v ** 2 / (2 * sig_s ** 2)) * np.cos(2 * np.pi * v / lam)

def stripes(cores, deltas, rot, sig_l, sig_s=0.5 * LAM, seed=SEED):
    d = director(cores, deltas, rot)
    theta = 0.5 * np.angle(d) % np.pi
    rng = np.random.default_rng(seed)
    NF = np.fft.fft2(rng.standard_normal((S, S)))
    resp = []
    for b in range(BINS):
        K = np.fft.fft2(np.fft.ifftshift(gabor(LAM, sig_l, sig_s, np.pi * b / BINS)), s=(S, S))
        resp.append(np.real(np.fft.ifft2(NF * K)))
    fb = theta / np.pi * BINS
    b0 = np.floor(fb).astype(int) % BINS
    frac = fb - np.floor(fb)
    acc = np.zeros((S, S))
    for b in range(BINS):
        w = np.where(b0 == b, 1 - frac, 0.0) + np.where((b0 + 1) % BINS == b, frac, 0.0)
        if w.any():
            acc += w * resp[b]
    vals = np.sort(acc[pad].ravel())
    thr = vals[int(0.45 * len(vals))]
    return (acc < thr) & pad

def img_of(bits):
    img = np.full((S, S), 255, np.uint8)
    img[bits] = 0
    return Image.fromarray(img)

# 1) whorl at 3 ridge lengths
wh_C = [(0.50 * S, 0.46 * S)]
wh_D = [(0.16 * S, 0.88 * S), (0.84 * S, 0.88 * S)]
row1 = [img_of(stripes(wh_C, wh_D, 0.0, sl)) for sl in (1.2 * LAM, 1.8 * LAM, 2.6 * LAM)]

# 2) arch at 3 charge distances (far = flatter bows)
archs = []
for dist in (2.4, 4.0, 8.0):
    C = [(0.50 * S, dist * S)]
    D = [(-0.6 * S, (dist + 0.4) * S), (1.6 * S, (dist + 0.4) * S)]
    archs.append(img_of(stripes(C, D, np.pi / 2, 1.8 * LAM)))   # rot: transverse

M = Image.new("L", (S * 3, S * 2), 128)
for i, im in enumerate(row1):
    M.paste(im, (i * S, 0))
for i, im in enumerate(archs):
    M.paste(im, (i * S, S))
M.save(f"{OUT}/_sweep.png")
print("sweep done: top = whorl sig_l 1.2/1.8/2.6, bottom = arch dist 2.4/4.0/8.0")
