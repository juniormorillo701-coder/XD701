"""Promo video for the fingerprint padlock: John's story + natural narration (Piper voice)."""
import math, subprocess, wave, os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

SRC = sys.argv[1]            # captura con el candado
WORK = sys.argv[2]           # carpeta temporal
OUT = sys.argv[3]            # mp4 final
VOICE = sys.argv[4]          # carpeta del modelo de voz piper (.onnx + .onnx.json)
os.makedirs(WORK, exist_ok=True)
W, H, FPS = 1080, 1920, 30
FB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
def font(s): return ImageFont.truetype(FB, s)

# ---------- narracion ----------
SCENES = [
    ("gym",     "John went to the gym, just like every day."),
    ("locker",  "He left his phone, his wallet, and his keys in the locker, with a cheap lock."),
    ("robbed",  "But when he came back, the locker was open. Everything was gone."),
    ("warn",    "Don't let this happen to you."),
    ("reveal",  "Meet the smart fingerprint padlock."),
    ("feat",    "It opens with just your finger. No keys to lose, and no codes to forget."),
    ("uses",    "Perfect for the gym, school, your luggage, or your storage unit."),
    ("cta",     "Protect what's yours. Get it today for only sixteen ninety-nine."),
]
CAPS = {"cta": "Protect what's yours. Get it today for only $16.99"}
import glob
from piper import PiperVoice
TTS = PiperVoice.load(glob.glob(f"{VOICE}/*.onnx")[0])
durs = []
for i, (k, txt) in enumerate(SCENES):
    f = f"{WORK}/n{i}.wav"
    with wave.open(f, "wb") as w: TTS.synthesize_wav(txt, w)
    with wave.open(f) as w: durs.append(w.getnframes() / w.getframerate())
PAD = 0.5
starts = np.cumsum([0] + [d + PAD for d in durs])
TOTAL = starts[-1] + 1.0

# audio de voz con silencios
SR = 22050
voice = np.zeros(int(TOTAL * SR), np.float32)
for i in range(len(SCENES)):
    f = f"{WORK}/n{i}.wav"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", f, "-ar", str(SR), "-ac", "1", f"{WORK}/r{i}.wav"], check=True)
    with wave.open(f"{WORK}/r{i}.wav") as w:
        a = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
    s = int((starts[i] + 0.15) * SR); voice[s:s + len(a)] += a[:len(voice) - s]
