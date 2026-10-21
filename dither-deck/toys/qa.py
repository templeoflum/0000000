import asyncio, base64, sys, os
from playwright.async_api import async_playwright

TOY, TAG = sys.argv[1], sys.argv[2]
KS = [float(x) for x in sys.argv[3].split(',')]
HERE = os.path.dirname(os.path.abspath(__file__))
OUTDIR = '/tmp/qa_shots'
os.makedirs(OUTDIR, exist_ok=True)

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        pg = await b.new_page(viewport={'width':760,'height':900})
        errs=[]
        pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto(f'file://{HERE}/{TOY}.html')
        await pg.wait_for_timeout(1500)
        for i,k in enumerate(KS):
            r = await pg.evaluate(f'''()=>{{
                window.atom.set({k});
                const c=document.querySelector("canvas"),x=c.getContext("2d");
                const d=x.getImageData(0,0,c.width,c.height).data;
                let n=0; for(let j=0;j<d.length;j+=4) if(d[j]>128) n++;
                return {{white:n/(d.length/4), png:c.toDataURL("image/png")}};
            }}''')
            print(f'k={k:.3f}: ink={1-r["white"]:.3f}')
            open(f'{OUTDIR}/{TAG}_{i}.png','wb').write(base64.b64decode(r['png'].split(',',1)[1]))
        res = await pg.evaluate('''()=>{
            const c=document.querySelector("canvas"), x=c.getContext("2d"), N=c.width*c.height;
            const steps=200, flips=[];
            let prev=null;
            for(let s=0;s<=steps;s++){
                window.atom.set(s/steps);
                const d=x.getImageData(0,0,c.width,c.height).data;
                const cur=new Uint8Array(N);
                for(let i=0;i<N;i++) cur[i]=d[i*4]>128?1:0;
                if(prev){let f=0;for(let i=0;i<N;i++) if(cur[i]!==prev[i]) f++;flips.push(f/N);}
                prev=cur;
            }
            flips.sort((a,b)=>b-a);
            return {max:(flips[0]*100).toFixed(2)+'%', mean:(flips.reduce((q,r2)=>q+r2,0)/flips.length*100).toFixed(2)+'%'};
        }''')
        print('granularity:', res)
        print('errors:', errs if errs else 'none')
        await b.close()

asyncio.get_event_loop().run_until_complete(main())
