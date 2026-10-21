"""A single replaceable frame; transport backpressure never blocks the clock."""
import asyncio


class LatestFrame:
    def __init__(self):
        self.value = None
        self.ready = asyncio.Event()
        self.dropped = 0

    def put(self, value):
        if self.value is not None:
            self.dropped += 1
        self.value = value
        self.ready.set()

    async def get(self):
        await self.ready.wait()
        value = self.value
        self.value = None
        self.ready.clear()
        return value
