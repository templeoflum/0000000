import asyncio,json
from pathlib import Path
import websockets
P=Path(__file__).resolve().parent
async def main():
 async with websockets.connect('ws://localhost:8766',max_size=10000000) as w:
  state=json.loads(await w.recv())
  async def drain():
   nonlocal state
   async for m in w:state=json.loads(m)
  t=asyncio.create_task(drain());rows=[]
  for action in ['settle','open','settle']:
   await w.send(json.dumps(dict(cmd='play_all',action=action)));await asyncio.sleep(5)
   slots=[s for c in state['clips'] for s in c['slots']]
   fx=[dict(key=f['key'],target=f['target'],amount=f.get('observed_amount'),bypassed=f.get('observed_bypassed')) for f in state['fx'] if f['has_amount']]
   row=dict(action=action,driven=sum(s['drive'] for s in slots),slots=len(slots),effects=fx,status=state.get('play_action'));rows.append(row);print(action,'driven',row['driven'],'effects_nonzero',sum(f['target']>.001 for f in fx),flush=True)
  (P/'recovery.json').write_text(json.dumps(rows,indent=2));assert rows[0]['driven']==rows[2]['driven']==0;assert rows[1]['driven']>0;assert all(f['target']<=.001 for r in rows for f in r['effects']);t.cancel()
asyncio.run(main())
