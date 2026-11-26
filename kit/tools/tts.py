"""Makes the voice lines with Kokoro (runs on your own PC, free).
Usage:  python tools/tts.py scenes/<name>/lines.json scenes/<name>/vo
lines.json: [{"id": "n1", "voice": "am_fenrir", "text": "Say numbers in words.", "speed": 1.0, "pitch": 0}]
Writes vo/<id>.wav (24 kHz, silence trimmed) and prints each line's length in seconds.
Voices: am_fenrir = the Sofa Money narrator, af_heart = Mom. pitch is in semitones (uses ffmpeg)."""
import json, sys, os, subprocess
import numpy as np, soundfile as sf
from kokoro import KPipeline

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
lines = json.load(open(sys.argv[1], encoding='utf-8')); out = sys.argv[2]; os.makedirs(out, exist_ok=True)
pipes = {}
for L in lines:
    lang = 'b' if L['voice'].startswith('b') else 'a'
    if lang not in pipes: pipes[lang] = KPipeline(lang_code=lang)
    p = pipes[lang]
    audio = []
    for _, _, a in p(L['text'], voice=L['voice'], speed=L.get('speed', 1.0)):
        audio.append(a.numpy() if hasattr(a, 'numpy') else np.asarray(a))
    a = np.concatenate(audio).astype(np.float32)
    raw = f"{out}/{L['id']}_raw.wav"; sf.write(raw, a, 24000)
    dst = f"{out}/{L['id']}.wav"
    semis = L.get('pitch', 0)
    if semis:
        r = 2 ** (semis / 12)
        f = f"asetrate={int(24000*r)},aresample=24000,atempo={1/r:.5f}"
        subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', raw, '-af', f, dst], check=True)
    else:
        os.replace(raw, dst)
    d, sr = sf.read(dst)
    # trim silence
    thr = 0.01; idx = np.where(np.abs(d) > thr)[0]
    d = d[max(0, idx[0]-2400): idx[-1]+1200]
    sf.write(dst, d, sr)
    print(L['id'], round(len(d)/sr, 2))
