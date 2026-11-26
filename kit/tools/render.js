// Renders a scene (scenes/<name>/index.html) to pictures or to a silent video.
//
//   node tools/render.js scenes/hidden-room shots 1,4.5,8 out/hr        -> out/hr_1.00.jpg, out/hr_4.50.jpg, ...
//   node tools/render.js scenes/hidden-room video 0 14.3 out/hidden-room_video.mp4
//   node tools/render.js "scenes/how-it-works?p=sm" video 0 18.6 out/hiw_video.mp4   (?p=... is passed to the page)
//
// The page must set window.ready = true when it has loaded, and expose window.renderAt(t) that draws
// the frame for time t (seconds). Every frame is drawn from t alone, so renders are repeatable.
// Uses headless Chromium (Playwright) with SwiftShader (software WebGL, works on any PC) and ffmpeg.
const { chromium } = require('playwright');
const { spawn } = require('child_process');
const http = require('http'), fs = require('fs'), path = require('path');

const ROOT = path.resolve(__dirname, '..');   // the kit folder: node_modules/ and scenes/ are served from here
const types = {
  '.html': 'text/html', '.js': 'text/javascript', '.mjs': 'text/javascript', '.css': 'text/css',
  '.woff2': 'font/woff2', '.woff': 'font/woff', '.json': 'application/json', '.png': 'image/png',
  '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.webp': 'image/webp', '.svg': 'image/svg+xml',
  '.glb': 'model/gltf-binary', '.gltf': 'model/gltf+json', '.hdr': 'application/octet-stream',
  '.wav': 'audio/wav', '.mp3': 'audio/mpeg',
};

function serve() {
  return new Promise(res => {
    const s = http.createServer((q, r) => {
      const rel = decodeURIComponent(q.url.split('?')[0]);
      const p = path.join(ROOT, rel);
      if (!p.startsWith(ROOT)) { r.writeHead(403); r.end(); return; }
      fs.readFile(p, (e, d) => {
        if (e) { r.writeHead(404); r.end(); console.log('404 (file not found):', rel); return; }
        r.writeHead(200, { 'Content-Type': types[path.extname(p).toLowerCase()] || 'application/octet-stream' });
        r.end(d);
      });
    }).listen(0, '127.0.0.1', () => res(s));
  });
}

function usage() {
  console.log('Usage:\n  node tools/render.js <scene folder> shots <t1,t2,...> <out prefix>\n  node tools/render.js <scene folder> video <start s> <end s> <out.mp4>');
  process.exit(1);
}

(async () => {
  const [dirArg, mode, a, b, c] = process.argv.slice(2);
  if (!dirArg || !['shots', 'video'].includes(mode)) usage();
  const [dp, dq] = dirArg.replace(/\\/g, '/').replace(/\/+$/, '').split('?');
  if (!fs.existsSync(path.join(ROOT, dp, 'index.html'))) { console.log('No index.html in', path.join(ROOT, dp)); process.exit(1); }

  const srv = await serve(); const port = srv.address().port;
  const br = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
  const pg = await br.newPage({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: 1 });
  pg.on('console', m => { if (m.type() === 'error') console.log('PAGE', m.text()); });
  pg.on('pageerror', e => console.log('PAGEERR', e.message));
  await pg.goto(`http://127.0.0.1:${port}/${dp}/index.html${dq ? '?' + dq : ''}`);
  await pg.waitForFunction(() => window.ready === true, null, { timeout: 180000 });

  if (mode === 'shots') {
    if (!a || !b) usage();
    fs.mkdirSync(path.dirname(path.resolve(b)), { recursive: true });
    for (const t of a.split(',').map(Number)) {
      await pg.evaluate(t => window.renderAt(t), t);
      const f = `${b}_${t.toFixed(2)}.jpg`;
      await pg.screenshot({ path: f, type: 'jpeg', quality: 90 });
      console.log('shot', f);
    }
  } else {
    if (!a || !b || !c) usage();
    fs.mkdirSync(path.dirname(path.resolve(c)), { recursive: true });
    const fps = 30, s = Number(a), e = Number(b);
    const tmp = c + '.tmp.mp4';   // renamed when ffmpeg finishes, so a stopped render never looks finished
    const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(fps), '-c:v', 'mjpeg', '-i', '-',
      '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '17', '-pix_fmt', 'yuv420p', tmp], { stdio: ['pipe', 'inherit', 'inherit'] });
    let ffOk = true;
    const finished = new Promise(r => {
      ff.on('error', err => { ffOk = false; console.log('ffmpeg could not start (is it installed and on PATH?):', err.message); r(-1); });
      ff.on('close', code => r(code));
    });
    ff.stdin.on('error', () => { ffOk = false; });
    const n0 = Math.round(s * fps), n1 = Math.round(e * fps); const t0 = Date.now();
    for (let i = n0; i < n1 && ffOk; i++) {
      await pg.evaluate(t => window.renderAt(t), i / fps);
      const buf = await pg.screenshot({ type: 'jpeg', quality: 92 });
      if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
      if ((i - n0) % 30 === 0) {
        const per = (Date.now() - t0) / 1000 / (i - n0 + 1);
        console.log(`frame ${i - n0 + 1}/${n1 - n0}  ${per.toFixed(2)} s/frame  about ${Math.ceil(per * (n1 - i) / 60)} min left`);
      }
    }
    ff.stdin.end(); const code = await finished;
    if (code !== 0 || !ffOk) { console.log('ffmpeg failed, video not written'); process.exitCode = 1; }
    else { fs.renameSync(tmp, c); console.log('done', c, `(${((Date.now() - t0) / 60000).toFixed(1)} min)`); }
  }
  await br.close(); srv.close();
})().catch(e => { console.error(e); process.exit(1); });