# musica de fondo simple (bajo + acordes suaves)
t = np.arange(len(voice)) / SR
bpm = 100; beat = 60 / bpm
chords = [[110, 130.8, 164.8], [87.3, 110, 130.8], [98, 123.5, 146.8], [82.4, 103.8, 123.5]]
music = np.zeros_like(voice)
for bi in range(int(TOTAL / beat) + 1):
    s0 = int(bi * beat * SR); n = int(beat * SR); seg = slice(s0, min(s0 + n, len(music)))
    tt = t[seg] - bi * beat
    ch = chords[(bi // 4) % 4]
    pad = sum(np.sin(2 * np.pi * f * 2 * tt) for f in ch) * 0.03 * np.exp(-tt * 1.5)
    kick = np.sin(2 * np.pi * (50 + 80 * np.exp(-tt * 30)) * tt) * np.exp(-tt * 12) * (0.25 if bi % 2 == 0 else 0.12)
    music[seg] += pad + kick
mix = voice * 1.6 + music * 0.6
mix /= max(1e-6, np.abs(mix).max() / 0.9)
with wave.open(f"{WORK}/audio.wav", "w") as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((mix * 32767).astype(np.int16).tobytes())

# ---------- imagen del candado ----------
src = Image.open(SRC).convert("RGB").crop((140, 680, 440, 1150))
# el boton naranja tapa la esquina inferior derecha: se reconstruye en espejo con la izquierda
# (el cuerpo va de x=22 a x=275, eje en 148.5)
a = np.array(src)
for y in range(380, src.height):
    for x in range(200, src.width):
        mx = 297 - x
        a[y, x] = a[y, mx] if mx >= 0 else (255, 255, 255)
src = Image.fromarray(a)
# quitar fondo blanco -> transparente
lock = src.convert("RGBA"); arr = np.array(lock)
wht = (arr[..., :3].min(axis=2) > 235)
arr[..., 3] = np.where(wht, 0, 255).astype(np.uint8)
lock = Image.fromarray(arr).filter(ImageFilter.SMOOTH)
def lock_img(h):
    return lock.resize((int(lock.width * h / lock.height), h), Image.LANCZOS)
LOCK_BIG, LOCK_MED, LOCK_SM = lock_img(900), lock_img(640), lock_img(420)

# ---------- utilidades de dibujo ----------
def ease(x): x = max(0., min(1., x)); return 1 - (1 - x) ** 3
def lerp(a, b, x): return a + (b - a) * x
def grad(c1, c2):
    g = np.linspace(0, 1, H)[:, None, None]
    a = (np.array(c1) * (1 - g) + np.array(c2) * g).astype(np.uint8)
    return Image.fromarray(np.repeat(a, W, axis=1))
BG = {k: grad(*c) for k, c in {
    "gym": ((25, 40, 80), (10, 15, 35)), "locker": ((40, 50, 65), (15, 18, 25)),
    "robbed": ((90, 10, 15), (20, 0, 5)), "warn": ((15, 15, 20), (0, 0, 0)),
    "reveal": ((255, 140, 40), (120, 30, 80)), "feat": ((20, 25, 45), (5, 5, 15)),
    "uses": ((30, 120, 110), (10, 40, 60)), "cta": ((255, 120, 30), (200, 40, 60))}.items()}

def ctext(d, txt, y, f, fill=(255, 255, 255), dx=0, stroke=0):
    w = d.textlength(txt, font=f); d.text(((W - w) / 2 + dx, y), txt, font=f, fill=fill,
                                           stroke_width=stroke, stroke_fill=(0, 0, 0))
def wrap(d, txt, f, maxw):
    lines, cur = [], ""
    for w in txt.split():
        if d.textlength((cur + " " + w).strip(), font=f) > maxw: lines.append(cur); cur = w
        else: cur = (cur + " " + w).strip()
    return lines + [cur]
def caption(img, txt, p):
    d = ImageDraw.Draw(img, "RGBA"); f = font(54)
    lines = wrap(d, txt, f, W - 160); h = len(lines) * 70 + 50; y0 = H - 330 - h
    a = int(200 * ease(p * 4))
    d.rounded_rectangle([60, y0, W - 60, y0 + h], 30, fill=(0, 0, 0, int(a * 0.75)))
    for i, l in enumerate(lines): ctext(d, l, y0 + 25 + i * 70, f, fill=(255, 255, 255, a))

def person(d, x, y, s=1.0, mood="happy", shirt=(40, 120, 230)):
    # cuerpo
    d.rounded_rectangle([x - 70 * s, y, x + 70 * s, y + 220 * s], 40 * s, fill=shirt)
    d.rectangle([x - 60 * s, y + 210 * s, x - 10 * s, y + 380 * s], fill=(30, 35, 50))
    d.rectangle([x + 10 * s, y + 210 * s, x + 60 * s, y + 380 * s], fill=(30, 35, 50))
    # cabeza
    hx, hy, r = x, y - 70 * s, 70 * s
    d.ellipse([hx - r, hy - r, hx + r, hy + r], fill=(205, 150, 110))
    d.chord([hx - r, hy - r - 8 * s, hx + r, hy + r * 0.2], 180, 360, fill=(40, 25, 20))
    for ex in (-25, 25): d.ellipse([hx + ex * s - 8 * s, hy - 5 * s, hx + ex * s + 8 * s, hy + 11 * s], fill=(20, 20, 20))
    if mood == "happy": d.arc([hx - 30 * s, hy + 5 * s, hx + 30 * s, hy + 45 * s], 20, 160, fill=(60, 20, 20), width=int(6 * s))
    else:
        d.arc([hx - 30 * s, hy + 35 * s, hx + 30 * s, hy + 70 * s], 200, 340, fill=(60, 20, 20), width=int(6 * s))
        d.ellipse([hx + 30 * s, hy + 10 * s, hx + 42 * s, hy + 30 * s], fill=(120, 190, 255))
def dumbbell(d, x, y, s=1.0, c=(180, 185, 195)):
    d.rectangle([x - 70 * s, y - 8 * s, x + 70 * s, y + 8 * s], fill=c)
    for sx in (-1, 1):
        d.rounded_rectangle([x + sx * 70 * s - 18 * s, y - 45 * s, x + sx * 70 * s + 18 * s, y + 45 * s], 8, fill=(50, 55, 65))
def lockers(d, open_door=None, open_amt=0.0, items=None):
    x0, y0, lw, lh = 140, 330, 200, 820
    for i in range(4):
        x = x0 + i * lw
        d.rectangle([x, y0, x + lw - 10, y0 + lh], fill=(120, 130, 145), outline=(70, 75, 85), width=6)
        for k in range(3): d.rectangle([x + 50, y0 + 60 + k * 25, x + lw - 60, y0 + 70 + k * 25], fill=(80, 88, 100))
        if i == open_door:
            d.rectangle([x + 8, y0 + 8, x + lw - 18, y0 + lh - 8], fill=(25, 25, 30))
            if items: items(d, x, y0)
            dw = (lw - 10) * (1 - open_amt)
            if dw > 4:
                d.rectangle([x, y0, x + dw, y0 + lh], fill=(135, 145, 160), outline=(70, 75, 85), width=6)
                d.rectangle([x + dw - 40, y0 + lh / 2 - 30, x + dw - 25, y0 + lh / 2 + 30], fill=(60, 60, 60))
    return x0, y0, lw, lh
def phone_wallet_keys(d, x, y0, p=1.0):
    d.rounded_rectangle([x + 40, y0 + 380, x + 100, y0 + 490], 10, fill=(20, 20, 20), outline=(200, 200, 210), width=4)
    d.rounded_rectangle([x + 60, y0 + 560, x + 170, y0 + 630], 10, fill=(120, 70, 30))
    d.ellipse([x + 110, y0 + 400, x + 150, y0 + 440], outline=(230, 200, 60), width=6)
    d.rectangle([x + 145, y0 + 415, x + 185, y0 + 425], fill=(230, 200, 60))
def cheap_lock(d, x, y, s=1.0):
    d.arc([x - 25 * s, y - 50 * s, x + 25 * s, y + 10 * s], 180, 360, fill=(170, 170, 170), width=int(8 * s))
    d.rounded_rectangle([x - 35 * s, y - 20 * s, x + 35 * s, y + 45 * s], 8, fill=(190, 150, 50))

def paste_center(img, im, cx, cy, scale=1.0, alpha=1.0):
    if scale != 1.0: im = im.resize((max(1, int(im.width * scale)), max(1, int(im.height * scale))), Image.LANCZOS)
    if alpha < 1: a = im.split()[3].point(lambda v: int(v * alpha)); im = im.copy(); im.putalpha(a)
    img.paste(im, (int(cx - im.width / 2), int(cy - im.height / 2)), im)

def glow(img, cx, cy, r, col, a=110):
    g = Image.new("RGBA", (W, H), (0, 0, 0, 0)); gd = ImageDraw.Draw(g)
    gd.ellipse([cx - r, cy - r, cx + r, cy + r], fill=col + (a,))
    g = g.filter(ImageFilter.GaussianBlur(80)); img.paste(g, (0, 0), g)

# ---------- escenas ----------
def scene(k, t, D):
    p = t / D
    img = BG[k].copy(); d = ImageDraw.Draw(img, "RGBA")
    if k == "gym":
        d.rectangle([0, 1250, W, H], fill=(35, 30, 45))
        ctext(d, "GYM", 180, font(150), fill=(255, 190, 60))
        for i in range(3): dumbbell(d, 260 + i * 280, 1000 - i * 0, 1.1)
        d.rectangle([150, 1060, 930, 1080], fill=(80, 80, 95))
        x = lerp(-150, 540, ease(p * 1.6)); bob = abs(math.sin(t * 8)) * 15 * (1 - ease(p * 1.6))
        person(d, x, 880 - bob, 1.0)
    elif k == "locker":
        oa = 1 - ease((p - 0.55) * 3)  # puerta se cierra
        lockers(d, 1, oa if p < 0.55 else oa, phone_wallet_keys)
        if p > 0.75:
            cheap_lock(d, 340 + 190 - 30, 330 + 410, 1.4 * ease((p - 0.75) * 5))
        ctext(d, "LOCKERS", 170, font(90), fill=(220, 225, 235))
        person(d, 830, 1250, 0.8)
    elif k == "robbed":
        shake = math.sin(t * 60) * 12 * (1 - ease(p))
        lockers(d, 1, 1.0)  # abierto y vacio
        d.line([470, 760, 540, 700], fill=(255, 220, 60), width=8)
        d.line([500, 700, 560, 760], fill=(255, 220, 60), width=8)
        if p > 0.4:
            s = ease((p - 0.4) * 4)
            f = font(int(120 * s) + 1)
            ctext(d, "EVERYTHING", 150, f, fill=(255, 255, 255), dx=shake, stroke=6)
            ctext(d, "WAS GONE!", 290, f, fill=(255, 60, 60), dx=-shake, stroke=6)
        person(d, 820, 1250, 0.8, mood="sad")
        if int(t * 6) % 2 == 0 and p < 0.5:
            d.rectangle([0, 0, W, H], fill=(255, 0, 0, 60))
    elif k == "warn":
        s = ease(p * 2.5)
        ctext(d, "Don't let this", 640, font(int(95 * s) + 1))
        ctext(d, "happen", 780, font(int(95 * s) + 1))
        ctext(d, "TO YOU", 930, font(int(190 * s) + 1), fill=(255, 190, 60))
    elif k == "reveal":
        cx, cy = 540, 900
        rays = Image.new("RGBA", (W, H), (0, 0, 0, 0)); rd = ImageDraw.Draw(rays)
        for i in range(16):
            a = t * 0.6 + i * math.pi / 8
            rd.polygon([(cx, cy), (cx + 1400 * math.cos(a), cy + 1400 * math.sin(a)),
                        (cx + 1400 * math.cos(a + 0.12), cy + 1400 * math.sin(a + 0.12))], fill=(255, 255, 255, 35))
        img.paste(rays, (0, 0), rays)
        glow(img, cx, cy, 380, (255, 255, 255), 160)
        sc = lerp(0.2, 1.0, ease(p * 2.2)) * (1 + 0.02 * math.sin(t * 4))
        paste_center(img, LOCK_BIG, cx, cy, sc)
        d = ImageDraw.Draw(img, "RGBA")
        ctext(d, "SMART", 110, font(110), stroke=5)
        ctext(d, "FINGERPRINT LOCK", 240, font(90), fill=(255, 235, 120), stroke=5)
    elif k == "feat":
        glow(img, 540, 560, 300, (60, 200, 220), 90)
        paste_center(img, LOCK_MED, 540, 560, 0.9 + 0.015 * math.sin(t * 3))
        d = ImageDraw.Draw(img, "RGBA")
        feats = [("Opens with your finger", 0.0), ("No keys to lose", 0.35), ("No codes to forget", 0.62)]
        for i, (tx, st) in enumerate(feats):
            e = ease((p - st) * 4)
            if e <= 0: continue
            y = 900 + i * 125; x = lerp(-700, 110, e)
            d.rounded_rectangle([x, y, x + 860, y + 105], 50, fill=(255, 255, 255, 30), outline=(80, 220, 200), width=4)
            d.ellipse([x + 20, y + 18, x + 89, y + 87], fill=(80, 220, 200))
            d.line([x + 38, y + 54, x + 50, y + 68, x + 72, y + 36], fill=(10, 30, 40), width=9)
            d.text((x + 115, y + 26), tx, font=font(50), fill=(255, 255, 255))
    elif k == "uses":
        ctext(d, "Perfect for...", 160, font(90))
        paste_center(img, LOCK_SM, 540, 560, 1.0)
        uses = ["GYM", "SCHOOL", "LUGGAGE", "STORAGE"]
        for i, u in enumerate(uses):
            e = ease((p - i * 0.18) * 4)
            if e <= 0: continue
            col, row = i % 2, i // 2
            x = 110 + col * 440; y = 880 + row * 200 + (1 - e) * 80
            d.rounded_rectangle([x, y, x + 410, y + 160], 35, fill=(255, 255, 255, int(235 * e)))
            f = font(60); w = d.textlength(u, font=f)
            d.text((x + (410 - w) / 2, y + 48), u, font=f, fill=(20, 90, 90, int(255 * e)))
    elif k == "cta":
        glow(img, 540, 700, 360, (255, 255, 255), 140)
        paste_center(img, LOCK_MED, 540, 700, 1 + 0.03 * math.sin(t * 5))
        d = ImageDraw.Draw(img, "RGBA")
        ctext(d, "PROTECT WHAT'S YOURS", 150, font(66), stroke=5)
        pulse = 1 + 0.06 * math.sin(t * 7) * ease(p * 3)
        bw, bh = 760 * pulse, 190 * pulse; by = 1070
        d.rounded_rectangle([540 - bw / 2, by, 540 + bw / 2, by + bh], 95, fill=(255, 255, 255))
        f = font(int(100 * pulse)); ctext(d, "ONLY $16.99", by + bh / 2 - 58 * pulse, f, fill=(220, 50, 50))
        ctext(d, "Order now!", 1300, font(75), stroke=4)
    return img

# ---------- render ----------
p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                      "-r", str(FPS), "-i", "-", "-i", f"{WORK}/audio.wav", "-c:v", "libx264", "-pix_fmt", "yuv420p",
                      "-crf", "21", "-c:a", "aac", "-b:a", "160k", "-shortest", OUT], stdin=subprocess.PIPE)
n = int(TOTAL * FPS)
for i in range(n):
    t = i / FPS
    si = min(len(SCENES) - 1, int(np.searchsorted(starts, t, side="right") - 1))
    k, txt = SCENES[si]; D = starts[si + 1] - starts[si] if si + 1 < len(starts) else 1
    lt = t - starts[si]
    img = scene(k, lt, D)
    caption(img, CAPS.get(k, txt), lt / D)
    # fundido entre escenas
    fade = min(ease(lt / 0.25), ease((D - lt) / 0.2)) if si < len(SCENES) - 1 else ease(lt / 0.25)
    if fade < 1:
        ImageDraw.Draw(img, "RGBA").rectangle([0, 0, W, H], fill=(0, 0, 0, int(255 * (1 - fade))))
    p.stdin.write(img.convert("RGB").tobytes())
p.stdin.close(); p.wait()
print("OK", OUT, round(TOTAL, 1), "s")
