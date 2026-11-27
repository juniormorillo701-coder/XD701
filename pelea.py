"""
100 HOMBRES vs 3 GORILAS
Simulación animada estilo caricatura. Genera pelea.mp4 con PIL + ffmpeg.

Uso:  python3 pelea.py   (requiere ffmpeg en el PATH, Pillow y numpy)
"""
import math
import random
import subprocess

import numpy as np
from PIL import Image, ImageDraw, ImageFont

random.seed(7)

W, H = 1280, 720
FPS = 30
DT = 1.0 / FPS
MAX_SECONDS = 60
OUT = "pelea.mp4"

GROUND_TOP = 200          # donde empieza el pasto (perspectiva)
N_MEN = 100
N_GORILLAS = 3


def font(size):
    for path in ("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
                 "/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf"):
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            pass
    return ImageFont.load_default()


F_BIG, F_MED, F_SMALL, F_POW = font(64), font(34), font(22), font(30)


def depth_scale(y):
    """Más lejos (arriba) = más pequeño."""
    return 0.65 + 0.55 * (y - GROUND_TOP) / (H - GROUND_TOP)


# ----------------------------------------------------------------- entidades
class Man:
    SHIRTS = [(220, 60, 60), (60, 120, 220), (240, 190, 40), (60, 170, 90),
              (150, 80, 200), (240, 130, 40), (40, 180, 190), (230, 230, 230)]
    SKINS = [(255, 220, 180), (230, 180, 140), (190, 130, 90), (140, 95, 60)]

    def __init__(self, i):
        self.x = random.uniform(30, 380)
        self.y = random.uniform(GROUND_TOP + 30, H - 30)
        self.vx = self.vy = 0.0
        self.z = 0.0          # altura cuando sale volando
        self.vz = 0.0
        self.state = "alive"  # alive | flying | ko
        self.shirt = random.choice(self.SHIRTS)
        self.skin = random.choice(self.SKINS)
        self.speed = random.uniform(85, 125)
        self.phase = random.uniform(0, 6.28)
        self.punch_cd = random.uniform(0, 0.8)
        self.punch_t = 0.0
        self.spin = 0.0
        self.angle = 0.0
        self.delay = random.uniform(0, 1.5)  # arrancan escalonados
        self.facing = 1


class Gorilla:
    def __init__(self, i):
        self.x = W - 260 + random.uniform(-30, 40)
        self.y = GROUND_TOP + 80 + i * 190
        self.hp = self.max_hp = 340.0
        self.cd = random.uniform(0.3, 1.0)
        self.swing_t = 0.0
        self.roar_t = 0.0
        self.state = "alive"   # alive | ko
        self.facing = -1
        self.hurt_t = 0.0
        self.phase = random.uniform(0, 6.28)
        self.name = ["KONG", "BRUTUS", "TITÁN"][i]


class Particle:
    def __init__(self, x, y, vx, vy, life, color, r):
        self.x, self.y, self.vx, self.vy = x, y, vx, vy
        self.life = self.max_life = life
        self.color, self.r = color, r


class Pow:
    WORDS = ["¡POW!", "¡BAM!", "¡ZAS!", "¡PUM!", "¡CRACK!", "¡WHAM!"]

    def __init__(self, x, y, big=False):
        self.x, self.y = x, y
        self.text = random.choice(self.WORDS)
        self.life = 0.6
        self.big = big
        self.color = random.choice([(255, 230, 0), (255, 120, 0), (255, 60, 60)])


# ----------------------------------------------------------------- mundo
men = [Man(i) for i in range(N_MEN)]
gorillas = [Gorilla(i) for i in range(N_GORILLAS)]
particles, pows = [], []
shake = 0.0
t = 0.0
FIGHT_START = 3.0        # segundos de presentación
end_time = None
winner = None


def dust(x, y, n=8, color=(170, 140, 100)):
    for _ in range(n):
        a = random.uniform(0, 6.28)
        s = random.uniform(30, 140)
        particles.append(Particle(x, y, math.cos(a) * s, math.sin(a) * s * 0.4 - 30,
                                  random.uniform(0.3, 0.7), color, random.uniform(3, 7)))


