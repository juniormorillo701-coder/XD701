import { Config } from "@remotion/cli/config";

Config.setVideoImageFormat("jpeg");
Config.setJpegQuality(90);
Config.setCodec("h264");
Config.setCrf(18); // high quality for TikTok re-encode
Config.setPixelFormat("yuv420p");
Config.setOverwriteOutput(true);
