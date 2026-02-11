# ABOUTME: TTS audio generation via Kokoro-82M through mlx-audio.
# ABOUTME: Handles WAV generation and MP3 conversion via ffmpeg.

import subprocess
import sys
import tempfile
from pathlib import Path


def generate_wav(text: str, output_prefix: str, voice: str, speed: float, lang_code: str) -> None:
    """Run Kokoro-82M via mlx-audio to generate WAV."""
    from mlx_audio.tts.generate import generate_audio

    generate_audio(
        text=text,
        model="mlx-community/Kokoro-82M-bf16",
        voice=voice,
        speed=speed,
        lang_code=lang_code,
        file_prefix=output_prefix,
        audio_format="wav",
        join_audio=True,
        verbose=True,
    )


def convert_to_mp3(wav_path: Path, mp3_path: Path) -> None:
    """Convert WAV to MP3 64kbps mono via ffmpeg."""
    result = subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(wav_path),
            "-codec:a",
            "libmp3lame",
            "-b:a",
            "64k",
            "-ac",
            "1",
            "-ar",
            "24000",
            str(mp3_path),
        ],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print(f"ffmpeg stderr:\n{result.stderr}", file=sys.stderr)
        result.check_returncode()


def generate_mp3(text: str, mp3_path: Path, voice: str, speed: float, lang_code: str) -> None:
    """Generate narration audio as MP3. Wraps WAV generation + conversion."""
    with tempfile.TemporaryDirectory() as tmpdir:
        wav_prefix = str(Path(tmpdir) / "narration")
        generate_wav(text, wav_prefix, voice, speed, lang_code)

        wav_path = Path(f"{wav_prefix}.wav")
        if not wav_path.exists():
            raise FileNotFoundError(f"Expected WAV not found at {wav_path}")

        convert_to_mp3(wav_path, mp3_path)