def update():
    global shake, end_time, winner
    alive_g = [g for g in gorillas if g.state == "alive"]
    alive_m = [m for m in men if m.state == "alive"]
    fighting = t >= FIGHT_START and winner is None

    # --- hombres
    for m in men:
        if m.state == "flying":
            m.x += m.vx * DT
            m.y += m.vy * DT
            m.vz -= 900 * DT
            m.z += m.vz * DT
            m.angle += m.spin * DT
            m.x = min(max(m.x, 10), W - 10)
            m.y = min(max(m.y, GROUND_TOP + 10), H - 10)
            if m.z <= 0:
                m.z = 0
                m.state = "ko"
                dust(m.x, m.y, 6)
            continue
        if m.state != "alive":
            continue
        m.phase += DT * 12
        m.punch_t = max(0, m.punch_t - DT)
        if not fighting or not alive_g or t - FIGHT_START < m.delay:
            continue
        g = min(alive_g, key=lambda g: (g.x - m.x) ** 2 + (g.y - m.y) ** 2)
        dx, dy = g.x - m.x, g.y - m.y
        d = math.hypot(dx, dy) + 1e-6
        m.facing = 1 if dx > 0 else -1
        reach = 58
        if d > reach:
            m.vx, m.vy = dx / d * m.speed, dy / d * m.speed
        else:
            m.vx *= 0.5
            m.vy *= 0.5
            m.punch_cd -= DT
            if m.punch_cd <= 0:
                m.punch_cd = random.uniform(0.6, 1.0)
                m.punch_t = 0.18
                g.hp -= random.uniform(1.0, 2.0)
                g.hurt_t = 0.1
                if random.random() < 0.08:
                    pows.append(Pow(g.x + random.uniform(-30, 30), g.y - 120))
        # separación entre hombres
        for o in alive_m:
            if o is m:
                continue
            ox, oy = m.x - o.x, m.y - o.y
            dd = ox * ox + oy * oy
            if 0 < dd < 22 * 22:
                k = (22 - math.sqrt(dd)) * 6
                m.vx += ox * k / math.sqrt(dd)
                m.vy += oy * k / math.sqrt(dd)
        m.x += m.vx * DT
        m.y += m.vy * DT
        m.y = min(max(m.y, GROUND_TOP + 10), H - 10)

    # --- gorilas
    for g in gorillas:
        g.swing_t = max(0, g.swing_t - DT)
        g.roar_t = max(0, g.roar_t - DT)
        g.hurt_t = max(0, g.hurt_t - DT)
        g.phase += DT * 3
        if g.state != "alive":
            continue
        if g.hp <= 0:
            g.state = "ko"
            g.hp = 0
            shake = max(shake, 14)
            dust(g.x, g.y, 30)
            pows.append(Pow(g.x, g.y - 140, big=True))
            continue
        if not fighting:
            continue
        near = [m for m in alive_m if (m.x - g.x) ** 2 + (m.y - g.y) ** 2 < 95 ** 2]
        # el gorila camina hacia el grupo más cercano
        if alive_m and not near:
            tgt = min(alive_m, key=lambda m: (m.x - g.x) ** 2 + (m.y - g.y) ** 2)
            dx, dy = tgt.x - g.x, tgt.y - g.y
            d = math.hypot(dx, dy) + 1e-6
            g.x += dx / d * 60 * DT
            g.y += dy / d * 60 * DT
            g.facing = 1 if dx > 0 else -1
        g.cd -= DT
        if g.cd <= 0 and near:
            g.cd = random.uniform(0.9, 1.4)
            g.swing_t = 0.3
            if random.random() < 0.15:
                g.roar_t = 1.0
            hits = random.sample(near, min(len(near), random.choice([1, 2, 2, 3])))
            for m in hits:
                a = math.atan2(m.y - g.y, m.x - g.x) + random.uniform(-0.4, 0.4)
                pw = random.uniform(260, 480)
                m.state = "flying"
                m.vx, m.vy = math.cos(a) * pw, math.sin(a) * pw * 0.5
                m.vz = random.uniform(300, 520)
                m.spin = random.choice([-1, 1]) * random.uniform(8, 16)
            if hits:
                g.facing = 1 if hits[0].x > g.x else -1
                shake = max(shake, 6)
                pows.append(Pow(g.x + g.facing * 60, g.y - 90))
                dust(g.x + g.facing * 50, g.y, 10)
        g.x = min(max(g.x, 60), W - 60)
        g.y = min(max(g.y, GROUND_TOP + 50), H - 20)

    # --- gorilas no se encimen
    for a in gorillas:
        for b in gorillas:
            if a is b:
                continue
            ox, oy = a.x - b.x, a.y - b.y
            d = math.hypot(ox, oy)
            if 0 < d < 220:
                a.x += ox / d * (220 - d) * 0.12
                a.y += oy / d * (220 - d) * 0.12

    for p in particles:
        p.x += p.vx * DT
        p.y += p.vy * DT
        p.vy += 200 * DT
        p.life -= DT
    particles[:] = [p for p in particles if p.life > 0]
    for p in pows:
        p.life -= DT
    pows[:] = [p for p in pows if p.life > 0]
    shake *= 0.85

    if winner is None and t > FIGHT_START:
        if not [g for g in gorillas if g.state == "alive"]:
            winner = "HOMBRES"
        elif not [m for m in men if m.state == "alive"]:
            winner = "GORILAS"
        if winner:
            end_time = t


