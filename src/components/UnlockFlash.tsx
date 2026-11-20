import React from "react";
import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { COLORS, FONT, SAFE } from "../theme";

/** Blue flash + expanding ring + "Under 1 second ⚡" badge. */
export const UnlockFlash: React.FC<{ text: string }> = ({ text }) => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();

  const flash = interpolate(frame, [0, 2, 12], [0, 0.85, 0], {
    extrapolateRight: "clamp",
  });
  const ring = interpolate(frame, [0, 16], [0, 1], { extrapolateRight: "clamp" });

  const badge = spring({
    frame: frame - 3,
    fps,
    config: { damping: 10, stiffness: 200, mass: 0.6 },
  });
  const exit = interpolate(frame, [durationInFrames - 5, durationInFrames], [1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <AbsoluteFill>
      <AbsoluteFill
        style={{
          background: `radial-gradient(circle at 50% 50%, ${COLORS.blueGlow} 0%, ${COLORS.blue} 45%, rgba(30,144,255,0) 80%)`,
          opacity: flash,
          mixBlendMode: "screen",
        }}
      />
      <AbsoluteFill style={{ alignItems: "center", justifyContent: "center" }}>
        <div
          style={{
            width: 900,
            height: 900,
            borderRadius: "50%",
            border: `${interpolate(ring, [0, 1], [40, 2])}px solid ${COLORS.blueGlow}`,
            boxShadow: `0 0 80px ${COLORS.blueGlow}`,
            transform: `scale(${interpolate(ring, [0, 1], [0.2, 1.5])})`,
            opacity: interpolate(ring, [0, 0.2, 1], [0, 1, 0]),
          }}
        />
      </AbsoluteFill>
      <AbsoluteFill
        style={{
          top: SAFE.top + 70,
          bottom: "auto",
          height: "auto",
          alignItems: "center",
          opacity: exit,
        }}
      >
        <div
          style={{
            fontFamily: FONT,
            fontWeight: 900,
            fontSize: 80,
            whiteSpace: "nowrap",
            color: COLORS.white,
            padding: "16px 40px",
            borderRadius: 28,
            background: `linear-gradient(135deg, ${COLORS.blue}, #0057D9)`,
            boxShadow: `0 0 50px rgba(79,195,255,0.8), 0 12px 30px rgba(0,0,0,0.4)`,
            transform: `scale(${interpolate(badge, [0, 1], [0.3, 1])})`,
            opacity: interpolate(badge, [0, 0.2], [0, 1], { extrapolateRight: "clamp" }),
            textShadow: "0 4px 12px rgba(0,0,0,0.45)",
          }}
        >
          {text}
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
