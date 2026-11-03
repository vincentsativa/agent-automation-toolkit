---
name: article-to-video
description: "Turn a written article (text file) into a narrated HD short-form video with stock footage, subtitles, and background music using MoneyPrinterTurbo. Strips the FOR PI ONLY / keyword research footer (explicitly, before running the CLI — it is NOT automatic). Run this whenever the user hands you an article file and says 'turn it into a video' or similar."
version: 1.0.0
author: Vinny Barreca
license: MIT
metadata:
  hermes:
    tags: [video, article, money-printer-turbo, content-creation, automation]
    related_skills: []
---

# Article to Video

Convert a written article into a narrated short-form video using MoneyPrinterTurbo. The pipeline reads the article text, strips out the keyword research / FOR PI ONLY footer, generates TTS voiceover, fetches relevant stock footage from Pexels, adds subtitles and background music, and outputs a 1080x1920 MP4.

## When to Use

- The user says "turn this article into a video"
- The user hands you a text file and says "make a video out of this"
- The user references article number N and wants a video version

## Prerequisites

MoneyPrinterTurbo must be installed and configured at `~/MoneyPrinterTurbo/` with:
- Python 3.11 virtual environment (managed via `uv`)
- A valid Pexels API key in `config.toml`
- Config set to use Pexels as the video source
- Local TTS (Edge TTS is free and built-in)

## Pipeline

```
RECEIVE article text --> CLEAN (strip FOR PI ONLY footer) --> RUN MoneyPrinterTurbo CLI --> DELIVER video path
```

## Workflow

### Step 1: Receive the Article

The user provides the article as a file path or pasted text. If it's an attached file, read it with `read_file`.

### Step 2: Strip the Footer

The article has a `-----------FOR PI ONLY--------DO NOT INCLUDE INSIDE OF ARTICLE-------------------------------------------------------` section and everything below it. Strip this before feeding the text to MoneyPrinterTurbo. This includes everything from the line starting with `-----------FOR PI ONLY` to the end of the file.

**This is NOT automatic.** The CLI reads whatever text you pass verbatim and will read the footer aloud as part of the voiceover. You must strip it yourself. Use this command:

```bash
awk '/FOR PI ONLY/{exit} {print}' /path/to/article.txt > /tmp/cleaned_article.txt
```

This prints every line up to (but not including) the first line containing `FOR PI ONLY`, and writes the result to `/tmp/cleaned_article.txt`. If the article has no footer, the whole file is copied unchanged.

### Step 3: Write Cleaned Text to Temp File

Write the cleaned article text to a temp file in `/tmp/` or under `~/MoneyPrinterTurbo/storage/tasks/`. The `awk` command in Step 2 already writes to `/tmp/cleaned_article.txt`. Verify the footer is gone before proceeding:

```bash
grep -c "FOR PI ONLY" /tmp/cleaned_article.txt   # must return 0
```

### Step 4: Ask Target Platform

Before running, ask the user which aspect ratio they want. Offer all three as choices via `clarify`:

1. **1080x1920 Portrait (9:16)** — YouTube Shorts, TikTok, Reels, Pinterest video pins
2. **1920x1080 Landscape (16:9)** — YouTube main channel, widescreen
3. **1080x1080 Square (1:1)** — Pinterest feed, Instagram feed

Default to portrait (9:16) if they say "whatever" or don't care.

### Step 5: Run MoneyPrinterTurbo CLI

```bash
cd ~/MoneyPrinterTurbo && uv run python cli.py \
  --video-subject "ARTICLE TITLE" \
  --video-script "$(cat /path/to/cleaned_article.txt)" \
  --video-source pexels \
  --voice-name "en-US-JennyNeural" \
  --bgm-type random \
  --subtitle-enabled
```

Key flags explained:
- `--video-subject` — The article title, used as fallback script title (required by CLI)
- `--video-script` — The full cleaned article text piped in via `$(cat ...)`
- `--video-source pexels` — Fetches stock footage from Pexels (free tier)
- `--voice-name` — TTS voice. `en-US-JennyNeural` is a good default. Others: `en-US-GuyNeural`, `en-GB-SoniaNeural`
- `--bgm-type random` — Adds royalty-free background music
- `--subtitle-enabled` — Generates timed subtitles overlaid on the video

### Step 6: Deliver the Result

The CLI outputs the final video path, e.g.:
```
~/MoneyPrinterTurbo/storage/tasks/<task-uuid>/final-1.mp4
```

**However, the CLI does not always produce a valid `final-*.mp4`.** It often hangs during the ffmpeg mux phase. After the process completes (or is killed by timeout), verify the output file exists and is valid:

