"""Synthesised sound library (no samples). All return mono float arrays at SR, or stereo (n,2)."""
import numpy as np
from scipy import signal
SR = 48000
rng = np.random.default_rng(307)

def t_(d): return np.arange(int(round(d * SR))) / SR
def env(n, a=.005, r=.1, curve=3):
    e = np.ones(n); na = max(1, int(a * SR)); nr = max(1, int(r * SR))
    e[:na] = np.linspace(0, 1, na)
    if nr < n: e[-nr:] *= np.linspace(1, 0, nr) ** curve
    return e
def bp(x, lo, hi, o=2):
    sos = signal.butter(o, [lo, hi], 'band', fs=SR, output='sos'); return signal.sosfilt(sos, x)
def lp(x, f, o=2):
    sos = signal.butter(o, f, 'low', fs=SR, output='sos'); return signal.sosfilt(sos, x)
def hp(x, f, o=2):
    sos = signal.butter(o, f, 'high', fs=SR, output='sos'); return signal.sosfilt(sos, x)
def noise(d): return rng.standard_normal(int(round(d * SR)))
def norm(x, p=1.0):
    m = np.max(np.abs(x)) + 1e-9; return x / m * p

def rain(d, heavy=1.0):
    n = noise(d); bed = bp(n, 400, 9000) * .25 + lp(noise(d), 600) * .15
    drops = np.zeros(len(bed))
    for _ in range(int(d * 90 * heavy)):
        i = rng.integers(0, len(bed) - 2000); L = rng.integers(200, 1200)
        drops[i:i + L] += hp(noise(L / SR), 2000)[:L] * np.exp(-np.arange(L) / (L / 5)) * rng.uniform(.1, .5)
    return bed + drops * .5
def roof_rain(d):
    n = bp(noise(d), 200, 3000) * .3
    taps = np.zeros(len(n))
    for _ in range(int(d * 160)):
        i = rng.integers(0, len(n) - 800); L = 600
        taps[i:i + L] += bp(noise(L / SR), 800, 4000)[:L] * np.exp(-np.arange(L) / 90) * rng.uniform(.1, .6)
    return n + taps * .6
def thunder(d=4.0, crack=True):
    n = noise(d); x = lp(n, 120, 4) * 3 * env(len(n), .3, d * .8, 2)
    rum = lp(noise(d), 60, 4) * 4 * np.clip(np.sin(np.linspace(0, np.pi, len(n))) ** .5, 0, 1)
    out = x + rum
    if crack:
        c = hp(noise(.5), 300) * np.exp(-t_(.5) * 9) * 1.2
        out[:len(c)] += c
    return out
def tick():
    x = bp(noise(.03), 2000, 7000) * np.exp(-t_(.03) * 200); return x * .6
def boom(d=2.5, f=42):
    t = t_(d); x = np.sin(2 * np.pi * (f + 30 * np.exp(-t * 8)) * t) * np.exp(-t * 1.6)
    return x + lp(noise(d), 200) * np.exp(-t * 6) * .6
def braam(d=2.2):
    t = t_(d); x = np.zeros(len(t))
    for f, a in [(55, 1), (55.6, .8), (110.4, .5), (82.5, .4), (164, .2)]:
        x += a * signal.sawtooth(2 * np.pi * f * t)
    x = lp(x, 900, 2) * env(len(t), .02, d * .8, 2) * .35
    return x
def screech(d=1.2):
    t = t_(d); x = np.zeros(len(t))
    for f in [1480, 1567, 1661, 2093]:
        x += np.sin(2 * np.pi * f * t + 3 * np.sin(2 * np.pi * 6.3 * t)) * .25
    x += bp(noise(d), 2000, 6000) * .3
    return x * env(len(t), .005, d * .9, 2)
def heartbeat(bpm_start, bpm_end, d):
    out = np.zeros(int(round(d * SR))); tt = 0.0
    while tt < d - .3:
        bpm = bpm_start + (bpm_end - bpm_start) * tt / d
        for off, a in [(0, 1), (.16, .7)]:
            i = int((tt + off) * SR); s = boom(.25, 48) * a
            e = min(len(out), i + len(s)); out[i:e] += s[:e - i]
        tt += 60 / bpm
    return lp(out, 150) * 1.4
def drone(d, f=43.65):
    t = t_(d); x = np.sin(2 * np.pi * f * t) + .5 * np.sin(2 * np.pi * f * 1.5 * t + 1) + .25 * np.sin(2 * np.pi * f * 2.02 * t)
    x *= 1 + .15 * np.sin(2 * np.pi * .3 * t)
    return x * .5
def strings(d, freqs=(220, 233.08, 246.94, 329.6)):
    t = t_(d); x = np.zeros(len(t))
    for i, f in enumerate(freqs):
        vib = 1 + .004 * np.sin(2 * np.pi * (5 + i * .3) * t)
        x += signal.sawtooth(2 * np.pi * f * vib * t) * .2
    x = bp(x, 200, 2500) * (1 + .3 * np.sin(2 * np.pi * 7 * t))
    return x
