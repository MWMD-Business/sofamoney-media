"""Soundtrack for 'Someone's on the top floor' (trailer style). Writes out/top-floor_audio_raw.wav (48 kHz stereo).
All sound is synthesised (tools/sfx.py + code here) plus the Sofa Money sound pack (walkie chirp, whoosh, scan beep).
Timings are the same T as in index.html."""
import sys, numpy as np, soundfile as sf
from pathlib import Path
HERE = Path(__file__).resolve().parent
KIT = HERE.parents[1]
OUT = KIT / 'out'; OUT.mkdir(exist_ok=True)
SND = str(KIT / 'sounds') + '/'
sys.path.insert(0, str(KIT / 'tools'))
from sfx import *
from scipy.signal import resample_poly

T = dict(hook=0, winOn=.4, shadow=1.35, cut1=2.5, lift=4.5, top=6.5, torchOff=8.3, door=8.7, open=9.3, hit=9.6,
         settle=10.6, glint=10.95, phone=11.3, n1=11.5, end=13.2, n2=13.45, total=16.2)
D = T['total']; m = Mix(D)
rg = np.random.default_rng(47)


def load(p):
    x, sr = sf.read(p); x = x.mean(1) if x.ndim > 1 else x
    return resample_poly(x, SR, sr) if sr != SR else x
def vo(name): return load(str(HERE / 'vo' / f'{name}.wav'))
def fade(x, a=.01, r=.05):
    x = x.copy(); na, nr = int(a * SR), int(r * SR)
    if na: x[:na] *= np.linspace(0, 1, na)
    if nr: x[-nr:] *= np.linspace(1, 0, nr)
    return x
def st(x, d=.012):  # cheap stereo widening
    k = int(d * SR); return np.stack([x, np.concatenate([np.zeros(k), x[:-k]])], 1)

# ---------- extra synth voices for this reel ----------
def squelch(d=.45):
    n = bp(noise(d), 900, 3800) * (1 + .8 * np.sign(np.sin(2 * np.pi * 37 * t_(d))))
    return n * env(len(n), .003, d * .7, 2) * .35
def static_bed(d):
    x = bp(noise(d), 1200, 5000) * .12
    crack = np.zeros(len(x))
    for _ in range(int(d * 25)):
        i = rg.integers(0, len(x) - 400); crack[i:i + 400] += bp(noise(400 / SR), 2000, 7000)[:400] * np.exp(-np.arange(400) / 60) * rg.uniform(.2, .8)
    return (x + crack * .5) * np.linspace(1, 0, len(x)) ** 1.5
def wind(d, base=.35):
    t = t_(d); x = lp(noise(d), 500, 2) * (1 + .6 * np.sin(2 * np.pi * .23 * t) + .3 * np.sin(2 * np.pi * .61 * t + 1))
    whistle = bp(noise(d), 700, 1100) * (.5 + .5 * np.sin(2 * np.pi * .17 * t)) * .5
    return (x + whistle) * base
def buzz(d=.6):
    t = t_(d); x = signal.sawtooth(2 * np.pi * 100 * t) * .2 + np.sin(2 * np.pi * 50 * t) * .2
    gate = (np.sin(2 * np.pi * 13 * t) > -.2).astype(float) * (np.sin(2 * np.pi * 3.1 * t) > -.6)
    return lp(x, 2500) * lp(gate, 200) * env(len(t), .01, .15)
def metal_ring(d=2.5, f=420):
    t = t_(d); x = np.zeros(len(t))
    for r, a, k in [(1, 1, 2.0), (2.76, .6, 3.0), (5.40, .35, 4.5), (8.93, .2, 6.0), (1.003, .7, 2.2)]:
        x += np.sin(2 * np.pi * f * r * t) * np.exp(-t * k) * a
    return x * .35
def roll_rumble(d, f0=7, f1=1.5):
    t = t_(d); rate = np.linspace(f0, f1, len(t)); ph = 2 * np.pi * np.cumsum(rate) / SR
    x = lp(noise(d), 220, 3) * (1 + .7 * np.sin(ph)) + bp(noise(d), 1500, 5000) * .12 * (1 + np.sin(ph * 3))
    return x * env(len(t), .02, .3, 2) * 1.4
def wobble(d=.7, r0=6, r1=34, f=1250):
    t = t_(d); rate = np.linspace(r0, r1, len(t)) ** 1; ph = 2 * np.pi * np.cumsum(rate) / SR
    am = (.5 + .5 * np.sin(ph)) ** 2
    x = (np.sin(2 * np.pi * f * t) * .4 + np.sin(2 * np.pi * f * 2.76 * t) * .15 + bp(noise(d), 2500, 7000) * .15) * am
    return x * np.linspace(.6, 1, len(t)) * env(len(t), .01, .05)
