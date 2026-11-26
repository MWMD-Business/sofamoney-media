"""Soundtrack for Project 307 'The Vault'. Writes out/p307-vault_audio_raw.wav (48 kHz stereo).
Two voices take turns: Project 307 (am_echo) and the Sofa Money narrator (am_fenrir), levelled to match.
All synthesised (tools/sfx.py + code here) plus the sound pack (walkie chirp for MWD LINE, scan beep for Safe Key, whoosh).
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

T = dict(e1=.15, L1=2.55, f1=2.75, L2=5.55, e2=5.8, st2=6.3, L3=8.05, f2=8.25, st3=8.7, W=10.15, e3=10.35, f3=11.7,
         P4=12.75, L4=13.25, e4=13.4, f4=15.3, END=16.5, e5=16.75, f5=19.1, total=22.3)
D = T['total']; m = Mix(D)
rg = np.random.default_rng(307)


def load(p):
    x, sr = sf.read(p); x = x.mean(1) if x.ndim > 1 else x
    return resample_poly(x, SR, sr) if sr != SR else x
def vo(name, rms=.2):
    x = load(str(HERE / 'vo' / f'{name}.wav')); r = np.sqrt(np.mean(x ** 2)) + 1e-9
    return x * (rms / r)
def fade(x, a=.01, r=.05):
    x = x.copy(); na, nr = int(a * SR), int(r * SR)
    if na: x[:na] *= np.linspace(0, 1, na)
    if nr: x[-nr:] *= np.linspace(1, 0, nr)
    return x
def st(x, d=.011):
    k = int(d * SR); return np.stack([x, np.concatenate([np.zeros(k), x[:-k]])], 1)

# ---------- extra voices ----------
def relay_clunk():
    t = t_(.5); body = np.sin(2 * np.pi * 70 * t) * np.exp(-t * 16) + lp(noise(.5), 1200) * np.exp(-t * 30) * .7
    clk = bp(noise(.03), 2500, 9000) * np.exp(-t_(.03) * 160)
    body[:len(clk)] += clk * 1.2; return body
def light_buzz(d=1.6):
    t = t_(d); x = signal.sawtooth(2 * np.pi * 100 * t) * .18 + np.sin(2 * np.pi * 50 * t) * .25
    flick = np.ones(len(t)); n = int(.32 * SR)
    for i in range(0, n, int(SR / 30)):
        if rg.random() < .45: flick[i:i + int(SR / 30)] = .15
    return lp(x, 2200) * flick * env(len(t), .01, .6)
def crackle(d=.32):
    x = np.zeros(int(round(d * SR)))
    for _ in range(9):
        i = rg.integers(0, len(x) - 600); x[i:i + 600] += bp(noise(600 / SR), 2000, 8000)[:600] * np.exp(-np.arange(600) / 70) * rg.uniform(.3, 1)
    return x
def stamp_thud():
    t = t_(.4); return np.sin(2 * np.pi * 85 * t) * np.exp(-t * 20) * .9 + bp(noise(.4), 400, 3000) * np.exp(-t * 35) * .8
def pulse_bed(d, f=49, bpm=100):
    out = np.zeros(int(round(d * SR))); step = 60 / bpm / 2; tt = 0; k = 0
    while tt < d - .3:
        s = signal.sawtooth(2 * np.pi * f * t_(.22)) * np.exp(-t_(.22) * 14) * (1 if k % 2 == 0 else .55)
        s = lp(s, 650); i = int(tt * SR); e = min(len(out), i + len(s)); out[i:e] += s[:e - i]; tt += step; k += 1
    return out * .5
def data_pips(d, density=14, lo=2400, hi=5200):
    x = np.zeros(int(round(d * SR)))
    for _ in range(int(d * density)):
        i = rg.integers(0, len(x) - 3000); f = rg.uniform(lo, hi); L = int(rg.integers(600, 2400))
        x[i:i + L] += np.sin(2 * np.pi * f * np.arange(L) / SR) * np.exp(-np.arange(L) / (L / 4)) * rg.uniform(.08, .25)
    return x
def room_tone(d):
    t = t_(d); return lp(noise(d), 180) * .5 + np.sin(2 * np.pi * 50 * t) * .05 + bp(noise(d), 300, 900) * .08

# ================= bed =================
m.add(0, st(room_tone(D)), .5)
dr = drone(T['P4'] + .2, 41.2); dr *= np.linspace(.55, 1, len(dr)); m.add(0, fade(dr, .05, .4), .32)
pb = pulse_bed(T['P4'] - .3, 49, 100); pb *= np.linspace(.45, 1.0, len(pb)); m.add(.3, fade(pb, .4, .3), .34)
sg = strings(T['P4'] - T['L1'], (196, 207.65, 293.66, 311.13)); sg *= np.linspace(0, 1, len(sg)) ** 1.6; m.add(T['L1'], fade(sg, .3, .4), .08)
# ================= hook =================
m.add(0.0, boom(2.6, 36), .6)
m.add(0.0, braam(1.6) * .7, .45)
m.add(.05, data_pips(1.2, 20), .5, .2)
# ================= lights on, one by one =================
for k, (tl, chirp) in enumerate([(T['L1'], None), (T['L2'], 'scan'), (T['L3'], 'chirp')]):
    m.add(tl - .02, relay_clunk(), .95, (-.3, .3, -.3)[k])
    m.add(tl, crackle(.32), .4, (-.3, .3, -.3)[k])
    m.add(tl, light_buzz(1.4), .22, (-.3, .3, -.3)[k])
    m.add(tl, braam(1.4) * .6, .32)
    m.add(tl, boom(1.6, 46), .4)
m.add(T['L1'] + .05, shimmer(1.0), .25, -.3)                       # Euro Eddie's glint
sb = load(SND + 'scanbeep.wav'); m.add(T['L2'] + .03, sb, .6, .3)   # sound pack: Safe Key NFC tap
m.add(T['L3'] - .02, load(SND + 'chirp.wav'), .95, -.3)            # sound pack: Nextel walkie chirp for MWD LINE
m.add(T['st2'], stamp_thud(), .8); m.add(T['st3'], stamp_thud(), .8)
for i in range(4):                                                  # MWD LINE rings: soft radio squelch pulses
    m.add(T['L3'] + .4 + i * .45, bp(noise(.12), 1200, 4000) * np.exp(-t_(.12) * 25), .12, -.3)
# ================= wide: three products, one creator =================
m.add(T['W'] - .2, load(SND + 'whoosh.wav'), .6)
m.add(T['e3'] - .05, data_pips(1.0, 16), .35)
m.add(T['f3'] - .02, boom(2.2, 40), .6)
m.add(T['f3'] - .02, braam(1.8) * .7, .5)
m.add(T['f3'], light_buzz(.9) * .6, .25, -.4)
# ================= file four: almost silence =================
m.add(T['P4'] - .1, load(SND + 'whoosh.wav'), .45, .1)
m.add(T['L4'] - .02, relay_clunk() * .7, .7)
m.add(T['L4'], crackle(.32), .3)
m.add(T['L4'], light_buzz(2.2) * .7, .16)
m.add(T['P4'] + .3, heartbeat(62, 70, T['END'] - T['P4'] - .3), .5)
m.add(T['f4'] - .2, riser(T['END'] - T['f4'] + .2), .4)
m.add(T['f4'] + .05, shimmer(1.2), .3)
# ================= end card: the 307 seal =================
m.add(T['END'], boom(3.0, 34), .7)
m.add(T['END'], braam(2.4), .5)
m.add(T['END'] + .01, stamp_thud() * 1.2, .9)
end_chord = strings(D - T['END'], (146.83, 174.61, 220.0, 293.66)) * .6 + warm_pad(D - T['END'], 146.83) * .9
m.add(T['END'] + .2, fade(end_chord, .8, .6), .3)
m.add(T['f5'] + .9, data_pips(.8, 30, 3000, 6000), .55, .1)          # "> DM @project307am" typing shimmer
m.add(T['f5'] + 1.5, data_pips(.5, 20, 2500, 4500), .35)
# ================= the two voices =================
for k in ('e1', 'f1', 'e2', 'f2', 'e3', 'f3', 'e4', 'f4', 'e5', 'f5'):
    m.add(T[k], vo(k), 1.0, voice=True)
out = m.render(duck=.6)
out = hp(out.T, 25).T
sf.write(str(OUT / 'p307-vault_audio_raw.wav'), out / np.max(np.abs(out)) * .8, SR)
for k in ('e1', 'f1', 'e2', 'f2', 'e3', 'f3', 'e4', 'f4', 'e5', 'f5'):
    print(k, T[k], '->', round(T[k] + len(load(str(HERE / 'vo' / f'{k}.wav'))) / SR, 2))
print('ok', round(len(out) / SR, 2), 's')
