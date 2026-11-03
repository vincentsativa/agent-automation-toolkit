# Songwriting & AI Music Prompting — Reference

Everything here is a GUIDELINE, not a rule. Art breaks rules on purpose.

## Song Structure

Common skeletons:
- **ABABCB** — Verse/Chorus/Verse/Chorus/Bridge/Chorus (most pop/rock)
- **AABA** — Verse/Verse/Bridge/Verse with refrain (jazz, ballads)
- **ABAB** — Verse/Chorus alternating (simple, direct)
- **AAA** — Strophic, no chorus (folk, storytelling)

Building blocks: Intro → Verse → Pre-Chorus → Chorus → Bridge → Outro

## Rhyme & Meter

- **Perfect**: lean/mean
- **Family**: crate/braid
- **Assonance**: had/glass (same vowels)
- **Consonance**: scene/when (different vowels)
- **Near/slant**: loose connection

Internal rhyme creates echoes within a line. Mixed rhyme types prevent nursery-rhyme effect.

## Emotional Arc

Map energy: Intro: 2-3 → Verse: 5-6 → Pre-Chorus: 7 → Chorus: 8-9 → Bridge: varies → Final Chorus: 9-10

Contrast is the most powerful dynamic tool. "Whisper before a scream" pattern.

## Lyric Craft

- **Show don't tell** — "Your hoodie's still on the hook by the door" beats "I was sad"
- **The hook** — usually the title, placed at first/last line of chorus
- **Prosody** — stable feelings pair with settled melodies/perfect rhymes; unstable feelings with wandering melodies/near-rhymes

## Parody/Adaptation

Map original structure: syllables per line, rhyme scheme, stressed syllables, held notes. Match stressed syllables to same beats. Match vowel sounds on long held notes. Monosyllabic swaps keep rhythm intact.

## Suno AI Prompt Engineering

### Style Formula
Genre + Mood + Era + Instruments + Vocal Style + Production + Dynamics + Dynamic Journey

Describe the arc: "Begins as a haunting whisper over sparse piano. Gradually layers in muted brass. Builds through the chorus..."

### Tools
- V4.5+ supports up to 1,000 chars in Style field
- NO artist names/trademarks — describe the sound
- Use Exclude Styles for what you don't want
- Unexpected genre combos: "bossa nova trap", "Appalachian gothic", "chiptune jazz"

### Metatags
Structure: [Intro] [Verse] [Pre-Chorus] [Chorus] [Bridge] [Instrumental Break] [Outro] [End]
Vocal: [Whispered] [Spoken Word] [Belted] [Falsetto] [Breathy] [Gritty] [Harmonies] [Choir]
Dynamics: [High Energy] [Building Energy] [Emotional Climax] [Gradual swell] [Slow Down]
Atmosphere: [Melancholic] [Euphoric] [Nostalgic] [Aggressive] [Dark Atmosphere]
SFX: [Vinyl Crackle] [Rain] [Applause] [Thunder]

### Phonetic Tricks
- Spell words as they sound: "through" → "thru", "Nous" → "Noose"
- ALL CAPS = louder
- Hyphenate: "lo-o-o-ove" for sustained melisma
- Spell out numbers: "24/7" → "twenty four seven"
- Space acronyms: "AI" → "A I"
- Test proper nouns in short clips first

## Workflow
1. Concept/hook first — emotional core
2. Map structure (if adapting)
3. Brainstorm freely before structuring
4. Draft lyrics into structure
5. Read aloud — catch meter stumbles
6. Build Suno style description with dynamic arc
7. Add metatags to lyrics
8. Generate 3-5 variations minimum
9. Pick best, use Extend/Continue
10. Expect ~3-5 generations per good result