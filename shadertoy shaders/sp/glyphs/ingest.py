#!/usr/bin/env python3
"""ingest.py — real writing systems as stroke data, one corpus file we own: glyphs/systems.json
Sources: Hershey vector fonts (public domain; Dr A. V. Hershey, NBS; James Hurt's .jhf packing) for Latin (simplex,
duplex-serif Times, gothic English, cursive), Greek, Cyrillic, Japanese kana/kanji; Make Me a Hanzi stroke MEDIANS
(Arphic PL fonts, Arphic Public License) for Chinese; Elder Futhark and Ogham encoded from their tables (straight
strokes). Each glyph: label + strokes (polylines) in a box where the system's cap height = 1, baseline y = 0, y up."""
import json, os, re, unicodedata
RAW = os.path.join(os.path.dirname(os.path.abspath(__file__)), "raw")
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "systems.json")

def read_jhf(path):
    """Hershey .jhf: 5-char id, 3-char pair count, then pairs; first pair = left/right; ' R' = pen up. Lines may wrap."""
    glyphs = []; buf = ""
    for line in open(path, encoding="latin-1").read().split("\n"):
        if not line: continue
        if re.match(r"^\s*\d+\s*\d+[A-Z\[\]\\^_`]", line) and len(line) >= 10 and buf == "": buf = line
        elif re.match(r"^\s*\d{1,5}\s*\d{1,3}", line[:10]) and buf and (len(buf) - 8) // 2 >= int(buf[5:8]):
            glyphs.append(buf); buf = line
        else: buf += line
    if buf: glyphs.append(buf)
    out = []
    for gl in glyphs:
        try: gid = int(gl[0:5]); n = int(gl[5:8])
        except ValueError: continue
        data = gl[8:8 + 2 * n]
        if len(data) < 2 * n: continue
        lm = ord(data[0]) - ord("R"); rm = ord(data[1]) - ord("R")
        strokes = []; cur = []
        for i in range(1, n):
            a, b = data[2 * i], data[2 * i + 1]
            if a == " " and b == "R":
                if cur: strokes.append(cur); cur = []
                continue
            x = ord(a) - ord("R"); y = -(ord(b) - ord("R"))          # Hershey y is down; flip to y up
            cur.append([x, y])
        if cur: strokes.append(cur)
        out.append({"id": gid, "lm": lm, "rm": rm, "strokes": strokes})
    return out

def norm(strokes, cap=21.0, base=-9.0, scale=None):
    """Hershey: baseline y=-9 (R row 9 down), cap height ~ 21 units above → map baseline 0, cap 1."""
    s = scale or (1.0 / cap)
    return [[[round((x) * s, 4), round((y - base) * s, 4)] for x, y in st] for st in strokes]

systems = {}
def add_font(key, name, fname, labels=None, first=0, count=None, note=""):
    g = read_jhf(os.path.join(RAW, fname))
    g = g[first:(first + count) if count else None]
    gl = []
    for i, e in enumerate(g):
        if not e["strokes"]: continue
        lab = labels[i] if labels and i < len(labels) else str(e["id"])
        gl.append({"label": lab, "strokes": norm(e["strokes"]), "adv": round((e["rm"] - e["lm"]) / 21.0, 4)})
    systems[key] = {"name": name, "source": f"Hershey {fname}", "note": note, "glyphs": gl}
    print(key, len(gl))

ascii_labels = [chr(c) for c in range(32, 127)]
add_font("latin_simplex", "Latin, Roman simplex (Hershey)", "rowmans.jhf", ascii_labels, note="single-stroke sans")
add_font("latin_times", "Latin, Times roman (Hershey duplex)", "timesr.jhf", ascii_labels, note="serifed, doubled strokes")
add_font("latin_gothic", "Latin, Gothic English (Hershey)", "gothiceng.jhf", ascii_labels, note="blackletter")
add_font("latin_cursive", "Latin, cursive (Hershey)", "cursive.jhf", ascii_labels, note="hand script")
add_font("greek", "Greek (Hershey)", "greek.jhf", ascii_labels, note="Greek in ASCII slots")
add_font("cyrillic", "Cyrillic (Hershey)", "cyrilc_1.jhf", ascii_labels, note="Cyrillic in ASCII slots")
add_font("japanese", "Japanese kana + kanji (Hershey)", "japanese.jhf", note="Hershey oriental set")
add_font("symbols", "Symbols, astrology (Hershey)", "astrology.jhf", note="zodiac / planets")

# Chinese: Make Me a Hanzi medians (stroke centrelines, 1024-unit em, y up with baseline offset)
hz = []
with open(os.path.join(RAW, "makemeahanzi_graphics.txt"), encoding="utf-8") as f:
    for i, line in enumerate(f):
        d = json.loads(line); ch = d["character"]
        if unicodedata.category(ch)[0] != "L": continue
        med = d["medians"]
        hz.append({"label": ch, "strokes": [[[round(x / 1024.0, 4), round((y + 124) / 1024.0, 4)] for x, y in st] for st in med], "adv": 1.0})
        if len(hz) >= 1200: break
systems["hanzi"] = {"name": "Chinese hanzi (Make Me a Hanzi medians)", "source": "skishore/makemeahanzi graphics.txt", "note": "stroke medians in writing order; first 1200 entries", "glyphs": hz}
print("hanzi", len(hz))

