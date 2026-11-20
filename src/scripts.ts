/**
 * ─────────────────────────────────────────────────────────────────────────────
 *  AD SCRIPTS — the only file you need to edit to change the ad.
 * ─────────────────────────────────────────────────────────────────────────────
 *
 *  Every script becomes its own composition in the Studio
 *  ("Padlock-Script1" … "Padlock-Script5").  All times are in SECONDS
 *  from the start of the video. The total length = endCard.toSec.
 *
 *  Assets are file names inside /public (clip, product photo, voice).
 *  Each script may point to different files (e.g. clip-gym.mp4, voice3.mp3).
 *
 *  Subtitles:
 *   - With no voice file (assets.voice = null) the captions show
 *     `captions.text`, spread evenly over the captions window.
 *   - If `voice.words` is empty, word timings are estimated automatically
 *     from the voice text and the real length of the mp3.
 *   - For frame-exact sync paste real timings in `voice.words`
 *     (e.g. from `npm run transcribe -- voice.mp3`, CapCut or any
 *     transcription tool).  Format: { text, startSec, endSec } where the
 *     times are relative to the START OF THE MP3 (not of the video).
 */

export type Word = {
  text: string;
  /** Seconds from the start of the mp3. */
  startSec: number;
  /** Seconds from the start of the mp3. */
  endSec: number;
};

export type AdScript = {
  id: string;
  label: string;
  assets: {
    clip: string;
    product: string;
    /** Narration mp3 in /public. `null` = no voice (captions then show `captions.text`). */
    voice: string | null;
    /** Optional click/unlock SFX in /public. `null` = silent unlock. */
    click: string | null;
  };
  product: {
    name: string;
    price: string;
    cta: string;
  };
  /** Big text at the top during the opening seconds. */
  hook: { text: string; fromSec: number; toSec: number };
  voice: {
    text: string;
    /** When the mp3 starts playing in the video. */
    startSec: number;
    volume: number;
    /** Optional exact word timings (relative to the mp3). */
    words: Word[];
  };
  /** Word-by-word TikTok captions. */
  captions: {
    /**
     * Text shown word-by-word when there is NO voice file (assets.voice = null).
     * Spread evenly across fromSec–toSec. Keep it short (~2 words per second).
     */
    text?: string;
    fromSec: number;
    toSec: number;
    /**
     * "bottom" = lower third (classic TikTok). "top" = under the top safe zone
     * (use it when the product fills the lower half of the clip, like clip.mp4).
     */
    placement: "top" | "bottom";
    /** Distance in px from the chosen edge. Bottom: keep ≥ 320. Top: keep ≥ 170. */
    offsetPx: number;
    /** Max words shown on screen at the same time. */
    maxWordsPerPage: number;
  };
  /** Blue flash + click when the padlock opens in the clip. */
  unlock: { atSec: number; toSec: number; text: string };
  /** Background clip. */
  clip: {
    /** Skip the first N seconds of clip.mp4. */
    startFromSec: number;
    /** Slow zoom over the whole clip (1 = no zoom). */
    zoomFrom: number;
    zoomTo: number;
    /** Keep the clip's own audio? 0 = muted. */
    volume: number;
  };
  /** Final card with product photo, name, price and CTA. */
  endCard: { fromSec: number; toSec: number };
};

const PRODUCT = {
  name: "Smart Fingerprint Padlock",
  price: "$16.99",
  cta: "LINK IN BIO 👇",
};

const ASSETS = {
  clip: "clip.mp4",
  product: "product.jpg",
  // Set to "voice.mp3" once you have a narration file in /public.
  voice: null as string | null,
  click: "click.wav",
};

/** Default timeline shared by every script (override per script if needed). */
const TIMELINE = {
  hook: { fromSec: 0, toSec: 2 },
  // clip.mp4: the fingerprint lights up blue at ~5.4 s → unlock flash there.
  // Captions go on top: in clip.mp4 the padlock fills the lower half of the frame.
  captions: { fromSec: 2, toSec: 5.4, placement: "top" as const, offsetPx: 230, maxWordsPerPage: 3 },
  unlock: { atSec: 5.4, toSec: 8 },
  clip: { startFromSec: 0, zoomFrom: 1, zoomTo: 1.15, volume: 0 },
  endCard: { fromSec: 8, toSec: 11 },
};

