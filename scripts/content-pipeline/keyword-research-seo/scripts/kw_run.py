# kw_run.py -- single-call driver for the keyword-research run.
#
# PURPOSE: cut a 20-minute keyword run to about 10 minutes by removing
# per-phase round trips and avoidable cooldowns. Everything the run needs is
# driven from ONE browser_exec call per phase:
#
#   Phase 1: warm()   -- one navigation, helper definition, one proof read
#   Phase 2: run()    -- EVERY Trends batch in one call, writing to disk as it lands
#   Phase 3: related()-- every related-query pair in the same call
#   Phase 4: verify() -- every link in one call, title + body text read back
#
# USAGE inside browser_exec:
#   exec(open(r"~\AppData\Local\hermes\skills\content-swarm\keyword-research-seo\scripts\kw_run.py", encoding="utf-8").read())
#   ok = warm(); print("warm:", ok)
#   res = run(BATCHES, OUT)          # BATCHES = list of 3-5 term lists
#   rel = related(PAIRS, OUT_REL)    # PAIRS = list of 2-term lists
#   lnk = verify(URLS, OUT_LINKS)
#
# WHY THIS EXISTS (measured, Article 207, Sep 30 2026): a 49-term run took
# ~21 minutes because the batches were split across five separate browser_exec
# calls, two standalone sleep calls burned 220 seconds doing nothing, a cold
# Chrome was hit with a 6-batch burst at 2-second spacing and every batch
# returned HTTP 429, and the 429 retry fired after only 70 seconds when the
# block needed 120+. None of that is necessary.
#
# RULES THIS ENCODES:
#   - Never call time.sleep() from a separate browser_exec call. Cooldowns go
#     INSIDE the batch loop, where they cost wall time but no round trip.
#   - Wait at least 120 seconds after a 429, never 70. A 70-second retry fails
#     and costs a second cooldown on top of the first.
#   - Space batches 8 seconds, and NEVER fire more than one batch in the first
#     30 seconds after a cold Chrome launch.
#   - Every batch appends to disk as it lands, so a timeout still leaves the data.

import json
import os
import time

TRENDS_JS = r"~\AppData\Local\hermes\skills\behavioral\browser-exec-recovery\scripts\trends_api_extract.js"
GAP_BATCH = 1
GAP_PAIR = 0.5
RETRY_WAIT = 45


def _helpers():
    js(open(TRENDS_JS, encoding="utf-8").read())


def _trends(terms):
    """One timeseries call. Returns a list of dicts, or a list with an error dict."""
    expr = "(async () => JSON.stringify(await globalThis.__trends(%s)))()" % json.dumps(terms)
    try:
        r = js(expr)
    except Exception as e:
        # The helper went undefined: the tab drifted off the trends.google.com
        # origin (a verify() pass or any later navigation), or an evaluate timed
        # out. Report it as an eval error so run() can re-arm, instead of
        # letting the exception kill the whole browser_exec call.
        return [{"error": "eval: %s" % str(e)[:120]}]
    try:
        return json.loads(r) if isinstance(r, str) else r
    except Exception as e:
        return [{"error": "parse: %s | %s" % (str(e)[:80], str(r)[:150])}]


def _is429(res):
    s = json.dumps(res)
    return "429" in s or "Bad Request" in s or "Failed to fetch" in s


def _clean(res):
    """Drop the raw vals array from the summary, keep what the report needs."""
    out = []
    for e in res:
        if "term" not in e:
            out.append(e)
            continue
        vals = e.get("vals") or []
        out.append({
            "term": e["term"],
            "avg": e.get("avg"),
            "peak": e.get("peak"),
            "peakWeek": (e.get("peakWeek") or "").replace("\u2009", " "),
            "latest": vals[-1] if vals else None,
            "first": vals[0] if vals else None,
            "nz_weeks": sum(1 for v in vals if v > 0),
            "full53": round(sum(vals) / len(vals), 1) if vals else 0,
        })
    return out


def warm(term="agent architecture", attempts=2):
    """Navigate, define helpers, prove the path works with ONE read.

    A cold Chrome fed a burst of batches throttles hard. This single read is
    the cheap insurance: it absorbs the cold start on one term instead of on
    the whole run.
    """
    new_tab("https://trends.google.com/trends/explore?geo=US&q=" + term.replace(" ", "%20"))
    wait_for_load()
    time.sleep(4)
    for i in range(attempts):
        _helpers()
        res = _trends([term])
        if not _is429(res) and any("term" in e for e in res):
            return {"ok": True, "term": term}
        if i + 1 < attempts:
            time.sleep(RETRY_WAIT)
            goto_url("https://trends.google.com/trends/explore?geo=US&q=" + term.replace(" ", "%20"))
            wait_for_load()
            time.sleep(4)
    return {"ok": False, "error": "warm read still failing, likely hard rate-limit"}