# ----------------------------------------------------------------- dibujo
def draw_background():
    img = Image.new("RGB", (W, H))
    arr = np.zeros((H, W, 3), dtype=np.uint8)
    for y in range(H):
        if y < GROUND_TOP:
            k = y / GROUND_TOP
            arr[y] = (int(120 + 100 * k), int(180 + 50 * k), 255)
        else:
            k = (y - GROUND_TOP) / (H - GROUND_TOP)
            arr[y] = (int(70 + 30 * k), int(150 + 40 * k), int(60 + 20 * k))
    img = Image.fromarray(arr)
    d = ImageDraw.Draw(img)
    # sol
    d.ellipse((1060, 30, 1150, 120), fill=(255, 235, 120))
    # montañas
    d.polygon([(0, GROUND_TOP), (180, 90), (380, GROUND_TOP)], fill=(110, 130, 150))
    d.polygon([(250, GROUND_TOP), (520, 60), (800, GROUND_TOP)], fill=(95, 115, 140))
    d.polygon([(650, GROUND_TOP), (900, 110), (1150, GROUND_TOP)], fill=(110, 130, 150))
    d.polygon([(1000, GROUND_TOP), (1180, 80), (1280, 150), (1280, GROUND_TOP)], fill=(95, 115, 140))
    # árboles de selva al fondo
    rnd = random.Random(3)
    for i in range(26):
        x = rnd.uniform(0, W)
        h = rnd.uniform(40, 80)
        d.rectangle((x - 4, GROUND_TOP - h * 0.4, x + 4, GROUND_TOP + 5), fill=(90, 60, 30))
        d.ellipse((x - h * 0.5, GROUND_TOP - h, x + h * 0.5, GROUND_TOP - h * 0.25), fill=(40, 120, 50))
    # matas de pasto
    for i in range(400):
        x = rnd.uniform(0, W)
        y = rnd.uniform(GROUND_TOP + 5, H)
        s = depth_scale(y)
        d.line((x, y, x - 3 * s, y - 8 * s), fill=(50, 120, 45), width=2)
        d.line((x, y, x + 3 * s, y - 9 * s), fill=(50, 120, 45), width=2)
    return img


BG = draw_background()


def rot(px, py, cx, cy, a):
    c, s = math.cos(a), math.sin(a)
    px, py = px - cx, py - cy
    return cx + px * c - py * s, cy + px * s + py * c


