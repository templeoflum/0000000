# End-to-end verification of toys/m8.html in headless chromium:
# ink per state, 200-step granularity sweep, screenshots.
import os, sys
from playwright.sync_api import sync_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
TOY = os.path.join(os.path.dirname(os.path.dirname(HERE)), "m8.html")
url = "file:///" + TOY.replace("\\", "/")

SNAP = """
() => {
  const c = document.getElementById('scene');
  const x = c.getContext('2d');
  const d = x.getImageData(0, 0, c.width, c.height).data;
  const a = new Uint8Array(c.width * c.height);
  for (let i = 0; i < a.length; i++) a[i] = d[i * 4] ? 0 : 1;
  window.__last = a;
  let black = 0;
  for (let i = 0; i < a.length; i++) black += a[i];
  return black / a.length;
}
"""

with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": 800, "height": 900})
    pg.goto(url)
    pg.wait_for_timeout(400)

    inks = {}
    for k in [0, 0.25, 0.5, 0.75, 1.0]:
        pg.evaluate(f"window.atom.set({k})")
        pg.wait_for_timeout(120)
        ink = pg.evaluate(SNAP)
        inks[k] = ink
        pg.locator("#scene").screenshot(path=os.path.join(HERE, f"web_k{int(k*100):03d}.png"))
        print(f"k={k:.2f} ink={ink:.4f}")

    # granularity: full 200-step sweep, measure flips between successive states
    pg.evaluate("window.atom.set(0)")
    pg.wait_for_timeout(100)
    pg.evaluate(SNAP)
    worst = 0.0
    for i in range(1, 201):
        pg.evaluate(f"window.atom.set({i}/200)")
        pg.evaluate(SNAP.replace("window.__last = a;", "const prev = window.__last; window.__last = a;")
                    .replace("return black / a.length;",
                             "let fl = 0; for (let i = 0; i < a.length; i++) fl += a[i] !== prev[i] ? 1 : 0; window.__flip = fl / a.length; return black / a.length;"))
        fl = pg.evaluate("window.__flip")
        if fl > worst:
            worst = fl
            print(f"  new worst at step {i}: {fl:.4f}")
    print(f"worst flip per 1/200 k-step (in-browser): {worst:.4f}")
    b.close()
