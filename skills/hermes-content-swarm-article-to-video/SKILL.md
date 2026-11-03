---
name: article-to-video
description: "Turn a written article (text file) into a narrated HD short-form video with stock footage, subtitles, and background music using MoneyPrinterTurbo. Strips the FOR PI ONLY / keyword research footer automatically. Run this whenever the user hands you an article file and says 'turn it into a video' or similar."
version: 1.1.0
author: Vinny Barreca
license: MIT
metadata:
  hermes:
    tags: [video, article, money-printer-turbo, content-creation, automation]
    related_skills: []
---

# Article to Video

Convert a written article into a narrated short-form video using MoneyPrinterTurbo. The pipeline reads the article text, strips out the keyword research / FOR PI ONLY footer, generates TTS voiceover, fetches relevant stock footage from Pexels, adds subtitles and background music, and outputs a 1080x1920 MP4. Long articles (>800 words) break the standard MoneyPrinterTurbo pipeline on typical consumer hosts; use the Offline Guaranteed Fallback for those cases.

## When to Use

- The user says "turn this article into a video"
- The user hands you a text file and says "make a video out of this"
- The user references article number N and wants a video version

## Prerequisites

MoneyPrinterTurbo must be installed and configured at `~/MoneyPrinterTurbo/` with:
- Python 3.11 virtual environment (managed via `uv`)
- A valid Pexels API key in `config.toml`
- A working LLM provider key (OpenAI or compatible) in `config.toml`
- Local TTS (Edge TTS is free and built-in)

## Pipeline

```
RECEIVE article text --> CLEAN (strip FOR PI ONLY footer) --> CHECK LENGTH/CONFIG --> RUN MoneyPrinterTurbo CLI OR OFFLINE FALLBACK --> DELIVER video path
```

## Workflow

### Step 1: Receive the Article

The user provides the article as a file path or pasted text. If it's an attached file, read it with `read_file`.

### Step 2: Strip the Footer

The article may have a `-----------FOR PI ONLY--------DO NOT INCLUDE INSIDE OF ARTICLE-------------------------------------------------------` section and everything below it. Strip this before feeding the text. This includes everything from the line starting with `-----------FOR PI ONLY` to the end of the file.

### Step 3: Write Cleaned Text to Temp File

Write the cleaned article text to a temp file in `/tmp/` or under `~/MoneyPrinterTurbo/storage/tasks/`. Use `~/MoneyPrinterTurbo/storage/tasks/article_<number>_cleaned.txt` for long articles that will use the offline fallback.

### Step 4: Check Length and Config

Estimate article length. If it exceeds roughly 800 words, do not use MoneyPrinterTurbo; switch to the offline fallback immediately.

Before invoking MoneyPrinterTurbo, verify `~/MoneyPrinterTurbo/config.toml` has:
- non-empty `openai_api_key` (or another working LLM provider configured)
- populated `pexels_api_keys`

If either is missing, stop and report the blocker. Do not silently fall forward.

### Step 5: Ask Target Platform

Ask the user which aspect ratio they want. Offer all three as choices via `clarify`:

1. **1080x1920 Portrait (9:16)** — YouTube Shorts, TikTok, Reels, Pinterest video pins
2. **1920x1080 Landscape (16:9)** — YouTube main channel, widescreen
3. **1080x1080 Square (1:1)** — Pinterest feed, Instagram feed

Default to portrait (9:16) if they say "whatever" or don't care.

### Step 6: Run MoneyPrinterTurbo CLI

```bash
cd ~/MoneyPrinterTurbo && uv run python cli.py \
  --video-subject "ARTICLE TITLE" \
  --video-script "$(cat /path/to/cleaned_article.txt)" \
  --video-source pexels \
  --voice-name "en-US-JennyNeural" \
  --bgm-type random \
  --subtitle-enabled
```

Add `--video-aspect "16:9"` for landscape, or `--video-aspect "1:1"` for square.

Key flags explained:
- `--video-subject` — The article title, used as fallback script title (required by CLI)
- `--video-script` — The full cleaned article text piped in via `$(cat ...)`
- `--video-source pexels` — Fetches stock footage from Pexels (free tier)
- `--voice-name` — TTS voice. Default: `en-US-JennyNeural`
- `--bgm-type random` — Adds royalty-free background music
- `--subtitle-enabled` — Generates timed subtitles overlaid on the video

### Step 7: Deliver the Result

The CLI outputs the final video path, e.g.:
`~\MoneyPrinterTurbo\storage\tasks\<task-uuid>\final-1.mp4`

Report this path and the task ID to the user. If they want the video delivered elsewhere (Telegram, etc.), use `send_message` with the `MEDIA:<path>` format to attach the file.

## Aspect Ratios

| Flag | Aspect | Resolution | Use Case |
|------|--------|------------|----------|
| `--video-aspect "9:16"` | Portrait | 1080x1920 | TikTok, Reels, Shorts, Pinterest video pins (default) |
| `--video-aspect "1:1"` | Square | 1080x1080 | Pinterest, Instagram feed |
| `--video-aspect "16:9"` | Landscape | 1920x1080 | YouTube, widescreen |

## Offline Guaranteed Fallback

If the article is longer than ~800 words, MoneyPrinterTurbo fails, or the config is unset, use this path. It produces a working 1280x720 landscape video without Pexels or non-local APIs:

