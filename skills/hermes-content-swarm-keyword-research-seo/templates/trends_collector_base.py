"""
Optimized trends collector for keyword research.
BATCHES 5 terms per API call. SINGLE pass (12-month data contains weekly
points; last 4 weeks = 3-month trend). No second pass needed.

This replaced the old one-term-at-a-time, two-pass approach that took 20+ minutes.
On a fresh IP, this completes in under 30 seconds for 15 terms.
"""
from pytrends.request import TrendReq
import json
import time


def collect_batched(batches, output_file='trends_results.json', delay=5):
    """
    Collect trends data for multiple batches of up to 5 terms each.
    Single API call per batch (5 terms). Single pass (12-month only).
    Derives 3-month trend from last 4 weeks of 12-month data.
    Falls back to individual terms only on 429.

    Args:
        batches: List of dicts: {"name": str, "terms": [str, ...]} (max 5 terms each)
        output_file: Path to save JSON results
        delay: Seconds between batches (default 5)

    Returns:
        Dict mapping term -> {"mean": float, "trend": "rising"|"falling"|"flat"}
    """
    pytrends = TrendReq(hl='en-US', tz=-240, timeout=(10, 25))
    results = {}

    for i, batch in enumerate(batches):
        name = batch['name']
        terms = batch['terms']
        print(f"\nBATCH {i+1}: {name} ({len(terms)} terms)")
        print("=" * 40)

        try:
            # Single API call for up to 5 terms, 12-month timeframe
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
                # Derive 3-month trend from last 4 weeks of 12-month data
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
                # 429 on batch: fall back to individual terms
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
                # Non-429 error: mark all terms as errored
                for t in terms:
                    results[t] = {"error": err}

        if i < len(batches) - 1:
            time.sleep(delay)

    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to {output_file}")
    return results


if __name__ == "__main__":
    # REPLACE with actual terms grouped by theme (max 5 per batch)
    batches = [
        {"name": "Core Article Concepts", "terms": [
            "Example Core Term 1",
            "Example Core Term 2",
            "Example Core Term 3",
            "Example Core Term 4",
            "Example Core Term 5",
        ]},
        {"name": "Adjacent/Benchmark Terms", "terms": [
            "Example Adjacent Term 1",
            "Example Adjacent Term 2",
        ]},
        {"name": "Ecosystem Terms", "terms": [
            "Example Ecosystem Term 1",
            "Example Ecosystem Term 2",
        ]},
    ]
    collect_batched(batches, output_file='trends_results.json', delay=5)
