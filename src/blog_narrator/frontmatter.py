# ABOUTME: Reads and updates YAML frontmatter in blog post files.
# ABOUTME: Uses string manipulation to preserve exact formatting (no YAML round-trip).

import re
from pathlib import Path


def update_frontmatter(post_path: Path, audio_url: str) -> None:
    """Add or update 'audio:' field in post frontmatter."""
    content = post_path.read_text()
    match = re.match(r"^---\n(.*?\n)---\n", content, re.DOTALL)
    if not match:
        raise ValueError(f"No frontmatter found in {post_path}")

    fm_text = match.group(1)
    audio_line = f'audio: "{audio_url}"\n'

    if re.search(r"^audio:", fm_text, re.MULTILINE):
        new_fm = re.sub(r"^audio:.*\n", audio_line, fm_text, flags=re.MULTILINE)
    else:
        new_fm = fm_text + audio_line

    new_content = f"---\n{new_fm}---\n" + content[match.end() :]
    post_path.write_text(new_content)
