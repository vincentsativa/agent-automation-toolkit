# Targeting an Open Dataset You Did Not Write the Client For

Patterns for querying a large open dataset (OpenStreetMap is the worked example)
through someone else's client, when the goal is **control over what gets
selected**, not just volume.

## Two controls exist, and only one is usually broken

| Control | Mechanism | Usually |
|---|---|---|
| Where | a bounding box resolved from a place name | fine |
| What category | which tags/fields the query asks for | owned by the client's author |

When someone asks for better targeting, the answer is almost always the second
row. Diagnose it before proposing anything: read the client's category table. If
it is a hardcoded keyword list authored by someone else, you do not own the
filter, you are borrowing a coarse one.

## Failure shapes a borrowed category table produces

Both look like an empty result. Neither is.

- **A phrase containing no trigger word returns nothing.** The match is a
  substring test against a fixed word list, and an unrecognised phrase falls
  through to a generic wildcard sweep that returns little or nothing. The fix is
  to find the trigger word the table actually carries, and to treat a zero as
  "phrase did not match a keyword" until proven otherwise.
- **An unrecognised vertical is silently widened.** One keyword maps to several
  tags OR'd together, so a specific ask returns the whole adjacent group with no
  way to separate the members. Example shape: a request for nail salons matched a
  keyword that mapped to hairdresser, beauty, spa and massage tags together, and
  returned a hairdresser, two beauty shops and a spa, with no nail salon in it.

## When the dataset has no tag for what you want

The vocabulary is the dataset's, not yours, and no query can invent a tag that
does not exist. When a sub-category genuinely has no tag of its own, precision has
to come from a second pass over a **name sub-filter**: pull the parent group by
tag, then filter the business names for the sub-category words. Verify the tag
vocabulary against the dataset's own tag documentation before promising a
sub-category can be targeted.

## Owning the filter: a curated vertical map

Replace keyword roulette with a curated map of exact tags per vertical, plus a
name sub-filter for the categories the dataset never split. Additions then cost
one line each instead of a hope that a keyword matches. Verticals with real tags
are exact and should be reached for first; categories with no tag are the ones
that need the sub-filter.

## Removing the shared server entirely (the real fix)

Every query to a free shared query endpoint competes with everyone else for one
rate-limited server. The same data is usually published as bulk extracts by
region from a mirror that serves files, not queries, and imposes no per-request
timeout. For OpenStreetMap that is Geofabrik's per-state `.osm.pbf` files.

Load the extract locally and the category filter becomes yours to write:

- `pyosmium` or `libosmium` for reading OSM data directly from Python.
- `osmium-tool` for command-line filtering and extracting one region from a
  larger file.
- `osm2pgsql` into PostgreSQL/PostGIS, which turns targeting into SQL over the
  tag columns, and makes the name sub-filter and any multi-signal scoring trivial.

This is the step that turns "more places" into "every place, at the same cost,"
and it is also what makes a dense metro as cheap as a small town.

## Evaluating third-party tooling for this

Search results for this space are dominated by scrapers for commercial map and
listing sites. Judge each candidate on two questions before reading its README:

- **Does it give you control of the filter, or a keyword box?** A keyword box is
  the same coarse control you already have.
- **Does the data it returns come with a category field you can filter on?** If
  not, it cannot support targeting work no matter how many records it returns.

The repositories that actually help are the low-level libraries that read and
index the open dataset, plus a query-building and preview tool for verifying a
query against a live map before shipping it. Tooling built around a commercial
map provider hands the category definition back to that provider.
