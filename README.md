# ComfyUI-Automated-Batch-Video-Upscaler-Real-ESRGAN-DVB
A ComfyUI workflow that extends standard Real-ESRGAN video upscaling with folder-based batch processing, dynamic filenames, audio/FPS preservation, and automated output organization.


# Batch Video Upscaler — Real-ESRGAN (ComfyUI)

## Purpose
Process multiple MP4 files from a directory, one file per queued execution, upscale their frames with RealESRGAN_x4plus, retain source audio and frame rate, and save to a dedicated output folder. The optional final custom node attempts to rename numbered SaveVideo outputs back to the original basename.

## Required nodes
- **ComfyUI core:** UpscaleModelLoader, ImageUpscaleWithModel, CreateVideo, SaveVideo.
- **VideoHelperSuite (VHS):** VHS_LoadVideoPath, VHS_VideoInfo.
- **Dream Video Batches (DVB):** For Each Filename [DVB], For Each Done [DVB].
- **StringConcatenate**, **PreviewAny**, and **MarkdownNote** from their respective installed packs.
- **Optional custom node:** ExactFilenameAfterSave (requires `custom_nodes/exact_filename_output/__init__.py`; NOT included in this JSON).

## Data flow
1. DVB selects one matching MP4 per queued execution; `filepath` feeds VHS_LoadVideoPath.
2. VHS_LoadVideoPath decodes frames, source audio, and video information.
3. UpscaleModelLoader loads `RealESRGAN_x4plus.safetensors`; ImageUpscaleWithModel upscales decoded frames.
4. VHS_VideoInfo.source_fps feeds CreateVideo.fps. Original audio feeds CreateVideo.audio.
5. CreateVideo packages upscaled frames, FPS, and audio as a VIDEO; SaveVideo encodes and saves it.
6. DVB `name` feeds StringConcatenate.`string_b`; `string_a` is `video/Andhbhakt/Up/` and delimiter is empty. The result feeds SaveVideo.filename_prefix and ExactFilenameAfterSave.filename_prefix.
7. SaveVideo.video feeds ExactFilenameAfterSave.video. The custom node attempts exact-filename renaming after save.
8. Upscaled frames also feed For Each Done.image, and DVB.foreach feeds For Each Done.foreach.

## Running a batch
- Edit DVB `directory` to your own absolute input directory; the supplied path is machine-specific.
- Set DVB `pattern` to `*.mp4` (or change it to match your media).
- **Batch Count next to Run = number of files you want to process**. DVB does not automatically queue all files in a single execution.
- Queue sequentially, not concurrently, especially when using exact-filename renaming.
- The DVB loop may track progress between runs; verify/reset its tracking state as needed before rerunning a batch.

## Output naming
- ComfyUI SaveVideo normally appends a counter, e.g. `2_00001_.mp4`.
- ExactFilenameAfterSave is a **custom, separately installed** node intended to rename it to `2.mp4` without re-encoding. It refuses to overwrite existing output files.
- **Caution:** This custom node has not been validated against every ComfyUI version; its filename matching can be fragile if matching files already exist. Inspect outputs before using on valuable footage.
- The relative prefix `video/Andhbhakt/Up/` resolves under the ComfyUI output directory. Change it for your own environment.

## Limits and troubleshooting
- RealESRGAN_x4plus is a nominal 4× spatial upscaler. Output dimensions and quality should be verified.
- VHS_LoadVideoPath currently loads all frames (`frame_load_cap=0`), which can exhaust RAM/VRAM for long videos. Use shorter clips or a chunked workflow for production.
- FPS is taken from `source_fps`; if you deliberately change loading cadence, reassess FPS choice.
- For Each Done depends on upscaled frames, not SaveVideo completion; the graph alone does not guarantee save completion before loop state advances.
- Check audio, duration, FPS, dimensions, and final filename on two test videos before large batches.
- This workflow is for sequential queued processing, not robust job orchestration, failure recovery, or concurrency.

## GitHub sharing
- Export this JSON and include a README listing exact custom-node dependencies and model download instructions.
- Do not publish your personal Windows directory paths, or replace them with placeholders before publishing.
- Do not distribute third-party model weights or custom-node code without checking licenses.
- This workflow JSON does **not** bundle the ExactFilenameAfterSave Python implementation.
