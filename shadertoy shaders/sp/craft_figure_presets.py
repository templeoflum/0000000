#!/usr/bin/env python3
"""craft_figure_presets.py — six crafted flavors for Figure 2D SP (L5C1), saved to pads 1-6.
FOLDED 8-slot contract: Size X Y Turn Outline Material Float Spin.
Material: fog → soft pillow → hard inked solid (edge/emboss/stroke inside).
Float: grounded → seated → airborne (contact shadow rises then lifts; drop grows).
Spin: one cyclic phase tumbling both planes on the diagonal axis.
Sets Arena-side slot config by param id, engine-side drives/manuals over the surface socket,
then asks the engine to capture each state as a preset. Re-run any time the clip is fresh.
  1 Anchor      — calm breathing pillow, face-on, grounded
  2 Orbit       — the wanderer: lissajous roam, floats up and lands
  3 Coin Flip   — the perspective show: diagonal tumble, vanish beats on the half clock
  4 Ghost       — pale apparition: Material breathes in the fog range, no ink ever
  5 Machine     — machined part: aperture cycling open/closed while rotating, hard and precise
  6 Chaos Bloom — full dance: everything driven wide on irrational clocks, never repeats"""
import json, time, asyncio, urllib.request, websockets

BASE = "http://localhost:8080/api/v1"
L, C = 5, 1

cj = json.load(urllib.request.urlopen(f"{BASE}/composition/layers/{L}/clips/{C}"))
sp = cj["video"]["sourceparams"]
ids = {k: v["id"] for k, v in sp.items()}

def put(name, val):
    req = urllib.request.Request(f"{BASE}/parameter/by-id/{ids[name]}",
        data=json.dumps({"value": val}).encode(), method="PUT", headers={"Content-Type": "application/json"})
    urllib.request.urlopen(req, timeout=2).read()

SLOTS = ["Size", "X", "Y", "Turn", "Outline", "Material", "Float", "Spin"]

# slot spec: (drive, manual, ratio, mult, offset, shape, lo, hi) — None = leave as is
def S(drive, manual=None, ratio=None, mult=None, offset=None, shape=None, lo=None, hi=None):
    return {"drive": drive, "manual": manual, "Ratio": ratio, "Mult": mult, "Offset": offset,
            "Shape": shape, "Lo": lo, "Hi": hi}

PRESETS = [
 (1, "Anchor", {"Pattern": "per-slot", "Seed": "0", "Spread": "1", "Depth": 1.0, "FM": 0.0}, {
    "Size":     S(True, ratio="1:4", shape="cosine", lo=0.38, hi=0.48, mult=1.0, offset=0.0),
    "X":        S(False, manual=0.5), "Y": S(False, manual=0.5),
    "Turn":     S(True, ratio="1:4", shape="rotate", mult=1.0, offset=0.0),
    "Outline":  S(True, ratio="1:2", shape="cosine", lo=0.0, hi=0.7, mult=1.0, offset=0.25),
    "Material": S(True, ratio="1:4", shape="cosine", lo=0.7, hi=0.95, mult=1.0, offset=0.5),
    "Float":    S(False, manual=0.25),
    "Spin":     S(False, manual=0.0)}),
 (2, "Orbit", {"Pattern": "fibonacci", "Seed": "3", "Spread": "2", "Depth": 1.0, "FM": 0.15}, {
    "Size":     S(True, lo=0.20, hi=0.45), "X": S(True, lo=0.05, hi=0.95), "Y": S(True, lo=0.05, hi=0.95),
    "Turn":     S(True, shape="rotate", mult=1.0, offset=0.0),
    "Outline":  S(False, manual=0.0),
    "Material": S(False, manual=0.6),
    "Float":    S(True, lo=0.0, hi=0.85),
    "Spin":     S(False, manual=0.0)}),
 (3, "Coin Flip", {"Pattern": "per-slot", "Seed": "0", "Spread": "1", "Depth": 1.0, "FM": 0.0}, {
    "Size":     S(False, manual=0.55),
    "X":        S(True, ratio="1:1", shape="cosine", lo=0.45, hi=0.55),
    "Y":        S(True, ratio="1:2", shape="cosine", lo=0.45, hi=0.55),
    "Turn":     S(False, manual=0.08), "Outline": S(False, manual=0.0),
    "Material": S(False, manual=0.9),
    "Float":    S(False, manual=0.45),
    "Spin":     S(True, ratio="1:2", shape="rotate", mult=1.0, offset=0.0)}),
 (4, "Ghost", {"Pattern": "near-unison", "Seed": "1", "Spread": "1", "Depth": 1.0, "FM": 0.0}, {
    "Size":     S(True, lo=0.50, hi=0.78), "X": S(True, lo=0.20, hi=0.80), "Y": S(True, lo=0.25, hi=0.75),
    "Turn":     S(False, manual=0.03), "Outline": S(False, manual=0.0),
    "Material": S(True, lo=0.02, hi=0.35),
    "Float":    S(False, manual=0.0),
    "Spin":     S(True, shape="sway", lo=0.44, hi=0.56)}),
 (5, "Machine", {"Pattern": "per-slot", "Seed": "0", "Spread": "1", "Depth": 1.0, "FM": 0.0}, {
    "Size":     S(False, manual=0.45),
    "X":        S(True, ratio="3:4", shape="cosine", lo=0.38, hi=0.62),
    "Y":        S(True, ratio="4:5", shape="cosine", lo=0.38, hi=0.62),
    "Turn":     S(True, ratio="1:1", shape="rotate", mult=1.0),
    "Outline":  S(True, ratio="2:3", shape="cosine", lo=0.15, hi=0.95),
    "Material": S(False, manual=0.95),
    "Float":    S(False, manual=0.3),
    "Spin":     S(False, manual=0.0)}),
 (6, "Chaos Bloom", {"Pattern": "irrationals", "Seed": "5", "Spread": "3", "Depth": 1.0, "FM": 0.45}, {
    "Size":     S(True, lo=0.10, hi=0.80), "X": S(True, lo=0.0, hi=1.0), "Y": S(True, lo=0.0, hi=1.0),
    "Turn":     S(True, shape="rotate", mult=2.0),
    "Outline":  S(True, lo=0.0, hi=1.0),
    "Material": S(True, lo=0.20, hi=1.0),
    "Float":    S(True, lo=0.0, hi=1.0),
    "Spin":     S(True, shape="rotate", mult=1.0)}),
]

async def main():
    async with websockets.connect("ws://localhost:8766/") as ws:
        async def cmd(o):
            o.update({"layer": L, "col": C}); await ws.send(json.dumps(o)); await asyncio.sleep(0.03)
        for pad, name, gl, slots in PRESETS:
            for k, v in gl.items(): put(k, v)
            for sl, cfg in slots.items():
                for suf, v in cfg.items():
                    if v is None: continue
                    if suf == "drive": await cmd({"cmd": "drive", "slot": sl, "on": v})
                    elif suf == "manual": await cmd({"cmd": "manual", "slot": sl, "value": v})
                    else: put(f"{sl} {suf}", v)
            await asyncio.sleep(1.2)                    # let the engine's refresh absorb the config
            await cmd({"cmd": "preset_save", "pad": pad})
            await asyncio.sleep(0.6)
            print(f"pad {pad}  {name}  saved")

asyncio.run(main())
