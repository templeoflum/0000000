"""Coherent latest-frame OSC delivery with bounded, independent identity reads."""
import asyncio
import time
import struct


def split_bundles(payloads, limit=1200):
    header = b'#bundle\0'+struct.pack('>Q', 1)
    packet = header
    for payload in payloads:
        offset = 16
        while offset < len(payload):
            size = struct.unpack('>i', payload[offset:offset+4])[0]+4
            block = payload[offset:offset+size]
            if len(packet)+size > limit and len(packet) > 16:
                yield packet
                packet = header
            packet += block
            offset += size
    if len(packet) > 16:
        yield packet


class PhaseFrames:
    lease_seconds = .2
    refresh_seconds = .07
    max_frame_age = .1

    def __init__(self, read, bundle, emit, valid, stopped, report):
        self.read, self.bundle, self.emit = read, bundle, emit
        self.valid, self.stopped, self.report = valid, stopped, report
        self.frame = None
        self.cache = {}
        self.jobs = {}
        self.last_sent = {}
        self.dropped = 0
        self.last_report = 0.
        self.sent = 0
        self.ready = asyncio.Event()

    def submit(self, number, sampled, rows):
        self.frame = (number, sampled, rows)
        self.ready.set()

    async def validate(self, key, rows):
        started = time.perf_counter()
        try:
            native = await self.read(key[0])
            # Validation uses fixed sample values only to inspect the route.
            # Delivery always picks the current complete frame after this read.
            current = [r for r in rows if self.valid(r)]
            if not current:
                return
            self.bundle(native, [(r[0], r[1], r[2]) for r in current])
            self.cache[key] = (native, started)
        except ValueError as ex:
            self.cache.pop(key, None)
            self.stopped(rows, str(ex))
        except Exception:
            # A slow/unavailable object loses its lease. Other objects continue.
            self.cache.pop(key, None)
        finally:
            if self.jobs.get(key) is asyncio.current_task():self.jobs.pop(key, None)
            self.ready.set()

    async def run(self):
        try:
            while True:
                self.ready.clear()
                now = time.perf_counter()
                frame = self.frame
                groups = {}
                if frame and now-frame[1] <= self.max_frame_age:
                    for row in frame[2]:
                        if not self.valid(row):
                            continue
                        route = row[2]
                        path = route.get('read') or f"/composition/layers/{route['layer']}/clips/{route['clip']}"
                        groups.setdefault((path,row[4]), []).append(row)
                groups={(path,gen,tuple((r[0],r[3]) for r in rows)):rows for (path,gen),rows in groups.items()}
                for key in set(self.jobs)-set(groups):self.jobs.pop(key).cancel()
                # New and least recently validated routes get the next free slot.
                for key, rows in sorted(groups.items(), key=lambda kv:self.cache.get(kv[0],({},-1e12))[1]):
                    if len(self.jobs) >= 4:
                        break
                    if key not in self.jobs and now-self.cache.get(key,({},-1e12))[1] >= self.refresh_seconds:
                        self.jobs[key] = asyncio.create_task(self.validate(key, rows))
                packets = []; delivered = []
                for key, rows in groups.items():
                    native, checked = self.cache.get(key, ({}, -1e12))
                    if now-checked > self.lease_seconds:
                        continue
                    rows = [r for r in rows if self.last_sent.get(r[0]) != frame[0]]
                    if not rows:
                        continue
                    try:
                        packets.append(self.bundle(native, [(r[0],r[1],r[2]) for r in rows]))
                        delivered.extend(r[0] for r in rows)
                    except ValueError as ex:
                        self.cache.pop(key,None); self.stopped(rows,str(ex))
                # No awaits between validity checks and UDP sends: every packet
                # in this batch belongs to one sampled frame and binding version.
                for packet in split_bundles(packets):
                    self.emit(packet)
                if delivered:
                    self.sent += len(delivered)
                    self.last_sent.update(dict.fromkeys(delivered,frame[0]))
                if frame and now-self.last_report >= .1:
                    waiting=[r[0] for key,rows in groups.items() if now-self.cache.get(key,({},-1e12))[1]>self.lease_seconds for r in rows]
                    self.report(sent=self.sent, delivery=dict(frame=frame[0], sampled=frame[1], reported=now, age_ms=round((now-frame[1])*1000,2), delivered=len(delivered), waiting=len(waiting), waiting_ids=waiting))
                    self.sent = 0; self.last_report = now
                active=set(groups)|set(self.jobs)
                self.cache={k:v for k,v in self.cache.items() if k in active}
                self.last_sent={pid:n for pid,n in self.last_sent.items() if frame and any(r[0]==pid for r in frame[2])}
                try:await asyncio.wait_for(self.ready.wait(),self.refresh_seconds)
                except TimeoutError:pass
        finally:
            tasks=list(self.jobs.values())
            for task in tasks:task.cancel()
            await asyncio.gather(*tasks,return_exceptions=True)
