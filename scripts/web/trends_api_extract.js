// Google Trends internal API extractor for browser_exec.
//
// Usage: the tab only needs to sit on the trends.google.com origin so the
// fetch calls carry the right cookies; it does not need to render.
//
//   1. new_tab("https://trends.google.com/trends/explore?geo=US&q=prefill%20tax")
//      wait_for_load(); time.sleep(3)
//   2. js(open("<path to this file>", encoding="utf-8").read())   // define helpers
//   3. js('(async () => JSON.stringify(await globalThis.__trends(["a","b","c"])))()')
//
// __trends(terms)  -> [{term, avg, peak, peakWeek, latest, first, weeks, vals}]
// __related(terms) -> {term: [{name, keys: [[query, formattedValue], ...]}, ...]}
//                     one entry per term, each holding its Top list then its
//                     Rising list (the two rankedList entries, in that order).
//
// Up to 5 terms per call. Write results to a file inside the browser_exec call
// and read it back: js() return values are dropped from `output` intermittently.
//
// CRITICAL: the response body is a `)]}'` prefix line followed by a comma and a
// newline. Strip it with an ANCHORED REGEX. A literal .replace(")]}'", "")
// leaves the trailing ",\n" behind and JSON.parse throws on every response.
//
// CRITICAL: the RELATED_QUERIES widget id is SUFFIXED per term in a multi-term
// comparison ("RELATED_QUERIES_0", "_1", "_2"), and is bare
// "RELATED_QUERIES" only for a single-term request. An exact-match lookup
// therefore returns "no RELATED_QUERIES widget" on every batch of two or more
// terms even though the widgets are all present. Match by PREFIX and iterate
// every match, pairing widget i with terms[i]. Because the widget itself does
// not carry its term name reliably (rankedList[].queryName comes back null),
// the term is taken from the ORDER of the request, not from the response.
// Keep related-query calls to TWO terms: three-term calls repeatedly returned
// "Runtime.evaluate timed out" while two-term calls returned on the first
// attempt, and a timed-out call leaves the helper undefined for the next one.

(function () {
  globalThis.__td = function (s) {
    return JSON.parse(String(s).replace(/^\)\]\}',?,?\s*/, ""));
  };

  globalThis.__explore = async function (terms) {
    const req = {
      comparisonItem: terms.map(function (t) {
        return { keyword: t, geo: "US", time: "today 12-m" };
      }),
      category: 0,
      property: ""
    };
    const u = "https://trends.google.com/trends/api/explore?hl=en-US&tz=-240&req=" +
      encodeURIComponent(JSON.stringify(req));
    const r = await fetch(u, { credentials: "include" });
    return await r.text();
  };

  globalThis.__trends = async function (terms) {
    let txt;
    try { txt = await globalThis.__explore(terms); }
    catch (e) { return [{ error: "explore fetch: " + String(e).slice(0, 200) }]; }
    let j;
    try { j = globalThis.__td(txt); }
    catch (e) { return [{ error: "explore parse: " + txt.slice(0, 200) }]; }

    const w = (j.widgets || []).find(function (x) { return x.id === "TIMESERIES"; });
    if (!w) return [{ error: "no TIMESERIES widget: " + txt.slice(0, 300) }];

    const u2 = "https://trends.google.com/trends/api/widgetdata/multiline?hl=en-US&tz=-240&req=" +
      encodeURIComponent(JSON.stringify(w.request)) + "&token=" + encodeURIComponent(w.token);
    const r2 = await fetch(u2, { credentials: "include" });
    const txt2 = await r2.text();
    let j2;
    try { j2 = globalThis.__td(txt2); }
    catch (e) { return [{ error: "multiline parse: " + txt2.slice(0, 200) }]; }

    const tl = (j2.default && j2.default.timelineData) ? j2.default.timelineData : [];
    return terms.map(function (t, i) {
      const vals = tl.map(function (pt) { return pt.value[i]; });
      const nz = vals.filter(function (v) { return v > 0; });
      let pk = 0, pkIdx = -1;
      vals.forEach(function (v, k) { if (v > pk) { pk = v; pkIdx = k; } });
      const avg = nz.length
        ? Math.round(nz.reduce(function (a, b) { return a + b; }, 0) / nz.length)
        : 0;
      return {
        term: t,
        avg: avg,
        peak: pk,
        peakWeek: (pkIdx >= 0 && tl[pkIdx]) ? tl[pkIdx].formattedTime : null,
        latest: vals.length ? vals[vals.length - 1] : null,
        first: vals.length ? vals[0] : null,
        weeks: vals.length,
        vals: vals
      };
    });
  };

  // Returns {term: [{name, keys}, {name, keys}]}, Top list first, Rising second.
  globalThis.__related = async function (terms) {
    let txt;
    try { txt = await globalThis.__explore(terms); }
    catch (e) { return { error: "explore fetch: " + String(e).slice(0, 200) }; }
    let j;
    try { j = globalThis.__td(txt); }
    catch (e) { return { error: "explore parse" }; }

    const ws = (j.widgets || []).filter(function (x) {
      return String(x.id).indexOf("RELATED_QUERIES") === 0;
    });
    if (!ws.length) {
      return { error: "no RELATED_QUERIES widget (ids: " +
        (j.widgets || []).map(function (x) { return x.id; }).join(",") + ")" };
    }

    const out = {};
    for (let i = 0; i < ws.length; i++) {
      const w = ws[i];
      const u2 = "https://trends.google.com/trends/api/widgetdata/relatedsearches?hl=en-US&tz=-240&req=" +
        encodeURIComponent(JSON.stringify(w.request)) + "&token=" + encodeURIComponent(w.token);
      let j2 = null;
      try {
        const r2 = await fetch(u2, { credentials: "include" });
        j2 = globalThis.__td(await r2.text());
      } catch (e) {
        out[terms[i] || ("term" + i)] = { error: "related parse" };
        continue;
      }
      const lists = [];
      for (const rl of ((j2.default && j2.default.rankedList) || [])) {
        lists.push({
          name: rl.queryName || null,
          keys: (rl.rankedKeyword || []).slice(0, 15).map(function (k) {
            return [k.query, k.formattedValue];
          })
        });
      }
      out[terms[i] || ("term" + i)] = lists;
    }
    return out;
  };
})();
