# Pardbox – Smart Fingerprint Padlock (anuncio TikTok)

Proyecto Remotion · 1080×1920 · 30 fps · 11 s.

## 1. Assets (en `/public`)

| Archivo        | Qué es                                                   |
| -------------- | -------------------------------------------------------- |
| `clip.mp4`     | Manos mojadas / con guantes abriendo el candado          |
| `product.jpg`  | Foto del producto sobre fondo blanco                     |
| `voice.mp3`    | Narración en inglés (opcional, hoy desactivada)          |
| `click.wav`    | Clic de desbloqueo (ya incluido, generado con `node tools/make-click.mjs`) |

## 2. Comandos

```bash
npm install                 # una sola vez

npm run dev                 # abre Remotion Studio  (= npx remotion studio)

npm run render              # renderiza el guion 2 → out/padlock-script2.mp4
# equivalente:
npx remotion render Padlock-Script2 out/padlock-script2.mp4

npx remotion render Padlock-Script3 out/padlock-script3.mp4   # otro guion
npm run render:all          # los 5 guiones
```

## 3. Cambiar el anuncio → solo `src/scripts.ts`

Cada guion es un objeto con hook, voz, textos, tiempos y assets. Cada uno
aparece como composición propia en el Studio (`Padlock-Script1` … `5`).

- **Tiempos** en segundos: `hook`, `captions`, `unlock` (momento en que se
  abre el candado en el clip), `endCard` (su `toSec` define la duración total).
- **Posición de subtítulos**: `captions.placement` (`"top"` o `"bottom"`) y
  `captions.offsetPx`. Con el clip actual van arriba porque el candado ocupa
  la mitad inferior.
- **Sin voz**: `assets.voice: null` → los subtítulos muestran `captions.text`.
  Cuando tengas `voice.mp3`, pon `voice: "voice.mp3"` en `ASSETS`.
- **Assets por guion**: `assets.clip`, `assets.voice`… (p. ej. `voice3.mp3`).
- **Clic opcional**: `assets.click: null` para quitarlo.
- Los guiones 1, 3, 4 y 5 traen **texto de borrador**: reemplázalo por tu copy.

### Sincronía de subtítulos

Por defecto los tiempos de cada palabra se **estiman** a partir del texto y
de la duración real de `voice.mp3`. Para sincronía exacta, pega los tiempos
reales en `voice.words` (relativos al inicio del mp3):

```ts
words: [
  { text: "Sweaty", startSec: 0.12, endSec: 0.48 },
  { text: "hands,", startSec: 0.48, endSec: 0.85 },
  // …
],
```

Si la voz arranca con silencio o no cuadra, también puedes moverla con
`voice.startSec`.

## 4. Márgenes seguros de TikTok

Nada importante en los 150 px de arriba ni en los 300 px de abajo. En el
Studio activa la prop `showSafeZones` (panel derecho) para ver las franjas
rojas.

## Estructura

```
src/
  scripts.ts          ← datos de los 5 guiones (lo único que se edita)
  PadlockAd.tsx       ← línea de tiempo
  Root.tsx            ← composiciones + medición de voz/clip
  captions.ts         ← estimación de tiempos y agrupación de palabras
  theme.ts            ← fuente, colores, zonas seguras
  components/         ← ClipLayer, HookText, Captions, UnlockFlash, EndCard, SafeZones
```
