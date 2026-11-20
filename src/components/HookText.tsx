import React from "react";
import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { COLORS, FONT, SAFE, outlined } from "../theme";

/** Big headline at the top. Each sentence pops in with a spring. */
export const HookText: React.FC<{ text: string }> = ({ text }) => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();

  // "Gym hands. Wet hands. Still opens 👆" → 3 chunks, last one highlighted.
  const chunks = text.match(/[^.!?]+[.!?]?/g)?.map((c) => c.trim()).filter(Boolean) ?? [text];

  const exit = interpolate(frame, [durationInFrames - 5, durationInFrames], [1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <AbsoluteFill
      style={{
        top: SAFE.top + 50,
        bottom: "auto",
        height: "auto",
        alignItems: "center",
        padding: `0 ${SAFE.side}px`,
        opacity: exit,
        transform: `scale(${interpolate(exit, [0, 1], [0.85, 1])})`,
      }}
    >
      <div
        style={{
          display: "flex",
          flexWrap: "wrap",
          justifyContent: "center",
          columnGap: 22,
          rowGap: 4,
          maxWidth: 960,
        }}
      >
        {chunks.map((chunk, i) => {
          const s = spring({
            frame: frame - i * 5,
            fps,
            config: { damping: 9, stiffness: 180, mass: 0.6 },
          });
          const isLast = i === chunks.length - 1 && chunks.length > 1;
          return (
            <span
              key={i}
              style={{
                fontFamily: FONT,
                fontWeight: 900,
                fontSize: 104,
                lineHeight: 1.08,
                letterSpacing: -1,
                color: isLast ? COLORS.yellow : COLORS.white,
                textAlign: "center",
                display: "inline-block",
                opacity: interpolate(s, [0, 0.2], [0, 1], { extrapolateRight: "clamp" }),
                transform: `scale(${interpolate(s, [0, 1], [0.3, 1])}) rotate(${interpolate(s, [0, 1], [-6, 0])}deg)`,
                ...outlined(14),
              }}
            >
              {chunk}
            </span>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};