def creak(d=.6, f0=180, f1=120):
    t = t_(d); f = np.linspace(f0, f1, len(t)) * (1 + .05 * np.sin(2 * np.pi * 23 * t))
    ph = 2 * np.pi * np.cumsum(f) / SR
    x = signal.sawtooth(ph) * (1 + .6 * np.sin(2 * np.pi * 31 * t))
    x = bp(x, 300, 2500) * env(len(t), .05, d * .5, 2)
    return x * .5
def step(soft=1.0):
    d = .18; x = lp(noise(d), 500) * np.exp(-t_(d) * 30) + bp(noise(d), 800, 3000) * np.exp(-t_(d) * 60) * .3
    return x * .7 * soft
def click():
    x = bp(noise(.02), 1500, 6000) * np.exp(-t_(.02) * 300); y = np.zeros(int(.12 * SR)); y[:len(x)] += x; i = int(.05 * SR); y[i:i + len(x)] += x * .7; return y
def thud(f=70):
    t = t_(.4); return np.sin(2 * np.pi * f * t) * np.exp(-t * 14) + lp(noise(.4), 300) * np.exp(-t * 25) * .5
def chime(d=2.0, base=880):
    t = t_(d); x = np.zeros(len(t))
    for i, (f, a) in enumerate([(base, 1), (base * 1.5, .6), (base * 2, .4), (base * 2.52, .3), (base * 3, .2)]):
        st = int(i * .06 * SR); tt = t[:len(t) - st]
        x[st:] += np.sin(2 * np.pi * f * tt) * np.exp(-tt * 2.2) * a
    return x * .4
def shimmer(d=1.5):
    t = t_(d); x = np.zeros(len(t))
    for k in range(18):
        f = rng.uniform(2000, 6000); st = rng.uniform(0, d * .7); i = int(st * SR); tt = t[:len(t) - i]
        x[i:] += np.sin(2 * np.pi * f * tt) * np.exp(-tt * 8) * .15
    return x
def blip(f=1200, d=.08):
    t = t_(d); return np.sin(2 * np.pi * f * t) * env(len(t), .002, d * .8) * .5
def scan_hum(d):
    t = t_(d); return (np.sin(2 * np.pi * 220 * t) * .3 + np.sin(2 * np.pi * (660 + 200 * np.sin(2 * np.pi * 1.3 * t)) * t) * .15) * env(len(t), .05, .1)
def cash():
    x = chime(.8, 1760) * .8; b = bp(noise(.15), 2000, 8000) * np.exp(-t_(.15) * 30) * .5; x[:len(b)] += b; return x
def warm_pad(d, root=146.83):
    t = t_(d); x = np.zeros(len(t))
    for f in [root, root * 1.26, root * 1.5, root * 2, root * .5]:
        for det in (-.6, .6):
            x += signal.sawtooth(2 * np.pi * (f + det) * t) * .08
    return lp(x, 1400) * env(len(t), .6, 1.2, 2)
def riser(d):
    t = t_(d); x = bp(noise(d), 500, 8000) * (t / d) ** 2
    x += np.sin(2 * np.pi * np.cumsum(np.linspace(200, 1200, len(t))) / SR) * (t / d) ** 3 * .2
    return x
def breath(d=.8, inhale=False):
    x = bp(noise(d), 300, 2500); x = x * np.sin(np.linspace(0, np.pi, len(x))) ** 1.5
    return x * .3

class Mix:
    def __init__(self, d):
        self.L = np.zeros(int(d * SR)); self.R = np.zeros(int(d * SR)); self.V = np.zeros(int(d * SR))
    def add(self, t, x, g=1.0, pan=0.0, voice=False):
        if x.ndim == 2: l, r = x[:, 0], x[:, 1]
        else: l = x * np.cos((pan + 1) * np.pi / 4) * 1.414; r = x * np.sin((pan + 1) * np.pi / 4) * 1.414
        i = int(t * SR);
        if i < 0: l, r = l[-i:], r[-i:]; i = 0
        e = min(len(self.L), i + len(l)); n = e - i
        if n <= 0: return
        tgt = self.V if voice else None
        if voice:
            self.V[i:e] += (l[:n] + r[:n]) / 2 * g
        else:
            self.L[i:e] += l[:n] * g; self.R[i:e] += r[:n] * g
    def render(self, duck=.35, fade_out=.3):
        # duck sfx under voice
        envv = np.abs(self.V); envv = lp(envv, 8, 1); envv = np.clip(envv / (envv.max() + 1e-9) * 4, 0, 1)
        envv = np.concatenate([envv[int(.08 * SR):], np.zeros(int(.08 * SR))])  # duck 80 ms early
        g = 1 - duck * envv
        L = self.L * g + self.V; R = self.R * g + self.V
        n = int(fade_out * SR); L[-n:] *= np.linspace(1, 0, n); R[-n:] *= np.linspace(1, 0, n)
        return np.stack([L, R], 1)
