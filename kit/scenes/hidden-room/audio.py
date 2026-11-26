"""Sound for 'There's €1,240 hidden in this room' (Sofa Money Reel). All music + effects synthesised here
(plus the Sofa Money sound pack in the kit's sounds/ folder). Writes out/hidden-room_audio_raw.wav (48 kHz stereo).
Run from anywhere: python scenes/hidden-room/audio.py"""
import sys, numpy as np, soundfile as sf
from pathlib import Path
HERE = Path(__file__).resolve().parent          # this scene's folder
KIT = HERE.parents[1]                           # the kit folder
OUT = KIT / 'out'; OUT.mkdir(exist_ok=True)
SND = str(KIT / 'sounds') + '/'                 # Sofa Money sound pack
sys.path.insert(0, str(KIT / 'tools'))
from sfx import SR, t_, env, bp, lp, hp, noise, rain, boom, riser, chime, shimmer
from scipy.signal import resample_poly, fftconvolve

D = 14.3; N = int(round(D * SR))
R = np.random.default_rng(1240)
# timeline (matches index.html)
SCRATCH, BACK0, SCAN0, TOTAL, ENDIN, LOOP = 4.52, 4.9, 5.7, 9.7, 11.5, 13.85
POPS = [6.2, 6.7, 7.2, 7.7, 8.2, 8.7]
VO = {'n1': .02, 'n2': 4.84, 'n3': 10.02, 'n4': 11.62}

mus = np.zeros((N, 2)); fx = np.zeros((N, 2)); vox = np.zeros(N)

def st(x, pan=0.0):
    if x.ndim == 2: return x
    return np.stack([x * np.cos((pan + 1) * np.pi / 4) * 1.414, x * np.sin((pan + 1) * np.pi / 4) * 1.414], 1)
def put(buf, t, x, g=1.0, pan=0.0):
    if buf.ndim == 2: x = st(x, pan)
    i = int(round(t * SR))
    if i < 0: x = x[-i:]; i = 0
    e = min(len(buf), i + len(x))
    if e > i: buf[i:e] += x[:e - i] * g
def load(p, sr_to=SR):
    x, sr = sf.read(p); x = x.mean(1) if x.ndim > 1 else x
    if sr != sr_to: x = resample_poly(x, sr_to, sr)
    return x
def fade(x, a=.004, r=.03):
    x = x.copy(); na = max(1, int(a * SR)); nr = max(1, int(r * SR)); x[:na] *= np.linspace(0, 1, na); x[-nr:] *= np.linspace(1, 0, nr); return x
mtof = lambda m: 440 * 2 ** ((m - 69) / 12)

# ---------------- instruments ----------------
def ep(f, d, vel=1.0):  # FM electric piano (Rhodes-like)
    t = t_(d); I = 1.6 * np.exp(-t * 5) * vel + .22
    x = np.sin(2 * np.pi * f * t + I * np.sin(2 * np.pi * f * t)) * np.exp(-t * 1.0)
    x += np.sin(2 * np.pi * f * 14.05 * t) * np.exp(-t * 32) * .07 * vel
    x *= 1 + .16 * np.sin(2 * np.pi * 4.2 * t)
    return fade(x * vel, .003, .12)
def chord(notes, d, vel=1.0, spread=.014):
    out = np.zeros(int(round((d + spread * len(notes)) * SR)))
    for i, m in enumerate(notes):
        x = ep(mtof(m), d, vel * (.88 + .24 * R.random())); s = int(i * spread * SR); out[s:s + len(x)] += x
    return lp(out, 3400) * .2
def kick(p=1.0):
    d = .42; t = t_(d); f = 44 + 120 * np.exp(-t * 30); x = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 7.5)
    c = hp(noise(.012), 1800) * np.exp(-t_(.012) * 380) * .45 * p; x[:len(c)] += c
    return np.tanh(x * 1.7) * .85
def softkick():
    return lp(kick(.3), 900) * .8
def clap():
    d = .3; x = np.zeros(int(d * SR))
    for k, off in enumerate([0, .012, .024]):
        n = bp(noise(.25), 900, 6000) * np.exp(-t_(.25) * (70 if k < 2 else 16)); i = int(off * SR); m = min(len(n), len(x) - i); x[i:i + m] += n[:m]
    x += np.sin(2 * np.pi * 185 * t_(d)) * np.exp(-t_(d) * 28) * .25
    return x * .55
def rim():
    d = .08; return (bp(noise(d), 1500, 5000) * np.exp(-t_(d) * 90) + np.sin(2 * np.pi * 820 * t_(d)) * np.exp(-t_(d) * 70) * .4) * .4
