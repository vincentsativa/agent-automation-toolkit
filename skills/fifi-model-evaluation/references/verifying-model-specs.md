# Verifying model specs locally

Order of trust for parameter counts, sizes, context windows:

1. **Local Ollama API (measured):**
   ```bash
   ollama show <model>            # human-readable: parameters, context, quantization
   curl -s -X POST http://127.0.0.1:11434/api/show \
     -d '{"model":"<model>:cloud"}'   # JSON: general.parameter_count, family, quantization_level
   ```
   Cloud-hosted tags end in `:cloud` and only exist after first run. `ollama list` shows which tags are registered locally; namespaced forms like `vendor/model` are rejected by `ollama show` unless registered.

2. **Primary published spec:** official library/model page (e.g. ollama.com/library/<model>), Hugging Face model card, or the technical report PDF. Authoritative advertised total (e.g. 309B total / 15B active for a MoE).

3. **OpenRouter model card** (`curl -s https://openrouter.ai/api/v1/models` filtered by id), reliable for per-provider pricing and the advertised architecture blurb.

Why both 1 and 2: Ollama's `general.parameter_count` often covers only tensors in the serving checkpoint, so it can read well below the advertised MoE total (161B reported vs 309B published, measured). Report both numbers and name the source; never reconcile them by guessing.

Never cite aggregate third-party indexes (routing/leaderboard sites) for size or spec, demonstrably wrong values in the same family (a 1.02T model indexed as 116B).

## When he asks which number is actually true
Reporting both numbers answers "what does each source say." Answering "which is real" needs three independent primary-source checks; if all three agree, name the verdict with the evidence instead of stopping at "they differ":

1. **HuggingFace safetensors total**, logical parameter count of the real checkpoint:
   ```bash
   curl -s "https://huggingface.co/api/models/<org>/<repo>" | \
     python3 -c "import sys,json;print(json.load(sys.stdin).get('safetensors'))"
   ```
   `total` in the result is the param count (e.g. 310,756,322,688 → 310.8B). Per-dtype breakdowns can be internally inconsistent with file sizes; trust `total`, cross-check with 2 and 3.
2. **config.json arithmetic**, independent of any metadata field:
   `layers × experts × 3 × hidden_size × moe_intermediate_size` gives routed-expert params alone (e.g. 48 × 256 × 3 × 4096 × 2048 = 309.2B, before attention/embeddings). Fetch with `curl -s https://huggingface.co/<org>/<repo>/raw/main/config.json`.
3. **Artifact-size cross-check**, `file_bytes × 8 ÷ bits_per_weight = params`. A published quant stated as "97 GB at BPW2.5" implies 97e9×8÷2.5 = 310.8B, matches check 1 exactly. Sum shard sizes via the HF tree API (`/api/models/<repo>/tree/main`) when no stated bpw exists (177.7GB of shards ≈ 311B logical params packed at ~4.6bpw).

If these say X and a UI field says Y, Y is metadata, not a measurement, say so.

## Probing what a label actually is (Ollama registry)
Ollama's website Size card and `/api/show` parameter_count both echo a manifest field, so pull the manifest to see it at the source:
```bash
curl -s "https://registry.ollama.ai/v2/library/<model>/manifests/<tag>"   # → config blob sha
# then GET https://registry.ollama.ai/v2/library/<model>/blobs/<sha256:...>
```
The blob shows hand-entered fields like `"model_type":"161B"` next to `file_type`, `remote_host`. `"layers":[]` means the tag is a cloud proxy, the weights on the provider's GPUs are not inspectable from outside; in that case the verdict rests on checks 1-3 plus the absence of any public checkpoint at the disputed size (search for it; a size no artifact anywhere matches is a label, not a model).
