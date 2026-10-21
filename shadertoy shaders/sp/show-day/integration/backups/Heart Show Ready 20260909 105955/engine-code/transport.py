"""Musical position and tap estimator, independent of Heart's motion Hold."""
import math
import statistics
import threading
import time


class Transport:
    def __init__(self):
        self.lock = threading.RLock()
        self.beats = 0.
        self.taps = []
        self.alignment = None

    def tap(self, now=None):
        now = time.monotonic() if now is None else now
        with self.lock:
            if self.taps and (now-self.taps[-1] > 3. or now <= self.taps[-1]):
                self.taps = []
            if self.taps and now-self.taps[-1] < .12:
                return None
            self.taps = (self.taps+[now])[-9:]
            if len(self.taps) < 2:
                return None
            return max(20., min(500., 60/statistics.median(
                b-a for a,b in zip(self.taps,self.taps[1:]))))

    def downbeat(self):
        with self.lock:
            self.alignment = self.beats
            self.beats = 0.

    def advance(self, dt, bpm):
        with self.lock:
            # A suspended process must not replay hours of musical time on wake.
            self.beats += min(.25,max(0.,dt))*bpm/60.
            alignment,self.alignment = self.alignment,None
            return alignment

    def snapshot(self, phrase_bars, now=None):
        now = time.monotonic() if now is None else now
        with self.lock:
            phrase_beats = max(1.,phrase_bars*4)
            position = self.beats % phrase_beats
            return {'beats':self.beats,'beat':int(position%4)+1,
                    'bar':int(position//4)+1,'phase':self.beats%1,
                    'phrase_bars':phrase_bars,
                    'taps':len(self.taps) if self.taps and now-self.taps[-1]<=3 else 0}


def tempo_value(value):
    value = float(value)
    if not math.isfinite(value) or not 20 <= value <= 500:
        raise ValueError('Tempo must be between 20 and 500 BPM')
    return value