def hat(o=False):
    d = .28 if o else .055; return hp(noise(d), 7200, 4) * np.exp(-t_(d) * (11 if o else 85)) * .33
def sub(m, d):
    t = t_(d); f = mtof(m) * (1 + .9 * np.exp(-t * 45)); x = np.sin(2 * np.pi * np.cumsum(f) / SR)
    x = np.tanh(x * 2.0 * np.exp(-t * (1.2 / max(d, .2)))) ; return fade(x, .002, .04) * .62
def bell(m, d=.7, vel=1.0):
    f = mtof(m); t = t_(d); I = 2.6 * np.exp(-t * 7)
    return fade(np.sin(2 * np.pi * f * t + I * np.sin(2 * np.pi * f * 3.5 * t)) * np.exp(-t * 4.5) * vel * .22, .001, .05)
def pad(notes, d, cut=1600):
    t = t_(d); x = np.zeros(len(t))
    for m in notes:
        for det in (-.12, .12):
            ph = 2 * np.pi * mtof(m + det) * t + R.random() * 6
            x += (2 * ((ph / (2 * np.pi)) % 1) - 1) * .06
    return lp(x, cut) * env(len(t), .35, .6, 2)
def crash(d=2.2):
    t = t_(d); x = hp(noise(d), 4500, 2) * np.exp(-t * 2.2) * .5
    for k in range(10): x += np.sin(2 * np.pi * R.uniform(3000, 9000) * t + R.random() * 6) * np.exp(-t * 3) * .02
    return x
def whoosh(d=.5, up=True):
    t = t_(d); n = noise(d); out = np.zeros(len(t)); seg = int(.01 * SR)
    for i in range(0, len(t) - seg, seg):
        u = i / len(t); fc = 400 + (5000 if up else 3000) * (u if up else 1 - u)
        out[i:i + seg] = bp(n[i:i + seg + 200], fc * .6, min(fc * 1.6, 20000))[:seg]
    return out * np.sin(np.linspace(0, np.pi, len(t))) ** 1.5 * .9
def rev_cymbal(d=.7):
    return crash(d)[::-1] * np.linspace(0, 1, int(round(d * SR))) ** 1.5
def coin(f0, a=1.0):
    d = .55; t = t_(d); x = np.zeros(len(t))
    for r, k, g in [(1, 9, 1), (2.76, 14, .7), (5.4, 22, .45), (8.93, 30, .3)]:
        x += np.sin(2 * np.pi * f0 * r * t + R.random() * 6) * np.exp(-t * k) * g
    x += hp(noise(d), 5000) * np.exp(-t * 120) * .3
    return x * .16 * a
def fwump():
    d = .45; t = t_(d); x = lp(noise(d), 700) * np.sin(np.linspace(0, np.pi, len(t))) ** 2 * .6
    x += np.sin(2 * np.pi * (90 - 40 * t) * t) * np.exp(-t * 9) * .4
    return x
def bloop():
    d = .17; t = t_(d); f = 760 * np.exp(-t * 7) + 230
    return fade(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 6) * .35, .002, .03)
def crackle(d):
    x = lp(noise(d), 3000) * .012
    for _ in range(int(d * 22)):
        i = R.integers(0, len(x) - 300); x[i:i + 60] += hp(noise(60 / SR), 2000)[:60] * R.uniform(.05, .3)
    return x

# ---------------- HOOK (0 - 4.52): cosy lo-fi with tension ----------------
B = .5  # 120 bpm
Fm9 = [53, 56, 60, 63, 67]; Dbmaj9 = [49, 56, 60, 63, 65]; C7b9 = [48, 52, 58, 61, 67]
put(mus, 0.0, chord(Fm9, 2.2, 1.0), 1.0)
put(mus, 1.25, chord(Fm9[1:], .9, .6), .9)
put(mus, 1.75, chord([56, 60, 63, 67], .5, .5), .7)
put(mus, 2.0, chord(Dbmaj9, 1.4, .95), 1.0)
put(mus, 0.0, sub(41, 1.9), .55); put(mus, 2.0, sub(37, 1.2), .55)
for k in range(9):
    t = k * B
    if t >= SCRATCH: break
    if k % 4 in (0, 2) and t < 3.0: put(mus, t, softkick(), .7)
    if k % 2 == 1 and t < 3.0: put(mus, t, rim(), .55, .15)
    for h in (0, .25):
        if t + h < 3.0: put(mus, t + h + (.03 if h else 0), hat(), .35 if h else .22, -.2)
