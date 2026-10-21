"""Atomic motion saves in a separate process, fed small coalesced changes."""
import asyncio
import json
from pathlib import Path
import sys

from motion_memory import MotionMemory


class MotionWriter:
    def __init__(self, memory, path):
        self.memory, self.path = memory, Path(path)
        self.process = None
        self.lock = asyncio.Lock()

    async def save(self):
        async with self.lock:
            if self.memory.revision == self.memory.saved_revision: return
            revision, changes = self.memory.changes()
            async def commit():
                if self.process is None or self.process.returncode is not None:
                    self.process = await asyncio.create_subprocess_exec(sys.executable, str(Path(__file__).resolve()), str(self.path), stdin=asyncio.subprocess.PIPE, stdout=asyncio.subprocess.PIPE)
                process = self.process
                process.stdin.write((json.dumps(dict(revision=revision, changes=changes), separators=(',', ':'), allow_nan=False)+'\n').encode())
                await process.stdin.drain()
                line = await process.stdout.readline()
                if not line: raise OSError('Motion save worker stopped')
                result = json.loads(line)
                if result.get('error'): raise OSError(result['error'])
                if result.get('saved') != revision: raise OSError('Motion save acknowledgement changed')
                self.memory.acknowledge(revision)
            write = asyncio.create_task(commit())
            try: await asyncio.shield(write)
            except asyncio.CancelledError:
                await write
                raise

    async def close(self):
        if self.process is not None and self.process.returncode is None:
            self.process.stdin.close()
            try: await asyncio.wait_for(self.process.wait(), 3)
            except TimeoutError:
                self.process.kill(); await self.process.wait()


def worker(path):
    memory = MotionMemory()
    try: memory.load(path)
    except (OSError, ValueError): pass  # Parent preserves an unreadable file.
    for line in sys.stdin:
        try:
            command = json.loads(line)
            for epoch, changes in command['changes'].items():
                old = memory.composition(epoch)
                updated = {kind: dict(old[kind] if isinstance(old.get(kind), dict) else {}) for kind in ('targets', 'scopes')}
                for kind in ('targets', 'scopes'):
                    for key, value in changes.get(kind, {}).items():
                        if value is None: updated[kind].pop(key, None)
                        else: updated[kind][key] = value
                memory.data['compositions'][epoch] = updated
            MotionMemory.write(path, memory.data)
            result = dict(saved=command['revision'])
        except (OSError, ValueError, KeyError, TypeError) as ex:
            result = dict(error=str(ex))
        print(json.dumps(result, separators=(',', ':')), flush=True)


if __name__ == '__main__': worker(Path(sys.argv[1]))
