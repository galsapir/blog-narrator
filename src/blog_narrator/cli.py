# ABOUTME: CLI entry point for blog-narrator.
# ABOUTME: Orchestrates markdown stripping, TTS generation, ID3 tagging, and frontmatter updates.

import argparse
import re
import sys
from pathlib import Path

import yaml

from .frontmatter import update_frontmatter
from .generate import generate_mp3
from .strip import parse_frontmatter, strip_markdown
from .tag import add_id3_tags

DEFAULT_CONFIG = {
    "author": "Unknown",
    "blog_name": "Blog",
    "voice": "af_heart",
    "speed": 1.0,
    "lang_code": "a",
    "audio_dir": "assets/audio",
    "posts_dir": "_posts",
    "min_words": 300,
}


def load_config() -> dict:
    """Load narrate.yml from current directory, falling back to defaults."""
    config = dict(DEFAULT_CONFIG)
    config_path = Path("narrate.yml")
    if config_path.exists():
        with open(config_path) as f:
            user_config = yaml.safe_load(f) or {}
        config.update(user_config)
    return config


def slug_from_filename(filename: str) -> str:
    """Extract slug: '2026-02-11-a-second-opinion.md' -> 'a-second-opinion'."""
    return re.sub(r"^\d{4}-\d{2}-\d{2}-", "", filename).removesuffix(".md")


def main() -> None:
    config = load_config()

    parser = argparse.ArgumentParser(
        prog="narrate",
        description="Generate audio narration for a blog post",
    )
    parser.add_argument("post", type=Path, help="Path to the markdown post file")
    parser.add_argument("--voice", default=None, help=f"Kokoro voice (default: {config['voice']})")
    parser.add_argument("--speed", type=float, default=None, help=f"Speech speed (default: {config['speed']})")
    parser.add_argument("--dry-run", action="store_true", help="Print stripped text without generating audio")
    parser.add_argument("--skip-frontmatter-update", action="store_true", help="Don't update post frontmatter")
    args = parser.parse_args()

    voice = args.voice or config["voice"]
    speed = args.speed or config["speed"]
    lang_code = config["lang_code"]
    audio_dir = Path(config["audio_dir"])
    min_words = config["min_words"]

    if not args.post.exists():
        print(f"File not found: {args.post}", file=sys.stderr)
        sys.exit(1)

    # 1. Read and parse
    text = args.post.read_text()
    frontmatter, body = parse_frontmatter(text)
    narration_text = strip_markdown(body)
    word_count = len(narration_text.split())

    if args.dry_run:
        print(narration_text)
        print(f"\n--- Stats ---")
        print(f"Characters: {len(narration_text)}")
        print(f"Words: {word_count}")
        return

    if word_count < min_words:
        print(
            f"Post has only {word_count} words (minimum {min_words}). Skipping.",
            file=sys.stderr,
        )
        sys.exit(1)

    # 2. Generate audio
    slug = slug_from_filename(args.post.name)
    audio_dir.mkdir(parents=True, exist_ok=True)
    mp3_path = audio_dir / f"{slug}.mp3"

    print(f"Generating audio with voice={voice}, speed={speed}...")
    generate_mp3(narration_text, mp3_path, voice, speed, lang_code)

    # 3. Tag
    title = frontmatter.get("title", slug)
    add_id3_tags(mp3_path, title=title, author=config["author"], blog_name=config["blog_name"])

    # 4. Update frontmatter
    audio_url = f"{config['audio_dir']}/{slug}.mp3"
    if not args.skip_frontmatter_update:
        update_frontmatter(args.post, audio_url)
        print(f'Frontmatter updated: audio: "{audio_url}"')

    # 5. Report
    from mutagen.mp3 import MP3

    audio = MP3(str(mp3_path))
    duration = audio.info.length
    size_mb = mp3_path.stat().st_size / (1024 * 1024)
    print(f"Generated: {mp3_path}")
    print(f"Duration:  {int(duration // 60)}:{int(duration % 60):02d}")
    print(f"Size:      {size_mb:.1f} MB")


if __name__ == "__main__":
    main()
