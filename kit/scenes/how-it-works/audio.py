import sys, json, numpy as np, soundfile as sf
from pathlib import Path
HERE = Path(__file__).resolve().parent          # this scene's folder
KIT = HERE.parents[1]                           # the kit folder
OUT = KIT / 'out'; OUT.mkdir(exist_ok=True)
SND = str(KIT / 'sounds') + '/'                 # Sofa Money sound pack
sys.path.insert(0, str(KIT / 'tools'))
from sfx import *
from scipy.signal import resample_poly
P = sys.argv[1]
CFG = {
 'sk': dict(lines=[('sk1', .6), ('sk2', 2.4), ('sk3', 7.5), ('sk4', 11.6), ('sk5', 15.7)], explode=2.6, labels=[2.6, 2.9, 3.4, 3.9, 8.0], extra=[('flip', 7.6), ('tap', 12.35), ('sent', 16.6)], end=19.4, total=21.6, root=146.83),
 'sm': dict(lines=[('sm1', .6), ('sm2', 2.4), ('sm3', 4.6), ('sm4', 8.6), ('sm5', 12.8)], explode=1.7, labels=[2.5, 4.7, 5.6, 8.7], extra=[('scan', 4.7), ('cash', 5.6)], end=15.0, total=18.6, root=164.81),
 'ml': dict(lines=[('ml1', .6), ('ml2', 3.2), ('ml3', 7.2), ('ml4', 10.2), ('ml5', 13.8)], explode=3.2, labels=[3.3, 7.3, 10.3], extra=[('chirp', 3.7), ('lock', 7.3), ('pops', 10.4)], end=15.6, total=19.0, root=138.59),
}[P]
D = CFG['total']; m = Mix(D)
def vo(n):
    x, sr = sf.read(str(HERE / 'vo' / f'{n}.wav')); return resample_poly(x, SR, sr)
def whoosh(d=.6):
    x = bp(noise(d), 400, 5000); return x * np.sin(np.linspace(0, np.pi, len(x))) ** 2 * .7
def chirp():
    a = blip(1800, .05); b = blip(2400, .06); out = np.zeros(int(.16 * SR)); out[:len(a)] += a; i = int(.07 * SR); out[i:i + len(b)] += b; return out
# music bed: warm pad + soft pulse
pad = warm_pad(D, CFG['root']); m.add(0, pad, .28)
for k in np.arange(.5, CFG['end'], 60 / 100):
    m.add(k, lp(boom(.4, 52), 160) * .8, .3)
    m.add(k + 30 / 100, hp(noise(.04), 7000) * np.exp(-t_(.04) * 90) * .4, .25)
m.add(.05, boom(1.5, 45), .45); m.add(.1, shimmer(1.2), .3)
m.add(CFG['explode'] - .2, whoosh(.8), .6); m.add(CFG['explode'] + .2, boom(1.0, 60) * .5, .4)
for t0 in CFG['labels']: m.add(t0, blip(1500, .05), .3); m.add(t0 + .06, blip(2000, .05), .25)
for name, t0 in CFG['extra']:
    if name == 'flip': m.add(t0, whoosh(.7), .5)
    if name == 'tap': m.add(t0, chime(2.0, 1046.5), .5); m.add(t0, boom(1.0, 60) * .4, .4)
    if name == 'sent': m.add(t0, chime(1.0, 1318.5), .35)
    if name == 'scan': m.add(t0, scan_hum(1.0), .35)
    if name == 'cash': m.add(t0, cash(), .5)
    if name == 'chirp': m.add(t0, chirp(), .5); m.add(t0 + 2.6, chirp(), .4)
    if name == 'lock': m.add(t0 + .2, click(), .6); m.add(t0 + .25, thud(120) * .4, .4)
    if name == 'pops':
        for i in range(3): m.add(t0 + i * .2, blip(900 + 300 * i, .06), .35)
m.add(CFG['end'] - .6, riser(.6), .3); m.add(CFG['end'], boom(2.0, 44), .55); m.add(CFG['end'], chime(2.0, 587.33), .3)
for n, t0 in CFG['lines']: m.add(t0, vo(n), 1.05, voice=True)
out = m.render(duck=.6); out = hp(out.T, 25).T
sf.write(str(OUT / f'how-it-works-{P}_audio_raw.wav'), out / np.max(np.abs(out)) * .8, SR); print('ok', P)
