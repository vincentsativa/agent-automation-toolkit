"""
Optimized trends collector for "Your Security Model Is Too Big" keyword research.
BATCHES 5 terms per API call. SINGLE pass (12-month data contains weekly
points; last 4 weeks = 3-month trend).
"""
from pytrends.request import TrendReq
import json
import time


def collect_batched(batches, output_file='trends_results.json', delay=5):
    pytrends = TrendReq(hl='en-US', tz=-240, timeout=(10, 25))
    results = {}

    for i, batch in enumerate(batches):
        name = batch['name']
        terms = batch['terms']
        print(f"\nBATCH {i+1}: {name} ({len(terms)} terms)")
        print("=" * 40)

        try:
            pytrends.build_payload(terms, cat=0, timeframe='today 12-m', geo='', gprop='')
            data = pytrends.interest_over_time()

            if data.empty:
                print("  No data returned for batch.")
                for t in terms:
                    results[t] = {"mean": 0.0, "trend": "flat"}
                continue

            for term in terms:
                if term not in data.columns:
                    results[term] = {"mean": 0.0, "trend": "flat"}
                    print(f"  {term}: no data (0.0)")
                    continue
                col = data[term]
                mean_val = round(float(col.mean()), 1)
                vals = col.tail(4).tolist()
                start_val = sum(vals[:2]) / 2 if len(vals) >= 2 else vals[0]
                end_val = sum(vals[-2:]) / 2 if len(vals) >= 2 else vals[-1]
                trend = "rising" if end_val > start_val else "falling" if end_val < start_val else "flat"
                results[term] = {"mean": mean_val, "trend": trend}
                print(f"  {term}: mean={mean_val}, trend={trend}")

        except Exception as e:
            err = str(e)
            print(f"  Error: {err}")

            if "429" in err:
                print("  429 hit. Falling back to individual terms with 8s delay...")
                time.sleep(30)
                for term in terms:
                    try:
                        pytrends.build_payload([term], cat=0, timeframe='today 12-m', geo='', gprop='')
                        d = pytrends.interest_over_time()
                        if not d.empty and term in d.columns:
                            col = d[term]
                            mean_val = round(float(col.mean()), 1)
                            vals = col.tail(4).tolist()
                            start_val = sum(vals[:2]) / 2 if len(vals) >= 2 else vals[0]
                            end_val = sum(vals[-2:]) / 2 if len(vals) >= 2 else vals[-1]
                            trend = "rising" if end_val > start_val else "falling" if end_val < start_val else "flat"
                            results[term] = {"mean": mean_val, "trend": trend}
                            print(f"  {term}: mean={mean_val}, trend={trend}")
                        else:
                            results[term] = {"mean": 0.0, "trend": "flat"}
                            print(f"  {term}: no data (0.0)")
                        time.sleep(8)
                    except Exception as e2:
                        print(f"  {term}: failed - {e2}")
                        results[term] = {"error": str(e2)}
                        if "429" in str(e2):
                            time.sleep(60)
            else:
                for t in terms:
                    results[t] = {"error": err}

        if i < len(batches) - 1:
            time.sleep(delay)

    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to {output_file}")
    return results


if __name__ == "__main__":
    # Batch 1 - Core article concepts (umbrella terms, product names, coined terms)
    # Batch 2 - Adjacent/benchmark terms
    # Batch 3 - Ecosystem/hardware terms

    batches = [
        {"name": "Core Article Concepts", "terms": [
            "Cisco Antares",
            "Gemini Flash Cyber",
            "Fugu-Cyber",
            "small AI security models",
            "AI vulnerability detection",
        ]},
        {"name": "Adjacent/Benchmark Terms", "terms": [
            "multi-agent security",
            "AI supply chain security",
            "AI model cheating",
            "local AI security",
            "data sovereignty AI",
        ]},
        {"name": "Ecosystem Terms", "terms": [
            "AI agent security",
            "AI endpoint security",
            "frontier model security",
            "AI vulnerability scanning",
            "CrowdStrike AI worm",
        ]},
    ]
    collect_batched(batches, output_file='trends_results.json', delay=5)
