"""Fast mystery-box reel soundtrack (9 s loop). Writes out/mystery-box_audio_raw.wav. Synth + sound pack, no voice."""
import sys, numpy as np, soundfile as sf
from pathlib import Path
HERE = Path(__file__).resolve().parent; KIT = HERE.parents[1]; OUT = KIT / 'out'; SND = str(KIT / 'sounds') + '/'
sys.path.insert(0, str(KIT / 'tools'))
from sfx import *
from scipy.signal import resample_poly
T = dict(c2=.4, c1=.8, o1=1.2, o2=2.3, o3=3.4, scan=4.3, lock=4.9, hero=5.5, end=6.7, loop=8.6, total=9.0)
D = T['total']; m = Mix(D)
def load(p):
    x, sr = sf.read(p); x = x.mean(1) if x.ndim > 1 else x
    return resample_poly(x, SR, sr) if sr != SR else x
def kick():
    t = t_(.3); return np.sin(2 * np.pi * np.cumsum(130 * np.exp(-t * 26) + 44) / SR) * np.exp(-t * 8)
def snare():
    t = t_(.2); return (bp(noise(.2), 1200, 7000) * .7 + np.sin(2 * np.pi * 190 * t) * .4) * np.exp(-t * 18)
def hat(): return hp(noise(.05), 7000) * np.exp(-t_(.05) * 70) * .5
def beat(d, bpm=150, start=0.0):
    out = np.zeros(int(round(d * SR))); b = 60 / bpm
    for i in range(int(d / (b / 2))):
        for x, g, on in [(kick(), 1.0, i % 4 == 0), (snare(), .8, i % 4 == 2), (hat(), .45, True)]:
            if on: s = int(i * b / 2 * SR); e = min(len(out), s + len(x)); out[s:e] += x[:e - s] * g
    return out
def bass(d, root=55.0, bpm=150):
    out = np.zeros(int(round(d * SR))); b = 60 / bpm
    for i in range(int(d / b)):
        f = [root, root, root * 1.19, root * .89][(i // 2) % 4]; t = t_(b * .9)
        x = lp(signal.sawtooth(2 * np.pi * f * t), 450) * np.exp(-t * 3); s = int(i * b * SR); e = min(len(out), s + len(x)); out[s:e] += x[:e - s]
    return out * .6
def buzzer():
    t = t_(.35); return lp(signal.square(2 * np.pi * 110 * t) * .5 + signal.square(2 * np.pi * 116 * t) * .5, 1800) * env(len(t), .005, .08)
def tick(f=1800):
    t = t_(.08); return np.sin(2 * np.pi * f * t) * np.exp(-t * 60)
# countdown + tense bed
for i, tt in enumerate([0, T['c2'], T['c1']]): m.add(tt, tick(1500 + 300 * i), .6); m.add(tt, boom(.4, 60) * .5, .4)
m.add(0, beat(T['o3'], 150) * np.linspace(.6, 1, int(round(T['o3'] * SR))), .42)
m.add(0, bass(T['o3']), .45)
m.add(0, riser(T['o3']) * .5, .25)
# box openings
for i, o in enumerate([T['o1'], T['o2'], T['o3']]):
    m.add(o - .15, load(SND + 'whoosh.wav'), .5, (-.3, 0, .3)[i])
    m.add(o, load(SND + 'pop.wav'), .8)
    if i < 2: m.add(o + .55, buzzer(), .45)
# jackpot drop
J = T['o3']
m.add(J + .1, boom(2.2, 38), 1.0); m.add(J + .1, braam(1.4), .5); m.add(J + .12, shimmer(1.2), .4)
m.add(J + .1, beat(T['end'] - J - .1, 128) * 1.0, .45); m.add(J + .1, bass(T['end'] - J - .1, 49.0, 128), .5)
m.add(T['scan'], load(SND + 'nightvision.wav'), .85); m.add(T['scan'] + .3, load(SND + 'scanbeep.wav'), .6)
for i in range(int((T['lock'] - T['scan'] - .2) / .07)): m.add(T['scan'] + .2 + i * .07, blip(1400 + 90 * (i % 9), .04), .15)
m.add(T['lock'], load(SND + 'cash.wav'), .95); m.add(T['lock'], boom(1.6, 42), .6)
# end card + loop lead-in
m.add(T['end'], load(SND + 'chirp.wav'), .9); m.add(T['end'], warm_pad(T['loop'] - T['end'], 146.83), .35); m.add(T['end'] + .05, chime(1.2, 784), .3)
m.add(T['loop'], tick(1500), .6); m.add(T['loop'], boom(.4, 60) * .5, .4)
out = m.render(duck=.0, fade_out=.01); out = hp(out.T, 25).T
sf.write(str(OUT / 'mystery-box_audio_raw.wav'), out / np.max(np.abs(out)) * .8, SR); print('ok')
