#!/usr/bin/env python3
"""One-shot reminder: Friday 12pm, the OSM targeting build session starts that evening."""
import datetime

BUILD_NIGHT = "Friday, September 25, 2026, that evening"

msg = f"""REMINDER. Tonight is the build session. {BUILD_NIGHT}, we start building the local OpenStreetMap index for prospect targeting.

Why we are building it: we do not own the category filter today. It is a hardcoded keyword table inside OpenLeads, written by someone else. Tested live on 9/23: nail salons in Tampa returned a hairdresser and a spa instead of nail salons, and law offices in Tampa returned zero because the trigger words are matched as substrings. That is the filter, not the data.

What we are building: a local index instead of live queries. Step 1, download the Geofabrik state file, Florida first, roughly a gigabyte, currently dated September 22. Step 2, load it with pyosmium or into PostgreSQL with osm2pgsql. Step 3, query it locally with SQL where the filter is ours. Step 4, add a vertical by adding a rule, no keyword roulette and no throttling.

Why it works: the bottleneck is the shared free Overpass server rate limiting and timing out, not the data. The same Manhattan query with a 180 second timeout returned HTTP 200, 400 elements, 386 domains, and 55 published emails in a single call. New York works fine. The tool's hardcoded 25 second timeout is what returns zero.

Four things to settle at the start: which state files first, pyosmium against the raw file versus osm2pgsql into Postgres, where the index lives on disk, and whether it replaces the OpenLeads local source or sits beside it.

The full plan is saved at ~/money_ideas/BUILD_PLAN_local_osm_index.md, including the GitHub repos checked live on 9/23 and the 20 minute timeout fallback.

The 20 outreach emails scheduled for Wednesday morning went out to Orlando area businesses starting at 9:00 AM on 9/23."""

print(msg)
