# Vendor Site Verification for Ghostwriter Terminal

## Static HTML / Noisy Pages

Some vendor sites (especially project landing pages like toolmetry-one.vercel.app) render as static HTML with generic containers and sparse text nodes. The browser snapshot may show headings and paragraphs but miss tables, charts, or inline stats.

When this happens:
1. Scroll to the specific results section on the page.
2. Take a `browser_snapshot(full=true)`.
3. Extract numbers from the raw StaticText nodes.

Do not assume the page failed to load just because the compact snapshot looks thin. The data is often there, just fragmented across generic containers.

## Example: Toolmetry Site (July 13, 2026)

The compact snapshot showed only headings and a few paragraphs. A `full=true` snapshot revealed all four result rows (SQLite, Memory, Git, Filesystem) with before/after percentages and improvement deltas, all as individual StaticText nodes under generic containers.

Key takeaway: when verifying vendor/project sites with minimal interactive elements, always use `full=true`.
