"""check_setup.py  ->  checks this PC has everything the kit needs, then renders one test picture.

Run it from the kit folder with the kit's Python:
    Windows:      .venv/Scripts/python tools/check_setup.py
    Mac / Linux:  .venv/bin/python tools/check_setup.py
Every line says OK or what to do. Add --no-render to skip the test picture.
"""
import importlib, os, re, shutil, subprocess, sys
from pathlib import Path

KIT = Path(__file__).resolve().parents[1]
WIN = os.name == 'nt'
problems = []


def ok(msg):
    print('  OK    ' + msg)


def bad(msg, fix):
    print('  FIX   ' + msg + '\n        -> ' + fix)
    problems.append(msg)


def run(args, **kw):
    try:
        return subprocess.run(args, capture_output=True, text=True, encoding='utf-8', errors='replace', **kw)
    except OSError as e:
        return subprocess.CompletedProcess(args, 1, '', str(e))


print(f'Sofa Money video kit: setup check ({KIT})\n')

# 1. Python
v = sys.version_info
if (3, 10) <= v[:2] <= (3, 12):
    ok(f'Python {v.major}.{v.minor}')
else:
    bad(f'Python {v.major}.{v.minor} (needs 3.10, 3.11 or 3.12; 3.13 cannot install the voice)',
        'winget install -e --id Python.Python.3.12   then make the venv with:  py -3.12 -m venv .venv' if WIN
        else 'install Python 3.12 and make the venv with: python3.12 -m venv .venv')
if sys.prefix == sys.base_prefix:
    print('  NOTE  this is not the kit\'s .venv Python. Use .venv/Scripts/python (Windows) or .venv/bin/python.')

# 2. Python packages
for mod, pipname in [('numpy', 'numpy'), ('scipy', 'scipy'), ('soundfile', 'soundfile'),
                     ('kokoro', 'kokoro'), ('faster_whisper', 'faster-whisper')]:
    try:
        importlib.import_module(mod)
        ok(f'Python package {pipname}')
    except Exception as e:  # noqa: BLE001
        bad(f'Python package {pipname} missing ({type(e).__name__})',
            ('.venv/Scripts/python' if WIN else '.venv/bin/python') + ' -m pip install -r requirements.txt')

# 3. ffmpeg
ff = shutil.which('ffmpeg'); fp = shutil.which('ffprobe')
if ff and fp:
    enc = run([ff, '-hide_banner', '-encoders']).stdout
    if 'libx264' in enc:
        ok('ffmpeg + ffprobe (with libx264)')
    else:
        bad('ffmpeg has no libx264 encoder', 'install a full build: winget install -e --id Gyan.FFmpeg' if WIN else 'install ffmpeg with libx264')
else:
    bad('ffmpeg/ffprobe not found on PATH',
        'winget install -e --id Gyan.FFmpeg   (then close and reopen the terminal / restart Claude Code)' if WIN
        else 'install ffmpeg (brew install ffmpeg / sudo apt install ffmpeg)')

# 4. Node + packages + browser
node = shutil.which('node')
if node:
    nv = run([node, '--version']).stdout.strip()
    major = int(re.sub(r'[^0-9.]', '', nv).split('.')[0] or 0)
    (ok if major >= 18 else lambda m: bad(m, 'install Node.js LTS: winget install -e --id OpenJS.NodeJS.LTS'))(f'Node.js {nv}')
else:
    bad('Node.js not found on PATH', 'winget install -e --id OpenJS.NodeJS.LTS   (then reopen the terminal)' if WIN
        else 'install Node.js 18 or newer')

need = ['three/build/three.module.js', '@fontsource/inter', '@fontsource/space-grotesk', '@fontsource/anton',
        '@fontsource/chakra-petch', '@fontsource/jetbrains-mono', 'playwright']
missing = [n for n in need if not (KIT / 'node_modules' / n).exists()]
if missing:
    bad('Node packages missing: ' + ', '.join(missing), 'npm install   (in the kit folder)')
else:
    ok('Node packages (three.js 0.160, fonts, playwright)')

browser_ok = False
if node and not missing:
    js = "const {chromium}=require('playwright');const p=chromium.executablePath();console.log(require('fs').existsSync(p)?'yes':'no')"
    r = run([node, '-e', js], cwd=KIT)
    if r.stdout.strip() == 'yes':
        ok('Chromium for Playwright'); browser_ok = True
    else:
        bad('Chromium for Playwright not installed', 'npx playwright install chromium   (in the kit folder)')

# 5. Test render
if '--no-render' not in sys.argv and node and not missing and browser_ok and ff:
    print('\n  ...rendering one test picture of scenes/hidden-room (can take a minute)')
    (KIT / 'out').mkdir(exist_ok=True)
    pic = KIT / 'out' / '_setup_test_2.00.jpg'
    if pic.exists():
        pic.unlink()
    r = run([node, 'tools/render.js', 'scenes/hidden-room', 'shots', '2', 'out/_setup_test'], cwd=KIT, timeout=600)
    if pic.exists() and pic.stat().st_size > 20000:
        ok(f'test render worked: {pic}  (open it to check it looks like a cosy room)')
    else:
        bad('test render failed', 'see the output below, then ask Claude Code to fix it\n' + (r.stdout + r.stderr)[-1500:])

print('\n' + ('ALL GOOD - the kit is ready to make videos.' if not problems
              else f'{len(problems)} thing(s) to fix (see FIX lines above), then run this check again.'))
sys.exit(1 if problems else 0)