export const SCRIPTS: AdScript[] = [
  // ── GUION 1 ── (placeholder: replace hook / voice with your real copy) ──
  {
    id: "script1",
    label: "Guion 1 – No more keys (borrador)",
    assets: ASSETS,
    product: PRODUCT,
    hook: { ...TIMELINE.hook, text: "Lost your key again? 🔑" },
    voice: {
      text: "Stop losing keys. Just touch it and it opens. Smart Fingerprint Padlock. Link in bio.",
      startSec: 0,
      volume: 1,
      words: [],
    },
    captions: { ...TIMELINE.captions, text: "No keys. No codes. Just your finger." },
    unlock: { ...TIMELINE.unlock, text: "No keys. No codes ⚡" },
    clip: TIMELINE.clip,
    endCard: TIMELINE.endCard,
  },

  // ── GUION 2 ── "Wet hands" ──────────────────────────────────────────────
  {
    id: "script2",
    label: "Guion 2 – Wet hands",
    assets: ASSETS,
    product: PRODUCT,
    hook: { ...TIMELINE.hook, text: "Gym hands. Wet hands. Still opens 👆" },
    voice: {
      text: "Sweaty hands, wet hands, gloves off… doesn't matter. Your fingerprint opens it in under a second. Smart Fingerprint Padlock. Link in bio.",
      startSec: 0,
      volume: 1,
      words: [],
    },
    captions: { ...TIMELINE.captions, text: "Sweaty hands. Wet hands. Gloves off. Doesn't matter." },
    unlock: { ...TIMELINE.unlock, text: "Under 1 second ⚡" },
    clip: TIMELINE.clip,
    endCard: TIMELINE.endCard,
  },

  // ── GUION 3 ── (placeholder) ────────────────────────────────────────────
  {
    id: "script3",
    label: "Guion 3 – Gym locker (borrador)",
    assets: ASSETS,
    product: PRODUCT,
    hook: { ...TIMELINE.hook, text: "Your gym locker needs this 🏋️" },
    voice: {
      text: "Forgot your locker code mid workout? Not anymore. One touch and you're in. Smart Fingerprint Padlock. Link in bio.",
      startSec: 0,
      volume: 1,
      words: [],
    },
    captions: { ...TIMELINE.captions, text: "Forgot your locker code? Not anymore." },
    unlock: { ...TIMELINE.unlock, text: "One touch ⚡" },
    clip: TIMELINE.clip,
    endCard: TIMELINE.endCard,
  },

  // ── GUION 4 ── (placeholder) ────────────────────────────────────────────
  {
    id: "script4",
    label: "Guion 4 – Share access (borrador)",
    assets: ASSETS,
    product: PRODUCT,
    hook: { ...TIMELINE.hook, text: "The whole family, one lock 👨‍👩‍👧" },
    voice: {
      text: "Save up to ten fingerprints. Everyone gets in, nobody needs a key. Smart Fingerprint Padlock. Link in bio.",
      startSec: 0,
      volume: 1,
      words: [],
    },
    captions: { ...TIMELINE.captions, text: "Up to 10 fingerprints. Zero keys." },
    unlock: { ...TIMELINE.unlock, text: "Up to 10 fingerprints ⚡" },
    clip: TIMELINE.clip,
    endCard: TIMELINE.endCard,
  },

  // ── GUION 5 ── (placeholder) ────────────────────────────────────────────
  {
    id: "script5",
    label: "Guion 5 – USB charge (borrador)",
    assets: ASSETS,
    product: PRODUCT,
    hook: { ...TIMELINE.hook, text: "No batteries. Ever. 🔋" },
    voice: {
      text: "Charge it with USB, forget it for months. Touch and it opens. Smart Fingerprint Padlock. Link in bio.",
      startSec: 0,
      volume: 1,
      words: [],
    },
    captions: { ...TIMELINE.captions, text: "USB charge. Lasts for months." },
    unlock: { ...TIMELINE.unlock, text: "USB rechargeable ⚡" },
    clip: TIMELINE.clip,
    endCard: TIMELINE.endCard,
  },
];

export const DEFAULT_SCRIPT_ID = "script2";

export const getScript = (id: string): AdScript => {
  const script = SCRIPTS.find((s) => s.id === id);
  if (!script) {
    throw new Error(
      `Unknown scriptId "${id}". Available: ${SCRIPTS.map((s) => s.id).join(", ")}`,
    );
  }
  return script;
};
