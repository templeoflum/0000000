import asyncio, sys, os
from playwright.async_api import async_playwright

KSET = float(sys.argv[1]) if len(sys.argv)>1 else 0.55
HERE = os.path.dirname(os.path.abspath(__file__))
DECK = os.path.join(HERE, 'deck_slim.html')

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        pg = await b.new_page(viewport={'width':900,'height':1000})
        errs=[]
        pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto('file://' + DECK)
        await pg.wait_for_timeout(3000)
        counts = await pg.evaluate('[...document.querySelectorAll("#bar > .row")].map(r=>r.children.length)')
        print('rows (atoms, mols, vers):', counts)
        async def probe():
            return await pg.evaluate('''()=>{
                const c=document.getElementById("view");
                const d=c.getContext("2d").getImageData(0,0,680,680).data;
                let dark=0; for(let i=0;i<d.length;i+=4) if(d[i]<128) dark++;
                return {ink:+(dark/(d.length/4)).toFixed(3), tag:document.getElementById("tag").textContent};
            }''')
        await pg.evaluate(f'''()=>{{
            const r=document.getElementById("rail").getBoundingClientRect();
            const x=r.left+r.width*(30+360*{KSET})/420;
            document.getElementById("rail").dispatchEvent(new MouseEvent("mousedown",{{clientX:x,bubbles:true}}));
            document.getElementById("rail").dispatchEvent(new MouseEvent("mouseup",{{bubbles:true}}));
        }}''')
        print(f'k={KSET} set')
        na = counts[0]; nm = counts[1]
        for i in range(na):
            await pg.evaluate(f'document.querySelectorAll("#bar > .row:not(.mol) .dot")[{i}].dispatchEvent(new MouseEvent("click",{{bubbles:true}}))')
            print(f'atom[{i}]:', await probe())
        for i in range(nm):
            await pg.evaluate(f'document.querySelectorAll("#bar > .row.mol .dot")[{i}].dispatchEvent(new MouseEvent("click",{{bubbles:true}}))')
            print(f'mol[{i}]:', await probe())
        kx = await pg.evaluate('(parseFloat(document.getElementById("knob").getAttribute("cx"))-30)/360')
        print('knob still:', round(kx,3))
        print('errors:', errs if errs else 'none')
        await b.close()

asyncio.get_event_loop().run_until_complete(main())
