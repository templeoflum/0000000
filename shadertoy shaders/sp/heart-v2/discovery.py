"""Persistent scoped discovery. Clip handoff is independent of mode inspection."""
import asyncio
import copy
import json
import sys
import time
import urllib.request
from pathlib import Path
from scan import discover, refresh_active, read_active, native_phases
from catalog_updates import clip_patch, merge_patches


class Discovery:
    def __init__(self, emit, active=read_active, inspect=native_phases):
        self.emit, self.active, self.inspect = emit, active, inspect
        self.catalog = {'epoch':'','targets':[],'layers':[]}
        self.serial = 0
        self.revision = 0
        self.priority = set()
        self.layers = set()
        self.due = {}
        self.inflight = {}
        self.stopped = False
        self.pending = None
        self.flush_handle = None

    def publish(self, started, **extra):
        message = dict(serial=self.serial, started=started, **extra)
        if message.get('event') == 'clip': message['clip_layers'] = [message['layer_id']]
        if self.pending is None: self.pending = message
        else:
            old = self.pending
            self.pending = dict(old, **message)
            self.pending['started'] = min(old['started'], started)
            self.pending['leases'] = dict(old.get('leases', {}), **message.get('leases', {}))
            self.pending['clip_layers'] = sorted(set(old.get('clip_layers', [])) | set(message.get('clip_layers', [])))
            if old.get('patch') and message.get('patch'): self.pending['patch'] = merge_patches(old['patch'], message['patch'])
        if self.flush_handle is None: self.flush_handle = asyncio.get_running_loop().call_later(.008, self.flush)

    def flush(self):
        self.flush_handle = None
        message, self.pending = self.pending, None
        if message is not None and not self.stopped and message['serial'] == self.serial: self.emit(message)

    def configure(self, message):
        if message['serial'] != self.serial or 'catalog' in message:
            self.pending = None
            if self.flush_handle is not None: self.flush_handle.cancel(); self.flush_handle = None
        self.serial = message['serial']
        self.priority = set(message.get('priority', []))
        self.layers = set(message.get('layers', []))
        if 'catalog' in message:
            self.catalog = copy.deepcopy(message['catalog']); self.revision += 1
        for lid in message.get('launches', []):
            self.due[lid] = 0

    async def poll_layer(self, layer, serial, revision):
        started = time.perf_counter()
        try:
            lid, clip = await asyncio.to_thread(self.active, layer)
            if serial != self.serial or revision != self.revision:
                return
            result = refresh_active(self.catalog, {lid:clip},incremental=True)
            if result.get('needs_full'):
                # Structural edits need the explicit Refresh path, never an
                # automatic full composition fetch while the performer plays.
                result=refresh_active(self.catalog,{lid:None},incremental=True)
                self.publish(started,error='Clip grid changed; use Refresh for its new controls')
            if result.get('_changed'):
                patch=clip_patch(self.catalog,result,lid);self.catalog = result
                # Retire outgoing routes immediately; prepare new ones separately.
                self.publish(started,patch=patch,event='clip',layer_id=lid)
        except Exception as ex:
            self.publish(started,error='Clip discovery: '+str(ex))
        finally:
            self.inflight.pop(layer['id'],None)

    async def clips(self):
        while not self.stopped:
            now=time.perf_counter()
            for layer in sorted(self.catalog['layers'],key=lambda l:self.due.get(l['id'],0)):
                lid=layer['id']
                if len(self.inflight)>=4:break
                if lid in self.inflight or now<self.due.get(lid,0):continue
                self.due[lid]=now+(.15 if lid in self.layers else .4 if layer.get('active') else .8)
                self.inflight[lid]=asyncio.create_task(self.poll_layer(copy.deepcopy(layer),self.serial,self.revision))
            await asyncio.sleep(.025)

    async def modes(self):
        while not self.stopped:
            started=time.perf_counter();serial=self.serial;revision=self.revision
            snapshot=dict(epoch=self.catalog['epoch'],native_phase_mode=self.catalog.get('native_phase_mode',False),targets=copy.deepcopy(self.catalog['targets']))
            snapshot['_phase_priority']=list(self.priority)
            # Eight parameters per batch, at most 48 per second. New clip
            # controls are prioritized without starving existing paused drives.
            fresh=any('_phase_checked' not in p for t in snapshot['targets'] if t.get('scope')=='clip' for p in t['params'] if p.get('phase_route'))
            result=await asyncio.to_thread(self.inspect,copy.deepcopy(snapshot),snapshot,budget=24 if fresh else 8)
            if serial==self.serial and revision==self.revision:
                current={p['id']:p for t in self.catalog['targets'] for p in t['params']}
                changed=set();leases={}
                for target in result['targets']:
                    for p in target['params']:
                        live=current.get(p['id'])
                        if live is None or any(live.get(k)!=p.get(k) for k in ('name','type','min','max','phase_route')):continue
                        for key in ('animation','native_phase','in','out'):
                            if live.get(key)!=p.get(key):changed.add(target['id'])
                            if key in p:live[key]=p[key]
                            else:live.pop(key,None)
                        if '_phase_checked' in p:
                            live['_phase_checked']=p['_phase_checked'];leases[str(p['id'])]=p['_phase_checked']
                        if 'value' in p:live['value']=p['value']
                first=not self.catalog.get('native_phase_mode')
                self.catalog['native_phase_mode']=True
                if changed or first:
                    targets=[t for t in self.catalog['targets'] if t['id'] in changed]
                    self.publish(started,patch=dict(epoch=self.catalog['epoch'],remove=[],layers=[],targets=targets,native_phase_mode=True,stage_only=bool(targets) and all(t.get('stage') or t.get('scope')=='stage' for t in targets)),event='prepared',leases=leases)
                else:self.publish(started,leases=leases)
            await asyncio.sleep(max(.01,1/6-(time.perf_counter()-started)))


async def main():
    def emit(value):print(json.dumps(value,separators=(',',':')),flush=True)
    worker=Discovery(emit)
    async def commands():
        while line:=await asyncio.to_thread(sys.stdin.readline):
            worker.configure(json.loads(line))
        worker.stopped=True
        raise SystemExit
    await asyncio.gather(commands(),worker.clips(),worker.modes())


if __name__=='__main__':
    if Path(__file__).with_name('api-paused.json').exists():raise SystemExit('Heart API paused')
    asyncio.run(main())
