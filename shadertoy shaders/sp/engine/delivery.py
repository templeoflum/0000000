"""Bounded, fair latest-value delivery for continuous Arena parameters."""
from collections import OrderedDict, deque
import threading
import time


class LatestValues:
    def __init__(self, limit=4096, hz=60):
        self.limit = limit
        self.interval = 1.0 / hz
        self.last_sent = {}
        self.pending = OrderedDict()
        self.lock = threading.Lock()
        self.generation = 0
        self.replaced = 0
        self.sent = 0
        self.max_age_ms = 0.0
        self.written_at = {}
        self.active_gaps = deque(maxlen=2048)

    def put(self, item):
        pid, value = item
        with self.lock:
            if pid in self.pending:
                self.replaced += 1
            elif len(self.pending) >= self.limit:
                self.pending.popitem(last=False)
            # Updating an existing key preserves its place in the fair rotation.
            self.pending[pid] = (value, self.pending[pid][1] if pid in self.pending else time.perf_counter())

    def take(self, count=64):
        with self.lock:
            result = []
            now = time.perf_counter()
            for pid in list(self.pending):
                if len(result) >= count:
                    break
                value, created = self.pending[pid]
                # State toggles are immediate; continuous gestures share one output cadence.
                if not isinstance(value, bool) and now-self.last_sent.get(pid, -1e9) < self.interval:
                    continue
                del self.pending[pid]
                self.last_sent[pid] = now
                result.append((pid, value))
                self.max_age_ms = max(self.max_age_ms, (now-created)*1000)
            if len(self.last_sent) > self.limit*2:
                self.last_sent = {pid:t for pid,t in self.last_sent.items() if now-t<2}
            self.sent += len(result)
            return result

    def written(self, pid, active=False):
        """Actual socket-send completion spacing, separate from queue dequeue timing."""
        now=time.perf_counter()
        with self.lock:
            previous=self.written_at.get(pid)
            if active and previous is not None and now-previous<1:
                self.active_gaps.append((now-previous)*1000)
            self.written_at[pid]=now
            if len(self.written_at)>self.limit*2:
                self.written_at={p:t for p,t in self.written_at.items() if now-t<2}

    def qsize(self):
        with self.lock:
            return len(self.pending)

    def discard(self, pid):
        """Drop one released target without losing unrelated pending manual values."""
        with self.lock:
            self.pending.pop(pid,None);self.last_sent.pop(pid,None)

    def clear(self):
        with self.lock:
            self.generation += 1
            self.pending.clear()
            self.last_sent.clear()
            self.written_at.clear()
            self.active_gaps.clear()

    def metrics(self):
        with self.lock:
            gaps=sorted(self.active_gaps)
            return {"send_gap_p95_ms":round(gaps[int((len(gaps)-1)*.95)],2) if gaps else None,"send_gap_max_ms":round(max(gaps),2) if gaps else None,"pending": len(self.pending), "coalesced": self.replaced,
                    "dequeued": self.sent, "max_pending_age_ms": round(self.max_age_ms, 2)}
