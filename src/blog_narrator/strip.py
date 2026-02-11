# ABOUTME: Converts markdown blog post content to plain text for TTS narration.
# ABOUTME: Handles frontmatter, footnotes, images, code blocks, and all standard markdown syntax.

import re


def parse_frontmatter(text: str) -> tuple[dict, str]:
    """Split post into frontmatter dict and body text."""
    match = re.match(r"^---\n(.*?\n)---\n", text, re.DOTALL)
    if not match:
        raise ValueError("No YAML frontmatter found")
    import yaml

    fm = yaml.safe_load(match.group(1)) or {}
    body = text[match.end() :]
    return fm, body


def strip_markdown(body: str) -> str:
    """Convert markdown body to plain narration text.

    Processing order matters to avoid partial matches on nested syntax.
    """
    text = body

    # 1. HTML comments (<!--more--> etc.)
    text = re.sub(r"<!--.*?-->", "", text, flags=re.DOTALL)

    # 2. Fenced code blocks (``` delimited, possibly with language tag)
    text = re.sub(r"```[^\n]*\n.*?```", "", text, flags=re.DOTALL)

    # 3. Images: ![alt](path)
    text = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", text)

    # 4. Image captions: standalone italic line (*text* on its own line)
    text = re.sub(r"^\*([^*]+)\*\s*$", "", text, flags=re.MULTILINE)

    # 5. Horizontal rules (--- alone on a line) → paragraph break
    text = re.sub(r"^\s*---\s*$", "\n", text, flags=re.MULTILINE)

    # 6. Footnote definitions at end of file
    text = re.sub(
        r"^\[\^\d+\]:.*?(?=\n\[\^\d+\]:|\n\n|\Z)",
        "",
        text,
        flags=re.MULTILINE | re.DOTALL,
    )

    # 7. Footnote inline references
    text = re.sub(r"\[\^\d+\]", "", text)

    # 8. Jekyll/Liquid template tags
    text = re.sub(r"\{\{.*?\}\}", "", text)
    text = re.sub(r"\{%.*?%\}", "", text)

    # 9. Headers → text with pacing
    text = re.sub(r"^#{1,6}\s+(.+)$", r"\n\n\1\n", text, flags=re.MULTILINE)

    # 10. Links: [text](url) → text
    text = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", text)

    # 11. Bold markers
    text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)

    # 12. Italic markers (not mid-word)
    text = re.sub(r"(?<!\w)\*([^*]+?)\*(?!\w)", r"\1", text)

    # 13. Inline code backticks
    text = re.sub(r"`([^`]+)`", r"\1", text)

    # 14. Remaining HTML tags
    text = re.sub(r"<[^>]+>", "", text)

    # 15. Blockquote markers
    text = re.sub(r"^>\s?", "", text, flags=re.MULTILINE)

    # 16. Collapse excessive newlines
    text = re.sub(r"\n{3,}", "\n\n", text)

    # 17. Clean up
    text = text.strip()

    return text
