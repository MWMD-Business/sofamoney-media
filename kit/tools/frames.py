"""frames.py video.mp4 t1,t2,... sheet.jpg [width]  ->  one contact-sheet picture of those moments.

Use it to look at a finished render (open the sheet with the Read tool) or at an example video in
reference-videos/. Up to 5 frames per row; each frame is scaled to `width` pixels wide (default 360).
Example:  python tools/frames.py out/Hidden-Room-FINAL.mp4 0.5,3,6,9,12 out/check.jpg
"""
import os, subprocess, sys, tempfile


def main(video, times, sheet, width=360):
    ts = [float(t) for t in times.split(',') if t.strip()]
    width = int(width)
    tmp = tempfile.mkdtemp(prefix='frames_')
    files = []
    for k, t in enumerate(ts):
        f = os.path.join(tmp, f'f{k:02d}.jpg')
        subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-ss', str(t), '-i', video, '-frames:v', '1',
                        '-vf', f'scale={width}:-2', '-q:v', '3', f], check=True)
        if os.path.exists(f):
            files.append(f)
    if not files:
        sys.exit('No frames could be read (check the times are inside the video).')
    if len(files) == 1:
        os.replace(files[0], sheet); print(sheet); return
    cols = min(5, len(files)); rows = (len(files) + cols - 1) // cols
    args = []
    for f in files:
        args += ['-i', f]
    def pos(n, unit):  # xstack positions are written as sums: 0, w0, w0+w0, ...
        return '0' if n == 0 else '+'.join([unit] * n)
    layout = '|'.join(f'{pos(k % cols, "w0")}_{pos(k // cols, "h0")}' for k in range(len(files)))
    fill = ':fill=black' if rows * cols != len(files) else ''
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error'] + args +
                   ['-filter_complex', f'xstack=inputs={len(files)}:layout={layout}{fill}', '-frames:v', '1', '-q:v', '3', sheet],
                   check=True)
    print(sheet)


if __name__ == '__main__':
    if len(sys.argv) not in (4, 5):
        sys.exit(__doc__)
    main(*sys.argv[1:])
