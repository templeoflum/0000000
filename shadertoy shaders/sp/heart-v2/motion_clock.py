"""One beat transport; continuous phase distance integrated from its intervals."""
import math

# Four-point Gaussian quadrature, split at every ramp boundary. Constant
# intervals take one sample, including arbitrarily long scheduler stalls.
QUADRATURE = ((-.8611363115940526, .3478548451374538),
              (-.3399810435848563, .6521451548625461),
              (.3399810435848563, .6521451548625461),
              (.8611363115940526, .3478548451374538))


def integral(fn, start, end, ramps=()):
    if end <= start:
        return 0.
    ramps = [(a, b) for a, b in ramps if b > a and a < end and b > start]
    cuts = sorted({start, end, *(max(start, a) for a, b in ramps),
                   *(min(end, b) for a, b in ramps)})
    total = 0.
    for a, b in zip(cuts, cuts[1:]):
        active = [y-x for x, y in ramps if x < b and y > a]
        if not active:
            total += (b-a)*fn((a+b)/2)
            continue
        # Only changing sections need subdivision. No elapsed time is discarded.
        count = max(1, math.ceil((b-a)/(min(active)/4)))
        width = (b-a)/count
        for i in range(count):
            mid = a+(i+.5)*width
            total += width/2*sum(w*fn(mid+x*width/2) for x, w in QUADRATURE)
    return total


class MotionClock:
    def __init__(self):
        self.beat = 0.
        self.turn = 0.
        self.now = None
        self.frame = 0
        self.paths = {}

    def interval(self, dt, now, bpm, hold=False):
        start = now-max(0., dt)
        if self.now is not None:
            start = max(start, min(now, self.now))
        self.now = now
        self.frame += 1
        beats = (now-start)*bpm/60
        self.beat += beats
        if not hold:
            self.turn += beats/32
        return start, now, 0. if hold else bpm/60/32

    def path(self, keys, factor):
        keys = tuple(keys)
        if keys not in self.paths:
            self.paths[keys] = self.turn*factor
        return self.paths[keys]

    def downbeat(self):
        self.beat = self.turn = 0.
        self.paths = dict.fromkeys(self.paths, 0.)
