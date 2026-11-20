import React, { useMemo } from "react";
import { AbsoluteFill, Audio, Sequence, staticFile, useVideoConfig } from "remotion";
import { estimateWords } from "./captions";
import { Captions } from "./components/Captions";
import { ClipLayer } from "./components/ClipLayer";
import { EndCard } from "./components/EndCard";
import { HookText } from "./components/HookText";
import { SafeZones } from "./components/SafeZones";
import { UnlockFlash } from "./components/UnlockFlash";
import { getScript, type Word } from "./scripts";

export type PadlockAdProps = {
  scriptId: string;
  showSafeZones: boolean;
  /** Filled automatically by calculateMetadata (Root.tsx). */
  voiceDurationSec?: number;
  clipDurationSec?: number;
};

export const PadlockAd: React.FC<PadlockAdProps> = ({
  scriptId,
  showSafeZones,
  voiceDurationSec,
  clipDurationSec,
}) => {
  const { fps } = useVideoConfig();
  const s = getScript(scriptId);
  const f = (sec: number) => Math.round(sec * fps);

  // Word timings in VIDEO time.
  const words = useMemo(() => {
    const shift = (list: Word[], by: number) =>
      list.map((w) => ({ ...w, startSec: w.startSec + by, endSec: w.endSec + by }));

    if (s.assets.voice && s.voice.words.length > 0) {
      return shift(s.voice.words, s.voice.startSec);
    }
    if (s.assets.voice) {
      const dur = voiceDurationSec ?? s.endCard.toSec - s.voice.startSec;
      return shift(estimateWords(s.voice.text, dur), s.voice.startSec);
    }
    // No voice: on-screen text spread over the captions window.
    const span = s.captions.toSec - s.captions.fromSec;
    return shift(estimateWords(s.captions.text ?? s.voice.text, span, 0.1, 0.25), s.captions.fromSec);
  }, [s, voiceDurationSec]);

  // The clip keeps playing a few frames under the end card while it slides in.
  const clipEnd = f(s.endCard.fromSec) + 12;
  const usableClipSec = (clipDurationSec ?? Infinity) - s.clip.startFromSec;
  const clipFrames = Number.isFinite(usableClipSec) ? Math.max(1, Math.floor(usableClipSec * fps)) : clipEnd;

  return (
    <AbsoluteFill style={{ backgroundColor: "black" }}>
      <Sequence durationInFrames={clipEnd} name="Clip">
        <ClipLayer
          src={s.assets.clip}
          startFromSec={s.clip.startFromSec}
          clipFrames={clipFrames}
          zoomFrom={s.clip.zoomFrom}
          zoomTo={s.clip.zoomTo}
          volume={s.clip.volume}
          unlockFrame={f(s.unlock.atSec)}
        />
      </Sequence>

      <Sequence from={f(s.hook.fromSec)} durationInFrames={f(s.hook.toSec - s.hook.fromSec)} name="Hook">
        <HookText text={s.hook.text} />
      </Sequence>

      <Captions
        words={words}
        fromSec={s.captions.fromSec}
        toSec={s.captions.toSec}
        placement={s.captions.placement}
        offsetPx={s.captions.offsetPx}
        maxWordsPerPage={s.captions.maxWordsPerPage}
      />

      <Sequence from={f(s.unlock.atSec)} durationInFrames={f(s.unlock.toSec - s.unlock.atSec)} name="Unlock">
        <UnlockFlash text={s.unlock.text} />
        {s.assets.click ? <Audio src={staticFile(s.assets.click)} volume={0.9} /> : null}
      </Sequence>

      <Sequence from={f(s.endCard.fromSec)} durationInFrames={f(s.endCard.toSec - s.endCard.fromSec)} name="End card">
        <EndCard image={s.assets.product} name={s.product.name} price={s.product.price} cta={s.product.cta} />
      </Sequence>

      {s.assets.voice ? (
        <Sequence from={f(s.voice.startSec)} name="Voice">
          <Audio src={staticFile(s.assets.voice)} volume={s.voice.volume} />
        </Sequence>
      ) : null}

      {showSafeZones ? <SafeZones /> : null}
    </AbsoluteFill>
  );
};
