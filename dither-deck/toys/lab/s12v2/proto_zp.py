#!/usr/bin/env python3
"""S12 v2 prototype — the zero-pole fingerprint.

orientation: director field d = H/|H|, H = prod(z-cores)/prod(z-deltas)
(Sherlock & Monro 1993: cores = +1/2 zeros, deltas = -1/2 poles; 2*theta = arg H).

phase: solve laplacian(u) = div(g), g = R90(d)/lam, by FFT — the least-squares
phase whose gradient crosses the director. near a singularity curl(d) != 0 so
no consistent phase exists: the projection's failure is the minutiae.

k: singularity pair (charge-conserving) rises through the pad:
arch -> tented -> loop -> whorl.
"""
import numpy as np
from PIL import Image
import os

OUT = os.path.dirname(os.path.abspath(__file__))
S = 340
LAM = 9.0                      # ridge pitch, px

y, x = np.mgrid[0:S, 0:S].astype(float)
z = x + 1j * y

# pad: the fingertip oval (fractions of S)
PAD_RX, PAD_RY, PAD_CY = 0.40 * S, 0.46 * S, 0.52 * S
pad = ((x - S / 2) / PAD_RX) ** 2 + ((y - PAD_CY) / PAD_RY) ** 2 <= 1.0

def field(cores, deltas):
    """director field d = e^{i 2 theta} from zero-pole charges"""
    H = np.ones_like(z, dtype=complex)
    for c in cores:
        H *= (z - c[0] - 1j * c[1])
    for d_ in deltas:
        H /= (z - d_[0] - 1j * d_[1])
    d = H / (np.abs(H) + 1e-12)
    return d

def ridges(d, lam=LAM):
    """phase by Hodge projection; stripes = cos(2 pi u); 1-bit within pad"""
    g = np.array([-d.imag, d.real]) / lam      # R90(d)/lam: phase runs ACROSS ridges
    div = np.gradient(g[0], axis=1) + np.gradient(g[1], axis=0)
    # FFT Poisson solve (periodic): u = -ifft2(fft(div)/k^2), k=0 mode -> 0
    f = np.fft.fft2(div)
    kx = np.fft.fftfreq(S) * 2 * np.pi
    KY, KX = np.meshgrid(kx, kx, indexing="ij")
    k2 = KX ** 2 + KY ** 2
    k2[0, 0] = 1.0
    u = np.real(np.fft.ifft2(-f / k2))
    u -= u.mean()
    cont = 0.5 + 0.5 * np.cos(2 * np.pi * u)
    cont = np.where(pad, cont, 1.0)
    # ink: 45th percentile WITHIN the pad (02's law, pad-region variant)
    vals = np.sort(cont[pad].ravel())
    thr = vals[int(0.45 * len(vals))]
    bits = (cont < thr) & pad
    return bits, cont, u

def render(k, cores, deltas, tag):
    bits, cont, u = field(cores, deltas), None, None
    bits, cont, u = ridges(bits)
    img = np.full((S, S), 255, np.uint8)
    img[bits] = 0
    Image.fromarray(img).save(f"{OUT}/zp_{tag}.png")
    print(f"{tag}: ink={bits.sum()/pad.sum():.4f} (within pad)")

# journey: singularity positions in absolute px. pairs conserve charge.
JOURNEY = [
    # (tag, cores, deltas)
    ("arch",   [(0.50, 2.40)], [(-0.50, 2.80), (1.50, 2.80)]),   # pair far below pad
    ("tented", [(0.50, 1.55)], [(0.18, 1.90), (0.82, 1.90)]),    # nearing the pad
    ("loop",   [(0.44, 0.60)], [(0.62, 1.02), (1.45, 2.60)]),    # core + one delta in play
    ("whorl",  [(0.50, 0.46)], [(0.16, 0.88), (0.84, 0.88)]),    # core centred, deltas flanking
]
for tag, cores, deltas in JOURNEY:
    C = [(cx * S, cy * S) for cx, cy in cores]
    D = [(dx * S, dy * S) for dx, dy in deltas]
    render(tag, C, D, tag)
print("done")