def draw_man(d, m, ox, oy):
    s = depth_scale(m.y)
    x, y = m.x + ox, m.y + oy
    # sombra
    d.ellipse((x - 10 * s, y - 3 * s, x + 10 * s, y + 3 * s), fill=(40, 80, 35))
    if m.state == "ko":
        # acostado, ojos de X
        d.line((x - 16 * s, y - 3, x + 10 * s, y - 3), fill=m.shirt, width=max(2, int(6 * s)))
        d.line((x - 16 * s, y - 3, x - 26 * s, y - 1), fill=(40, 40, 70), width=max(2, int(3 * s)))
        hx = x + 16 * s
        d.ellipse((hx - 6 * s, y - 9 * s, hx + 6 * s, y + 3 * s), fill=m.skin)
        d.text((hx - 4 * s, y - 14 * s), "x", fill=(0, 0, 0), font=F_SMALL if s > 0.9 else None)
        return
    by = y - m.z
    a = m.angle if m.state == "flying" else 0
    walk = math.sin(m.phase) * 6 * s if (abs(m.vx) + abs(m.vy) > 20) else 0
    hip = (x, by - 18 * s)
    neck = (x, by - 38 * s)
    head = (x, by - 46 * s)
    pts = {
        "lf": (x - 5 * s + walk, by), "rf": (x + 5 * s - walk, by),
        "hip": hip, "neck": neck, "head": head,
    }
    if m.punch_t > 0:
        hand1 = (x + m.facing * 20 * s, by - 34 * s)
    else:
        hand1 = (x + m.facing * 10 * s, by - 26 * s + walk * 0.5)
    hand2 = (x - m.facing * 8 * s, by - 24 * s - walk * 0.5)
    pts["h1"], pts["h2"] = hand1, hand2
    if m.state == "flying":
        pts["h1"] = (x + 14 * s, by - 44 * s)
        pts["h2"] = (x - 14 * s, by - 44 * s)
        pts = {k: rot(*v, x, by - 24 * s, a) for k, v in pts.items()}
    lw = max(2, int(3 * s))
    pants = (40, 40, 70)
    d.line((pts["lf"], pts["hip"]), fill=pants, width=lw)
    d.line((pts["rf"], pts["hip"]), fill=pants, width=lw)
    d.line((pts["hip"], pts["neck"]), fill=m.shirt, width=max(3, int(7 * s)))
    d.line((pts["neck"], pts["h1"]), fill=m.shirt, width=lw)
    d.line((pts["neck"], pts["h2"]), fill=m.shirt, width=lw)
    r = 7 * s
    hx, hy = pts["head"]
    d.ellipse((pts["h1"][0] - 2.5 * s, pts["h1"][1] - 2.5 * s, pts["h1"][0] + 2.5 * s, pts["h1"][1] + 2.5 * s), fill=m.skin)
    d.ellipse((hx - r, hy - r, hx + r, hy + r), fill=m.skin, outline=(60, 40, 30))
    if m.state == "flying":
        d.ellipse((hx - 2 * s, hy, hx + 2 * s, hy + 4 * s), fill=(0, 0, 0))  # boca de grito


