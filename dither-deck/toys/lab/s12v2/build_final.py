#!/usr/bin/env python3
"""build_final.py — S12v2 final frames, plan (b): crisp cold-start keyframes
pinned at rail stops 0/4/8/12, warm-start bridges between, then native
upsample to 680^2 with a short relaxation so ridges sharpen at deck pitch
(LAM=14px, matched to the reference). square domain, no pad; ink = global
45th percentile (02's law). the whorl keyframe is pushed further developed
(core higher, deltas wider) so the rail ENDS somewhere.

resumable: every work unit checkpoints every CHUNK steps; call repeatedly
with a seconds budget until "ALL DONE".

usage: python build_final.py <budget_seconds> [only <kind>]
"""
import numpy as np
from PIL import Image
import os, sys, time, json

OUT = os.path.dirname(os.path.abspath(__file__))
SEED = 7
EPS, ALPHA, DT = 0.3, 0.25, 0.02
NSTOPS = 13
COLD_STEPS, BRIDGE_STEPS, RELAX_STEPS = 15000, 8000, 2000
CHUNK = 2000

KEY = [  # (core1, core2, deltaA, deltaB) as fractions of S, y down.
    # core2 rides exactly on deltaB through arch/tented/loop — zero over pole
    # cancels, no singularity — then separates at the whorl: two cores = the
    # composite +1 winding a true target whorl needs (one +1/2 core can only
    # ever make a recurve).
    [(0.50, 1.30), (1.05, 1.75), (-0.05, 1.75), (1.05, 1.75)],   # arch
    [(0.50, 1.00), (0.68, 0.90), (0.32, 0.90), (0.68, 0.90)],    # tented
    [(0.44, 0.58), (1.50, 2.60), (0.64, 0.98), (1.50, 2.60)],    # loop (delta B exits)
    [(0.47, 0.44), (0.53, 0.40), (0.10, 0.90), (0.90, 0.90)],    # whorl (two cores)
]
KEYSTOPS = {0: 0, 4: 1, 8: 2, 12: 3}   # stop -> KEY index

def lam(S): return 7.0 if S == 340 else 14.0

def charges_at(f):
    t = f / (NSTOPS - 1) * (len(KEY) - 1)
    i = min(int(t), len(KEY) - 2)
    u = t - i
    out = []
    for c in range(4):
        a, b = KEY[i][c], KEY[i + 1][c]
        out.append((a[0] * (1 - u) + b[0] * u, a[1] * (1 - u) + b[1] * u))
    return [out[0], out[1]], [out[2], out[3]]

def tensors_at(f, S):
    y, x = np.mgrid[0:S, 0:S].astype(float)
    z = x + 1j * y
    cores, deltas = charges_at(f)
    H = np.ones_like(z)
    for cx, cy in cores:
        H *= (z - cx * S - 1j * cy * S)
    for dx, dy in deltas:
        px, py = dx * S, dy * S
        if px == int(px): px += 0.5   # a delta exactly on a sample point
        if py == int(py): py += 0.5   # divides by zero and poisons the field
        H /= (z - px - 1j * py)
    d = H / (np.abs(H) + 1e-12)
    top = (int(S / 2), int(0.10 * S))
    th_top = 0.5 * np.angle(d[top[1], top[0]])
    d = d * np.exp(-2j * th_top)
    theta = 0.5 * np.angle(d)
    ct, st = np.cos(theta), np.sin(theta)
    return (ct * ct + ALPHA * st * st,
            st * st + ALPHA * ct * ct,
            (1 - ALPHA) * ct * st)

def make_anneal(axx, ayy, axy, S):
    q0sq = (2 * np.pi / lam(S)) ** 2
    def divAgrad(q):
        gx = np.roll(q, -1, 1) - q
        gy = np.roll(q, -1, 0) - q
        fx = axx * gx + axy * gy
        fy = axy * gx + ayy * gy
        return (fx - np.roll(fx, 1, 1)) + (fy - np.roll(fy, 1, 0))
    def step(p, n):
        for _ in range(n):
            b = divAgrad(p) + q0sq * p
            b = divAgrad(b) + q0sq * b
            p = p + DT * (EPS * p - b - p ** 3)
            np.clip(p, -5, 5, out=p)
        return p
    return step

