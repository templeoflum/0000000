# S17 ADVECT — optimized offline prototype (per-stop runner, continuation via npz)
import numpy as np, sys, time, os
from PIL import Image

G = 340
Du, Dv = 0.21, 0.105
F, kK = 0.0545, 0.062
DT = 1.0
LAB = rf"C:\Users\User\Documents\0000000\dither-deck\toys\lab\17"

# ---- S12's flow field (cylinder + circulation, whorl, vertical stream)
R = 55.0; U = 1.0; GT = 1.0
G2v = GT * 2 * U * R
yy, xx = np.mgrid[0:G, 0:G].astype(np.float64)
dx = xx - G / 2 + 0.5; dy = yy - G / 2 + 0.5
r = np.hypot(dx, dy); th = np.arctan2(dy, dx)
ALPHA = -np.pi / 2
thr_ = th - ALPHA
outside = r >= R
vr = np.zeros_like(r); vt = np.zeros_like(r)
vr[outside] = U * np.cos(thr_[outside]) * (1 - R * R / r[outside] ** 2)
vt[outside] = -U * np.sin(thr_[outside]) * (1 + R * R / r[outside] ** 2) - G2v / r[outside]
vx = vr * np.cos(th) - vt * np.sin(th)
vy = vr * np.sin(th) + vt * np.cos(th)
spd = np.hypot(vx, vy)
tx = np.where(spd > 1e-3, vx / np.maximum(spd, 1e-12), -np.sin(th)).astype(np.float32)
ty = np.where(spd > 1e-3, vy / np.maximum(spd, 1e-12), np.cos(th)).astype(np.float32)

def tensors(rho, D0):
    Dxx = (D0 * (1 - rho + rho * tx * tx)).astype(np.float32)
    Dxy = (D0 * rho * tx * ty).astype(np.float32)
    Dyy = (D0 * (1 - rho + rho * ty * ty)).astype(np.float32)
    Dxxf = 0.5 * (Dxx + np.roll(Dxx, -1, axis=1))
    Dxyf = 0.5 * (Dxy + np.roll(Dxy, -1, axis=1))
    Dxyg = 0.5 * (Dxy + np.roll(Dxy, -1, axis=0))
    Dyyg = 0.5 * (Dyy + np.roll(Dyy, -1, axis=0))
    return Dxxf, Dxyf, Dxyg, Dyyg

def aniso_lap(c, T):
    Dxxf, Dxyf, Dxyg, Dyyg = T
    gx = np.roll(c, -1, axis=1) - c
    gy_xf = 0.25 * (np.roll(c, (-1, 0), (0, 1)) - np.roll(c, (1, 0), (0, 1))
                    + np.roll(c, -1, axis=0) - np.roll(c, 1, axis=0))
    Fx = Dxxf * gx + Dxyf * gy_xf
    gy = np.roll(c, -1, axis=0) - c
    gx_yf = 0.25 * (np.roll(c, (0, -1), (0, 1)) - np.roll(c, (0, 1), (0, 1))
                    + np.roll(c, -1, axis=1) - np.roll(c, 1, axis=1))
    Fy = Dxyg * gx_yf + Dyyg * gy
    return (Fx - np.roll(Fx, 1, axis=1)) + (Fy - np.roll(Fy, 1, axis=0))

def run(u, v, rho, steps):
    Tu = tensors(rho, Du); Tv = tensors(rho, Dv)
    for _ in range(steps):
        uvv = u * v * v
        u += DT * (aniso_lap(u, Tu) - uvv + F * (1 - u))
        v += DT * (aniso_lap(v, Tv) + uvv - (F + kK) * v)
    return u, v

def seed(u, v):
    rng = np.random.default_rng(17)
    v[:] = np.where(rng.random((G, G)) < 0.08, 0.5, 0.0)
    u[:] = 1.0 - 0.5 * v

def show(v, name, ink=0.45):
    thr = np.quantile(v, 1 - ink)
    b = v >= thr
    Image.fromarray((~b * 255).astype(np.uint8)).save(os.path.join(LAB, name + ".png"))
    print(f"{name}: coverage={b.mean():.4f}")
    return b

if __name__ == "__main__":
    rho = float(sys.argv[1]); steps = int(sys.argv[2])
    state = os.path.join(LAB, "state.npz")
    if os.path.exists(state):
        z = np.load(state); u = z["u"]; v = z["v"]
        print(f"continuing from saved state")
    else:
        u = np.ones((G, G), np.float32); v = np.zeros((G, G), np.float32); seed(u, v)
    t0 = time.time()
    u, v = run(u, v, rho, steps)
    np.savez(state, u=u, v=v)
    b = show(v, f"rho{rho:.2f}")
    np.save(os.path.join(LAB, f"bits_rho{rho:.2f}.npy"), b)
    print(f"rho={rho} steps={steps} elapsed={time.time()-t0:.1f}s")
