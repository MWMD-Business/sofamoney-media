"""Soundtrack for the NexTalk ad 'Don't look back'. Writes out/nextalk-crew_audio_raw.wav (48 kHz stereo).
Walkie voices are filtered like a radio, with the sound-pack walkie chirp on every key-down.
Everything else is synthesised (tools/sfx.py + code here). Timings are the same T as in index.html."""
import sys, numpy as np, soundfile as sf
from pathlib import Path
HERE = Path(__file__).resolve().parent
KIT = HERE.parents[1]
OUT = KIT / 'out'; OUT.mkdir(exist_ok=True)
SND = str(KIT / 'sounds') + '/'
sys.path.insert(0, str(KIT / 'tools'))
from sfx import *
from scipy.signal import resample_poly

T = dict(A=0, B=2.4, C=4.0, ka=4.12, a1=4.35, kr=7.3, D=7.35, kj=7.45, j1=7.62, kj2=8.75, ks=8.85, s1=9.0, ks2=10.1,
         E=10.15, drop=10.75, stop=11.3, crew=11.35, kss=11.4, s2=11.55, turn=12.1, G=12.75, END=14.0, total=16.6)
D = T['total']; m = Mix(D)
rg = np.random.default_rng(77)


def load(p):
    x, sr = sf.read(p); x = x.mean(1) if x.ndim > 1 else x
    return resample_poly(x, SR, sr) if sr != SR else x
def fade(x, a=.01, r=.05):
    x = x.copy(); na, nr = int(a * SR), int(r * SR)
    if na: x[:na] *= np.linspace(0, 1, na)
    if nr: x[-nr:] *= np.linspace(1, 0, nr)
    return x
def cut(x, d): n = int(round(d * SR)); return x[:n] if len(x) >= n else np.concatenate([x, np.zeros(n - len(x))])
def radio(name):
    """walkie voice: band-limited, a little crunchy, with a hiss bed"""
    x = load(str(HERE / 'vo' / f'{name}.wav')); x = x / (np.sqrt(np.mean(x ** 2)) + 1e-9) * .12
    y = bp(x, 380, 3300, 3); y = np.tanh(y * 3.2) / 3.2 * 1.6
    hiss = bp(noise(len(y) / SR), 1500, 6000) * .012
    pad = np.zeros(int(.06 * SR))
    return np.concatenate([pad, y + hiss, pad])
def squelch(d=.16):
    n = bp(noise(d), 900, 5000) * np.exp(-t_(d) * 18); return n * .6
def wet_step(heavy=1.0):
    x = step(.8 * heavy); s = bp(noise(.1), 1500, 6500) * np.exp(-t_(.1) * 32) * .3
    y = np.zeros(max(len(x), len(s))); y[:len(x)] += x; y[:len(s)] += s; return y
def engine(d, f0=40, f1=95):
    t = t_(d); f = np.linspace(f0, f1, len(t)) * (1 + .03 * np.sin(2 * np.pi * 7 * t)); ph = 2 * np.pi * np.cumsum(f) / SR
    x = signal.sawtooth(ph) * .5 + signal.sawtooth(ph * 2.02) * .25 + lp(noise(d), 300) * .3
    return lp(x, 900) * env(len(t), .2, .3)
def screech(d=.5):
    t = t_(d); f = 1900 + 500 * np.sin(2 * np.pi * 3 * t); ph = 2 * np.pi * np.cumsum(f) / SR
    return (bp(noise(d), 1500, 4500) * .6 + np.sin(ph) * .12) * env(len(t), .03, .25)
def door_slam():
    t = t_(.35); return np.sin(2 * np.pi * 75 * t) * np.exp(-t * 22) + lp(noise(.35), 1400) * np.exp(-t * 30) * .7
def kick():
    t = t_(.35); f = 120 * np.exp(-t * 25) + 45; return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 8)
def snare():
    t = t_(.22); return (bp(noise(.22), 1200, 7000) * .7 + np.sin(2 * np.pi * 190 * t) * .4) * np.exp(-t * 18)
def hat():
    return hp(noise(.05), 7000) * np.exp(-t_(.05) * 70) * .5
def beat(d, bpm=124):
    out = np.zeros(int(round(d * SR))); b = 60 / bpm; n = int(d / (b / 2))
    for i in range(n):
        t0 = i * b / 2
        for x, g, on in [(kick(), 1.0, i % 4 == 0 or i % 8 == 7), (snare(), .8, i % 4 == 2), (hat(), .5, True)]:
            if on:
                s = int(t0 * SR); e = min(len(out), s + len(x)); out[s:e] += x[:e - s] * g
    return out
