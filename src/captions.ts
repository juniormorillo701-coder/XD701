import type { Word } from "./scripts";

/**
 * Estimates word timings when no real ones are provided: spreads the words
 * over the spoken part of the mp3, weighting longer words more and adding
 * small pauses after commas / periods / ellipses.
 */
export const estimateWords = (
  text: string,
  audioDurationSec: number,
  leadInSec = 0.15,
  tailSec = 0.35,
): Word[] => {
  const tokens = text.split(/\s+/).filter(Boolean);
  if (tokens.length === 0) return [];

  const pauseAfter = (t: string) =>
    /(\.\.\.|…|[.!?])$/.test(t) ? 5 : /[,;:]$/.test(t) ? 3 : 0;
  const weightOf = (t: string) =>
    Math.max(t.replace(/[^\p{L}\p{N}]/gu, "").length, 2) + 2;

  const totalUnits = tokens.reduce(
    (sum, t, i) => sum + weightOf(t) + (i < tokens.length - 1 ? pauseAfter(t) : 0),
    0,
  );
  const span = Math.max(audioDurationSec - leadInSec - tailSec, 0.5);
  const secPerUnit = span / totalUnits;

  let cursor = leadInSec;
  return tokens.map((t) => {
    const start = cursor;
    const end = start + weightOf(t) * secPerUnit;
    cursor = end + pauseAfter(t) * secPerUnit;
    return { text: t, startSec: start, endSec: end };
  });
};

export type CaptionPage = {
  words: Word[];
  startSec: number;
  endSec: number;
};

/** Groups words into short "pages" (max N words, broken at punctuation). */
export const toPages = (words: Word[], maxWordsPerPage: number): CaptionPage[] => {
  const pages: CaptionPage[] = [];
  let current: Word[] = [];
  const flush = () => {
    if (current.length === 0) return;
    pages.push({
      words: current,
      startSec: current[0].startSec,
      endSec: current[current.length - 1].endSec,
    });
    current = [];
  };
  for (const w of words) {
    current.push(w);
    if (current.length >= maxWordsPerPage || /[.,!?…;:]$/.test(w.text)) flush();
  }
  flush();
  return pages;
};

/** Text as shown on screen: uppercase, without trailing punctuation. */
export const displayWord = (t: string) =>
  t.replace(/(\.\.\.|[.,!?…;:])+$/u, "").toUpperCase();
