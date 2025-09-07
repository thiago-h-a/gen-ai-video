"""
Video utilities:
- reencode_to_spec: normalize arbitrary input to a web-friendly MP4 (H.264/AAC)
- placeholder_video: quick local animated placeholder when remote generation is unavailable
"""
from __future__ import annotations
import os
from typing import List
import numpy as np
import cv2
import ffmpeg  # ffmpeg-python
from moviepy.editor import VideoClip, AudioFileClip


def reencode_to_spec(in_path: str, out_path: str, width: int = 1280, height: int = 720, fps: int = 24) -> None:
    """
    Re-encode to a widely compatible MP4:
    - Video: H.264 (yuv420p), letterboxed 16:9 without stretching
    - Audio: AAC 128 kbps
    - 'faststart' for progressive streaming
    """
    (
        ffmpeg
        .input(in_path)
        .output(
            out_path,
            vcodec="libx264",
            acodec="aac",
            vf=f"scale=w={width}:h={height}:force_original_aspect_ratio=decrease,"
               f"pad={width}:{height}:(ow-iw)/2:(oh-ih)/2,format=yuv420p",
            r=fps,
            movflags="+faststart",
            preset="fast",
            crf=23,
            audio_bitrate="128k",
        )
        .overwrite_output()
        .run(quiet=True)
    )


def _uuid4_hex() -> str:
    import uuid
    return uuid.uuid4().hex


def _wrap_text(text: str, max_chars: int = 40) -> List[str]:
    """
    Minimal word-wrap to ~max_chars per line (naive, but sufficient for overlay).
    """
    words = text.split()
    lines, line = [], []
    for w in words:
        # include spaces between words in the count
        if sum(len(x) for x in line) + len(line) + len(w) > max_chars:
            lines.append(" ".join(line))
            line = [w]
        else:
            line.append(w)
    if line:
        lines.append(" ".join(line))
    return lines


def _animate_frame(t: float, W: int, H: int, seed: int, text_lines: List[str]):
    """
    Generate a frame of animated procedural noise with a subtle vignette and moving text.
    """
    rng = np.random.default_rng(seed + int(t * 10))
    noise = (rng.random((H, W, 1)) * 255).astype(np.uint8)
    frame = np.concatenate([noise, noise, noise], axis=2)

    # Vignette (radial falloff)
    Y, X = np.ogrid[:H, :W]
    cx, cy = W / 2, H / 2
    dist = np.sqrt((X - cx) ** 2 + (Y - cy) ** 2)
    vignette = 1 - (dist / dist.max()) * 0.5
    frame = (frame * vignette[..., None]).astype(np.uint8)

    # Overlay prompt lines with a little vertical motion
    y = int(H * 0.2)
    for i, line in enumerate(text_lines[:5]):
        dy = int(5 * np.sin(t + i))
        cv2.putText(
            frame, line, (int(W * 0.08), y + dy),
            cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 2, cv2.LINE_AA
        )
        y += int(H * 0.08)
    return frame


def placeholder_video(prompt: str, width: int = 1280, height: int = 720, fps: int = 24, duration: int = 8) -> str:
    """
    Produce a small placeholder MP4 locally so the UX remains intact even without remote providers.
    """
    lines = _wrap_text(prompt)
    seed = np.random.default_rng().integers(0, 2**31 - 1)

    def make_frame(t: float):
        return _animate_frame(t, width, height, int(seed), lines)

    clip = VideoClip(make_frame=make_frame, duration=duration)

    # Attach silent audio for better player compatibility (looped 1s WAV)
    silent_wav = os.path.join(os.getcwd(), "_silence.wav")
    if not os.path.exists(silent_wav):
        import wave, struct
        framerate = 44100
        with wave.open(silent_wav, "w") as wf:
            wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(framerate)
            for _ in range(framerate):  # 1 second of silence
                wf.writeframes(struct.pack("<h", 0))

    try:
        from moviepy.audio.fx.all import audio_loop
        audio = AudioFileClip(silent_wav)
        audio = audio_loop(audio, duration=duration)
        clip = clip.set_audio(audio)
    except Exception:
        # No audio is fine; some environments may lack codecs
        pass

    tmp_path = os.path.join(os.getcwd(), f"placeholder_{_uuid4_hex()}.mp4")
    clip.write_videofile(tmp_path, fps=fps, codec="libx264", audio_codec="aac", preset="fast", verbose=False, logger=None)
    return tmp_path
