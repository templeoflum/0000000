# FINAL ladder for M8: gel-coupled Gray-Scott x S12 flow, 13 stops, bitpack to JS.
import numpy as np
from PIL import Image
import os, base64, json

OUT = os.path.dirname(os.path.abspath(__file__))

G = 224
Du, Dv = 0.21, 0.105
F, KK = 0.0545, 0.062
DT = 1.0

CX = CY = G / 2.0
R = 110.0 / 680.0 * G
U0 = 1.0
ALPHA = -np.pi / 2
GAMMA_T = 0.6
VCAP = 2.2                     # cap |v| near the core skin: keeps CFL <= 1 at c<=0.45

yy, xx = np.mgrid[0:G, 0:G].astype(np.float64)
dx = xx - CX; dy = yy - CY
r = np.maximum(np.sqrt(dx * dx + dy * dy), 1e-9)
th = np.arctan2(dy, dx)
GAM = GAMMA_T * 4 * np.pi * U0 * R
vr = U0 * np.cos(th - ALPHA) * (1 - R * R / (r * r))
vt = -U0 * np.sin(th - ALPHA) * (1 + R * R / (r * r)) + GAM / (2 * np.pi * r)
VX = vr * np.cos(th) - vt * np.sin(th)
VY = vr * np.sin(th) + vt * np.cos(th)
SOLID = r < R
mag = np.sqrt(VX**2 + VY**2)
sc = np.minimum(1.0, VCAP / np.maximum(mag, 1e-9))
VX *= sc; VY *= sc
VX[SOLID] = 0.0; VY[SOLID] = 0.0
VMAX = float(np.sqrt(VX**2 + VY**2).max())
print(f"VMAX(capped)={VMAX:.3f}  CFL at c=0.45: {0.45*VMAX:.3f}")

def lap9(a):
    return (0.2 * (np.roll(a, 1, 0) + np.roll(a, -1, 0) +
                   np.roll(a, 1, 1) + np.roll(a, -1, 1))
            + 0.05 * (np.roll(np.roll(a, 1, 0), 1, 1) +
                      np.roll(np.roll(a, 1, 0), -1, 1) +
                      np.roll(np.roll(a, -1, 0), 1, 1) +
                      np.roll(np.roll(a, -1, 0), -1, 1))
            - a)

def upwind(a, vx, vy):
    axp = a - np.roll(a, 1, 1); axm = np.roll(a, -1, 1) - a
    ayp = a - np.roll(a, 1, 0); aym = np.roll(a, -1, 0) - a
    return np.where(vx >= 0, vx * axp, vx * axm) + np.where(vy >= 0, vy * ayp, vy * aym)

def run(c, steps):
    rng = np.random.RandomState(42)
    u = np.ones((G, G)); v = np.zeros((G, G))
    m = rng.rand(G, G) < 0.08
    u[m] = 0.5; v[m] = 0.5
    vx, vy = c * VX, c * VY
    u[SOLID] = 1.0; v[SOLID] = 0.0
    for t in range(steps):
        uvv = u * v * v
        u += DT * (Du * lap9(u) - uvv + F * (1 - u))
        v += DT * (Dv * lap9(v) + uvv - (F + KK) * v - upwind(v, vx, vy))
        np.clip(u, 0, 1, out=u); np.clip(v, 0, 1, out=v)
        u[SOLID] = 1.0; v[SOLID] = 0.0
    return v

STOPS = [0.0, 0.025, 0.05, 0.075, 0.10, 0.13, 0.16, 0.20, 0.24, 0.28, 0.33, 0.39, 0.45]
TIMES = [520] + [700] * (len(STOPS) - 1)

frames = []
for c, T in zip(STOPS, TIMES):
    v = run(c, T)
    thr = np.percentile(v, 74.0)
    b = (v >= thr).astype(np.uint8)     # 1 = ink
    ink = float(b.mean())
    frames.append(b)
    Image.fromarray((1 - b) * 255).resize((G * 3, G * 3), Image.NEAREST).save(
        os.path.join(OUT, f"F_c{c:.3f}.png"))
    print(f"c={c:.3f} t={T} ink={ink:.4f}")

diffs = [float(np.mean(frames[i] != frames[i + 1])) for i in range(len(frames) - 1)]
worst = max(diffs) * (len(frames) - 1) / 200
print("inter-stop flips:", ["%.3f" % d for d in diffs])
print("worst flip per 1/200 k-step: %.4f" % worst)

strip = np.concatenate([(1 - b) * 255 for b in frames], axis=1).astype(np.uint8)
Image.fromarray(strip).resize((G * len(frames) * 2, G * 2), Image.NEAREST).save(
    os.path.join(OUT, "journey_final.png"))

# bitpack MSB-first, base64, as S13 does
packed = []
for b in frames:
    by = np.packbits(b.flatten())
    packed.append(base64.b64encode(by.tobytes()).decode())
with open(os.path.join(OUT, "frames.json"), "w") as f:
    json.dump({"G": G, "stops": STOPS, "times": TIMES, "frames": packed}, f)
print("frames.json written, KB:", sum(len(p) for p in packed) // 1024)
