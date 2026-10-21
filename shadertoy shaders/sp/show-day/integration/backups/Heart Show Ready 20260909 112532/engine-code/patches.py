"""Serialized patch work with cancellation; no concurrent shared-engine editors."""
import threading
import time
from concurrent.futures import ThreadPoolExecutor

class Cancelled(Exception):pass

class Operations:
    def __init__(self):
        self.lock=threading.RLock();self.number=0;self.active=False;self.status='Idle';self.started=None
        self.pool=ThreadPoolExecutor(max_workers=1,thread_name_prefix='heart-patch');self.pending=set();self._busy=False
    @property
    def busy(self):
        # Include queued and cancelled-but-not-drained work: writers must not race it.
        return self._busy
    def cancel(self):
        with self.lock:
            self.number+=1
            if self.pending:self.status='Remaining patch steps cancelled; an in-flight renderer request may still finish'
    def check(self,token):
        if token!=self.number:raise Cancelled()
    def progress(self,token,message):
        with self.lock:
            self.check(token);self.status=message
    def snapshot(self):
        # Publishing runs on the motion loop. Never wait for a blocking renderer write.
        active=self._busy;running=self.active;started=self.started;stage=self.status
        return {'active':active,'running':running,'stage':stage,
                'elapsed':round(time.monotonic()-started,1) if running and started else 0}
    def write(self,token,fn,*args):
        with self.lock:
            self.check(token);return fn(*args)
    def submit(self,fn):
        with self.lock:
            self.number+=1;token=self.number;self.pending.add(token);self._busy=True;self.status='Queued'
        def run():
            running=False
            try:
                with self.lock:
                    if token!=self.number:return
                    self.active=True;running=True;self.status='Applying';self.started=time.monotonic()
                fn(token)
                with self.lock:
                    self.check(token);self.status='Ready'
            except Cancelled:pass
            except Exception as exc:
                with self.lock:
                    if token==self.number:self.status='Failed: '+str(exc)
            finally:
                with self.lock:
                    self.pending.discard(token);self._busy=bool(self.pending)
                    if running:self.active=False
        try:return self.pool.submit(run)
        except Exception:
            with self.lock:self.pending.discard(token);self._busy=bool(self.pending)
            raise


def validate_snapshot(path, layers):
    """Fail before mutation when named layer/clip dependencies cannot resolve."""
    import xml.etree.ElementTree as ET
    from collections import Counter
    root=ET.parse(path).getroot()
    def name(node):
        return next((p.get('value',p.get('default','')) for g in node.findall('Params') for p in g if p.get('name')=='Name'),'')
    layer_nodes=root.findall('Layer');names=[name(n) for n in layer_nodes]
    for role,saved in layers.items():
        if names.count(role)!=1:raise ValueError('Missing or ambiguous layer '+role)
        li=layer_nodes[names.index(role)].get('layerIndex')
        if saved['clip'] is None:continue
        # First deck is the active deck represented by the REST composition.
        deck=next((d for d in root.findall('Deck') if d.get('deckIndex','0')==root.get('currentDeckIndex','0')),None)
        matches=[c for c in deck.findall('Clip') if c.get('layerIndex')==li and name(c)==saved['clip']] if deck is not None else []
        if len(matches)!=1:raise ValueError('Missing or ambiguous clip '+role+'/'+saved['clip'])


def composition_signature(comp):
    import targets
    def fx(v):return [e.get('name') for e in (v or {}).get('effects',[])]
    return {'size':[comp['video']['width']['value'],comp['video']['height']['value']],
            'effects':fx(comp['video']),
            'groups':[(targets.label(g),fx(g.get('video'))) for g in comp.get('layergroups',[])],
            'layers':[(targets.label(l),fx(l.get('video')),[(targets.label(c),c['video'].get('description'),fx(c['video'])) for c in l['clips'] if c.get('video')]) for l in comp['layers']]}


def _composition_epoch(comp):
    """Runtime root IDs are completion evidence only, never saved target identities."""
    video=comp.get('video') or {}
    nodes=[comp.get('name'),video.get('width'),video.get('height'),
           (comp.get('tempocontroller') or {}).get('tempo')]
    ids=tuple(node.get('id') if isinstance(node,dict) else None for node in nodes)
    return ids if any(value is not None for value in ids) else None


def open_verified(post, read, path, signature, check, timeout=12):
    """Confirm a completed open, not an already-open lookalike with a pending POST.

    Arena may leave the POST pending after loading. Accept that case only after a
    root-ID generation change or an observed transition from a different snapshot,
    followed by stable matching readback. An acknowledged POST still needs matching
    readback. A repeated identical snapshot without ack or generation evidence is
    deliberately unconfirmed; structural equality alone cannot prove it reopened.
    """
    import time,json
    expected=json.dumps(signature,sort_keys=True)
    def matches(comp):
        return comp.get('name',{}).get('value')==path.stem and json.dumps(composition_signature(comp),sort_keys=True)==expected
    check()
    before_epoch=None;saw_other=False
    try:
        before=read();before_epoch=_composition_epoch(before);saw_other=not matches(before)
    except (OSError,ValueError,KeyError):pass
    check()
    outcome={}
    def request():
        try:check();post('/composition/open',path.as_uri());outcome['ack']=True
        except Exception as exc:outcome['error']=exc
    threading.Thread(target=request,daemon=True,name='arena-open').start()
    end=time.monotonic()+timeout;stable=None
    while time.monotonic()<end:
        check()
        try:
            comp=read()
            if matches(comp):
                epoch=_composition_epoch(comp)
                changed=before_epoch is not None and epoch is not None and epoch!=before_epoch
                if outcome.get('ack'):return comp
                if saw_other or changed:
                    if stable is None:stable=time.monotonic()
                    if time.monotonic()-stable>=.5:return comp
                else:stable=None
            else:saw_other=True;stable=None
        except (OSError,ValueError,KeyError):stable=None
        if outcome.get('error') and not isinstance(outcome['error'],(TimeoutError,OSError)):raise outcome['error']
        time.sleep(.1)
    raise TimeoutError('Snapshot open was not confirmed by acknowledgement or a new composition generation')