# Elder Futhark: 24 runes, straight strokes on a stave, box x 0..0.6, y 0..1 (encoded from the standard forms)
F = {}
def rune(name, ch, *strokes): F[name] = (ch, [list(map(list, s)) for s in strokes])
rune("fehu", "ᚠ", [(0,0),(0,1)], [(0,1),(0.5,0.75)], [(0,0.7),(0.5,0.45)])
rune("uruz", "ᚢ", [(0,0),(0,1)], [(0,1),(0.5,0.7)], [(0.5,0.7),(0.5,0)])
rune("thurisaz", "ᚦ", [(0,0),(0,1)], [(0,0.8),(0.45,0.5)], [(0.45,0.5),(0,0.2)])
rune("ansuz", "ᚨ", [(0,0),(0,1)], [(0,1),(0.5,0.7)], [(0,0.7),(0.5,0.4)])
rune("raido", "ᚱ", [(0,0),(0,1)], [(0,1),(0.45,0.75)], [(0.45,0.75),(0,0.5)], [(0,0.5),(0.45,0)])
rune("kenaz", "ᚲ", [(0.45,1),(0,0.5)], [(0,0.5),(0.45,0)])
rune("gebo", "ᚷ", [(0,0.15),(0.55,0.85)], [(0,0.85),(0.55,0.15)])
rune("wunjo", "ᚹ", [(0,0),(0,1)], [(0,1),(0.45,0.75)], [(0.45,0.75),(0,0.5)])
rune("hagalaz", "ᚺ", [(0,0),(0,1)], [(0.55,0),(0.55,1)], [(0,0.6),(0.55,0.4)])
rune("naudiz", "ᚾ", [(0.25,0),(0.25,1)], [(0,0.4),(0.5,0.6)])
rune("isa", "ᛁ", [(0,0),(0,1)])
rune("jera", "ᛃ", [(0.05,0.9),(0.35,0.6)], [(0.35,0.6),(0.05,0.3)], [(0.55,0.1),(0.25,0.4)], [(0.25,0.4),(0.55,0.7)])
rune("eihwaz", "ᛇ", [(0.25,0),(0.25,1)], [(0.25,1),(0,0.85)], [(0.25,0),(0.5,0.15)])
rune("perthro", "ᛈ", [(0,0),(0,1)], [(0,1),(0.45,0.85)], [(0.45,0.85),(0.15,0.6)], [(0.15,0.4),(0.45,0.15)], [(0.45,0.15),(0,0)])
rune("algiz", "ᛉ", [(0.3,0),(0.3,1)], [(0.3,0.55),(0,0.9)], [(0.3,0.55),(0.6,0.9)])
rune("sowilo", "ᛊ", [(0.5,1),(0,0.65)], [(0,0.65),(0.5,0.35)], [(0.5,0.35),(0,0)])
rune("tiwaz", "ᛏ", [(0.3,0),(0.3,1)], [(0.3,1),(0,0.75)], [(0.3,1),(0.6,0.75)])
rune("berkanan", "ᛒ", [(0,0),(0,1)], [(0,1),(0.45,0.8)], [(0.45,0.8),(0,0.5)], [(0,0.5),(0.45,0.2)], [(0.45,0.2),(0,0)])
rune("ehwaz", "ᛖ", [(0,0),(0,1)], [(0,1),(0.3,0.6)], [(0.3,0.6),(0.6,1)], [(0.6,1),(0.6,0)])
rune("mannaz", "ᛗ", [(0,0),(0,1)], [(0.6,0),(0.6,1)], [(0,1),(0.6,0.55)], [(0.6,1),(0,0.55)])
rune("laguz", "ᛚ", [(0,0),(0,1)], [(0,1),(0.45,0.6)])
rune("ingwaz", "ᛜ", [(0.3,1),(0,0.5)], [(0,0.5),(0.3,0)], [(0.3,0),(0.6,0.5)], [(0.6,0.5),(0.3,1)])
rune("dagaz", "ᛞ", [(0,0),(0,1)], [(0.6,0),(0.6,1)], [(0,1),(0.6,0)], [(0,0),(0.6,1)])
rune("othala", "ᛟ", [(0.3,1),(0,0.6)], [(0,0.6),(0.3,0.2)], [(0.3,0.2),(0.6,0.6)], [(0.6,0.6),(0.3,1)], [(0.3,0.2),(0,0)], [(0.3,0.2),(0.6,0)])
systems["futhark"] = {"name": "Elder Futhark (24 runes)", "source": "encoded from the standard forms", "note": "straight strokes, no horizontals",
    "glyphs": [{"label": f"{ch} {n}", "strokes": st, "adv": 0.9} for n, (ch, st) in F.items()]}
# Ogham: 20 feda on a stem: aicme B right, H left, M across diagonal, A across short
og = []
names = [("B",1),("L",2),("F",3),("S",4),("N",5),("H",1),("D",2),("T",3),("C",4),("Q",5),("M",1),("G",2),("NG",3),("Z",4),("R",5),("A",1),("O",2),("U",3),("E",4),("I",5)]
for k, (lab, n) in enumerate(names):
    aic = k // 5; st = [[[0.3, 0.0], [0.3, 1.0]]]
    for i in range(n):
        y = 0.85 - (i + 0.5) * (0.7 / n)
        if aic == 0: st.append([[0.3, y], [0.6, y]])
        elif aic == 1: st.append([[0.0, y], [0.3, y]])
        elif aic == 2: st.append([[0.05, y - 0.08], [0.55, y + 0.08]])
        else: st.append([[0.15, y], [0.45, y]])
    og.append({"label": f"ᚁ {lab}", "strokes": st, "adv": 0.9})
systems["ogham"] = {"name": "Ogham (20 feda)", "source": "encoded from the aicmí tables", "note": "count × side on a stem", "glyphs": og}
json.dump(systems, open(OUT, "w"), ensure_ascii=False)
print("wrote", OUT, sum(len(v["glyphs"]) for v in systems.values()), "glyphs")
