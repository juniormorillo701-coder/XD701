"""Audio ASMR para el video en loop (8 s exactos, sin voz): beeps, clic al abrir/cerrar y un beat que empata al repetirse."""
import sys, json, wave
import numpy as np
WORK = sys.argv[1]; SR = 44100; D = 8.0
n = int(D * SR); rng = np.random.default_rng(7)
out = np.zeros(n, np.float32); music = np.zeros(n, np.float32)
def add(buf, at, sig):
    i = int(at * SR) % n; m = min(len(sig), n - i); buf[i:i + m] += sig[:m]; buf[:len(sig) - m] += sig[m:]  # envuelve al inicio
def env(d, atk, dec):
    x = np.arange(int(d * SR)) / SR; return np.minimum(1, x / max(atk, 1e-4)) * np.exp(-x * dec), x
def beep(f, d=0.14):
    e, x = env(d, 0.003, 18); return np.sin(2 * np.pi * f * x) * e * 0.35
def click(pitch=1.0, amp=1.0):
    e, x = env(0.09, 0.0003, 70)
    body = np.sin(2 * np.pi * 3200 * pitch * x) * 0.4 + np.sin(2 * np.pi * 900 * pitch * x) * 0.5
    return (body + rng.normal(0, 1, len(x)) * 0.6) * e * amp
def thunk():
    e, x = env(0.25, 0.001, 22); return (np.sin(2 * np.pi * (90 + 120 * np.exp(-x * 40)) * x) + rng.normal(0, 1, len(x)) * 0.2 * np.exp(-x * 60)) * e * 0.8
def shimmer():
    e, x = env(0.9, 0.01, 4); return sum(np.sin(2 * np.pi * f * x) for f in (1568, 2093, 2637)) * e * 0.08
add(out, 2.25, beep(1400)); add(out, 2.6, beep(1400)); add(out, 2.95, beep(1760))
add(out, 3.05, beep(2349, 0.25))                       # ok
add(out, 3.12, click(1.0, 1.0)); add(out, 3.16, click(0.8, 0.6)); add(out, 3.15, shimmer())
add(out, 6.02, click(0.7, 1.0)); add(out, 6.04, thunk())
# beat lo-fi 120 bpm: 16 tiempos = 8 s, empata perfecto al repetir
beat = 0.5; chords = [[220, 261.6, 329.6], [174.6, 220, 261.6], [196, 246.9, 293.7], [164.8, 207.7, 246.9]]
for b in range(16):
    t0 = b * beat
    e, x = env(0.45, 0.002, 10); add(music, t0, np.sin(2 * np.pi * (48 + 60 * np.exp(-x * 30)) * x) * e * (0.6 if b % 2 == 0 else 0.0))
    if b % 4 == 2: e, x = env(0.2, 0.001, 25); add(music, t0, rng.normal(0, 1, len(x)) * e * 0.18)   # snare suave
    e, x = env(0.06, 0.001, 70); add(music, t0 + 0.25, rng.normal(0, 1, len(x)) * e * 0.05)
    if b % 4 == 0:
        e, x = env(2.0, 0.08, 1.2); add(music, t0, sum(np.sin(2 * np.pi * f * x) for f in chords[b // 4]) * e * 0.07)
mix = out * 1.0 + music * 0.55
mix /= np.abs(mix).max() / 0.9
with wave.open(f"{WORK}/audio.wav", "wb") as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((mix * 32767).astype(np.int16).tobytes())
json.dump({"total": D, "scenes": [{"key": "loop", "start": 0, "dur": D}], "rim": ["#33ddff", "#ff7a33"]}, open(f"{WORK}/timeline.json", "w"))
print("ok")
