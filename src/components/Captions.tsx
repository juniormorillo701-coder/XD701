import React, { useMemo } from "react";
import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { displayWord, toPages } from "../captions";
import type { Word } from "../scripts";
import { COLORS, FONT, SAFE, outlined } from "../theme";

type Props = {
  /** Word timings already shifted to VIDEO time (seconds). */
  words: Word[];
  fromSec: number;
  toSec: number;
  placement: "top" | "bottom";
  offsetPx: number;
  maxWordsPerPage: number;
};

/** TikTok-style word-by-word captions: white + black outline, active word yellow. */
export const Captions: React.FC<Props> = ({ words, fromSec, toSec, placement, offsetPx, maxWordsPerPage }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = frame / fps;

  const pages = useMemo(() => toPages(words, maxWordsPerPage), [words, maxWordsPerPage]);

  if (t < fromSec || t >= toSec) return null;

  // Current page = the last page that has started (stays until the next one).
  const pageIndex = pages.findLastIndex((p) => p.startSec <= t);
  if (pageIndex === -1) return null;
  const page = pages[pageIndex];
  const next = pages[pageIndex + 1];
  // Hide during long silences (> 0.6 s after the page ended).
  const holdUntil = next ? next.startSec : page.endSec + 0.6;
  if (t > Math.min(holdUntil, page.endSec + 0.6)) return null;

  const pageFrame = frame - Math.round(Math.max(page.startSec, fromSec) * fps);
  const pop = spring({ frame: pageFrame, fps, config: { damping: 14, stiffness: 260, mass: 0.5 } });

  const activeIndex = page.words.findLastIndex((w) => w.startSec <= t);

  return (
    <AbsoluteFill
      style={{
        height: "auto",
        ...(placement === "top"
          ? { top: Math.max(offsetPx, SAFE.top + 20), bottom: "auto" }
          : { top: "auto", bottom: Math.max(offsetPx, SAFE.bottom + 20) }),
        alignItems: "center",
        padding: `0 ${SAFE.side}px`,
      }}
    >
      <div
        style={{
          display: "flex",
          flexWrap: "wrap",
          justifyContent: "center",
          columnGap: 38,
          maxWidth: 940,
          transform: `scale(${interpolate(pop, [0, 1], [0.8, 1])})`,
        }}
      >
        {page.words.map((w, i) => {
          const active = i === activeIndex;
          return (
            <span
              key={`${pageIndex}-${i}`}
              style={{
                fontFamily: FONT,
                fontWeight: 900,
                fontSize: 86,
                lineHeight: 1.15,
                color: active ? COLORS.yellow : COLORS.white,
                transform: `scale(${active ? 1.04 : 1})`,
                display: "inline-block",
                ...outlined(12),
              }}
            >
              {displayWord(w.text)}
            </span>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};
