"""Opt-in, bounded timing traces. No additional native observation or writes."""
import asyncio
import gc
import json
import time
from pathlib import Path


async def write_trace(path, value):
    # Even diagnostic serialization must yield in small chunks. A full JSON
    # encode in a thread still holds the interpreter lock and stalls delivery.
    file = await asyncio.to_thread(path.open, 'w')
    try:
        chunks = []; size = 0
        for chunk in json.JSONEncoder(separators=(',', ':')).iterencode(value):
            chunks.append(chunk); size += len(chunk)
            if size >= 16384:
                await asyncio.to_thread(file.write, ''.join(chunks)); chunks = []; size = 0
        if chunks: await asyncio.to_thread(file.write, ''.join(chunks))
    finally: await asyncio.to_thread(file.close)


async def engine_trace(engine, directory):
    while not engine.armed or not engine.connected: await asyncio.sleep(.1)
    await asyncio.sleep(3)
    events = []; samples = []; originals = []
    collecting = {}
    def gc_event(phase, info):
        generation = info['generation']; now = time.perf_counter()
        if phase == 'start': collecting[generation] = now
        elif generation in collecting:
            start = collecting.pop(generation)
            if now-start > .002: events.append((start, now-start, 'gc'+str(generation)))
    gc.callbacks.append(gc_event)
    def wrap(obj, name):
        original = getattr(obj, name)
        def measured(*args, **kwargs):
            start = time.perf_counter()
            try: return original(*args, **kwargs)
            finally:
                duration = time.perf_counter()-start
                if duration > .002 and len(events) < 10000: events.append((start, duration, name))
        setattr(obj, name, measured); originals.append((obj, name, original, measured))
    for obj, name in ((engine, 'reconcile'), (engine, 'state'), (engine.motion_memory, 'capture')): wrap(obj, name)
    try:
        for _ in range(80):
            samples.append(dict(now=time.perf_counter(), gaps=list(engine.gaps), work=list(engine.work), epoch=engine.epoch, owned=len(engine.owned)))
            await asyncio.sleep(.25)
    finally:
        gc.callbacks.remove(gc_event)
        for obj, name, original, measured in originals:
            if getattr(obj, name) is measured: setattr(obj, name, original)
        await write_trace(Path(directory)/'engine-trace.json', dict(events=events, samples=samples))


async def bridge_trace(frames, directory):
    while not frames.frame or not frames.frame[2]: await asyncio.sleep(.1)
    await asyncio.sleep(3)
    packets = []; reads = []; reports = []
    original_emit, original_read, original_report = frames.emit, frames.read, frames.report
    def emit(packet):
        original_emit(packet)
        if len(packets) < 30000: packets.append((time.perf_counter(), frames.frame[0], frames.frame[1], packet.hex()))
    async def read(path):
        started = time.perf_counter()
        native = await original_read(path)
        finished = time.perf_counter(); values = []
        for row in frames.frame[2] if frames.frame else []:
            route = row[2]
            if route.get('read') != path: continue
            p = native
            for k in route.get('path', []): p = p.get(k, {}) if isinstance(p, dict) else {}
            values.append((row[0], p.get('value'), p.get('in'), p.get('out')))
        if len(reads) < 20000: reads.append((started, finished, path, values))
        return native
    def report(**m):
        original_report(**m)
        if len(reports) < 1000: reports.append(m)
    frames.emit, frames.read, frames.report = emit, read, report
    try: await asyncio.sleep(20)
    finally:
        if frames.emit is emit: frames.emit = original_emit
        if frames.read is read: frames.read = original_read
        if frames.report is report: frames.report = original_report
        await write_trace(Path(directory)/'delivery-trace.json', dict(packets=packets, reads=reads, reports=reports))
