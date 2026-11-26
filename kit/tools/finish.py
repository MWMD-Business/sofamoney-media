"""finish.py video.mp4 audio_raw.wav OUT.mp4  ->  the finished Reel.

1. Levels the audio to -14 LUFS, true peak -2 dB (tools/level.py), so the final file stays under -1 dB.
2. Puts it on the silent render with Instagram-safe settings: H.264 1080x1920, 30 fps, at most 16 Mbps,
   AAC 192 kbps 48 kHz, fast start.
3. Checks the video and audio lengths match and prints the final loudness.
Writes to a temporary name first and renames at the end, so a stopped run never leaves a half file.
"""
import os, subprocess, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from level import level, loudness  # noqa: E402


def duration(path):
    r = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', path],
                       capture_output=True, text=True)
    try:
        return float(r.stdout.strip())
    except ValueError:
        sys.exit(f'ffprobe could not read {path}')


def main(video, audio, out):
    out = Path(out); out.parent.mkdir(parents=True, exist_ok=True)
    leveled = str(out.with_name(out.stem + '_audio.wav'))
    tmp = str(out.with_name(out.stem + '.tmp.mp4'))
    # The AAC encoder can push peaks up, so if the finished file peaks above -1 dB, level again with more headroom.
    for tp in (-2.0, -3.5, -5.0):
        level(audio, leveled, tp)
        dv, da = duration(video), duration(leveled)
        if abs(dv - da) > 0.15:
            print(f'WARNING: video is {dv:.2f} s but audio is {da:.2f} s. The finished file uses the shorter one.')
        cmd = ['ffmpeg', '-y', '-loglevel', 'error', '-i', video, '-i', leveled, '-map', '0:v:0', '-map', '1:a:0',
               '-c:v', 'libx264', '-preset', 'medium', '-crf', '19', '-maxrate', '16M', '-bufsize', '16M',
               '-pix_fmt', 'yuv420p', '-r', '30', '-c:a', 'aac', '-b:a', '192k', '-ar', '48000',
               '-movflags', '+faststart', '-shortest', tmp]
        if subprocess.run(cmd).returncode != 0:
            sys.exit('ffmpeg failed, nothing written')
        fI, fP = loudness(tmp)
        if fP <= -1.0:
            break
        print(f'peak {fP:.1f} dB after encoding, levelling again with more headroom...')
    os.replace(tmp, out)
    print(f'{out}: {duration(str(out)):.2f} s, {fI:.1f} LUFS, true peak {fP:.1f} dB, '
          f'{os.path.getsize(out) / 1e6:.1f} MB')
    if abs(fI + 14) > 0.7 or fP > -1.0:
        print('CHECK THE SOUND: want -14 LUFS and true peak -1 dB or lower.')


if __name__ == '__main__':
    if len(sys.argv) != 4:
        sys.exit(__doc__)
    main(*sys.argv[1:])
