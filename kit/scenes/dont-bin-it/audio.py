"""Soundtrack for 'Don't bin it'. Writes out/dont-bin-it_audio_raw.wav (48 kHz stereo).
All synthesised (tools/sfx.py + code here) plus the Sofa Money sound pack (night vision, scan beep, pop, cash, whoosh).
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

T = dict(rec=1.35, rew0=1.5, rew1=2.7, m1=2.95, wait=5.0, slow=6.45, catch=7.78, stamp=7.85, tilt=8.55, scan0=9.05,
         sweep1=9.95, tag0=10.0, cash=11.2, whip=11.55, m2=11.9, end=13.8, n1=14.0, n2=15.55, total=18.3)
D = T['total']; m = Mix(D)
rg = np.random.default_rng(2860)


def load(p):
    x, sr = sf.read(p); x = x.mean(1) if x.ndim > 1 else x
    return resample_poly(x, SR, sr) if sr != SR else x
def vo(name): return load(str(HERE / 'vo' / f'{name}.wav'))
def fade(x, a=.01, r=.05):
    x = x.copy(); na, nr = int(a * SR), int(r * SR)
    if na: x[:na] *= np.linspace(0, 1, na)
    if nr: x[-nr:] *= np.linspace(1, 0, nr)
    return x
def st(x, d=.011):
    k = int(d * SR); return np.stack([x, np.concatenate([np.zeros(k), x[:-k]])], 1)
def cut(x, d): n = int(round(d * SR)); return x[:n] if len(x) >= n else np.concatenate([x, np.zeros(n - len(x))])

# ---------- extra synth voices ----------
def scratch():
    """record scratch: two fast back-and-forth pitch swipes"""
    out = []
    for a, b, d in [(260, 1500, .09), (1500, 180, .11), (300, 1100, .07)]:
        t = t_(d); f = np.linspace(a, b, len(t)); ph = 2 * np.pi * np.cumsum(f) / SR
        x = signal.sawtooth(ph) * .5 + bp(noise(d), 800, 6000) * .5
        out.append(x * np.sin(np.linspace(0, np.pi, len(t))) ** .5)
    return lp(np.concatenate(out), 7000) * .9
def tape_rewind(d):
    t = t_(d); base = 1400 + 900 * (t / d)
    f = base * (1 + .35 * np.sin(2 * np.pi * 37 * t) * np.sin(2 * np.pi * 3.3 * t) + .2 * np.sin(2 * np.pi * 11 * t))
    ph = 2 * np.pi * np.cumsum(f) / SR
    chirp = np.sin(ph) * (.5 + .5 * np.abs(np.sin(2 * np.pi * 9 * t))) * .35
    hiss = bp(noise(d), 3000, 9000) * .25
    wob = lp(noise(d), 300) * .4 * (1 + np.sin(2 * np.pi * 23 * t))
    return (chirp + hiss + wob) * env(len(t), .03, .08)
def tape_stop():
    t = t_(.35); f = 600 * np.exp(-t * 9) + 40; ph = 2 * np.pi * np.cumsum(f) / SR
    return np.sin(ph) * np.exp(-t * 5) * .5 + thud(60) [:len(t)] * .6
def wet_step():
    x = step(.8); s = bp(noise(.12), 1200, 6000) * np.exp(-t_(.12) * 30) * .35
    y = np.zeros(max(len(x), len(s))); y[:len(x)] += x; y[:len(s)] += s; return y
def plastic_tick(f):
    t = t_(.06); return (np.sin(2 * np.pi * f * t) * .5 + bp(noise(.06), 2000, 8000) * .5) * np.exp(-t * 70)
def clatter(n=7):
    out = np.zeros(int(.5 * SR))
    for k in range(n):
        i = int(rg.uniform(0, .32) * SR); x = plastic_tick(rg.uniform(700, 2600)) * rg.uniform(.4, 1)
        out[i:i + len(x)] += x
    return out
def cardboard_hit():
    t = t_(.5); body = np.sin(2 * np.pi * 95 * t) * np.exp(-t * 18) + lp(noise(.5), 900) * np.exp(-t * 22) * .9
    slap = bp(noise(.08), 600, 3500) * np.exp(-t_(.08) * 40)
    body[:len(slap)] += slap * .8; return body
def rustle(d=.4):
    return bp(noise(d), 800, 5000) * (.3 + .7 * np.abs(np.sin(2 * np.pi * 7 * t_(d)))) * env(int(round(d * SR)), .03, .1) * .4
def slow_rain(d, factor=3):
    r = rain(d / factor + .1); x = resample_poly(r, factor, 1)
    return lp(cut(x, d), 2500) * 1.3
def pluck(f, d=1.0, damp=4.0):
    t = t_(d); x = np.zeros(len(t))
    for k, a in [(1, 1), (2, .45), (3, .22), (4, .1)]:
        x += np.sin(2 * np.pi * f * k * t) * np.exp(-t * (damp + k * 1.5)) * a
    return x * env(len(t), .003, .15) * .35
def pizz(f): return pluck(f, .5, 11)
def tremolo_sting(d=1.3):
    t = t_(d); x = np.zeros(len(t))
    for f in (880, 932.3, 1318.5):
        x += np.sin(2 * np.pi * f * t + 2 * np.sin(2 * np.pi * 5.5 * t)) * .2
    return x * (.55 + .45 * np.sin(2 * np.pi * 14 * t)) * env(len(t), .4, .4)
def whoom(d=1.4):
    t = t_(d); f = 220 * np.exp(-t * 2.2) + 35; ph = 2 * np.pi * np.cumsum(f) / SR
    return (np.sin(ph) * .7 + lp(noise(d), 400) * .5) * env(len(t), .05, .5)

# ================= HOOK: slow motion, frozen in the air =================
m.add(0.0, boom(2.6, 34), .65)                                   # sound from frame 0
m.add(0.0, whoom(1.5), .55)
m.add(0.0, st(slow_rain(T['rec'] + .05)), .55)
dr = drone(T['rec'] + .05, 41.2) * np.linspace(.6, 1, int(round((T['rec'] + .05) * SR)))
m.add(0.0, dr, .35)
for k, tt in enumerate([.05, .75]):
    m.add(tt, boom(.6, 50) * .9, .5)
m.add(.1, cut(strings(1.3, (110, 116.5, 164.8)), 1.25), .08)
# record scratch + freeze
m.add(T['rec'] - .02, scratch(), .85)
# ================= REWIND =================
m.add(T['rew0'], tape_rewind(T['rew1'] - T['rew0']), .75)
m.add(T['rew0'], load(SND + 'whoosh.wav')[::-1], .5, -.3)
m.add(T['rew1'] - .05, tape_stop(), .7)
# ================= THE STORY (real time, rain) =================
r = rain(D - T['rew1']); r *= np.minimum(1, np.arange(len(r)) / (.25 * SR))
m.add(T['rew1'], np.stack([r, np.roll(r, 1100)], 1), .42)
for _ in range(40):                                              # drips on the bin lid / sill
    tt = rg.uniform(T['rew1'], D - .5); m.add(tt, plastic_tick(rg.uniform(1800, 3200)) * .25, .4, rg.uniform(-.6, .6))
for k in range(5):                                               # Mom's wet footsteps (story walk 0.5-2.0)
    m.add(T['rew1'] + .5 + k * .32, wet_step(), .55, -.1 + .05 * k)
notes = [220, 261.6, 329.6, 261.6, 246.9, 293.7, 349.2, 293.7, 220, 261.6, 329.6, 392.0, 349.2, 329.6]
for i, f in enumerate(notes):                                    # sneaky pizzicato bed under Mom
    tt = T['rew1'] + .1 + i * .16
    if tt > T['wait'] - .05: break
    m.add(tt, pizz(f), .3, -.3 + .6 * (i % 2))
    if i % 4 == 0: m.add(tt, pizz(f / 2), .3)
# "...wait."  music stops dead, sting, heart starts
m.add(T['wait'], tremolo_sting(1.3), .14)
m.add(T['wait'], boom(1.2, 55) * .6, .4)
m.add(T['wait'] + .3, heartbeat(80, 120, T['slow'] - T['wait'] - .3), .55)
# the throw
m.add(T['rew1'] + 3.0, rustle(.4), .5)
m.add(T['rew1'] + 3.55, load(SND + 'whoosh.wav'), .7, .3)
# ================= SLOW MOTION -> THE CATCH =================
m.add(T['slow'], whoom(1.4), .7)
m.add(T['slow'], heartbeat(55, 55, T['catch'] - T['slow']), .7)
m.add(T['slow'] + .1, riser(T['catch'] - T['slow'] - .1), .45)
m.add(T['catch'], cardboard_hit(), 1.0)
m.add(T['catch'], boom(2.0, 44), .8)
m.add(T['catch'] + .01, clatter(8), .6)
m.add(T['stamp'], braam(1.2) * .8, .55)
m.add(T['stamp'], bp(noise(.18), 300, 4000) * np.exp(-t_(.18) * 20), .5)
m.add(T['tilt'], rustle(.45), .45)
# ================= SOFA MONEY SCAN =================
m.add(T['scan0'] - .08, load(SND + 'nightvision.wav'), .9)       # sound pack: night vision -> scan mode
m.add(T['scan0'] + .1, scan_hum(T['sweep1'] - T['scan0'] - .1), .55)
for k in range(4): m.add(T['scan0'] + .15 + k * .2, load(SND + 'scanbeep.wav'), .4, -.4 + k * .27)
for i in range(4): m.add(T['tag0'] + i * .3, load(SND + 'pop.wav'), 1.1, (-.4, .4, -.3, .3)[i])
for i in range(12): m.add(T['tag0'] + .05 + i * .1, blip(1400 + i * 60, .03), .15)
c = fade(cut(load(SND + 'cash.wav'), .6), .001, .15); m.add(T['cash'], c, .85)
m.add(T['cash'] + .02, chime(1.2, 1318.5), .25)
gp = warm_pad(T['whip'] - T['scan0'] + .2, 146.83); m.add(T['scan0'], fade(gp, .2, .25), .65)
arp = [293.66, 369.99, 440.0, 587.33, 440.0, 369.99]
for i in range(16):
    tt = T['scan0'] + .15 + i * .15
    if tt > T['whip'] - .2: break
    m.add(tt, pluck(arp[i % 6], .6, 6), .32, -.2 + .4 * (i % 2))
# ================= PUNCH LINE: whip to the door, dead quiet (just rain) =================
m.add(T['whip'] - .02, load(SND + 'whoosh.wav'), .65, -.4)
# ================= END CARD: the drop =================
m.add(T['end'], boom(2.4, 46), .7); m.add(T['end'], chime(2.4, 587.33), .3); m.add(T['end'] + .02, shimmer(1.6), .3)
pad = warm_pad(D - T['end'], 146.83); m.add(T['end'], pad, .4)
for i, f in enumerate([293.66, 369.99, 440.0, 587.33, 440.0, 369.99, 293.66, 369.99, 440.0, 554.37, 659.25, 554.37, 440.0, 369.99, 440.0, 587.33, 440, 369.99]):
    tt = T['end'] + .1 + i * .3125
    if tt > D - .5: break
    m.add(tt, pluck(f, .9), .2, -.25 + .5 * (i % 2))
# ================= VOICES =================
m.add(T['m1'], vo('m1'), 4.4, voice=True)
m.add(T['m2'], vo('m2'), 4.6, voice=True)
m.add(T['n1'], vo('n1'), 3.3, voice=True)
m.add(T['n2'], vo('n2'), 3.3, voice=True)
out = m.render(duck=.6)
out = hp(out.T, 25).T
sf.write(str(OUT / 'dont-bin-it_audio_raw.wav'), out / np.max(np.abs(out)) * .8, SR)
for k in ('m1', 'm2', 'n1', 'n2'):
    print(k, 'from', T[k], 'to', round(T[k] + len(vo(k)) / SR, 2))
print('ok', round(len(out) / SR, 2), 's')
