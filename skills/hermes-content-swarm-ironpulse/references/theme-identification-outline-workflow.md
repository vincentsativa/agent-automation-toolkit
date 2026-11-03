# Theme-Identification + Outline Writing Workflow

When Vinny provides a **data file directory** plus optionally a **draft article to exclude**, and asks for N themes not yet covered on PhantomByte, with specific constraints (e.g., "one MUST be engineering/architecture-related, one must NOT be about engineering/infrastructure"), the workflow differs from both scratch ideation (Phase 3) and pre-defined thesis population (Phase 6).

## Workflow

1. **Read the draft article** (if provided with a path like `C:\Users\<user>\OneDrive\Desktop\ARTICLE 70 COMPLETE.txt`). Note its themes — these are EXCLUDED from the new theme proposals. Do NOT write about or overlap with the draft's subject matter.

2. **Scan articles.phantom-byte.com** to capture the full list of existing article titles and themes. This is the "already covered" set. Every proposed theme must be genuinely new — no overlap with existing coverage.

3. **Read all data files** in the provided directory. The user will point to a folder like `TODAYS DATA FILES` on the desktop. **Path pitfall:** Vinny's OneDrive path is `/mnt/c/Users/<user>/OneDrive/Desktop/` not `/mnt/c/Users/<user>/Desktop/`. The OneDrive path is the correct one for data file folders that live on the desktop.

4. **Extract all stories/themes from data files.** Each report (Grok, Perplexity, Larry, Frank/TensorFeed, IronPulse) may have different structures and section headers. Parse all of them into a unified set of potential themes.

5. **Cross-reference against the existing site themes + the draft article's themes.** Anything already covered is eliminated. What remains are the fresh themes.

6. **Apply the user's constraints.** Typical pattern: "3 themes, one MUST be engineering/architecture, one must NOT be about engineering/infrastructure." Filter the fresh themes through these constraints.

7. **Write a full outline for each theme.** Each outline should follow PhantomByte structural preferences (visceral hook, evidence stack, creative leap, deployment urgency, solution section, loop-back close). Each outline should reference specific stories/data from the data files with source attribution. Include a SOURCES section at the bottom with specific citations.

8. **Save each outline as a SEPARATE text file** to the desktop:
   - Pattern: `OUTLINE N - [Short Theme Name].txt`
   - Path: `/mnt/c/Users/<user>/OneDrive/Desktop/OUTLINE N - Theme Name.txt`
   - 3 outlines = 3 separate files

9. **Email all outlines as attachments** to hello@phantom-byte.com via IONOS SMTP. Use `MIMEMultipart` with `MIMEBase` for each file attachment (never inline body). Subject line should describe what's in the email. Include a brief summary in the email body listing each outline's title and one-line pitch.

10. **Notify via Telegram** with a concise message: each outline title, its angle (1 sentence), and confirmation that files are on desktop + emailed.

## Constraints Checklist

- [ ] Theme 1 is engineering/architecture-related
- [ ] Theme 2 is NOT about engineering/infrastructure
- [ ] Theme 3 can be anything (wildcard)
- [ ] None of the themes overlap with existing PhantomByte articles
- [ ] None of the themes overlap with the draft article (if provided)
- [ ] Each outline references specific data from the provided files with source attribution
- [ ] Each outline follows PhantomByte style: no em dashes, direct tone, evidence-first

## Pitfalls

- **OneDrive path:** Vinny's desktop data folders are at `/mnt/c/Users/<user>/OneDrive/Desktop/`, not `/mnt/c/Users/<user>/Desktop/`. The latter path may exist but won't contain the data folders. Always check the OneDrive path first.
- **Draft article exclusion:** If Vinny says "do not write about this article," it means the article's themes are off-limits, not that you can't reference its data points. Use the data, skip the thesis.
- **Constraint enforcement:** The constraint matters. If all 3 proposed themes end up being infrastructure-related, you've failed the constraint. Force diversity before writing.
- **Separate files per outline:** Vinny expects individual text files, not one combined document. Each outline gets its own file.