def draw_gorilla(d, g, ox, oy):
    s = depth_scale(g.y) * 1.15
    x, y = g.x + ox, g.y + oy
    fur = (45, 40, 40) if g.hurt_t <= 0 else (120, 50, 50)
    face = (95, 80, 75)
    d.ellipse((x - 55 * s, y - 10 * s, x + 55 * s, y + 10 * s), fill=(40, 80, 35))
    if g.state == "ko":
        d.ellipse((x - 70 * s, y - 40 * s, x + 50 * s, y + 2 * s), fill=fur)
        d.ellipse((x + 30 * s, y - 45 * s, x + 75 * s, y - 5 * s), fill=fur)
        d.ellipse((x + 40 * s, y - 35 * s, x + 70 * s, y - 12 * s), fill=face)
        d.text((x + 45 * s, y - 42 * s), "x x", fill=(255, 255, 255), font=F_SMALL)
        # estrellitas de mareo
        for k in range(3):
            a = t * 4 + k * 2.1
            sx, sy = x + 52 * s + math.cos(a) * 28, y - 65 * s + math.sin(a) * 8
            d.text((sx, sy), "*", fill=(255, 240, 0), font=F_MED)
        return
    bob = math.sin(g.phase) * 3
    f = g.facing
    # piernas
    d.ellipse((x - 40 * s, y - 40 * s, x - 5 * s, y + 2 * s), fill=fur)
    d.ellipse((x + 5 * s, y - 40 * s, x + 40 * s, y + 2 * s), fill=fur)
    # cuerpo
    d.ellipse((x - 50 * s, y - 120 * s + bob, x + 50 * s, y - 25 * s), fill=fur)
    d.ellipse((x - 28 * s, y - 100 * s + bob, x + 28 * s, y - 40 * s), fill=(80, 70, 70))  # pecho
    # brazos
    swing = g.swing_t / 0.3 if g.swing_t > 0 else 0
    arm_a = -1.9 + 2.6 * (1 - swing) if swing > 0 else 0.25
    sx, sy = x + f * 40 * s, y - 100 * s + bob
    ex = sx + f * math.cos(arm_a) * 70 * s
    ey = sy + math.sin(arm_a + 1.2) * 70 * s
    d.line((sx, sy, ex, ey), fill=fur, width=int(28 * s))
    d.ellipse((ex - 16 * s, ey - 16 * s, ex + 16 * s, ey + 16 * s), fill=fur)
    bx, byy = x - f * 42 * s, y - 98 * s + bob
    d.line((bx, byy, bx - f * 18 * s, y - 15 * s), fill=fur, width=int(26 * s))
    d.ellipse((bx - f * 18 * s - 15 * s, y - 30 * s, bx - f * 18 * s + 15 * s, y), fill=fur)
    # cabeza
    hx, hy = x + f * 10 * s, y - 135 * s + bob
    d.ellipse((hx - 30 * s, hy - 30 * s, hx + 30 * s, hy + 28 * s), fill=fur)
    d.ellipse((hx - 20 * s + f * 4 * s, hy - 10 * s, hx + 20 * s + f * 4 * s, hy + 24 * s), fill=face)
    # ojos enojados
    for e in (-9, 9):
        ex2 = hx + f * 4 * s + e * s
        d.ellipse((ex2 - 4 * s, hy - 6 * s, ex2 + 4 * s, hy + 2 * s), fill=(255, 255, 255))
        d.ellipse((ex2 - 2 * s, hy - 4 * s, ex2 + 2 * s, hy), fill=(200, 0, 0))
    d.line((hx - 16 * s, hy - 14 * s, hx - 2 * s, hy - 8 * s), fill=(20, 15, 15), width=int(4 * s))
    d.line((hx + 16 * s, hy - 14 * s, hx + 2 * s, hy - 8 * s), fill=(20, 15, 15), width=int(4 * s))
    # boca
    if g.roar_t > 0 or swing > 0:
        d.ellipse((hx - 10 * s + f * 4 * s, hy + 6 * s, hx + 10 * s + f * 4 * s, hy + 22 * s), fill=(120, 0, 0))
        d.rectangle((hx - 7 * s + f * 4 * s, hy + 7 * s, hx + 7 * s + f * 4 * s, hy + 10 * s), fill=(255, 255, 255))
    else:
        d.line((hx - 8 * s + f * 4 * s, hy + 14 * s, hx + 8 * s + f * 4 * s, hy + 14 * s), fill=(30, 20, 20), width=int(3 * s))
    if g.roar_t > 0:
        d.text((hx - 60, hy - 85 * s), "¡GRRAAAH!", fill=(255, 255, 255), font=F_MED,
               stroke_width=3, stroke_fill=(0, 0, 0))
    # barra de vida
    bw = 90
    px, py = g.x + ox - bw / 2, g.y + oy - 180 * s
    d.rectangle((px - 2, py - 2, px + bw + 2, py + 12), fill=(0, 0, 0))
    k = max(0, g.hp / g.max_hp)
    col = (60, 220, 60) if k > 0.5 else (240, 200, 0) if k > 0.25 else (230, 40, 40)
    d.rectangle((px, py, px + bw * k, py + 10), fill=col)
    d.text((px + bw / 2, py - 14), g.name, fill=(255, 255, 255), font=F_SMALL, anchor="mm",
           stroke_width=2, stroke_fill=(0, 0, 0))


