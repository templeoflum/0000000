"""Bounded read-only observation of native parameter automation ownership."""
import time


class OwnershipObserver:
    def __init__(self, clips, available, generation, current, read_phase, release,
                 clock=time.monotonic, rate=20, interval=1.):
        self.clips=clips;self.available=available;self.generation=generation
        self.current=current;self.read_phase=read_phase;self.release=release
        self.clock=clock;self.spacing=1./rate;self.interval=interval
        self.next=0.;self.last={};self.turn=0;self.polls=0;self.errors=0

    def step(self):
        now=self.clock()
        if now<self.next or not self.available():return False
        candidates=[];keys=set()
        for clip in self.clips():
            if not getattr(clip,'taken',False):continue
            for slot in clip.slots:
                if hasattr(slot,'choices') or '' not in slot.ids:continue
                key=(id(clip),id(slot),slot.ids['']);keys.add(key)
                checked=self.last.get(key,float('-inf'))
                if now-checked<self.interval or getattr(slot,'claim_inflight',False):continue
                moving=slot.drive or (slot.prev is not None and now-slot.t0<slot.dur)
                priority=getattr(slot,'owner','unverified')=='heart' and moving
                candidates.append((checked,key,clip,slot,priority))
        self.last={key:value for key,value in self.last.items() if key in keys}
        if not candidates:return False
        # Four priority reads then one other read; oldest checked wins within a lane.
        priority=self.turn%5!=4
        lane=[item for item in candidates if item[4]==priority] or candidates
        _,key,clip,slot,_=min(lane,key=lambda item:item[0])
        self.turn+=1;self.next=now+self.spacing;self.last[key]=now
        with slot.ownership_lock:
            epoch=slot.claim_epoch;pid=slot.ids[''];generation=self.generation()
            if slot.claim_inflight:return False
        self.polls+=1
        try:
            phase=self.read_phase(pid)
            if not isinstance(phase,str) or not phase:raise ValueError('Missing phase source')
        except Exception:
            self.errors+=1;return True
        with slot.ownership_lock:
            if (not self.available() or not self.current(clip,slot) or slot.ids.get('')!=pid
                    or self.generation()!=generation or slot.claim_epoch!=epoch or slot.claim_inflight):
                return True
            slot.phase_checked=self.clock();slot.native_phase=phase
            # Static readback NEVER reclaims a released or unverified parameter.
            if phase!='static':self.release(clip,slot,phase)
        return True

    def run(self):
        while True:
            try:self.step()
            except Exception:self.errors+=1
            time.sleep(self.spacing)
