"""check_voice.py audio.wav "line" ... : transcribe (faster-whisper small.en) and check each line is heard, with numbers normalised."""
import sys, re
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
from faster_whisper import WhisperModel
import soundfile as sf, numpy as np
from scipy.signal import resample_poly
U = 'zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen seventeen eighteen nineteen'.split()
TENS = {'twenty': 20, 'thirty': 30, 'forty': 40, 'fifty': 50, 'sixty': 60, 'seventy': 70, 'eighty': 80, 'ninety': 90}
def words2num(ws):
    out, cur, tot, num = [], 0, 0, False
    def flush():
        nonlocal cur, tot, num
        if num: out.append(str(tot + cur))
        cur = tot = 0; num = False
    for i, w in enumerate(ws):
        if w in U: cur += U.index(w); num = True
        elif w in TENS: cur += TENS[w]; num = True
        elif w == 'hundred' and num: cur *= 100
        elif w == 'thousand' and num: tot += cur * 1000; cur = 0
        elif w == 'and' and num and i + 1 < len(ws) and (ws[i + 1] in U or ws[i + 1] in TENS): continue
        else: flush(); out.append(w)
    flush(); return out
def norm(s):
    s = s.lower().replace('€', ' euro ').replace(',', '')
    s = re.sub(r"(\d)\s*euro", r"\1 euro", s)
    w = re.sub(r"[^a-z0-9' ]", ' ', s).split()
    w = ['euro' if x == 'euros' else x for x in w]
    w = [{"there's": 'there is', "it's": 'it is'}.get(x, x) for x in w]
    w = ' '.join(w).split()
    return words2num(w)
m = WhisperModel('small.en', device='cpu', compute_type='int8')
x, sr = sf.read(sys.argv[1]); x = x.mean(1) if x.ndim > 1 else x
x = resample_poly(x, 16000, sr).astype(np.float32)
segs, _ = m.transcribe(x, beam_size=5, vad_filter=False)
heard = ' '.join(s.text for s in segs); print('HEARD:', heard)
H = ' '.join(norm(heard)); bad = 0
for line in sys.argv[2:]:
    w = norm(line); ok = ' '.join(w) in H
    if not ok: bad += 1
    print(('OK  ' if ok else 'MISS'), line, '' if ok else f"-> expected '{' '.join(w)}'")
print('RESULT:', 'all lines heard' if bad == 0 else f'{bad} line(s) missed')
