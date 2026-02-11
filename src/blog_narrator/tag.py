# ABOUTME: ID3 tag management for generated MP3 narration files.
# ABOUTME: Adds Spotify-ready metadata (title, artist, album, genre).

from pathlib import Path


def add_id3_tags(mp3_path: Path, title: str, author: str, blog_name: str) -> None:
    """Add ID3 tags to the MP3 file."""
    from mutagen.id3 import ID3, TALB, TCON, TIT2, TPE1
    from mutagen.mp3 import MP3

    audio = MP3(str(mp3_path))
    audio.tags = ID3()
    audio.tags.add(TIT2(encoding=3, text=[title]))
    audio.tags.add(TPE1(encoding=3, text=[author]))
    audio.tags.add(TALB(encoding=3, text=[blog_name]))
    audio.tags.add(TCON(encoding=3, text=["Podcast"]))
    audio.save()
