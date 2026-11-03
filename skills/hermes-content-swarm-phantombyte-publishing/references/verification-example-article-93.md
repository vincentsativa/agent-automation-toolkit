# Ghostwriter Verification Example, Article 93 (June 8, 2026)

Real execution transcript showing cross-file verification when a primary source URL fails. Use this as a reproduction recipe.

## The scenario
Outline referenced MIT Technology Review article for Meta hack details. Direct browser navigation to the claimed URL returned 404. Multiple daily data files contained corroborated facts.

## Files consulted
1. `tensorfeed_report_2026-06-08.md`, contained full summary of the MIT TR article with Somesh Jha quote, Obama White House account detail, and attacker methodology.
2. `blogwatcher-dump-2026-06-08.txt`, contained The Decoder article with exact account count (20,225), timeline (April 17–May 31), and mechanism description.
3. `ironpulse-2026-06-08.txt`, did NOT contain Meta hack story (Apple WWDC dominated this feed).
4. `Excluding the stories in the uploaded data (don't.md`, contained Anthropic self-improvement confirmation not present in other files.

## Verification pattern applied
- Primary source (MIT TR URL) → 404. Flagged as unverified.
- Cross-referenced TensorFeed + Blogwatcher → both contained same facts with attribution.
- Treated data files as verified sources, cited as "reported via TensorFeed" / "reported via The Decoder."
- Did NOT fabricate a working MIT TR URL.

## Key quote preservation
Somesh Jha observation about agents being "very eager to finish the task", preserved from TensorFeed summary, attributed correctly.

## Hard numbers verified
- 20,225 accounts (Blogwatcher via The Decoder)
- April 17–May 31 timeline (Blogwatcher via The Decoder)
- 11.94% / 7.47% (arXiv 2606.06523 abstract, direct browser)
- 20pp / 28pp safety reduction (arXiv 2606.06529 abstract, direct browser)

## Lesson
When a claimed vendor URL fails, the answer is not to drop the fact, it is to search the remaining daily data files for corroboration. Each file has a different source mix; the fact you need may be in the one you did not read first.