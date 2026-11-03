# Provider Usage Metering and Model Build Comparison

Use when the question is "how much more efficient is this build than the previous one" or "is my usage actually down." Work in this order: identify the builds, identify the meter, then measure only what the meter sees.

## 1. Identify the build from the catalog, not from the name

Ollama cloud exposes two catalog endpoints with different detail. `/api/tags` is the richer one.

```bash
KEY=<provider key>
curl -s -H "Authorization: Bearer $KEY" https://ollama.com/api/tags \
  | python3 -c "import sys,json;[print(json.dumps(m)) for m in json.load(sys.stdin)['models'] if 'deepseek' in m['name']]"
```

Fields that decide identity and efficiency:

- `size`, weight-file bytes. Same `size` on two tags means the same weights.
- `digest`, differs on a rebuild even when `size` and everything else match.
- `modified_at`, a second tag hours after the first is a rebuild, not a release line.
- `capabilities`, `completion`, `thinking`, `tools`, `vision`.

`/v1/models` adds per-slug metadata that `/api/tags` omits, and is where to read context window and default reasoning effort:

```bash
curl -s -H "Authorization: Bearer $KEY" https://ollama.com/v1/models \
  | python3 -c "import sys,json;[print(json.dumps(m,indent=1)) for m in json.load(sys.stdin)['models'] if 'deepseek' in m['slug']]"
```

Read `context_window`, `max_context_window`, `default_reasoning_level`, `supported_reasoning_levels`, `input_modalities`. Identical values across the two tags plus identical `size` settles it: same model, rebuilt digest, no parameter or quantization change to point at.

## 2. Find the meter

```bash
curl -s -H "Authorization: Bearer $KEY" "https://ollama.com/api/usage?range=7d"
```

Ollama's usage payload returns `request_count` ONLY. There is no token count, no GPU-seconds, no per-model cost field. Accepted parameters: `range` (`7d`, `30d`), `granularity` (`day`), `group_by` (`model`). Parameters it rejects, do not waste calls on them: `granularity=hour`, `include=limits`, `fields=tokens`. Endpoints that do not exist: `/api/usage/models`, `/api/subscription`, `/api/plan`, `/api/account`, `/api/me` (405).

Per-model breakdown:

```bash
curl -s -H "Authorization: Bearer $KEY" "https://ollama.com/api/usage?range=30d&group_by=model" \
  | python3 -c "import sys,json;d=json.load(sys.stdin);print(d['totals'].get('groups'));[print(b['from'][:10], b['request_count'], {g['model']:g['request_count'] for g in b.get('groups',[])}) for b in d['buckets']]"
```

## 3. Read the timeline, not the total

The `totals.groups` array covers the whole range. `buckets[].groups` covers each day and is the only view that shows a model switch. The signature of a switch: the new tag absent or near-zero for most days, then a single day where it appears and the old tag collapses to zero the next day. Report those dates and both sides' counts; do not quote the 30-day split as if it described the current setup.

If total daily requests held roughly flat across the switch, usage did not fall, only the model consuming it changed, and that is the finding.

## 4. Measure the builds only on axes the user can use

With a request-count meter and a flat-rate/exempt plan, no output-length benchmark converts to money. What remains measurable and useful:

- wall-clock per typical request (latency he feels)
- time to first token, if the provider returns it
- tool round trips per completed task (the only lever that changes a request-metered bill)

Run both tags on the same prompt set at the same `reasoning_effort`, and report the effort setting. If `usage.completion_tokens_details` is null/missing, reasoning tokens are unreported, so token deltas are not a throughput comparison and must be labeled as such.

## Pitfalls

- Reasoning effort swings output length more than a version bump does. An unmatched-effort comparison is noise.
- One prompt per task type is an anecdote. Say "three prompts, small sample" or run a wider suite.
- A dated tag is a rebuild stamp. Do not translate `:1017` into a version claim.
- Do not report a 30-day `totals.groups` split as the user's current usage pattern.