def motor(d):
    t = t_(d); f = 95 + 60 * np.clip(np.sin(np.pi * t / d), 0, 1)
    ph = 2 * np.pi * np.cumsum(f) / SR
    x = signal.sawtooth(ph) * .3 + signal.sawtooth(ph * 2.01) * .15
    return lp(x, 900) * env(len(t), .15, .25)
def rattle(d, density=30):
    x = np.zeros(int(round(d * SR)))
    for _ in range(int(d * density)):
        i = rg.integers(0, len(x) - 900); L = int(rg.integers(300, 900))
        x[i:i + L] += bp(noise(L / SR), 1500, 6000)[:L] * np.exp(-np.arange(L) / (L / 6)) * rg.uniform(.15, .5)
    return x
def pass_whoosh(d=.22):
    n = bp(noise(d), 300, 2500) * np.sin(np.linspace(0, np.pi, int(round(d * SR)))) ** 2
    return n * .5
def power_down(d=.5):
    t = t_(d); f = np.linspace(900, 80, len(t)); ph = 2 * np.pi * np.cumsum(f) / SR
    return np.sin(ph) * env(len(t), .005, d * .6) * .25
def sub_drop(d=1.8, f0=70, f1=28):
    t = t_(d); f = f0 * (f1 / f0) ** (t / d); ph = 2 * np.pi * np.cumsum(f) / SR
    return np.sin(ph) * np.exp(-t * 1.2) * 1.1
def pluck(f, d=1.2):
    t = t_(d); x = np.zeros(len(t))
    for k, a in [(1, 1), (2, .45), (3, .25), (4, .12)]:
        x += np.sin(2 * np.pi * f * k * t) * np.exp(-t * (3 + k * 1.5)) * a
    return x * env(len(t), .003, .2) * .35
def pulse_bed(d, f=55, bpm=96):
    """low trailer ostinato: short dark stabs on 8ths"""
    out = np.zeros(int(round(d * SR))); step = 60 / bpm / 2; tt = 0; k = 0
    while tt < d - .3:
        s = signal.sawtooth(2 * np.pi * f * t_(.22)) * np.exp(-t_(.22) * 14) * (1 if k % 2 == 0 else .6)
        s = lp(s, 600); i = int(tt * SR); e = min(len(out), i + len(s)); out[i:e] += s[:e - i]; tt += step; k += 1
    return out * .5

# ================= HOOK (outside) =================
m.add(0.0, load(SND + 'chirp.wav'), 1.0)                       # sound pack: Nextel walkie chirp, frame 0
m.add(.16, squelch(.42), .8, .1)
m.add(.05, static_bed(1.3), .7, .1)
m.add(0.0, boom(2.4, 36), .55)
m.add(0.0, st(wind(T['cut1'] + .3)), .55)
m.add(.7, creak(1.1, 90, 70), .25, .5)                         # crane cable groan
m.add(T['winOn'], buzz(.75), .35, .2)
m.add(T['winOn'], click(), .5, .2)
m.add(1.05, load(SND + 'whoosh.wav'), .8, -.1)                 # crash zoom
m.add(1.42, braam(2.0), .8)
m.add(1.42, boom(2.0, 44), .5)
m.add(T['shadow'] + .2, roll_rumble(1.0, 6, 3), .35, .4)        # something heavy rolls across the floor up there
m.add(T['shadow'] + .25, screech(1.1), .07)
dr = drone(T['open'] + .05) * .9; dr = fade(dr, .2, .05)
m.add(0.0, dr, .3)
pb = pulse_bed(T['open'] - .3, 55, 96); pb *= np.linspace(.5, 1.0, len(pb))
m.add(.3, fade(pb, .5, .05), .32)
# ================= CUT 1: ground floor =================
m.add(T['cut1'] - .25, riser(.25), .35)
m.add(T['cut1'], braam(2.2), .75); m.add(T['cut1'], boom(2.2, 40), .7)
m.add(T['cut1'] + .03, click(), .7, .3)                         # torch on
tt = T['cut1'] + .25
while tt < T['lift'] - .1:
    m.add(tt, step(.9), .6, .15 if int(tt * 10) % 2 else -.15); tt += 1 / 1.8
fl = bp(noise(T['lift'] - T['cut1']), 300, 3000) * (.5 + .5 * np.abs(np.sin(2 * np.pi * 1.3 * t_(T['lift'] - T['cut1']))))
m.add(T['cut1'], st(fade(fl, .2, .1)), .15)                     # plastic sheeting flapping
m.add(T['cut1'], st(wind(T['lift'] - T['cut1'], .2)), .5)
# ================= CUT 2: the lift =================
m.add(T['lift'] - .2, riser(.2), .3)
m.add(T['lift'], braam(2.0), .7); m.add(T['lift'], boom(2.0, 42), .6)
m.add(T['lift'], thud(55), .8)
m.add(T['lift'] + .05, motor(T['top'] - T['lift']), .55)
m.add(T['lift'], st(rattle(T['top'] - T['lift'], 40)), .4)
for k in range(10):                                            # each floor slab rushing past
    u = (k + .5) / 10; tt = T['lift'] + .25 + u * (T['top'] - T['lift'] - .5)
    m.add(tt, pass_whoosh(.22), .5, (-1) ** k * .3)
