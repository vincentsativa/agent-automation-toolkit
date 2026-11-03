# DeepSeek V4 Flash (0731), Local Inference Sizing

Facts verified Aug 2026. Use when Vinny asks how to run V4 Flash locally, how many machines, or what it costs.

## Model facts

- **284B total params, 13B active** (MoE). Active share ~4.6%.
- **1M context** (1,048,576 tokens), max output 384K.
- Official weights: **FP4 + FP8 mixed**, ~160 GB on disk (159.61 GB safetensors; 167 GB with DSpark draft module fused).
- Full-precision inference needs **~170-175 GB total memory** (158 GB weights + ~10 GB KV cache + overhead).
- MIT license. 0731 = same architecture as April preview, only re-post-trained (agentic focus).

## Quantization tiers (Unsloth GGUF)

| Tier | Size | Min RAM | Comfortable |
|---|---|---|---|
| UD-Q8_K_XL (lossless) | 162 GB | 169 GB | 192 GB |
| UD-Q4_K_XL (near-lossless) | 155 GB | 192 GB | 192 GB |
| Q4_K_M (community) | ~142 GB | 150 GB | 192 GB |
| UD-IQ3_XXS (recommended) | 104 GB | 110 GB | 128 GB |
| UD-IQ2_M / Q2_K_XL | ~91-97 GB | 128 GB | 128 GB |
| IQ2XXS (antirez) | ~87 GB | 128 GB | 128 GB |

## Mac mini, the key constraint

- **Mac mini tops out at 64 GB unified memory** (M4 Pro / M5 Pro). It does NOT go to 128 GB, that's Mac Studio / MacBook Pro territory.
- So a single Mac mini CANNOT run V4 Flash at any tier. You must either string minis together or buy a bigger single machine.
- **Stringing minis works** (llama.cpp rpc-server distributed inference, MLX multi-device pooling) but is slow: Thunderbolt interconnect (~10 GB/s) vs internal bandwidth (273-307 GB/s). Expect low single-digit tok/s.
- **Mac mini count:**
  - IQ3_XXS (~104 GB): 2x 64GB minis (~$4,000-5,000)
  - Q4_K_M (~142 GB): 3x 64GB minis (~$6,000-7,500)
  - Official FP4/FP8 (~160 GB): 3x 64GB minis (~$6,000-7,500)
- **Single-machine alternative:** Mac Studio M4 Max 128 GB (~$3,999) runs IQ3_XXS; Mac Studio M4 Ultra 192 GB (~$6,000+) runs full official weights. One machine, no stringing.

## DGX Spark (GB10), the better answer

- **128 GB unified memory per unit**, ~$4,000 each. QSFP direct interconnect (200 Gbps, ~16 GB/s measured).
- **2x DGX Spark (~$8,000, 256 GB)** is the reference deployment for V4 Flash. DeepSeek ships an official **DeepSeek-V4-Flash-DSpark** build optimized for it.
- Documented 2-node recipe (tonyd2wild/DeepSeek-v4-Flash-DSpark-60-tok-s-900K-ctx-2x-DGX-Spark) hits **55-60 tok/s with 1M context** via vLLM TP=2.
- **Verdict: 2x DGX Spark crushes 3x Mac mini.** More memory (256 vs 192 GB), faster interconnect, official software path, 10x+ the tok/s. Best price-to-performance point in local inference.

## API reference (for the "just use the API" comparison)

- $0.14 / 1M input (cache miss), $0.0028 / 1M (cache hit), $0.28 / 1M output.
- 2,500 concurrent requests. Peak/off-peak pricing announced (2x during Beijing business hours), no effective date yet.
- For most users the API is cheaper than owning hardware; self-hosting wins only for privacy, no-network, or fine-tuning needs.
