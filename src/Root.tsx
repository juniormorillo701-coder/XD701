import React from "react";
import { CalculateMetadataFunction, Composition, staticFile } from "remotion";
import { getAudioDurationInSeconds, getVideoMetadata } from "@remotion/media-utils";
import { PadlockAd, PadlockAdProps } from "./PadlockAd";
import { SCRIPTS, getScript } from "./scripts";
import { FPS, HEIGHT, WIDTH } from "./theme";

const safe = async <T,>(p: Promise<T>): Promise<T | undefined> => {
  try {
    return await p;
  } catch (e) {
    console.warn("[padlock-ad] Could not read media metadata:", e);
    return undefined;
  }
};

/** Duration comes from the script; real asset lengths are measured for caption sync & looping. */
const calculateMetadata: CalculateMetadataFunction<PadlockAdProps> = async ({ props }) => {
  const s = getScript(props.scriptId);
  const [voiceDurationSec, clipMeta] = await Promise.all([
    s.assets.voice ? safe(getAudioDurationInSeconds(staticFile(s.assets.voice))) : undefined,
    safe(getVideoMetadata(staticFile(s.assets.clip))),
  ]);
  return {
    durationInFrames: Math.round(s.endCard.toSec * FPS),
    props: { ...props, voiceDurationSec, clipDurationSec: clipMeta?.durationInSeconds },
  };
};

export const RemotionRoot: React.FC = () => (
  <>
    {SCRIPTS.map((s) => (
      <Composition
        key={s.id}
        id={`Padlock-${s.id.replace("script", "Script")}`}
        component={PadlockAd}
        width={WIDTH}
        height={HEIGHT}
        fps={FPS}
        durationInFrames={Math.round(s.endCard.toSec * FPS)}
        defaultProps={{ scriptId: s.id, showSafeZones: false } as PadlockAdProps}
        calculateMetadata={calculateMetadata}
      />
    ))}
  </>
);