```bash
TEXT="...article text..."
VOICE="en-US-JennyNeural"
FF="C:\\tmp\\article102_stock"
mkdir -p "$FF"
edge-tts --voice "$VOICE" --text "$TEXT" --write-media "$FF/narration.mp3"
DUR=$(ffprobe -v quiet -show_entries format=duration -of csv=p=0 "$FF/narration.mp3")
ffmpeg -y -f lavfi -i color=c=0x080c1e:s=1280x720:d=$DUR \
  -vf "drawtext=fontfile=C\:/Windows/Fonts/arial.ttf:text='IndexShare':fontsize=44:fontcolor=white:x=(w-text_w)/2:y=(h-text_h)/2:enable='between(t,0,5)'" \
  -an -c:v libx264 -pix_fmt yuv420p -crf 18 "$FF/visuals_looped.mp4"
ffmpeg -y -i "$FF/visuals_looped.mp4" -i "$FF/narration.mp3" \
  -c:v copy -c:a aac -b:a 192k -shortest "$FF/final_landscape.mp4"
```

## Common Commands (One-Shot)

### Default run (Pexels stock footage + voiceover + music + subs)

```bash
cd ~/MoneyPrinterTurbo && uv run python cli.py \
  --video-subject "Article Title Here" \
  --video-script "$(cat /tmp/cleaned_article.txt)" \
  --video-source pexels \
  --voice-name "en-US-JennyNeural" \
  --bgm-type random \
  --subtitle-enabled
```

### No background music (speech only)

```bash
cd ~/MoneyPrinterTurbo && uv run python cli.py \
  --video-subject "Article Title Here" \
  --video-script "$(cat /tmp/cleaned_article.txt)" \
  --video-source pexels \
  --voice-name "en-US-JennyNeural" \
  --bgm-type none \
  --subtitle-enabled
```

### Local footage instead of Pexels

Place `.mp4` files in `~/MoneyPrinterTurbo/storage/local_videos/` first, then:

```bash
cd ~/MoneyPrinterTurbo && uv run python cli.py \
  --video-subject "Article Title Here" \
  --video-script "$(cat /tmp/cleaned_article.txt)" \
  --video-source local \
  --video-materials "clip1.mp4,clip2.mp4" \
  --no-match-materials-to-script \
  --voice-name "en-US-JennyNeural" \
  --bgm-type random \
  --subtitle-enabled
```

### Landscape (16:9) instead of default portrait (9:16)

```bash
cd ~/MoneyPrinterTurbo && uv run python cli.py \
  --video-subject "Article Title Here" \
  --video-script "$(cat /tmp/cleaned_article.txt)" \
  --video-source pexels \
  --video-aspect "16:9" \
  --voice-name "en-US-JennyNeural" \
  --bgm-type random \
  --subtitle-enabled
```

## Available TTS Voices

| Voice Name | Description |
|------------|-------------|
| `en-US-JennyNeural` | Female, American English (default) |
| `en-US-GuyNeural` | Male, American English |
| `en-GB-SoniaNeural` | Female, British English |
| `en-GB-RyanNeural` | Male, British English |
| `en-AU-NatashaNeural` | Female, Australian English |
| `en-CA-ClaraNeural` | Female, Canadian English |

Find the full list in the MoneyPrinterTurbo voice reference or test with any Edge TTS voice name.

## Common Pitfalls

1. **Forgetting to strip the FOR PI ONLY footer.** The keyword research sections at the bottom contain SEO metadata and internal notes. They will be read aloud as part of the voiceover if not removed, making the video look unprofessional. Always strip everything from `-----------FOR PI ONLY` to the end of the file.

2. **Article text with em dashes.** MoneyPrinterTurbo's TTS handles standard punctuation fine, but if the article uses em dashes or unconventional formatting, the voiceover may sound stilted. The user's articles already use proper punctuation per their style rules, so this is usually fine.

3. **Long articles break MoneyPrinterTurbo.** Use the offline fallback for anything over ~800 words.

4. **Partial outputs.** If MoneyPrinterTurbo crashes or returns a 1-second video, fix it or use the offline fallback. Do not report a stub result and stop. Always deliver a full-length video or state the exact blocker.

5. **Duration mismatch.** A file can exist but be very short. Always run ffprobe and confirm duration before reporting success.

6. **Config not set.** Ensure `~/MoneyPrinterTurbo/config.toml` has `pexels_api_keys` populated before running. The CLI will error with a clear message if the key is missing.

7. **Local footage licensing.** Only use footage from `~/MoneyPrinterTurbo/storage/local_videos/` when its license is verified as free to use and commercially redistributable for the target brand channel.

## Verification Checklist

- [ ] Article text cleaned — no FOR PI ONLY / keyword research sections remain
- [ ] Checked article length; if >800 words, used Offline Guaranteed Fallback path instead of MoneyPrinterTurbo
- [ ] If using MoneyPrinterTurbo, confirmed `config.toml` has API keys populated first
- [ ] `uv run python cli.py` executed with correct flags (or offline fallback executed)
- [ ] **Video duration matches narration duration** (compare ffprobe output; do not assume correctness)
- [ ] **Aspect ratio confirmed** (1280x720 for landscape, 1080x1920 for portrait, 1080x1080 for square)
- [ ] Video file exists and is non-trivial in size (>1 MB for reasonable videos)
- [ ] Video path reported to user (and delivered if requested)