put(mus, 0.0, crackle(4.5), 1.0)
# suspense into the cushion: C7b9 tremolo pad + heartbeat kicks
sp = pad(C7b9, 1.6, 1200); sp *= 1 + .35 * np.sin(2 * np.pi * 8 * t_(1.6)); sp *= np.linspace(.4, 1.1, len(sp))
put(mus, 2.95, sp, .9)
for t in (3.0, 3.5, 4.0):
    put(mus, t, softkick(), .9)
put(mus, 3.25, chord([60, 64, 67, 70, 73], 1.3, .55), .55)
# hard stop of the music at the scratch (dead silence after the punchline)
i0 = int(SCRATCH * SR)
snip = mus[int((SCRATCH - .34) * SR):i0].mean(1).copy()
mus[i0:int(SCAN0 * SR)] *= 0

# ---------------- DROP (5.7 - 9.7): beat + scan pops ----------------
G0 = SCAN0
prog = [(G0, [41], [53, 56, 60, 65]), (G0 + 1.0, [37], [53, 56, 61, 65]), (G0 + 2.0, [44], [56, 60, 63, 68]), (G0 + 3.0, [39], [55, 58, 63, 67])]
for t, bs, ch in prog:
    put(mus, t, chord(ch, 1.05, .9), 1.25)
    put(mus, t, pad(ch, 1.05, 2200), .6)
    b = bs[0]
    put(mus, t, sub(b, .45), 1.0); put(mus, t + .75, sub(b, .2), .85); put(mus, t + .875, sub(b + 12, .12), .5)
for k in range(8):
    t = G0 + k * B
    put(mus, t, kick(), 1.0)
    if k % 2 == 1: put(mus, t, clap(), .95)
    put(mus, t + .25, hat(True), .5, .2)
    for h in (.125, .375): put(mus, t + h, hat(), .35, -.25)
# gold bell arps (16ths, quiet)
arp_notes = [[65, 68, 72, 77], [65, 68, 73, 77], [68, 72, 75, 80], [67, 70, 75, 79]]
for bi, (t, _, _) in enumerate(prog):
    for s in range(8):
        put(mus, t + s * .125, bell(arp_notes[bi][s % 4], .35, .55 if s % 2 else .8), .55, .35 if s % 2 else -.35)
# snare roll + riser into the total
for j in range(8):
    put(mus, TOTAL - .5 + j * .0625, clap() * (.35 + .65 * j / 7), .5)
put(fx, TOTAL - 1.0, riser(1.0), .3)

# ---------------- TOTAL + PUNCH (9.7 - 11.5) ----------------
Ab = [56, 60, 63, 68, 72]
put(mus, TOTAL, chord(Ab, 1.9, 1.0), 1.3); put(mus, TOTAL, pad(Ab, 1.85, 2600), .9)
put(mus, TOTAL, sub(44, 1.0), 1.0)
put(mus, TOTAL, crash(2.4), .55)
for t in (TOTAL, TOTAL + 1.0): put(mus, t, kick(), .8)
for t in (TOTAL + .5, TOTAL + 1.5): put(mus, t, clap(), .55)
for k in range(8): put(mus, TOTAL + k * .25, hat(), .25, .2)

# ---------------- END CARD (11.5 - 13.85): Db - Eb - Ab cadence ----------------
cad = [(ENDIN + .2, 37, [53, 56, 61, 65], 1.0), (ENDIN + 1.2, 39, [55, 58, 63, 67], .5), (ENDIN + 1.7, 44, [56, 60, 63, 68, 72], .65)]
for t, b, ch, d in cad:
    put(mus, t, chord(ch, d + .05, .85), 1.1); put(mus, t, pad(ch, d + .05, 2000), .55); put(mus, t, sub(b, d), .8)
for k in range(4): put(mus, ENDIN + .2 + k * .5, kick(), .55)
for k in range(8): put(mus, ENDIN + .2 + k * .25, hat(), .22)
for s, m in enumerate([68, 72, 75, 80, 84]): put(mus, ENDIN + 1.7 + s * .08, bell(m, .9, .9), .6)
put(fx, ENDIN + 1.7, shimmer(1.2), .25)

# ---------------- LOOP TAIL (13.85 - 14.3): back to the cosy start ----------------
put(mus, LOOP, chord(Fm9, .5, .8), .9); put(mus, LOOP, crackle(.45), 1.0)