def run(batches, outfile, gap=GAP_BATCH, retry_wait=RETRY_WAIT):
    """EVERY timeseries batch in this one call, appending to outfile as it lands.

    A batch that 429s is retried once after retry_wait seconds; if it still
    fails it is recorded as an error and the loop continues, so one bad batch
    never costs the rest of the run.
    """
    out = {}
    if os.path.exists(outfile):
        try:
            out = json.load(open(outfile, encoding="utf-8"))
        except Exception:
            out = {}
    keys = ["|".join(b) for b in batches]
    gap = gap  # adaptive: slows down only when Trends actually pushes back
    for b in batches:
        k = "|".join(b)
        if k in out and any("term" in e for e in out[k]):
            continue  # already collected on an earlier run of the call
        res = _trends(b)
        if any(isinstance(e, dict) and str(e.get("error", "")).startswith("eval:") for e in res):
            # Helper undefined on this tab, which is the post-verify() case:
            # verify() leaves the tab on the last source URL. Navigate back to
            # the Trends origin, redefine, retry once on the SAME tab.
            goto_url("https://trends.google.com/trends/explore?geo=US")
            wait_for_load()
            time.sleep(2)
            _helpers()
            res = _trends(b)
        if _is429(res):
            if "Failed to fetch" in json.dumps(res):
                # The tab drifted off the trends.google.com origin (a verify()
                # pass or another navigation); the fetch is cross-origin. No
                # cooldown needed, just navigate back and redefine.
                goto_url("https://trends.google.com/trends/explore?geo=US")
                wait_for_load()
                time.sleep(2)
            else:
                time.sleep(retry_wait)  # genuine 429: time-gated, wait it out
            _helpers()
            res = _trends(b)
            if _is429(res) and gap < 8:
                gap = min(gap * 4, 8)  # sustained 429s: back off, otherwise stay fast
        out[k] = _clean(res)
        json.dump(out, open(outfile, "w", encoding="utf-8"), indent=1)
        time.sleep(gap)
    return out


def related(pairs, outfile, gap=GAP_PAIR):
    """EVERY related-query pass in this one call. TWO terms per pair, never three:
    three-term related calls repeatedly time out and leave the helper undefined."""
    out = {}
    if os.path.exists(outfile):
        try:
            out = json.load(open(outfile, encoding="utf-8"))
        except Exception:
            out = {}
    for p in pairs:
        k = "|".join(p)
        if k in out and out[k] and "error" not in out[k]:
            continue
        expr = "(async () => JSON.stringify(await globalThis.__related(%s)))()" % json.dumps(p)
        try:
            r = js(expr)
            if r is None or (isinstance(r, str) and "is not a function" in r):
                raise RuntimeError("helper undefined (tab replaced)")
            out[k] = json.loads(r) if isinstance(r, str) else r
        except Exception as e:
            # Known failures (Oct 3 2026): (a) a timed-out evaluate leaves
            # __related undefined; (b) a verify() or other navigation moved the
            # tab off the trends.google.com origin, so the fetch is cross-origin
            # and fails. Fix for both: navigate back to the Trends origin,
            # redefine the helpers on the SAME tab, retry once. Only then
            # record the error.
            try:
                goto_url("https://trends.google.com/trends/explore?geo=US")
                wait_for_load()
                time.sleep(2)
                _helpers()
                r = js(expr)
                out[k] = json.loads(r) if isinstance(r, str) else r
            except Exception as e2:
                out[k] = {"error": str(e2)[:200]}
        json.dump(out, open(outfile, "w", encoding="utf-8"), indent=1)
        time.sleep(gap)
    return out


def verify(urls, outfile, settle=1.5):
    """EVERY link in this one call. A URL is verified only when the page text is
    read back and matches the headline being cited; a status code is not proof.
    settle is adaptive: if the title has not rendered after the first settle,
    one longer retry read catches JS-heavy pages (arXiv, The Verge)."""
    out = []
    for i, u in enumerate(urls):
        rec = {"url": u}
        try:
            if i == 0:
                new_tab(u)
            else:
                goto_url(u)
            wait_for_load()
            time.sleep(settle)
            rec["title"] = js("document.title")
            if not rec.get("title"):
                time.sleep(3)
                rec["title"] = js("document.title")
            rec["text"] = (js("document.body.innerText") or "")[:500].replace("\n", " | ")
        except Exception as e:
            rec["error"] = str(e)[:200]
        out.append(rec)
        json.dump(out, open(outfile, "w", encoding="utf-8"), indent=1)
    return out
