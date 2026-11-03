# Catalog display name to API model ID

Applies to any vendor with a browse page plus an inference API (NVIDIA build
portal, OpenRouter, Together, Groq, Fireworks, Bedrock, Vertex).

## Why the two never match

Catalog pages key models by marketing name. Inference endpoints key them by a
namespaced deployment slug owned by the vendor or the upstream lab. The slug
also changes independently of the name (`nemotron-3.5-lightning-30b-a3b` ->
`nvidia/nemotron-3.5-lightning-30b-a3b`; `gpt-oss-20b` -> `openai/gpt-oss-20b`),
and the endpoint's own naming wins over the page's.

## Procedure

1. Pull the endpoint's live catalog, not the page. The endpoint is the only
   authority on what it will accept.
2. Match by substring, case-insensitive, longest-anchor first. A short anchor
   like `cosmos` or `nemotron` returns many rows; the decisive token is the
   version/parameter suffix.
3. Zero matches: the model is not served by that endpoint, or the slug differs
   from the name in a way substring search cannot bridge. Check the vendor's
   own docs page for that model for an explicit "model id" line before
   guessing a slug.
4. Matched, but the model is a non-chat microservice (image gen, video, ASR,
   TTS, translation, detection, rerank, embedding): it will be absent from the
   chat list or present but unroutable. Say so; do not silently drop it and do
   not silently promise it works.
5. Write the resolved IDs, and in the report show the user the exact ID list so
   they can check before the next call fails on them.

## Trap

Do not assume a name that fails substring matching means the model is
unavailable. Vendors rename slugs freely and the catalog page is often ahead of
the deployed endpoint. Both outcomes need distinguishing: "not deployed" and
"named differently" lead to different fixes.