m.add(T['lift'] + .2, riser(T['top'] - T['lift'] - .2), .45)
m.add(T['top'], thud(48), 1.0); m.add(T['top'] + .02, st(rattle(.5, 70)), .6)
m.add(T['top'] + .08, chime(1.6, 392) * .6, .35)                # dull lift ding
# ================= TOP FLOOR =================
tt = T['top'] + .45
while tt < T['door'] - .1:
    m.add(tt, step(.8), .5, .12 if int(tt * 10) % 2 else -.12); tt += 1 / 1.6
m.add(T['top'] + .3, heartbeat(72, 128, T['open'] - T['top'] - .3), .6)
m.add(T['top'], st(wind(T['open'] - T['top'], .15)), .5)
sg = strings(T['open'] - T['top'], (220, 233.08, 246.94, 311.1)); sg *= np.linspace(0, 1, len(sg)) ** 2
m.add(T['top'], fade(sg, .1, .03), .1)
for k in range(9):                                             # torch flicker crackle
    m.add(T['torchOff'] - .45 + k * .05, click(), .25, .3)
m.add(T['torchOff'], power_down(.5), .4, .3)
m.add(T['door'], creak(.85, 150, 85), .8)
m.add(T['door'] - .2, riser(T['open'] - T['door'] + .25), .7)    # big riser into the door ... then nothing
# dead silence from T['open'] to T['hit'] (everything above is cut there)
m.L[int(T['open'] * SR):int(T['hit'] * SR)] *= 0; m.R[int(T['open'] * SR):int(T['hit'] * SR)] *= 0
# ================= THE HIT: Euro Eddie =================
m.add(T['hit'], boom(3.2, 38), .95)
m.add(T['hit'], braam(2.6), .95)
m.add(T['hit'], sub_drop(2.0), .6)
m.add(T['hit'], metal_ring(2.8, 330), .55)
m.add(T['hit'], lp(noise(.6), 2500) * np.exp(-t_(.6) * 7), .5)
m.add(T['hit'] - .05, roll_rumble(T['settle'] - T['hit'] + .1, 9, 2.0), .75)   # heavy coin rolling at you
m.add(T['settle'] - .05, wobble(.7, 6, 34, 1180), .45)           # coin wobbling down (Euler's disk)
m.add(T['settle'] + .66, metal_ring(1.2, 880) * .7, .3)          # final settle 'ting'
m.add(T['glint'], chime(2.2, 1174.66), .35)
m.add(T['glint'], shimmer(1.5), .45)
# ================= THE DROP: warm Sofa Money music =================
pad = warm_pad(D - T['glint'] + .2, 146.83)
m.add(T['glint'] - .1, pad, .45)
notes = [293.66, 369.99, 440.0, 587.33, 440.0, 369.99, 293.66, 369.99, 440.0, 554.37, 659.25, 554.37, 440.0, 369.99, 440.0, 587.33]
bt = 60 / 96 / 2
for i, f in enumerate(notes * 2):
    tt = T['phone'] + .05 + i * bt
    if tt > D - .6: break
    m.add(tt, pluck(f, .9), .22, -.25 + .5 * (i % 2))
m.add(T['phone'] - .05, load(SND + 'whoosh.wav'), .5, -.2)       # phone up
m.add(T['phone'] + .3, load(SND + 'scanbeep.wav'), .35)
# ================= END CARD =================
m.add(T['end'], boom(2.6, 44), .75); m.add(T['end'], braam(1.6) * .5, .45)
m.add(T['end'], chime(2.6, 587.33), .3); m.add(T['end'] + .02, shimmer(1.8), .3)
m.add(T['end'], warm_pad(D - T['end'], 146.83 * 1.5), .25)
m.add(T['n2'] + 2.31, load(SND + 'chirp.wav'), .7)               # walkie chirp again: loops back to the hook
# ================= VOICE =================
m.add(T['n1'], vo('n1'), 2.9, voice=True)
m.add(T['n2'], vo('n2'), 2.9, voice=True)
out = m.render(duck=.55)
out = hp(out.T, 25).T
sf.write(str(OUT / 'top-floor_audio_raw.wav'), out / np.max(np.abs(out)) * .8, SR)
print('ok', round(len(out) / SR, 2), 's;  n1 ends', round(T['n1'] + len(vo('n1')) / SR, 2), ' n2 ends', round(T['n2'] + len(vo('n2')) / SR, 2))
