/* standalone bench of toy 22's inner loop, no DOM */
const S = 680, N = S * S;
const P = 34, SIG = 0.24, SIG2 = 2 * SIG * SIG;
const GT = new Float32Array(1025);
for (let i = 0; i <= 1024; i++) GT[i] = Math.exp(-(i / 2048) / SIG2);
const XC = new Float32Array(N), YC = new Float32Array(N);
for (let y = 0; y < S; y++) for (let x = 0; x < S; x++) { XC[y * S + x] = x - S / 2; YC[y * S + x] = y - S / 2; }
const L3 = new Float32Array(N).fill(0.5);
const F = new Float32Array(N);
const img = { data: new Uint8ClampedArray(N * 4) };
const hist = new Uint32Array(2049);

function apply(k) {
  const dth = 30 * k * Math.PI / 180;
  const w = k <= 0.72 ? 0 : (k - 0.72) / (1 - 0.72);
  const a1 = Math.PI / 4 + dth / 2, a2 = Math.PI / 4 - dth / 2;
  const c1 = Math.cos(a1) / P, s1 = Math.sin(a1) / P;
  const c2 = Math.cos(a2) / P, s2 = Math.sin(a2) / P;
  for (let i = 0; i < N; i++) {
    const px = XC[i], py = YC[i];
    let u = px * c1 + py * s1, v = -px * s1 + py * c1;
    let du = u - Math.floor(u + 0.5), dv = v - Math.floor(v + 0.5);
    let g = ((du * du + dv * dv) * 2048) | 0; if (g > 1024) g = 1024;
    const l1 = GT[g];
    u = px * c2 + py * s2; v = -px * s2 + py * c2;
    du = u - Math.floor(u + 0.5); dv = v - Math.floor(v + 0.5);
    g = ((du * du + dv * dv) * 2048) | 0; if (g > 1024) g = 1024;
    let L = l1 * GT[g];
    if (w > 0) L *= (1 - w) + w * L3[i];
    F[i] = L;
  }
  hist.fill(0);
  for (let i = 0; i < N; i++) { let q = (F[i] * 2048) | 0; if (q < 0) q = 0; if (q > 2048) q = 2048; hist[q]++; }
  const target = N * 0.45; let acc = 0, thr = 0;
  for (let q = 2048; q >= 0; q--) { acc += hist[q]; if (acc >= target) { thr = (q - 0.5) / 2048; break; } }
  const d = img.data;
  for (let i = 0; i < N; i++) {
    const on = F[i] >= thr;
    const v = on ? 0 : 255, j = i * 4;
    d[j] = v; d[j + 1] = v; d[j + 2] = v; d[j + 3] = 255;
  }
}

apply(0.3); apply(0.3);   // warmup
for (const k of [0.05, 0.5, 0.9]) {
  const ts = [];
  for (let r = 0; r < 5; r++) { const a = Date.now(); apply(k); ts.push(Date.now() - a); }
  console.log('k=' + k, ts.join(' '));
}
