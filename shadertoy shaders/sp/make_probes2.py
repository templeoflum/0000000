#!/usr/bin/env python3
"""make_probes2.py — SP probes for text + textures, pilot standard.
SP Glyphmass: text-mass probe (tests the luma key, stands in for glyphs/logos).
              Slots: Size(0) · Reveal(1) · Weight(2) · Density(3)
SP Grain    : finish probe, texture a.  Slots: Amount(0) · Flicker(1, cyclic) · Grit(2) · Level(3)
SP Scan     : finish probe, texture b.  Slots: Count(0) · Phase(1, cyclic) · Duty(2) · Soft(3)"""
import sp_header as S

# ── SP Glyphmass ─────────────────────────────────────────────────────────────
S.CYC.clear()
GLY = [("tSize", "Size"), ("tReveal", "Reveal"), ("tWeight", "Weight"), ("tDensity", "Density")]
gin = list(S.ROOT)
gin += S.slot("tSize", "Size", default=0.4, drive=False)
gin += S.slot("tReveal", "Reveal", default=1.0, drive=True)
gin += S.slot("tWeight", "Weight", default=0.5)
gin += S.slot("tDensity", "Density", default=0.5)

gly_body = f"""
float spH1(float n) {{ return fract(sin(n) * 43758.5453); }}
void main() {{
    float H = TIME * heartRate;

    float SZ = {S.call("tSize", 0)};       // type size — the fundamental
    float RV = {S.call("tReveal", 1)};     // write-on in reading order, drivable
    float WT = {S.call("tWeight", 2)};     // stroke weight
    float DN = {S.call("tDensity", 3)};    // line fill / word density

    vec2 uv = gl_FragCoord.xy / RENDERSIZE.xy;

    // ── greeked paragraph: lines of words, x-height + ascenders/descenders, ragged right ──
    float lineH = 0.045 + SZ * 0.075;                       // line height incl leading
    float nL = clamp(floor(0.42 / lineH), 1.0, 8.0);        // block of lines, centered
    float yTop = 0.5 + nL * lineH * 0.5;
    float y = (yTop - uv.y) / lineH;
    float li = floor(y); float fy = fract(y);

    float cellW = lineH * 0.40;                             // glyph aspect
    float x = (uv.x - 0.08) / cellW;
    float ci = floor(x); float fx = fract(x);
    float cols = 0.84 / cellW;

    float v = 0.0;
    if (li >= 0.0 && li < nL && ci >= 0.0) {{
        float len = cols * (0.45 + 0.5 * spH1(li * 7.31)) * (0.55 + 0.45 * DN);   // ragged right
        if (li == nL - 1.0) len *= 0.6;                                            // short last line
        float space = step(0.86 - (1.0 - DN) * 0.12, spH1(li * 17.3 + ci));        // word gaps
        float g = spH1(li * 57.1 + ci * 9.7);
        float top = (g < 0.22) ? 0.10 : 0.34;               // some ascenders
        float bot = (g > 0.82) ? 0.94 : 0.78;               // some descenders, baseline 0.78
        float w = 0.35 + WT * 0.5;
        float ink = step(top, fy) * step(fy, bot) * step(abs(fx - 0.5), w * 0.5)
                  * (1.0 - space) * step(ci, len);
        float order = (li * cols + ci) / (nL * cols);       // reading order
        v = ink * step(order, RV + 0.0001);
    }}
    gl_FragColor = vec4(vec3(v), v);                        // white type, transparent page
}}
"""
print("wrote", S.emit("SP Glyphmass — text-mass probe for the luma-key layer. SMART PARAM v4.", "SP probe", gin, gly_body, "SP Glyphmass", S.groups(GLY)))

# ── SP Grain ─────────────────────────────────────────────────────────────────
S.CYC.clear()
GRN = [("aAmount", "Amount"), ("aFlicker", "Flicker"), ("aGrit", "Grit"), ("aLevel", "Level")]
ain = list(S.ROOT)
ain += S.slot("aAmount", "Amount", default=0.5, drive=False)
ain += S.slot("aFlicker", "Flicker", default=0.0, drive=True, cyclic=True)
ain += S.slot("aGrit", "Grit", default=0.3)
ain += S.slot("aLevel", "Level", default=0.5)

grain_body = f"""
float spH2(vec2 p) {{ return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453); }}
void main() {{
    float H = TIME * heartRate;

    float AM = {S.call("aAmount", 0)};     // how much grain — the fundamental
    float FL = {S.call("aFlicker", 1)};    // cyclic phase — drive = live grain
    float GR = {S.call("aGrit", 2)};       // fine ↔ chunky
    float LV = {S.call("aLevel", 3)};      // value center

    vec2 px = gl_FragCoord.xy / (1.0 + GR * 5.0);
    float n = spH2(floor(px) + floor(FL * 64.0) * 0.37);
    float dev = abs(n - 0.5) * 2.0;
    float a = step(1.0 - AM * 0.75, dev) * (0.25 + LV * 0.75);   // sparse speckles, transparent elsewhere
    float col = step(0.5, n);                                     // salt & pepper
    gl_FragColor = vec4(vec3(col) * a, a);
}}
"""
print("wrote", S.emit("SP Grain — finish probe: grain. SMART PARAM v4.", "SP probe", ain, grain_body, "SP Grain", S.groups(GRN)))

# ── SP Scan ──────────────────────────────────────────────────────────────────
S.CYC.clear()
SCN = [("bCount", "Count"), ("bPhase", "Phase"), ("bDuty", "Duty"), ("bSoft", "Soft")]
bin_ = list(S.ROOT)
bin_ += S.slot("bCount", "Count", default=0.4, drive=False)
bin_ += S.slot("bPhase", "Phase", default=0.0, drive=True, cyclic=True)
bin_ += S.slot("bDuty", "Duty", default=0.5)
bin_ += S.slot("bSoft", "Soft", default=0.3)

scan_body = f"""
void main() {{
    float H = TIME * heartRate;

    float CT = {S.call("bCount", 0)};      // line count — the fundamental
    float PH = {S.call("bPhase", 1)};      // cyclic — drive = scroll
    float DU = {S.call("bDuty", 2)};       // line thickness share
    float SO = {S.call("bSoft", 3)};       // edge softness

    float lines = 4.0 + floor(CT * 116.0);
    float y = fract(gl_FragCoord.y / RENDERSIZE.y * lines + PH);
    float hf = clamp(DU, 0.02, 0.98) * 0.5;
    float e = 0.01 + SO * 0.4;
    float v = smoothstep(0.5 - hf - e, 0.5 - hf, y) * (1.0 - smoothstep(0.5 + hf, 0.5 + hf + e, y));
    gl_FragColor = vec4(vec3(v), v);   // lines only, transparent between
}}
"""
print("wrote", S.emit("SP Scan — finish probe: scanlines. SMART PARAM v4.", "SP probe", bin_, scan_body, "SP Scan", S.groups(SCN)))
