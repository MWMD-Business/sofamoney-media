import sys, numpy as np, soundfile as sf
from pathlib import Path
HERE = Path(__file__).resolve().parent          # this scene's folder
KIT = HERE.parents[1]                           # the kit folder
OUT = KIT / 'out'; OUT.mkdir(exist_ok=True)
SND = str(KIT / 'sounds') + '/'                 # Sofa Money sound pack
sys.path.insert(0, str(KIT / 'tools'))
from sfx import *
T = dict(title=0, room=1.4, tv=3.0, laptop=5.0, turn=6.4, climb=7.3, hatch=9.0, attic=10.4, flash=12.0, coat=13.0, box=14.0, kneel=15.0, lid=15.3, cas=16.2, glint=16.6, phone=17.5, scan=18.0, result=19.0, n1=19.3, end=21.6, n2=21.9, total=25.5)
D = T['total']; m = Mix(D)
def vo(name):
    x, sr = sf.read(str(HERE / 'vo' / f'{name}.wav'))
    if sr != SR:
        from scipy.signal import resample_poly
        x = resample_poly(x, SR, sr)
    return x
# title
m.add(.05, boom(2.0, 38), .5)
for k in range(3): m.add(.2 + k * .5, tick(), .5)
# rain: window (living room) then roof (attic)
r = rain(T['hatch'] - T['room'] + .5)
r *= np.minimum(1, np.arange(len(r)) / (.8 * SR))
m.add(T['room'] - .3, np.stack([r, np.roll(r, 900)], 1), .32)
rr = roof_rain(D - T['hatch'])
rr *= np.minimum(1, np.arange(len(rr)) / (1.0 * SR))
m.add(T['hatch'], np.stack([rr, np.roll(rr, 700)], 1), .26)
m.add(2.4, thunder(4.5, crack=False), .35, -.4)
# drone + dread through the whole night part
dr = drone(T['end'] - T['room'] + .5); dr *= np.linspace(.4, 1, len(dr))
m.add(T['room'], dr, .22)
st = strings(T['flash'] - T['attic'] + .2); st = st * np.linspace(0, 1, len(st)) ** 2
m.add(T['attic'], st, .12)
# torch click
m.add(T['room'] - .1, click(), .7, .3)
# footsteps living room (bob 1.7 Hz)
t = T['room'] + .25
while t < T['climb']:
    m.add(t, step(.8), .55, .15 if int(t * 10) % 2 else -.15); t += 1 / 1.7
m.add(3.9, creak(.5, 160, 120), .35, -.2)
# stairs: creaky steps
t = T['climb']
while t < T['hatch'] - .15:
    m.add(t, step(1.0), .6); m.add(t + .02, creak(.35, 220 + 40 * np.sin(t * 5), 150), .28); t += .42
m.add(T['tv'] + .2, thud(60) * .0, 0)
# hatch + ladder
m.add(T['hatch'] + .12, creak(.75, 140, 90), .6)
_n = bp(noise(.45), 300, 3000); m.add(T['hatch'] + .72, _n * np.linspace(.3, 1, len(_n)) * .4, .6)
m.add(T['hatch'] + 1.15, thud(55), .8)
m.add(T['hatch'] + 1.35, step(1.0), .5)
# attic: heartbeat builds, flash scare
m.add(T['attic'] + .4, heartbeat(70, 130, T['flash'] - T['attic'] - .4), .55)
m.add(T['flash'], boom(3.0, 40), 1.0)
m.add(T['flash'], braam(2.4), .7)
m.add(T['flash'], screech(1.0), .25)
m.add(T['flash'] - .02, thunder(5.0, crack=True), .9, .5)
m.add(T['flash'] + .6, heartbeat(140, 110, 1.6), .55)
m.add(T['coat'] + .15, breath(1.0), .5)
# walk to chest
for k in range(3): m.add(T['box'] + .2 + k * .45, step(.9), .5); m.add(T['box'] + .25 + k * .45, creak(.3, 200, 160), .15)
m.add(T['kneel'] + .2, thud(45) * .5, .6)
# lid creak + case
m.add(T['lid'] - .05, creak(.85, 120, 70), .7)
m.add(T['lid'] + .7, thud(50), .5)
m.add(T['cas'], click(), .6); m.add(T['cas'] + .05, thud(120) * .4, .5)
m.add(T['glint'], chime(2.6, 659.25), .55)
m.add(T['glint'], shimmer(1.6), .5)
m.add(T['glint'] - .2, warm_pad(T['end'] - T['glint'] + 3.9, 146.83) * .9, .35)
# phone
_n = bp(noise(.35), 500, 4000); m.add(T['phone'] + .05, _n * np.linspace(1, 0, len(_n)) * .3, .5)
m.add(T['phone'] + .45, blip(1400), .5)
m.add(T['scan'], scan_hum(T['result'] - T['scan']), .35)
for k in range(4): m.add(T['scan'] + k * .25, blip(900 + k * 150, .05), .3)
m.add(T['result'], cash(), .7)
m.add(T['result'] + .02, chime(1.5, 1318.5), .3)
# end
m.add(T['end'] - 1.2, riser(1.2), .35)
m.add(T['end'], boom(3.2, 44), .7)
m.add(T['end'], chime(3.0, 587.33), .35)
m.add(T['end'] + .02, shimmer(2), .35)
# voice
m.add(T['n1'], vo('n1'), 1.0, voice=True)
m.add(T['n2'], vo('n2'), 1.0, voice=True)
out = m.render(duck=.5)
out = hp(out.T, 25).T
sf.write(str(OUT / 'burglar_audio_raw.wav'), out / np.max(np.abs(out)) * .8, SR)
print('ok', len(out) / SR)
