"""Soundtrack for Reel 48 'POV: you just crashed a €4,000,000 jet'. Writes out/jet-crash_audio_raw.wav (48 kHz stereo).
All synthesised (tools/sfx.py + code here) plus the sound pack (whoosh, night vision, scan beep, cash, chirp).
Timings are the same T as in index.html."""
import sys, numpy as np, soundfile as sf
from pathlib import Path
HERE = Path(__file__).resolve().parent; KIT = HERE.parents[1]; OUT = KIT / 'out'; OUT.mkdir(exist_ok=True)
SND = str(KIT / 'sounds') + '/'
sys.path.insert(0, str(KIT / 'tools'))
from sfx import *
from scipy.signal import resample_poly

T = dict(n1=.15, slow=.6, freeze=2.45, reveal=2.6, n2=2.7, settle=3.5, tail=3.7, n3=3.9, riser=4.3, scan=5.2, beep=5.6,
         tag=5.7, lock=7.1, hero=7.4, n4=8.1, logo=9.9, loop=10.85, total=11.0)
D = T['total']; m = Mix(D); rg = np.random.default_rng(48)
def load(p):
    x, sr = sf.read(p); x = x.mean(1) if x.ndim > 1 else x
    return resample_poly(x, SR, sr) if sr != SR else x
def vo(k, rms=.2):
    x = load(str(HERE / 'vo' / f'{k}.wav')); return x * (rms / (np.sqrt(np.mean(x ** 2)) + 1e-9))
def fade(x, a=.005, r=.05):
    x = x.copy(); na, nr = int(a * SR), int(r * SR)
    if na: x[:na] *= np.linspace(0, 1, na)
    if nr: x[-nr:] *= np.linspace(1, 0, nr)
    return x