def bass(d, root=55.0, bpm=124):
    out = np.zeros(int(round(d * SR))); b = 60 / bpm
    notes = [root, root, root * 1.2, root * .89]
    for i in range(int(d / b)):
        f = notes[(i // 2) % 4]; t = t_(b * .9); x = signal.sawtooth(2 * np.pi * f * t) * np.exp(-t * 3)
        x = lp(x, 500); s = int(i * b * SR); e = min(len(out), s + len(x)); out[s:e] += x[:e - s]
    return out * .5

# ================= ambience =================
r = rain(D); m.add(0, np.stack([r, np.roll(r, 1300)], 1), .42)
m.add(0, lp(noise(D), 160) * .35, .5)                                   # city hum
# ================= the walk: mates + stalkers footsteps =================
tt = .05
while tt < 11.3:
    for k, off in enumerate((0, .11, .23)):
        m.add(tt + off, wet_step(.55), .32, (-.4, 0, .4)[k])
    tt += .53
tt = .25
while tt < T['drop'] + .2:
    g = .12 + .5 * (tt / T['drop']) ** 1.6                            # the stalkers' steps get louder (closer)
    m.add(tt, wet_step(1.3), g, -.1); m.add(tt + .27, wet_step(1.25), g * .9, .15); tt += .74
tt = T['turn'] + .4
while tt < T['END']:
    g = .5 * np.exp(-(tt - T['turn']) * .9)
    m.add(tt, wet_step(1.3), g, -.3); m.add(tt + .2, wet_step(1.2), g * .9, .3); tt += .5
# ================= thriller music =================
dr = drone(T['E'] + .1, 43.65); dr *= np.linspace(.5, 1, len(dr)); m.add(0, fade(dr, .05, .08), .3)
st = strings(T['E'] - T['B'] + .1, (220, 233.08, 261.63, 277.18)); st *= np.linspace(0, 1, len(st)) ** 1.8; m.add(T['B'], fade(st, .2, .08), .09)
m.add(0.0, boom(2.2, 38), .6)
m.add(0.0, braam(1.5) * .6, .35)
m.add(T['B'] - .05, boom(1.2, 48) * .7, .4)
m.add(T['C'] - .05, load(SND + 'whoosh.wav'), .45)
m.add(T['D'] - .05, boom(1.2, 46) * .6, .35)
m.add(T['C'], heartbeat(78, 130, T['E'] - T['C'] + .55), .5)
m.add(T['D'], riser(T['E'] - T['D']), .3)
# dead quiet before the drop: cut everything but rain + heartbeat
i0, i1 = int(T['E'] * SR), int(T['drop'] * SR)
m.L[i0:i1] *= .25; m.R[i0:i1] *= .25
m.add(T['E'] + .1, heartbeat(120, 120, .6), .55)
# ================= the walkie: chirp on every key-down, squelch on release =================
for kd, ku in [(T['ka'], T['kr']), (T['kj'], T['kj2']), (T['ks'], T['ks2']), (T['kss'], T['kss'] + 1.05)]:
    m.add(kd, load(SND + 'chirp.wav'), .85)
    m.add(ku, squelch(), .35)
for k in ('a1', 'j1', 's1', 's2'):
    m.add(T[k] - .06, radio(k), 2.4, voice=True)
# ================= the drop: headlights, the crew =================
m.add(T['drop'] - .4, engine(1.2, 35, 110), .55, .4)
m.add(T['drop'], screech(.55), .3, .3)
m.add(T['drop'], boom(2.6, 40), .95)
m.add(T['drop'], braam(1.8), .6)
m.add(T['drop'] + .02, beat(T['END'] - T['drop']), .42)
m.add(T['drop'] + .02, bass(T['END'] - T['drop']), .5)
m.add(T['stop'], engine(T['END'] - T['stop'] + .5, 32, 34) * .5, .3, .3)
m.add(T['crew'] + .05, door_slam(), .55, .35); m.add(T['crew'] + .28, door_slam(), .5, .5)
m.add(T['turn'], load(SND + 'whoosh.wav')[::-1], .3, -.2)
# ================= end card =================
m.add(T['END'] - .02, load(SND + 'chirp.wav'), .9)
m.add(T['END'], boom(2.4, 44), .7)
m.add(T['END'] + .05, chime(2.2, 659.25), .3)
m.add(T['END'] + .05, shimmer(1.6), .3)
m.add(T['END'], warm_pad(D - T['END'], 110.0), .35)
m.add(T['END'] + .02, beat(D - T['END'] - .2) * np.linspace(1, 0, int(round((D - T['END'] - .2) * SR))), .28)
out = m.render(duck=.6)
out = hp(out.T, 25).T
sf.write(str(OUT / 'nextalk-crew_audio_raw.wav'), out / np.max(np.abs(out)) * .8, SR)
for k in ('a1', 'j1', 's1', 's2'):
    print(k, T[k], '->', round(T[k] + len(load(str(HERE / 'vo' / f'{k}.wav'))) / SR, 2))
print('ok', round(len(out) / SR, 2), 's')
