import React from "react";
import { AbsoluteFill } from "remotion";
import { SAFE } from "../theme";

/** Studio-only guide: red = covered by TikTok UI. Toggle with the `showSafeZones` prop. */
export const SafeZones: React.FC = () => (
  <AbsoluteFill style={{ pointerEvents: "none" }}>
    <div style={{ position: "absolute", top: 0, left: 0, right: 0, height: SAFE.top, background: "rgba(255,0,0,0.3)" }} />
    <div style={{ position: "absolute", bottom: 0, left: 0, right: 0, height: SAFE.bottom, background: "rgba(255,0,0,0.3)" }} />
  </AbsoluteFill>
);
