"""Narracion (Piper), musica y efectos del video 3D. Escribe audio.wav y timeline.json.
Uso: python3 audio.py <voz> <carpeta> [config.json]  (config: lines [[key,text,min_dur]], text, bg, rim, ring)"""
import sys, json, wave, glob
import numpy as np
from piper import PiperVoice
VOICE, WORK = sys.argv[1], sys.argv[2]
CFG = json.load(open(sys.argv[3])) if len(sys.argv) > 3 else {}
SR = 22050
LINES = [
    ("drop",   "This lock has no keyhole.", 2.6),
    ("scan",   "Just touch it... and it opens.", 4.2),
    ("spin",   "No keys to lose. No codes to forget. Only your fingerprint unlocks it.", 4.5),
    ("places", "Your gym locker. Your backpack. Your suitcase.", 5.0),
    ("denied", "Anyone else? Denied.", 3.6),
    ("cta",    "Get yours for sixteen ninety-nine. Use code, bienvenido ten, for ten percent off. Link in bio.", 6.0),
]
LINES = [tuple(x) for x in CFG.get("lines", LINES)]
tts = PiperVoice.load(glob.glob(f"{VOICE}/*.onnx")[0])
clips = []
for k, txt, mn in LINES:
    f = f"{WORK}/v_{k}.wav"
    with wave.open(f, "wb") as w: tts.synthesize_wav(txt, w)
    with wave.open(f) as w:
        a = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768; sr = w.getframerate()
    assert sr == SR
    clips.append(a)
scenes, t = [], 0.0
for (k, txt, mn), a in zip(LINES, clips):
    lead = 0.9 if k == "drop" else 0.35          # tras la caida, la voz entra despues del golpe
    d = max(mn, lead + len(a) / SR + 0.45)
    scenes.append({"key": k, "start": round(t, 3), "dur": round(d, 3), "vo": round(t + lead, 3), "text": txt}); t += d
TOTAL = t + 0.3
n = int(TOTAL * SR); tt = np.arange(n) / SR
voice = np.zeros(n, np.float32); sfx = np.zeros(n, np.float32); music = np.zeros(n, np.float32)
for s, a in zip(scenes, clips):
    i = int(s["vo"] * SR); voice[i:i + len(a)] += a[:n - i]
rng = np.random.default_rng(1)
def add(buf, at, sig):
    i = int(at * SR); buf[i:i + len(sig)] += sig[:max(0, n - i)]
def env(d, atk, dec):
    x = np.arange(int(d * SR)) / SR; return np.minimum(1, x / max(atk, 1e-4)) * np.exp(-x * dec), x
def boom():
    e, x = env(1.2, 0.002, 4); return (np.sin(2 * np.pi * (40 + 90 * np.exp(-x * 18)) * x) * 0.9 + rng.normal(0, 1, len(x)) * np.exp(-x * 25) * 0.25) * e
def click():
    e, x = env(0.12, 0.0005, 60); return (np.sin(2 * np.pi * 2400 * x) * 0.5 + rng.normal(0, 1, len(x)) * 0.5) * e * 0.8
def whoosh(d=0.5):
    x = np.arange(int(d * SR)) / SR; nz = rng.normal(0, 1, len(x)); out = np.zeros_like(nz); y = 0
    for i in range(len(nz)):                       # filtro paso bajo que se abre y cierra
        a = 0.02 + 0.25 * np.sin(np.pi * x[i] / d); y += a * (nz[i] - y); out[i] = y
    return out * np.sin(np.pi * x / d) * 0.9
def buzz():
    e, x = env(0.45, 0.005, 2); return np.sign(np.sin(2 * np.pi * 110 * x)) * e * 0.25
def ding():
    e, x = env(1.5, 0.002, 3); return (np.sin(2 * np.pi * 1318 * x) + 0.5 * np.sin(2 * np.pi * 1976 * x)) * e * 0.35
def beep(f=1500):
    e, x = env(0.12, 0.003, 25); return np.sin(2 * np.pi * f * x) * e * 0.3
S = {s["key"]: s for s in scenes}
if "drop" in S: add(sfx, S["drop"]["start"] + 0.55, boom())    # aterriza el candado
add(sfx, S["scan"]["start"] + 1.0, beep(1200)); add(sfx, S["scan"]["start"] + 1.9, beep(1800))
add(sfx, S["scan"]["start"] + 2.1, click())                    # se abre
for s in scenes[1:]: add(sfx, s["start"] - 0.25, whoosh())
pl = S["places"]; [add(sfx, pl["start"] + pl["dur"] * f - 0.15, whoosh(0.35)) for f in (1/3, 2/3)]
add(sfx, S["denied"]["start"] + 1.3, buzz()); add(sfx, S["denied"]["start"] + 1.75, buzz())
add(sfx, S["cta"]["start"] + 0.6, ding())
# musica: pulso oscuro con bajo y hi-hat, entra despues del golpe
bpm = 110; beat = 60 / bpm; start = S["drop"]["start"] + 0.55 if "drop" in S else 0.2
roots = [55, 55, 49, 41.2]
for b in range(int((TOTAL - start) / beat)):
    t0 = start + b * beat
    e, x = env(beat, 0.003, 9); add(music, t0, np.sin(2 * np.pi * (45 + 70 * np.exp(-x * 35)) * x) * e * (0.5 if b % 2 == 0 else 0.3))
    r = roots[(b // 8) % 4]; e2, x2 = env(beat, 0.01, 3)
    add(music, t0, (np.sin(2 * np.pi * r * x2) + 0.3 * np.sin(2 * np.pi * r * 2 * x2)) * e2 * 0.25)
    e3, x3 = env(0.05, 0.001, 80); add(music, t0 + beat / 2, rng.normal(0, 1, len(x3)) * e3 * 0.06)
fade = np.clip((TOTAL - tt) / 1.0, 0, 1)
mix = voice * 1.0 + sfx * 0.55 + music * 0.22 * fade
mix /= np.abs(mix).max() / 0.92
with wave.open(f"{WORK}/audio.wav", "wb") as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((mix * 32767).astype(np.int16).tobytes())
json.dump({"total": round(TOTAL, 3), "scenes": scenes, **{k: CFG[k] for k in ("text", "bg", "rim", "ring") if k in CFG}}, open(f"{WORK}/timeline.json", "w"), indent=1)
print(json.dumps(scenes, indent=0), TOTAL)
