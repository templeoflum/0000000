# M8 prototype: Gray-Scott reaction-diffusion advected by potential flow past a
# cylinder with circulation. Slider k = coupling strength c of the advection.
# Parents: S12 (flow field) x S13 (Gray-Scott coat).
import numpy as np
from PIL import Image
import os

OUT = os.path.dirname(os.path.abspath(__file__))

G = 224                      # S13's lattice
Du, Dv = 0.21, 0.105         # S13's diffusion pair
F, KK = 0.0545, 0.062        # Pearson spot regime (S13's values)
DT = 1.0
STEPS = 520                  # S13's mature-coat time

# --- S12's flow field on the lattice --------------------------------------
CX = CY = G / 2.0
R = 110.0 / 680.0 * G        # S12's core radius in lattice units (~36.2)
U0 = 1.0
ALPHA = -np.pi / 2           # vertical ruling, as S12
GAMMA_T = 0.6                # fixed circulation: deltas riding the flanks

yy, xx = np.mgrid[0:G, 0:G].astype(np.float64)
dx = xx - CX
dy = yy - CY
r = np.sqrt(dx * dx + dy * dy)
r = np.maximum(r, 1e-9)
th = np.arctan2(dy, dx)
GAM = GAMMA_T * 4 * np.pi * U0 * R     # S12's Gamma from Gamma-tilde
vr = U0 * np.cos(th - ALPHA) * (1 - R * R / (r * r))
vt = -U0 * np.sin(th - ALPHA) * (1 + R * R / (r * r)) + GAM / (2 * np.pi * r)
VX = vr * np.cos(th) - vt * np.sin(th)
VY = vr * np.sin(th) + vt * np.cos(th)
SOLID = r < R                # cylinder is solid: no reaction inside
VX[SOLID] = 0.0
VY[SOLID] = 0.0
VMAX = np.sqrt(VX**2 + VY**2).max()
print(f"R={R:.2f} cells, |v|max={VMAX:.3f} (U0=1 units)")

# --- Gray-Scott with upwind advection --------------------------------------
def lap9(a):
    return (0.2 * (np.roll(a, 1, 0) + np.roll(a, -1, 0) +
                   np.roll(a, 1, 1) + np.roll(a, -1, 1))
            + 0.05 * (np.roll(np.roll(a, 1, 0), 1, 1) +
                      np.roll(np.roll(a, 1, 0), -1, 1) +
                      np.roll(np.roll(a, -1, 0), 1, 1) +
                      np.roll(np.roll(a, -1, 0), -1, 1))
            - a)

def upwind(a, vx, vy):
    # first-order upwind for -(v.grad a), periodic
    axp = a - np.roll(a, 1, 1)     # a - a(x-1)
    axm = np.roll(a, -1, 1) - a    # a(x+1) - a
    ayp = a - np.roll(a, 1, 0)
    aym = np.roll(a, -1, 0) - a
    return np.where(vx >= 0, vx * axp, vx * axm) + \
           np.where(vy >= 0, vy * ayp, vy * aym)

def seed():
    rng = np.random.RandomState(42)
    u = np.ones((G, G))
    v = np.zeros((G, G))
    m = rng.rand(G, G) < 0.08      # S13's "8% static"
    u[m] = 0.5
    v[m] = 0.5
    return u, v

def run(c):
    u, v = seed()
    vx = c * VX
    vy = c * VY
    u[SOLID] = 1.0
    v[SOLID] = 0.0
    for t in range(STEPS):
        uvv = u * v * v
        u += DT * (Du * lap9(u) - uvv + F * (1 - u) - upwind(u, vx, vy))
        v += DT * (Dv * lap9(v) + uvv - (F + KK) * v - upwind(v, vx, vy))
        np.clip(u, 0, 1, out=u)
        np.clip(v, 0, 1, out=v)
        u[SOLID] = 1.0
        v[SOLID] = 0.0
    return v

def cut(field, pct):
    thr = np.percentile(field, pct)
    return (field >= thr).astype(np.uint8), 1 - (field < thr).mean()

if __name__ == "__main__":
    import sys
    cmax = float(sys.argv[1]) if len(sys.argv) > 1 else 0.30
    NSTOP = int(sys.argv[2]) if len(sys.argv) > 2 else 12
    cs = np.linspace(0, cmax, NSTOP)
    PCT = float(sys.argv[3]) if len(sys.argv) > 3 else 74.0
    stops = []
    for c in cs:
        field = run(c)
        b, ink = cut(field, PCT)
        stops.append(b)
        print(f"c={c:.3f}  ink={ink:.3f}")
    # renders
    scale = 3
    for i, b in enumerate(stops):
        img = Image.fromarray((1 - b) * 255).resize((G * scale, G * scale), Image.NEAREST)
        img.save(os.path.join(OUT, f"stop{i:02d}_c{cs[i]:.3f}.png"))
    # journey strip
    strip = np.concatenate([(1 - b) * 255 for b in stops], axis=1).astype(np.uint8)
    Image.fromarray(strip).resize((G * NSTOP, G), Image.NEAREST).save(os.path.join(OUT, "journey.png"))
    # flip fractions between adjacent stops
    diffs = [float(np.mean(stops[i] != stops[i + 1])) for i in range(NSTOP - 1)]
    per_step = [d * (NSTOP - 1) / 200 for d in diffs]
    print("inter-stop flip:", ["%.3f" % d for d in diffs])
    print("worst flip per 1/200 k-step: %.4f (limit ~0.025)" % max(per_step))