def centered(d, y, text, f, fill=(255, 255, 255)):
    d.text((W / 2, y), text, fill=fill, font=f, anchor="mm", stroke_width=4, stroke_fill=(0, 0, 0))


def render():
    img = BG.copy()
    d = ImageDraw.Draw(img)
    ox = random.uniform(-shake, shake)
    oy = random.uniform(-shake, shake)

    # orden por profundidad
    ents = [("m", m, m.y) for m in men] + [("g", g, g.y) for g in gorillas]
    ents.sort(key=lambda e: (e[1].state != "ko", e[2]))
    for kind, e, _ in ents:
        if kind == "m":
            draw_man(d, e, ox, oy)
        else:
            draw_gorilla(d, e, ox, oy)

    for p in particles:
        a = p.life / p.max_life
        r = p.r * (0.5 + a)
        c = tuple(int(cc * a + 200 * (1 - a)) for cc in p.color)
        d.ellipse((p.x - r + ox, p.y - r + oy, p.x + r + ox, p.y + r + oy), fill=c)
    for p in pows:
        k = 1 - p.life / 0.6
        f = F_BIG if p.big else F_POW
        d.text((p.x + ox, p.y + oy - k * 30), p.text, fill=p.color, font=f, anchor="mm",
               stroke_width=4, stroke_fill=(0, 0, 0))

    # HUD
    alive_m = sum(m.state == "alive" for m in men)
    alive_g = sum(g.state == "alive" for g in gorillas)
    d.rounded_rectangle((20, 15, 380, 75), 12, fill=(0, 0, 0))
    d.text((35, 25), f"HOMBRES: {alive_m}/100", fill=(120, 200, 255), font=F_MED)
    d.rounded_rectangle((W - 340, 15, W - 20, 75), 12, fill=(0, 0, 0))
    d.text((W - 325, 25), f"GORILAS: {alive_g}/3", fill=(255, 140, 100), font=F_MED)
    if t >= FIGHT_START:
        d.text((W / 2, 45), f"{t - FIGHT_START:5.1f}s", fill=(255, 255, 255), font=F_MED,
               anchor="mm", stroke_width=3, stroke_fill=(0, 0, 0))

    if t < FIGHT_START:
        centered(d, 300, "100 HOMBRES  vs  3 GORILAS", F_BIG, (255, 230, 0))
        n = 3 - int(t)
        centered(d, 400, str(n) if t < 2.4 else "¡PELEEN!", F_BIG,
                 (255, 80, 80) if t >= 2.4 else (255, 255, 255))
    if winner:
        dt_ = t - end_time
        if dt_ > 0.5:
            d.rectangle((0, 260, W, 460), fill=(0, 0, 0))
            centered(d, 320, f"¡GANAN LOS {winner}!", F_BIG, (255, 230, 0))
            centered(d, 400, f"Tiempo: {end_time - FIGHT_START:.1f}s   |   "
                             f"Hombres en pie: {alive_m}   |   Gorilas en pie: {alive_g}",
                     F_SMALL)
    return img


# ----------------------------------------------------------------- main
def main():
    global t
    proc = subprocess.Popen(
        ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
         "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-c:v", "libx264",
         "-pix_fmt", "yuv420p", "-crf", "20", "-preset", "medium", OUT],
        stdin=subprocess.PIPE)
    frames = 0
    while t < MAX_SECONDS:
        update()
        proc.stdin.write(render().tobytes())
        frames += 1
        t += DT
        if winner and t - end_time > 4:
            break
    proc.stdin.close()
    proc.wait()
    print(f"Listo: {OUT} ({frames} frames, {frames / FPS:.1f}s) — ganador: {winner}")


if __name__ == "__main__":
    main()
