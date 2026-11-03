---
name: baoyu-visual-creation
description: "Generate visual content (article illustrations, knowledge comics, infographics) via image_generate. Shared patterns: prompt construction, aspect ratio mapping, reference image handling, output structure."
version: 1.0.0
author: Hermes Agent (adapted from JimLiu/baoyu-skills)
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [baoyu, visual, illustration, infographic, comic, creative, image-generation, image_generate]
    homepage: https://github.com/JimLiu/baoyu-skills
---

# Baoyu Visual Creation

This umbrella skill covers three visual-creation workflows from the [baoyu-skills](https://github.com/JimLiu/baoyu-skills) project. All three use the same `image_generate` backend and share the same prompt-construction, reference-handling, and download patterns.

## Which Workflow?

| Workflow | Description | Reference |
|----------|-------------|-----------|
| **Article Illustrator** | Type × Style × Palette illustrations for articles | `references/baoyu-article-illustrator.md` |
| **Knowledge Comic** | Multi-page educational comics with characters, storyboard | `references/baoyu-comic.md` |
| **Infographic** | Layout × Style infographics (21×21 combinations) | `references/baoyu-infographic.md` |

## Shared Patterns (All Workflows)

### image_generate Tool Usage

The `image_generate` tool has this schema:
- `prompt` (string) — the text prompt
- `aspect_ratio` — one of `landscape`, `portrait`, `square`
- **Returns a URL**, not a local file — always download afterwards

Aspect ratio mapping:
- `16:9`, `4:3`, `3:2` → `landscape`
- `9:16`, `3:4`, `2:3` → `portrait`
- `1:1` → `square`

Download pattern (use absolute paths, never relative):
```bash
curl -fsSL "<url>" -o /absolute/path/to/output.png
```

Auto-retry on failure once.

### Reference Image Handling

`image_generate` does NOT accept reference images. When the user provides a reference:
1. Call `vision_analyze` on the image to extract style, palette, composition
2. Record the text description
3. Embed it in the prompt as text

### Prompt File Requirement (HARD)

Before calling `image_generate`, ALWAYS write the prompt to a file under `prompts/`. This is the reproducibility record. No image generation without a saved prompt file first.

### Core Principles (All Workflows)
- **Data integrity**: preserve source statistics verbatim. "73% increase" stays "73% increase"
- **Strip secrets**: scan source content for API keys, tokens, credentials before writing any output
- **Don't illustrate metaphors literally** — visualize the underlying concept

### Output Directory Conventions

| Workflow | Default Output Dir |
|----------|-------------------|
| Article file as input | `{article-dir}/imgs/` |
| Pasted content article | `illustrations/{topic-slug}/` |
| Comic | `comic/{topic-slug}/` |
| Infographic | `infographic/{topic-slug}/` |

Use `clarify` sparingly (1-2 questions max per turn). If the user specified everything in their request, skip `clarify` entirely.