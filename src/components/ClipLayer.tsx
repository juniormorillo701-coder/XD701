import React from "react";
import {
  AbsoluteFill,
  Loop,
  OffthreadVideo,
  interpolate,
  spring,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
  Easing,
} from "remotion";

type Props = {
  src: string;
  startFromSec: number;
  /** Length (in frames) of the usable part of the clip, for looping. */
  clipFrames: number;
  zoomFrom: number;
  zoomTo: number;
  volume: number;
  /** Frame (relative to this layer) where the padlock opens → zoom punch. */
  unlockFrame: number;
};

export const ClipLayer: React.FC<Props> = ({
  src,
  startFromSec,
  clipFrames,
  zoomFrom,
  zoomTo,
  volume,
  unlockFrame,
}) => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();

  const slowZoom = interpolate(frame, [0, durationInFrames], [zoomFrom, zoomTo], {
    extrapolateRight: "clamp",
    easing: Easing.inOut(Easing.quad),
  });

  // Quick "punch" zoom when the lock opens.
  const punch = spring({
    frame: frame - unlockFrame,
    fps,
    config: { damping: 12, stiffness: 220 },
    durationInFrames: 12,
  });
  const punchScale = frame >= unlockFrame
    ? interpolate(punch, [0, 1], [1.08, 1])
    : 1;

  const video = (
    <OffthreadVideo
      src={staticFile(src)}
      trimBefore={Math.round(startFromSec * fps)}
      volume={volume}
      muted={volume === 0}
      style={{ width: "100%", height: "100%", objectFit: "cover" }}
    />
  );

  return (
    <AbsoluteFill
      style={{
        transform: `scale(${slowZoom * punchScale})`,
        transformOrigin: "50% 45%",
      }}
    >
      {clipFrames < durationInFrames ? (
        <Loop durationInFrames={Math.max(1, clipFrames)}>{video}</Loop>
      ) : (
        video
      )}
      {/* Gentle top/bottom gradients so white text is always readable. */}
      <AbsoluteFill
        style={{
          background:
            "linear-gradient(180deg, rgba(0,0,0,0.45) 0%, rgba(0,0,0,0) 28%, rgba(0,0,0,0) 62%, rgba(0,0,0,0.5) 100%)",
        }}
      />
    </AbsoluteFill>
  );
};
