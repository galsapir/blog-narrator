# blog-narrator

Add AI-narrated audio to your Jekyll blog posts. Runs locally on Apple Silicon via [Kokoro-82M](https://huggingface.co/hexgrad/Kokoro-82M) — generates a 15-minute narration in under 60 seconds, sounds good, costs nothing.

## Quick start

**Prerequisites:** macOS with Apple Silicon (M1+), Python 3.10+, [ffmpeg](https://formulae.brew.sh/formula/ffmpeg) (`brew install ffmpeg`).

### 1. Install

```bash
pip install git+https://github.com/galsapir/blog-narrator.git
```

### 2. Configure

Copy the example config to your blog root and edit it:

```bash
cp narrate.yml.example narrate.yml
```

```yaml
author: "Your Name"
blog_name: "Your Blog"
voice: "af_heart"     # see voice guide below
speed: 1.0
audio_dir: "assets/audio"
min_words: 300
```

### 3. Add the player

Copy `jekyll/_includes/audio-player.html` to your blog's `_includes/` directory.

Add it to your post layout (`_layouts/post.html`), between the date and content:

```html
<span class="post-date">{{ page.date | date_to_string }}</span>
{% include audio-player.html %}
{{ content }}
```

The player only renders on posts that have an `audio:` field in their frontmatter.

### 4. Narrate a post

```bash
cd your-blog/
narrate _posts/2026-02-11-my-post.md
```

This will:
- Strip the markdown to clean narration text
- Generate speech via Kokoro-82M (downloads the model on first run, ~200 MB)
- Convert to 64kbps mono MP3 via ffmpeg
- Add ID3 tags (title, author, album — Spotify-ready)
- Update the post's frontmatter with the audio path
- Report duration and file size

### 5. Preview

```bash
bundle exec jekyll serve
```

The audio player appears on the narrated post. Commit and push to deploy.

## Usage

```bash
# Narrate a post
narrate _posts/my-post.md

# Preview the stripped text (no audio generation)
narrate --dry-run _posts/my-post.md

# Use a different voice
narrate --voice am_adam _posts/my-post.md

# Adjust speed
narrate --speed 1.1 _posts/my-post.md

# Skip frontmatter update (useful for re-generating audio)
narrate --skip-frontmatter-update _posts/my-post.md
```

## Voice guide

Kokoro-82M ships with 54 preset voices. These are the ones that work best for blog narration:

| Voice | Description | Best for |
|-------|-------------|----------|
| `af_heart` | American female, warm and natural | General narration (default) |
| `af_bella` | American female, clear and polished | Technical content |
| `am_adam` | American male, deep and clear | Long-form essays |
| `am_michael` | American male, conversational | Casual writing |
| `bf_emma` | British female, polished and articulate | Formal writing |
| `bm_daniel` | British male, warm baritone | Storytelling |

Use `--dry-run` to preview the text, then test a few voices on a short post to find one that fits your writing style.

## How the player works

The audio player is a single self-contained HTML file (~260 lines) with inline CSS and JavaScript. No external dependencies.

**Features:**
- Play/pause, seek bar, elapsed/total time, playback speed (1×–2×)
- Dark mode support via CSS custom properties
- Accessible: `aria-label` on all interactive elements, keyboard navigable
- Responsive: works on mobile
- Conditional: only renders when `audio:` exists in the post's frontmatter

**Customizing the look:** The player uses CSS custom properties for theming. If your Jekyll theme defines these, the player picks them up automatically:

```css
--border-color    /* left accent border */
--muted-color     /* label text, buttons (idle), time display */
--heading-color   /* buttons (hover/active), seek thumb */
```

If your theme doesn't define these, the player falls back to sensible defaults (light gray border, muted gray text, dark accents).

## How markdown stripping works

The narration script converts markdown to plain text following this pipeline:

1. Strip YAML frontmatter
2. Strip HTML comments (`<!--more-->`, etc.)
3. Strip fenced code blocks
4. Strip images and captions
5. Strip horizontal rules
6. Strip footnote definitions and inline references
7. Strip Jekyll/Liquid template tags
8. Convert headers to text with natural pacing
9. Convert links to text (keep link text, drop URL)
10. Strip bold/italic markers (keep text)
11. Strip inline code backticks (keep text)
12. Strip remaining HTML tags
13. Strip blockquote markers (keep text)

Use `--dry-run` to verify the output before generating audio.

## Audio storage

MP3s at 64kbps mono are roughly 0.5 MB per minute. A typical 2,000-word post (~10 minutes) produces a ~5 MB file. This is fine stored directly in your git repo for up to ~50 posts. Beyond that, consider [Cloudflare R2](https://developers.cloudflare.com/r2/) (10 GB free, zero egress fees).

## Requirements

- **macOS with Apple Silicon** (M1, M2, M3, M4) — mlx-audio uses the Metal GPU
- **Python 3.10+**
- **ffmpeg** — for WAV-to-MP3 conversion (`brew install ffmpeg`)
- **~200 MB disk** for the Kokoro-82M model (downloaded on first run)
- **~3 GB RAM** during generation (uses unified memory)

## License

MIT