# ---------------- SOUND EFFECTS ----------------
# frame-0 hit + whooshes
put(fx, 0.0, boom(1.4, 38), .35)
put(fx, 2.88, load(SND + 'whoosh.wav'), .55, -.2); put(fx, 2.92, whoosh(.45, True), .35)
put(fx, 3.26, fwump(), .9)                              # cushion lifts
for i, (dt, f0) in enumerate([(0, 3300), (.07, 4100), (.13, 3700)]): put(fx, 4.0 + dt, coin(f0), 1.0, (-.3, .25, 0)[i])
put(fx, 4.2, bloop(), .9)                               # ...and the TV remote
# record scratch made from the music itself (DJ-style back-and-forth)
d = .42; tt = t_(d)
pos = np.where(tt < .09, .12 + 2.0 * tt, np.where(tt < .21, .30 - 2.2 * (tt - .09), .036 + 1.2 * (tt - .21) * np.exp(-(tt - .21) * 5)))
rate = np.abs(np.gradient(pos)) * SR
scr = np.interp(np.clip(pos * SR, 0, len(snip) - 1), np.arange(len(snip)), snip)
scr = bp(scr, 250, 5000) * 2.2 + bp(noise(d), 1200, 4000) * .04 * rate
scr = fade(scr, .002, .06); scr = scr / (np.max(np.abs(scr)) + 1e-9) * .9
put(fx, SCRATCH, scr, .95)
put(fx, BACK0 + .02, load(SND + 'whoosh.wav')[::-1], .5); put(fx, BACK0 + .1, whoosh(.5, False), .3)
put(fx, SCAN0 - .62, rev_cymbal(.62), .45)
put(fx, SCAN0, load(SND + 'nightvision.wav'), .9)        # sound pack #1: night vision -> scan mode on
put(fx, SCAN0, boom(2.0, 40), .55)
put(fx, SCAN0, crash(1.6), .35)
pentas = [80, 84, 87, 89, 92, 96]
for i, p in enumerate(POPS):
    put(fx, p, load(SND + 'scanbeep.wav'), .5, (-.5 + i * .2))
    put(fx, p + .02, bell(pentas[i], .6, 1.0), .9, (-.5 + i * .2))
    put(fx, p + .02, coin(2600 + i * 250, .7), .7)
c = load(SND + 'cash.wav'); c = fade(c[:int(.36 * SR)], .001, .12)
put(fx, TOTAL, c, 1.0)                                  # sound pack: cash register (ends before the next line)
put(fx, TOTAL, boom(2.2, 36), .8)
put(fx, ENDIN - .03, load(SND + 'chirp.wav'), .85)         # sound pack #2: walkie chirp on the end card
put(fx, ENDIN - .05, whoosh(.4, True), .3)
# rain bed (cut for the dead silence)
rb_ = rain(D, .8); rb_ = np.stack([rb_, np.roll(rb_, 1100)], 1)
g = np.ones(N); a, b_ = int(SCRATCH * SR), int((BACK0 + .5) * SR); g[a:b_] = np.concatenate([np.linspace(1, .0, int(.05 * SR)), np.zeros(b_ - a - int(.05 * SR))]); g[b_:b_ + int(.5 * SR)] = np.linspace(0, 1, int(.5 * SR))
fx += rb_ * g[:, None] * .07

# ---------------- VOICE ----------------
for k, t in VO.items():
    x = hp(load(str(HERE / 'vo' / f'{k}.wav')), 70)
    sp_ = x[np.convolve(np.abs(x), np.ones(480) / 480, 'same') > np.max(np.abs(x)) * .03]
    x = x / (np.sqrt((sp_ ** 2).mean()) + 1e-9) * .15        # same speech loudness for every line
    x = np.tanh(x * 1.4) / 1.4
    put(vox, t, x, 1.0)

# ---------------- MIX ----------------
e = lp(np.abs(vox), 9, 1); e = np.clip(e / (np.max(e) + 1e-9) * 5, 0, 1)
sh = int(.06 * SR); e = np.concatenate([e[sh:], np.zeros(sh)])
duck = 1 - .72 * lp(e, 6, 1).clip(0, 1)
dg = np.ones(N); i1, i2 = int(SCAN0 * SR), int((TOTAL + .4) * SR); dg[i1:i2] = .78
musm = mus * .55 * dg[:, None]; fxm = fx * .7
bed = (musm + fxm) * duck[:, None]
mix = bed + st(vox) * .72
# gentle bus glue + soft limit
mix = np.tanh(mix * 1.15) / 1.15
mix = hp(mix.T, 28).T
mix /= np.max(np.abs(mix)) + 1e-9
sf.write(str(OUT / 'hidden-room_audio_raw.wav'), mix * .89, SR)
sf.write(str(OUT / 'hidden-room_vox_only.wav'), vox / (np.max(np.abs(vox)) + 1e-9) * .8, SR)
print('ok', mix.shape, D)
