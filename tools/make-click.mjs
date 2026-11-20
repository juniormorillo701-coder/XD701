// Generates public/click.wav: a short, crisp mechanical "unlock" click (no external assets needed).
import { writeFileSync } from "node:fs";

const rate = 44100;
const len = Math.round(rate * 0.18);
const samples = new Float32Array(len);
let seed = 7;
const noise = () => ((seed = (seed * 16807) % 2147483647) / 2147483647) * 2 - 1;

const transient = (at, gain, decay, tone) => {
  const start = Math.round(at * rate);
  for (let i = 0; start + i < len; i++) {
    const t = i / rate;
    const env = Math.exp(-t / decay);
    samples[start + i] += gain * env * (0.6 * noise() + 0.4 * Math.sin(2 * Math.PI * tone * t));
  }
};
transient(0.0, 0.9, 0.004, 3200); // latch
transient(0.055, 0.7, 0.006, 1800); // shackle release

const data = Buffer.alloc(len * 2);
for (let i = 0; i < len; i++) data.writeInt16LE(Math.round(Math.max(-1, Math.min(1, samples[i])) * 32767), i * 2);
const header = Buffer.alloc(44);
header.write("RIFF", 0); header.writeUInt32LE(36 + data.length, 4); header.write("WAVE", 8);
header.write("fmt ", 12); header.writeUInt32LE(16, 16); header.writeUInt16LE(1, 20); header.writeUInt16LE(1, 22);
header.writeUInt32LE(rate, 24); header.writeUInt32LE(rate * 2, 28); header.writeUInt16LE(2, 32); header.writeUInt16LE(16, 34);
header.write("data", 36); header.writeUInt32LE(data.length, 40);
writeFileSync(new URL("../public/click.wav", import.meta.url), Buffer.concat([header, data]));
console.log("Wrote public/click.wav");
