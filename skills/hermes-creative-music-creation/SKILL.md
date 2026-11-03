---
name: music-creation
description: "AI music generation (HeartMuLa, Suno), songwriting craft, audio visualization — generate songs, write lyrics, craft Suno prompts, and visualize audio features via spectrograms."
category: creative
version: 1.0.0
author: Hermes Agent (consolidated)
license: MIT
---

# Music Creation — Generate, Write, Visualize

Consolidated guide to AI music generation, songwriting, and audio analysis tools. Covers three workflows:

1. **HeartMuLa** — open-source music generation from lyrics + tags (local GPU)
2. **songwriting + Suno prompts** — lyric craft, structure, Suno AI prompt engineering
3. **songsee** — audio spectrogram/feature visualization

---

## 1. HeartMuLa — Open-Source Music Generation

HeartMuLa is a family of open-source music foundation models (Apache-2.0) comparable to Suno, running locally with a GPU.

### Hardware Requirements
- **Minimum**: 8GB VRAM with `--lazy_load true`
- **Recommended**: 16GB+ VRAM
- **Multi-GPU**: `--mula_device cuda:0 --codec_device cuda:1`

### Installation

```bash
cd ~/
git clone https://github.com/HeartMuLa/heartlib.git
cd heartlib
uv venv --python 3.10 .venv
. .venv/bin/activate
uv pip install -e .

# Fix dependency conflicts
uv pip install --upgrade datasets transformers

# Download models
hf download --local-dir './ckpt' 'HeartMuLa/HeartMuLaGen'
hf download --local-dir './ckpt/HeartMuLa-oss-3B' 'HeartMuLa/HeartMuLa-oss-3B-happy-new-year'
hf download --local-dir './ckpt/HeartCodec-oss' 'HeartMuLa/HeartCodec-oss-20260123'
```

### Source Code Patches Required

**RoPE cache fix** in `src/heartlib/heartmula/modeling_heartmula.py` — add after `reset_caches` try/except, before `with device:`:
```python
from torchtune.models.llama3_1._position_embeddings import Llama3ScaledRoPE
for module in self.modules():
    if isinstance(module, Llama3ScaledRoPE) and not module.is_cache_built:
        module.rope_init()
        module.to(device)
```

**HeartCodec loading fix** — add `ignore_mismatched_sizes=True` to all `HeartCodec.from_pretrained()` calls.

### Generation

```bash
cd heartlib && . .venv/bin/activate
python ./examples/run_music_generation.py \
  --model_path=./ckpt --version="3B" \
  --lyrics="./assets/lyrics.txt" --tags="./assets/tags.txt" \
  --save_path="./assets/output.mp3" --lazy_load true
```

**Tags format** (comma-separated, no spaces): `piano,happy,wedding,synthesizer,romantic`
**Lyrics format**: Use bracketed structural tags: `[Verse]`, `[Chorus]`, `[Bridge]`, `[Outro]`

### Key Parameters
| Parameter | Default | Note |
|-----------|---------|------|
| `--max_audio_length_ms` | 240000 | Max 4 min |
| `--topk` | 50 | Top-k sampling |
| `--temperature` | 1.0 | Sampling temp |
| `--cfg_scale` | 1.5 | Classifier-free guidance |
| `--lazy_load` | false | Saves VRAM |
| `--mula_dtype` | bfloat16 | bf16 recommended |
| `--codec_dtype` | float32 | **Do NOT use bf16** — quality loss |

### Pitfalls
- Do NOT use bf16 for HeartCodec — degrades audio quality
- Tags may be ignored — lyrics tend to dominate
- RTX 5080 incompatibility reported
- CPU mode is extremely slow (30-60 min per song vs ~4 min on GPU)
- Links: [Repo](https://github.com/HeartMuLa/heartlib) · [Models](https://huggingface.co/HeartMuLa) · [Paper](https://arxiv.org/abs/2601.10547)

---

## 2. Songwriting & Suno AI Prompts

See `references/songwriting-guide.md` for the full reference including:
- Song structures (ABABCB, AABA, strophic, etc.)
- Rhyme, meter, and sound craft
- Emotional arc and dynamics mapping
- Lyric writing ("show don't tell", hooks, prosody)
- Parody/adaptation technique
- **Suno AI prompt engineering** — style/genre formula, metatags, Custom Mode
- Phonetic tricks for AI vocalists

### Suno Style Prompt Formula

```
Genre + Mood + Era + Instruments + Vocal Style + Production + Dynamics
```

**Bad**: `"sad rock song"`
**Good**: `"Cinematic orchestral spy thriller, 1960s Cold War era, smoky sultry female vocalist, big band jazz, brass section with trumpets and french horns, sweeping strings, minor key, vintage analog warmth"`

### Suno Metatags

Place `[bracketed]` tags in lyrics field:
- **Structure**: `[Intro]`, `[Verse]`, `[Pre-Chorus]`, `[Chorus]`, `[Bridge]`, `[Outro]`
- **Vocal**: `[Whispered]`, `[Belted]`, `[Falsetto]`, `[Breathy]`, `[Harmonies]`
- **Dynamics**: `[High Energy]`, `[Building Energy]`, `[Emotional Climax]`, `[Slow Down]`
- **Atmosphere**: `[Melancholic]`, `[Euphoric]`, `[Dark Atmosphere]`

Always use Custom Mode (separate Style + Lyrics). Lyrics limit ~3,000 chars.

---

## 3. songsee — Audio Spectrogram Visualization

CLI tool for generating spectrograms and multi-panel audio feature visualizations.

### Install
```bash
go install github.com/steipete/songsee/cmd/songsee@latest
```

### Usage
```bash
# Basic spectrogram
songsee track.mp3

# Multi-panel grid
songsee track.mp3 --viz spectrogram,mel,chroma,hpss,selfsim,loudness,tempogram,mfcc,flux

# Time slice
songsee track.mp3 --start 12.5 --duration 8 -o slice.jpg
```

### Visualization Types
| Type | Description |
|------|-------------|
| `spectrogram` | Standard frequency spectrogram |
| `mel` | Mel-scaled spectrogram |
| `chroma` | Pitch class distribution |
| `mfcc` | Mel-frequency cepstral coefficients |
| `tempogram` | Tempo estimation |
| `hpss` | Harmonic/percussive separation |

### Common Flags
`--style` (color palette), `--width/--height`, `--window/--hop` (FFT params), `--start/--duration` (time slice), `--format jpg|png`

Output images can be analyzed with `vision_analyze` for automated audio analysis.

### Notes
- WAV/MP3 decoded natively; other formats need `ffmpeg`
- Useful for comparing audio outputs, debugging synthesis, documenting pipelines