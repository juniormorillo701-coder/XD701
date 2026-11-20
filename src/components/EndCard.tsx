import React from "react";
import {
  AbsoluteFill,
  Img,
  interpolate,
  spring,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { COLORS, FONT, SAFE } from "../theme";

type Props = {
  image: string;
  name: string;
  price: string;
  cta: string;
};

/** Final card: product photo, name, price and a pulsing "LINK IN BIO" button. */
export const EndCard: React.FC<Props> = ({ image, name, price, cta }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const enter = spring({ frame, fps, config: { damping: 18, stiffness: 160 } });
  const img = spring({ frame: frame - 4, fps, config: { damping: 11, stiffness: 140 } });
  const nameIn = spring({ frame: frame - 8, fps, config: { damping: 14 } });
  const priceIn = spring({ frame: frame - 12, fps, config: { damping: 9, stiffness: 200 } });
  const ctaIn = spring({ frame: frame - 16, fps, config: { damping: 12 } });

  // Continuous pulse (~1.6 pulses per second) once the button is in.
  const pulse = 1 + 0.06 * Math.max(0, Math.sin(((frame - 16) / fps) * Math.PI * 3.2));
  const shine = ((frame * 18) % 1600) - 400;

  return (
    <AbsoluteFill
      style={{
        transform: `translateY(${interpolate(enter, [0, 1], [1920, 0])}px)`,
        background: `radial-gradient(circle at 50% 42%, #FFFFFF 0%, #FFFFFF 38%, #E6F1FF 75%, #CFE4FF 100%)`,
        paddingTop: SAFE.top + 40,
        paddingBottom: SAFE.bottom + 40,
        alignItems: "center",
        justifyContent: "space-between",
        fontFamily: FONT,
      }}
    >
      <div
        style={{
          fontWeight: 900,
          fontSize: 82,
          lineHeight: 1.05,
          color: COLORS.ink,
          textAlign: "center",
          padding: `0 ${SAFE.side}px`,
          letterSpacing: -1,
          opacity: nameIn,
          transform: `translateY(${interpolate(nameIn, [0, 1], [40, 0])}px)`,
        }}
      >
        {name}
      </div>

      <Img
        src={staticFile(image)}
        style={{
          width: 760,
          height: 760,
          objectFit: "contain",
          mixBlendMode: "multiply", // white photo background blends in
          transform: `scale(${interpolate(img, [0, 1], [0.6, 1])})`,
          opacity: interpolate(img, [0, 0.3], [0, 1], { extrapolateRight: "clamp" }),
        }}
      />

      <div
        style={{
          fontWeight: 900,
          fontSize: 120,
          color: COLORS.blue,
          letterSpacing: -2,
          transform: `scale(${interpolate(priceIn, [0, 1], [0.2, 1])})`,
          opacity: interpolate(priceIn, [0, 0.2], [0, 1], { extrapolateRight: "clamp" }),
        }}
      >
        {price}
      </div>

      <div
        style={{
          position: "relative",
          overflow: "hidden",
          fontWeight: 900,
          fontSize: 66,
          color: COLORS.white,
          background: COLORS.ink,
          padding: "30px 70px",
          borderRadius: 999,
          boxShadow: "0 16px 40px rgba(11,18,32,0.35)",
          opacity: ctaIn,
          transform: `translateY(${interpolate(ctaIn, [0, 1], [60, 0])}px) scale(${pulse})`,
        }}
      >
        {cta}
        <div
          style={{
            position: "absolute",
            top: 0,
            bottom: 0,
            left: shine,
            width: 140,
            background:
              "linear-gradient(90deg, rgba(255,255,255,0) 0%, rgba(255,255,255,0.35) 50%, rgba(255,255,255,0) 100%)",
            transform: "skewX(-20deg)",
          }}
        />
      </div>
    </AbsoluteFill>
  );
};