def seed_field(kind, S):
    rng = np.random.default_rng(SEED)
    y, x = np.mgrid[0:S, 0:S].astype(float)
    if kind == "arch":    # stripe-leaning seed: relaxes into clean arches
        return 0.25 * np.cos(2 * np.pi / lam(S) * y) + 0.08 * rng.standard_normal((S, S))
    return 0.08 * rng.standard_normal((S, S))   # pure noise: defect soup, loop/whorl

# ---- work units -----------------------------------------------------------
def unit_path(tag): return f"{OUT}/final_{tag}.npz"
def done_path(tag): return f"{OUT}/final_{tag}.done"

UNITS = []
for stop, ki in sorted(KEYSTOPS.items()):
    UNITS.append(("cold", stop, "arch" if ki < 2 else "noise"))
for f in range(NSTOPS):
    if f not in KEYSTOPS:
        UNITS.append(("bridge", f, None))
for f in range(NSTOPS):
    UNITS.append(("up", f, None))

def unit_tag(u): return f"{u[0]}{u[1]:02d}"

def run_unit(u, budget_end):
    kind, f, seedkind = u
    tag = unit_tag(u)
    if kind == "up":
        S = 680
        src = np.load(unit_path(f"bridge{f:02d}" if f not in KEYSTOPS else f"cold{f:02d}"))["p"]
        p = np.array(Image.fromarray(src.astype(np.float32), "F").resize((S, S), Image.BICUBIC))
        total = RELAX_STEPS
    else:
        S = 340
        total = COLD_STEPS if kind == "cold" else BRIDGE_STEPS
        if os.path.exists(unit_path(tag)):
            p = np.load(unit_path(tag))["p"]
        elif kind == "cold":
            p = seed_field(seedkind, S)
        else:
            prev = f - 1
            prevtag = f"cold{prev:02d}" if prev in KEYSTOPS else f"bridge{prev:02d}"
            p = np.load(unit_path(prevtag))["p"]
    done0 = int(np.load(unit_path(tag))["steps"]) if os.path.exists(unit_path(tag)) else 0
    step = make_anneal(*tensors_at(f, S), S)
    chunk = 400 if kind == "up" else CHUNK
    while done0 < total:
        n = min(chunk, total - done0)
        p = step(p, n)
        done0 += n
        np.savez(unit_path(tag), p=p, steps=done0)
        print(f"  {tag}: {done0}/{total}", flush=True)
        if time.time() > budget_end:
            return False
    open(done_path(tag), "w").write("ok")
    return True

def finish_680(f):
    p = np.load(unit_path(f"up{f:02d}"))["p"]
    thr = np.sort(p.ravel())[int(0.45 * p.size)]
    bits = p < thr
    img = np.full((680, 680), 255, np.uint8)
    img[bits] = 0
    Image.fromarray(img).save(f"{OUT}/h{f:02d}.png")
    return bits.mean()

def main():
    budget = float(sys.argv[1]) if len(sys.argv) > 1 else 270
    only = sys.argv[sys.argv.index("only") + 1] if "only" in sys.argv else None
    budget_end = time.time() + budget

    for u in UNITS:
        if only and u[0] != only:
            continue
        if os.path.exists(done_path(unit_tag(u))):
            continue
        # dependency check
        kind, f, _ = u
        if kind == "bridge" and f - 1 not in KEYSTOPS and not os.path.exists(done_path(f"bridge{f-1:02d}")):
            continue
        if kind == "up":
            dep = f"cold{f:02d}" if f in KEYSTOPS else f"bridge{f:02d}"
            if not os.path.exists(done_path(dep)):
                continue
        print(f"unit {unit_tag(u)}", flush=True)
        if not run_unit(u, budget_end):
            print("budget exhausted, resume me", flush=True)
            return

    remaining = [u for u in UNITS if not os.path.exists(done_path(unit_tag(u)))]
    if not remaining:
        print("ALL DONE, finishing 680 pngs", flush=True)
        inks = [finish_680(f) for f in range(NSTOPS)]
        print("inks:", " ".join(f"{v:.3f}" for v in inks), flush=True)
        ims = [Image.open(f"{OUT}/h{f:02d}.png").resize((340, 340)) for f in range(NSTOPS)]
        M = Image.new("L", (340 * NSTOPS, 340), 128)
        for i, im in enumerate(ims):
            M.paste(im, (i * 340, 0))
        M.save(f"{OUT}/_final680.png")
        print("montage saved", flush=True)
    else:
        print("pending:", " ".join(unit_tag(u) for u in remaining), flush=True)

if __name__ == "__main__":
    main()
