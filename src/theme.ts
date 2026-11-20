import { loadFont } from "@remotion/google-fonts/Montserrat";

const { fontFamily } = loadFont("normal", {
  weights: ["800", "900"],
  subsets: ["latin"],
});

export const FPS = 30;
export const WIDTH = 1080;
export const HEIGHT = 1920;

/** TikTok UI covers the top 150 px and the bottom 300 px. */
export const SAFE = { top: 150, bottom: 300, side: 60 };

export const FONT = `${fontFamily}, "Noto Color Emoji", "Apple Color Emoji", "Segoe UI Emoji", sans-serif`;

export const COLORS = {
  white: "#FFFFFF",
  black: "#000000",
  yellow: "#FFE600",
  blue: "#1E90FF",
  blueGlow: "#4FC3FF",
  ink: "#0B1220",
  bgLight: "#F4F7FB",
};

/** Thick black outline that stays legible on any background. */
export const outlined = (strokePx: number) =>
  ({
    WebkitTextStroke: `${strokePx}px ${COLORS.black}`,
    paintOrder: "stroke fill",
    textShadow: `0 6px 18px rgba(0,0,0,0.55)`,
  }) as const;
