// Renderiza index.html cuadro por cuadro en Chromium (WebGL) y arma el MP4 con ffmpeg.
// Uso: node render.js <timeline.json> <audio.wav> <salida.mp4> [--test t1,t2,...  (solo PNGs de prueba)]
const { chromium } = require('playwright');
const http = require('http'), fs = require('fs'), path = require('path'), { spawn } = require('child_process');

const [tlPath, audioPath, outPath] = process.argv.slice(2);
const testIdx = process.argv.indexOf('--test');
const tests = testIdx > 0 ? process.argv[testIdx + 1].split(',').map(Number) : null;
const FPS = 30, ROOT = __dirname;
const TYPES = { '.html': 'text/html', '.js': 'text/javascript', '.json': 'application/json' };

const server = http.createServer((req, res) => {
  const p = path.join(ROOT, decodeURIComponent(req.url.split('?')[0]));
  if (!p.startsWith(ROOT) || !fs.existsSync(p) || fs.statSync(p).isDirectory()) { res.writeHead(404); return res.end(); }
  res.writeHead(200, { 'Content-Type': TYPES[path.extname(p)] || 'application/octet-stream' });
  fs.createReadStream(p).pipe(res);
});

(async () => {
  await new Promise(r => server.listen(0, '127.0.0.1', r));
  const url = `http://127.0.0.1:${server.address().port}/index.html`;
  const tl = JSON.parse(fs.readFileSync(tlPath, 'utf8'));
  const browser = await chromium.launch({ args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
  const page = await browser.newPage({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: 1 });
  page.on('pageerror', e => console.error('PAGE ERROR', e.message));
  await page.goto(url);
  await page.waitForFunction(() => window.ready === true, null, { timeout: 60000 });
  await page.evaluate(t => window.setup(t), tl);

  if (tests) {
    for (const t of tests) {
      await page.evaluate(t => window.renderAt(t), t);
      await page.screenshot({ path: `${outPath}_${t}.png` });
    }
  } else {
    const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(FPS), '-c:v', 'mjpeg', '-i', '-',
      '-i', audioPath, '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '19', '-preset', 'medium',
      '-c:a', 'aac', '-b:a', '160k', '-shortest', '-movflags', '+faststart', outPath], { stdio: ['pipe', 'inherit', 'inherit'] });
    const n = Math.round(tl.total * FPS), t0 = Date.now();
    for (let i = 0; i < n; i++) {
      await page.evaluate(t => window.renderAt(t), i / FPS);
      const buf = await page.screenshot({ type: 'jpeg', quality: 93 });
      if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
      if (i % 60 === 0) console.log(`frame ${i}/${n}  ${((Date.now() - t0) / 1000).toFixed(0)}s`);
    }
    ff.stdin.end(); await new Promise(r => ff.on('close', r));
    console.log('OK', outPath);
  }
  await browser.close(); server.close();
})();