```bash
ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 /path/to/final.mp4
```

If the file is missing, corrupt (`moov atom not found`), or the CLI timed out mid-render, **manually reconstruct the final video** from the artifacts left in the task directory:

```bash
cd ~/MoneyPrinterTurbo/storage/tasks/<task-uuid>

# 1. Concatenate all temp clips into a single raw video
ffmpeg -y -f concat -safe 0 -i ffmpeg-concat-list.txt -c copy combined-raw.mp4

# 2. Burn subtitles and mux with audio
ffmpeg -y -i combined-raw.mp4 -i audio.mp3 \
  -vf "subtitles=subtitle.srt:force_style='FontName=Arial,FontSize=24,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,Outline=2,BorderStyle=3,Alignment=2,MarginV=40'" \
  -c:v libx264 -preset fast -crf 23 \
  -c:a aac -b:a 192k \
  -shortest final.mp4
```

If the video is going to be emailed, compress it first to avoid SMTP timeouts:

```bash
ffmpeg -y -i final.mp4 -c:v libx264 -crf 28 -preset fast -c:a copy final_compressed.mp4
```

Report the final video path to the user. If they want the video delivered elsewhere (Telegram, etc.), use `send_message` with the `MEDIA:<path>` format to attach the file.

## Aspect Ratios

| Flag | Aspect | Resolution | Use Case |
|------|--------|------------|----------|
| `--video-aspect "9:16"` | Portrait | 1080x1920 | TikTok, Reels, Shorts, Pinterest video pins (default) |
| `--video-aspect "1:1"` | Square | 1080x1080 | Pinterest, Instagram feed |
| `--video-aspect "16:9"` | Landscape | 1920x1080 | YouTube, widescreen |

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

Create the local videos directory if it doesn't exist, place `.mp4` files there, then:

```bash
mkdir -p ~/MoneyPrinterTurbo/storage/local_videos
cp /path/to/your/clip.mp4 ~/MoneyPrinterTurbo/storage/local_videos/
```

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

3. **Very long articles.** The TTS will read the full text. For a dense 2000+ word article, expect a 10-15 minute video. If the user wants something shorter, ask.

4. **Pexels rate limits.** The free Pexels API allows 200 requests per hour. This is sufficient for article-length videos. If you hit limits, switch to `--video-source pixabay` (also free, just register for a key).

5. **Config not set.** Ensure `~/MoneyPrinterTurbo/config.toml` has `pexels_api_keys` populated before running. The CLI will error with a clear message if the key is missing.

6. **`storage/local_videos/` doesn't exist on fresh install.** The directory is not created by the repo. Before copying local footage, run `mkdir -p ~/MoneyPrinterTurbo/storage/local_videos/` or the `cp` will fail. The same applies to `storage/tasks/` — MoneyPrinterTurbo creates it at runtime, but it's safe to ensure it exists.

7. **CLI timeout on long renders.** MoneyPrinterTurbo's video pipeline can take 5-10 minutes. The default foreground timeout of 300s may not be enough. Use `background=true` with `notify_on_complete=true`, then poll and wait. Do NOT set a short timeout and kill the process mid-render.

8. **ffmpeg concat step hangs.** The CLI sometimes hangs during the final `ffmpeg` concat/mux phase, leaving a broken `combined-1.mp4` (moov atom not found). If this happens, manually concatenate the temp clips and mux the audio/subtitles using the ffmpeg commands below.

9. **Large video files choke SMTP.** A 2-minute 1080x1920 video can be 40-50MB. Most SMTP servers will timeout uploading this. Compress the video with `ffmpeg -crf 28 -preset fast` before attaching to email. Target under 30MB.

10. **No `final-*.mp4` produced.** The CLI does not always emit a properly muxed final file. After the concat step, you may need to manually burn subtitles and mux audio with ffmpeg.

11. **LLM provider key missing.** `config.toml` defaults to `llm_provider = "openai"` with an empty `openai_api_key`. When you pass `--video-script` directly this is harmless (the script is used as-is), but the CLI still attempts term generation and logs `Error: openai: api_key is not set`. This is cosmetic for script-fed videos. If you ever want MoneyPrinterTurbo to generate a script from a subject (no `--video-script`), you must set a valid LLM key or switch `llm_provider` to a configured provider (e.g. `ollama`).

## Verification Checklist

- [ ] Article text cleaned — no FOR PI ONLY / keyword research sections remain
- [ ] Cleaned text written to temp file
- [ ] `uv run python cli.py` executed with correct flags
- [ ] Video file exists at the reported path
- [ ] Video path reported to user (and delivered if requested)