def siren(d):
    t = t_(d); f = np.where((t // .38) % 2 == 0, 960.0, 720.0); ph = 2 * np.pi * np.cumsum(f) / SR
    x = signal.square(ph) * .3 + np.sin(ph) * .5; return lp(x, 2500) * env(len(t), .05, .4)
def jet_roar(d):
    t = t_(d); f = np.linspace(500, 1400, len(t)); tone = np.sin(2 * np.pi * np.cumsum(f) / SR) * .15
    return (lp(noise(d), 1800) * .8 + bp(noise(d), 2500, 7000) * .3 + tone) * env(len(t), .02, d * .7)
def metal_screech(d=1.0):
    t = t_(d); f = 2400 + 600 * np.sin(2 * np.pi * 7 * t) + 300 * np.sin(2 * np.pi * 13 * t)
    x = bp(noise(d), 1800, 5200) * .5 + np.sin(2 * np.pi * np.cumsum(f) / SR) * .12
    return x * env(len(t), .01, .5)
def crackle(d, dens=70):
    x = np.zeros(int(round(d * SR)))
    for _ in range(int(d * dens)):
        i = rg.integers(0, len(x) - 700); x[i:i + 700] += bp(noise(700 / SR), 2500, 9000)[:700] * np.exp(-np.arange(700) / 60) * rg.uniform(.2, 1)
    return x
def tink():
    t = t_(.5); return (np.sin(2 * np.pi * 3150 * t) + .5 * np.sin(2 * np.pi * 4720 * t)) * np.exp(-t * 14) * .5
def kick():
    t = t_(.35); f = 130 * np.exp(-t * 26) + 44; return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 7)
def snare():
    t = t_(.22); return (bp(noise(.22), 1200, 7000) * .7 + np.sin(2 * np.pi * 190 * t) * .4) * np.exp(-t * 18)
def hat():
    return hp(noise(.05), 7000) * np.exp(-t_(.05) * 70) * .5
def beat(d, bpm=124):
    out = np.zeros(int(round(d * SR))); b = 60 / bpm
    for i in range(int(d / (b / 2))):
        for x, g, on in [(kick(), 1.0, i % 4 == 0 or i % 8 == 7), (snare(), .8, i % 4 == 2), (hat(), .5, True)]:
            if on:
                s = int(i * b / 2 * SR); e = min(len(out), s + len(x)); out[s:e] += x[:e - s] * g
    return out
def bassline(d, root=49.0, bpm=124):
    out = np.zeros(int(round(d * SR))); b = 60 / bpm; notes = [root, root, root * 1.335, root * 1.19]
    for i in range(int(d / b)):
        t = t_(b * .9); x = lp(signal.sawtooth(2 * np.pi * notes[(i // 2) % 4] * t), 420) * np.exp(-t * 3)
        s = int(i * b * SR); e = min(len(out), s + len(x)); out[s:e] += x[:e - s]
    return out * .55
def pulse_bed(d, f=41.2, bpm=96):
    out = np.zeros(int(round(d * SR))); stp = 60 / bpm / 2; k = 0
    while k * stp < d - .2:
        s = lp(signal.sawtooth(2 * np.pi * f * t_(.2)), 600) * np.exp(-t_(.2) * 14) * (1 if k % 2 == 0 else .5)
        i = int(k * stp * SR); e = min(len(out), i + len(s)); out[i:e] += s[:e - i]; k += 1
    return out * .6

# ================= crash (0 - 2.45) =================
FR = T['freeze']
bed = drone(FR + .3, 41.2) * .6 + pulse_bed(FR + .3) + braam(FR + .3) * .35
m.add(0, fade(bed[:int(FR * SR)], .002, .01), .5)
m.add(0, boom(2.4, 36), 1.0)                       # impact on frame 0
m.add(0, bp(noise(.25), 200, 3000) * np.exp(-t_(.25) * 18) * 1.4, .8)
m.add(.02, metal_screech(1.1), .45, .2)
m.add(0, crackle(2.2), .35, -.1)
m.add(0, jet_roar(1.2) * np.linspace(1, .2, int(round(1.2 * SR))), .35, -.3)
m.add(.25, siren(2.1), .12, .4)
# record scratch made from the bed itself, then dead silence
snip = bed[int((FR - .5) * SR):int(FR * SR)]; d = .3; tt = t_(d)
pos = np.where(tt < .08, .35 + 1.6 * tt, np.where(tt < .18, .478 - 2.2 * (tt - .08), .26 + .8 * (tt - .18) * np.exp(-(tt - .18) * 6)))
scr = np.interp(np.clip(pos * SR, 0, len(snip) - 1), np.arange(len(snip)), snip)
scr = bp(scr, 250, 5000) * 2.5 + bp(noise(d), 1200, 4000) * .05 * np.abs(np.gradient(pos)) * SR
m.add(FR, fade(scr / (np.max(np.abs(scr)) + 1e-9) * .9, .002, .05), .9)
# ================= reveal =================
m.add(T['reveal'], load(SND + 'whoosh.wav'), .7)
m.add(T['settle'] - .05, tink(), .5, .2)
m.add(T['tail'] - .02, boom(1.0, 55) * .5, .3)
m.add(T['tail'], bp(noise(.3), 600, 6000) * np.exp(-t_(.3) * 12), .25)
m.add(T['riser'], riser(T['scan'] - T['riser']), .4)
# ================= scan =================
m.add(T['scan'], load(SND + 'nightvision.wav'), .9)
m.add(T['scan'], boom(1.6, 44), .4)
m.add(T['beep'], load(SND + 'scanbeep.wav'), .7)
m.add(T['scan'] + .2, scan_hum(T['lock'] - T['scan'] - .2), .25)
for i in range(int((T['lock'] - T['tag']) / .085)):
    m.add(T['tag'] + i * .085, blip(1400 + rg.integers(0, 1600), .05), .18, rg.uniform(-.4, .4))
# ================= the drop: price lock =================
L = T['lock']
m.add(L, load(SND + 'cash.wav'), .95)
m.add(L, boom(2.6, 38), 1.0); m.add(L, braam(1.6), .45); m.add(L + .02, shimmer(1.4), .35)
m.add(L, beat(T['logo'] - L), .45); m.add(L, bassline(T['logo'] - L), .55)
# ================= logo + loop tail =================
m.add(T['logo'], load(SND + 'chirp.wav'), .95)
m.add(T['logo'], boom(1.0, 46), .5); m.add(T['logo'] + .02, chime(.9, 784), .25)
pre = bp(noise(.15), 300, 4000) * np.linspace(0, 1, int(round(.15 * SR))) ** 2
m.add(T['loop'], pre, .6); m.add(T['loop'], jet_roar(.15)[::-1] * .8, .4)
# ================= background music after the reveal (light plucky groove -> the drop) =================
def pluck(f, d=.32):
    t = t_(d); return (np.sin(2 * np.pi * f * t) + .35 * np.sin(4 * np.pi * f * t) + .12 * np.sin(6 * np.pi * f * t)) * np.exp(-t * 11)
b8 = 60 / 124 / 2; notes = [220, 261.63, 329.63, 392, 329.63, 261.63, 293.66, 349.23]
t0 = T['reveal'] + .25; i = 0
while t0 + i * b8 < L - .05:
    m.add(t0 + i * b8, pluck(notes[i % 8] * (1 if (i // 8) % 2 == 0 else 1.122)), .16 * min(1, .4 + i * .03), (-.3, .3)[i % 2]); i += 1
m.add(T['reveal'] + .25, fade(warm_pad(L - T['reveal'] - .25, 110.0), .4, .1), .18)
m.add(T['tail'], beat(T['scan'] - T['tail'])[:int((T['scan'] - T['tail']) * SR)] * .5, .22)
m.add(T['scan'], beat(L - T['scan']) * .7, .26)
m.add(T['logo'], fade(warm_pad(T['loop'] - T['logo'], 146.83), .02, .15), .3)
m.add(T['tail'] - .25, load(SND + 'whoosh.wav'), .45)
m.add(L - .3, load(SND + 'whoosh.wav')[::-1], .4)
# ================= narrator =================
for k in ('n1', 'n2', 'n3', 'n4'):
    m.add(T[k], vo(k), 1.0, voice=True)
out = m.render(duck=.6, fade_out=.01); out = hp(out.T, 25).T
sf.write(str(OUT / 'jet-crash_audio_raw.wav'), out / np.max(np.abs(out)) * .8, SR)
for k in ('n1', 'n2', 'n3', 'n4'):
    print(k, T[k], '->', round(T[k] + len(load(str(HERE / 'vo' / f'{k}.wav'))) / SR, 2))
