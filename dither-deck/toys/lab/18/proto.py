# S18 DEEP MASK prototype
# 1) honest void-and-cluster (Ulichney 1993) converged mask at 45% ink, 136x136 torus
# 2) Gaussian scale-space of that pattern; threshold each depth at exact 45th percentile
# 3) render candidate k-states upsampled x5 to 680, save PNGs
import numpy as np
from PIL import Image
import time, os

M = 136           # mask side; 136*5 = 680
DENS = 0.45
SIG_VC = 1.9      # void-and-cluster kernel width (mask pixels)
rng = np.random.default_rng(18)

def kernel(sig):
    r = int(np.ceil(3*sig))
    ax = np.arange(-r, r+1)
    k = np.exp(-(ax**2)/(2*sig*sig))
    k /= k.sum()
    return k, r

def conv2(P, sig):
    # toroidal separable gaussian via roll-based fft-free approach (fft is easier)
    r = int(np.ceil(3*sig))
    ax = np.arange(-r, r+1)
    g = np.exp(-(ax**2)/(2*sig*sig)); g /= g.sum()
    K = np.zeros_like(P, dtype=np.float64)
    # build 2d kernel centered at 0 with wrap
    yy, xx = np.meshgrid(ax, ax, indexing='ij')
    k2 = np.exp(-(xx**2+yy**2)/(2*sig*sig)); k2 /= k2.sum()
    Km = np.zeros((M, M))
    Km[:2*r+1, :2*r+1] = k2
    Km = np.roll(Km, (-r, -r), axis=(0,1))
    F = np.fft.rfft2(P.astype(np.float64))
    H = np.fft.rfft2(Km)
    return np.fft.irfft2(F*H, s=(M, M))

t0 = time.time()
# ---- void and cluster ----
nmin = int(round(DENS*M*M))
P = np.zeros((M, M), dtype=np.int8)
idx = rng.choice(M*M, nmin, replace=False)
P.flat[idx] = 1
_, r = kernel(SIG_VC)
ax = np.arange(-r, r+1)
yy, xx = np.meshgrid(ax, ax, indexing='ij')
k2 = np.exp(-(xx**2+yy**2)/(2*SIG_VC*SIG_VC)); k2 /= k2.sum()
Km = np.zeros((M, M)); Km[:2*r+1, :2*r+1] = k2
Km = np.roll(Km, (-r, -r), axis=(0,1))
H = np.fft.rfft2(Km)

def energy(P):
    return np.fft.irfft2(np.fft.rfft2(P.astype(np.float64))*H, s=(M, M))

# The roll approach: Km is centered at (0,0). Removing a minority pixel at (y,x)
# subtracts Km shifted so its center lands on (y,x): np.roll(Km,(y,x)).
E = energy(P)
max_moves = 400000
moves = 0
while moves < max_moves:
    Emin = np.where(P == 1, E, -np.inf)
    flat_rm = int(np.argmax(Emin))
    ry, rx = flat_rm//M, flat_rm % M
    E = E - np.roll(Km, (ry, rx), axis=(0,1))
    P[ry, rx] = 0
    Emaj = np.where(P == 0, E, np.inf)
    flat_ad = int(np.argmin(Emaj))          # largest void
    ay, ax_ = flat_ad//M, flat_ad % M
    if flat_ad == flat_rm:
        # swap would undo itself -> converged; put pixel back
        P[ry, rx] = 1
        E = E + np.roll(Km, (ry, rx), axis=(0,1))
        break
    P[ay, ax_] = 1
    E = E + np.roll(Km, (ay, ax_), axis=(0,1))
    moves += 1
print(f"V&C converged-ish after {moves} moves in {time.time()-t0:.1f}s")
assert P.sum() == nmin

np.save(os.path.join(os.path.dirname(__file__), "mask136.npy"), P)

# ---- scale space states ----
UP = 5
S = M*UP
def upscale_bilinear(F):
    # 136 -> 680 bilinear with wrap
    big = np.zeros((S, S))
    ys = (np.arange(S)+0.5)/UP - 0.5
    xs = (np.arange(S)+0.5)/UP - 0.5
    y0 = np.floor(ys).astype(int); x0 = np.floor(xs).astype(int)
    fy = ys - y0; fx = xs - x0
    y0m = y0 % M; y1m = (y0+1) % M; x0m = x0 % M; x1m = (x0+1) % M
    top = F[np.ix_(y0m, x0m)]*(1-fx)[None, :] + F[np.ix_(y0m, x1m)]*fx[None, :]
    bot = F[np.ix_(y1m, x0m)]*(1-fx)[None, :] + F[np.ix_(y1m, x1m)]*fx[None, :]
    return top*(1-fy)[:, None] + bot*fy[:, None]

def thr45(F):
    t = np.quantile(F, 0.45, method='linear')
    return (F < t)

sigs = [0.0, 0.6, 1.0, 1.5, 2.2, 3.2, 4.6, 6.6, 9.5, 13.0]
for sg in sigs:
    F = P.astype(np.float64) if sg == 0 else conv2(P, sg)
    B = thr45(upscale_bilinear(F))
    cov = B.mean()
    img = Image.fromarray((~B*255).astype(np.uint8))  # wait: black=on -> 0
    img = Image.fromarray(np.where(B, 0, 255).astype(np.uint8))
    img.save(os.path.join(os.path.dirname(__file__), f"state_sig{sg:.1f}.png"))
    print(f"sigma={sg:5.1f} ink={cov:.4f}")
print("done")
