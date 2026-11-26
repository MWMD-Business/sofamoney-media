"""level.py in.wav out.wav  ->  sets the loudness to -14 LUFS with true peak at most -2 dB (Instagram/TikTok level).

The -2 dB leaves room for the AAC encoder, which pushes peaks up a little, so the finished video stays under -1 dB.

Two passes of ffmpeg's loudnorm: measure, then correct (linear, so the mix isn't squashed). Output is 48 kHz.
Prints the final loudness and true peak. Needs ffmpeg on PATH. Works on Windows, Mac and Linux.
"""
import json, re, subprocess, sys

TARGET_I, TARGET_TP, TARGET_LRA = -14.0, -2.0, 11.0


def ffmpeg_stderr(args):
    r = subprocess.run(['ffmpeg', '-hide_banner', '-nostats'] + args, capture_output=True, text=True,
                       encoding='utf-8', errors='replace')
    return r.returncode, r.stderr


def measure(path, tp=TARGET_TP):
    code, err = ffmpeg_stderr(['-i', path, '-af', f'loudnorm=I={TARGET_I}:TP={tp}:LRA={TARGET_LRA}:print_format=json',
                               '-f', 'null', '-'])
    j = err[err.rfind('{'): err.rfind('}') + 1]
    if code != 0 or not j:
        sys.exit(f'ffmpeg could not read {path}:\n{err[-800:]}')
    return json.loads(j)


def loudness(path):
    """Integrated loudness (LUFS) and true peak (dBFS) of a file (audio or video)."""
    _, err = ffmpeg_stderr(['-i', path, '-af', 'ebur128=peak=true', '-f', 'null', '-'])
    tail = err[err.rfind('Summary'):]
    i = re.search(r'I:\s+(-?[\d.]+|-inf) LUFS', tail)
    p = re.search(r'Peak:\s+(-?[\d.]+|-inf) dBFS', tail)
    f = lambda m: float(m.group(1)) if m and m.group(1) != '-inf' else float('-inf')
    return f(i), f(p)


def level(src, dst, tp=TARGET_TP):
    m = measure(src, tp)
    af = (f"loudnorm=I={TARGET_I}:TP={tp}:LRA={TARGET_LRA}:measured_I={m['input_i']}:measured_TP={m['input_tp']}"
          f":measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true,"
          f"aresample=48000")
    code, err = ffmpeg_stderr(['-y', '-loglevel', 'error', '-i', src, '-af', af, '-ar', '48000', dst])
    if code != 0:
        sys.exit(f'ffmpeg failed:\n{err[-800:]}')
    return loudness(dst)


if __name__ == '__main__':
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    I, P = level(sys.argv[1], sys.argv[2])
    ok = abs(I - TARGET_I) <= 0.5 and P <= -1.0
    print(f'{sys.argv[2]}: {I:.1f} LUFS, true peak {P:.1f} dB  ->  {"OK" if ok else "CHECK THIS (want -14 LUFS, peak -1 dB or lower)"}')
