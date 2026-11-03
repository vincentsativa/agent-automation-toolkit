---
name: browser-exec-recovery
description: Use when browser_exec fails with BU_CDP_URL unreachable.
trigger: "browser_exec fails with 'BU_CDP_URL ... unreachable' or 'actively refused it', or the browser harness cannot connect to the automation Chrome."
---

# Browser Exec Backend Recovery

When `browser_exec` fails with a fatal error like:

```
browser-harness: fatal: BU_CDP_URL=http://127.0.0.1:9223 unreachable after 30s:
<urlopen error [WinError 10061] ... actively refused it> -- is the dedicated
automation Chrome running?
```

The dedicated automation Chrome is not running. The harness needs a Chrome
instance listening on the CDP port. Recover by launching it manually, then
retry the `browser_exec` call.

## Recovery steps

1. Launch the dedicated Chrome DETACHED so it outlives the shell that spawned
   it. The verified command on this host is PowerShell `Start-Process` run from
   `terminal`:

   ```bash
   powershell -Command "Start-Process -FilePath 'C:\Program Files\Google\Chrome\Application\chrome.exe' -ArgumentList '--remote-debugging-port=9223','--user-data-dir=~\AppData\Local\chrome-kw','--no-first-run','--no-default-browser-check','about:blank'"
   sleep 8; curl -s --max-time 5 http://127.0.0.1:9223/json/version
   ```

   **`terminal(background=true)` can print `DevTools listening on ws://127.0.0.1:9223/...`
   and still leave the port dead.** The child stays tied to the tool's shell job,
   so when that shell exits Chrome exits with it and the next `browser_exec`
   reports the same `actively refused` error that sent you here. Never read the
   "DevTools listening" line as success; the curl probe is the only proof.
   `cmd //c start "" chrome.exe ...` returns before Chrome binds the port and
   then reports it dead for the same reason. `Start-Process` detaches properly.

   On this Windows host the dedicated profile lives at
   `$LOCALAPPDATA/chrome-kw` (verified Sep 2026 — the older
   `$LOCALAPPDATA/hermes/chrome-kw` path does not exist and Chrome silently
   creates a fresh profile at it, losing the persisted session state):

   ```bash
   "/c/Program Files/Google/Chrome/Application/chrome.exe" \
     --remote-debugging-port=9223 \
     --user-data-dir="$LOCALAPPDATA/chrome-kw" \
     --no-first-run --no-default-browser-check about:blank
   ```

2. Verify the CDP endpoint is up before retrying:

   ```bash
   sleep 5; curl -s http://127.0.0.1:9223/json/version
   ```

   A JSON response with `webSocketDebuggerUrl` confirms readiness.

   **A first probe that comes back connection refused is not a verdict about the environment.** The bind takes a few seconds and the launch can land while another chrome child still holds the profile, so the same command that looks like it failed is often listening a few seconds later. Probe again, and if two probes a few seconds apart are both refused, re-run the IDENTICAL `Start-Process` command once and probe a third time. Re-running is the fix that works; do not conclude the browser backend is unavailable, and do not change the port, the profile dir, or the launch mechanism to "fix" it, because a different profile dir silently starts a brand-new profile and loses the persisted session state that the dedicated dir exists to keep.

3. Retry the `browser_exec` call. The harness connects to the already-running
   Chrome. Use a named session (`session='...'`) to keep the work isolated.

**`BU_CDP_URL` is empty in the shell, and that is not a problem.** Checking
`echo "$BU_CDP_URL"` returns an empty string even when the harness is healthy,
because the variable is injected into the harness process, not exported to the
`terminal` tool's shell. Never conclude the backend is down from that. The real
liveness test is the curl probe in step 2: a JSON body with
`webSocketDebuggerUrl` means go, a connection refused means run the recovery
launch. Check the port, not the variable.

## Batch extraction pattern (many URLs in one session)

When a job needs the same read from many pages (Trends batches, a link
verification sweep), do NOT write the per-page navigation and polling by hand
at the call site. Drive it from a loop inside one `browser_exec` call that
writes every result to a JSON file, then read that file back. The loop survives
timeouts far better than a single giant call, and the file is the artifact you
aggregate from. Two shapes that work:

- **One fresh named session per item** (`kw<article>_b1` … `_b8`) when each item
  is a separate site fetch subject to per-instance rate limiting.
- **One session for a sequential sweep** of URLs that differ only in path.

**`Page.navigate timed out after 5s waiting for the daemon` on a sweep URL is a
transient daemon hiccup, not a dead URL, and it can hit SEVERAL CONSECUTIVE URLs,
not just one.** Re-run the unverified remainder in a fresh named session with a
longer settle instead of dropping them or reporting them broken. A sweep that
flags five sources in a row and then returns all five clean on the retry was
never a link problem, and the timeouts cluster at the head of a long sweep
because that is where the daemon is coldest. Record a per-URL `error` key and
re-run only the errored ones; a link is UNVERIFIED until a page read confirms
its title, so an errored entry is neither a pass nor a fail.

Write each result to disk inside the loop, including a per-item `"error"` key on
failure, so a partial run still leaves you the data you collected:

```python
import json
out = []
for u in urls:
    rec = {"url": u}
    try:
        new_tab(u); wait_for_load(); time.sleep(3)
        rec["title"] = js("document.title")
        rec["text"]  = (js("document.body.innerText") or "")[:500].replace("\n", " | ")
    except Exception as e:
        rec["error"] = str(e)[:250]
    out.append(rec)
open(r"C:\Users\<user>\AppData\Local\hermes\cache\documents\sweep.json", "w", encoding="utf-8").write(json.dumps(out, indent=1))
```

Use `new_tab` for the first URL in a fresh session and `goto_url` for subsequent
ones in the same session; `goto_url` on the very first navigation can time out
against a cold daemon. A `time.sleep(3)` after `wait_for_load()` covers the
client-side render on JS-heavy pages (arXiv, The Verge) whose titles are absent
from the initial HTML.

A sweep like this is the right way to verify citation links before shipping a
report. One trap: **a URL is not verified until the page text confirms it**, not
by a status code from a scripted client (see the 403/429 note in SKILL.md) and
not by a slug that merely looks right. Read back `document.title` and the
opening body text and match them against the headline and byline being cited.

## Persistent logged-in sessions for a site

The automation Chrome runs its OWN persistent profile (`$LOCALAPPDATA/chrome-kw`),
which is NOT the user's everyday Chrome profile. A site he is already signed into
in his daily browser shows a sign-in wall here. Check which profile you are
actually in before promising access to his logins; the harness's local mode
resolves to the dedicated automation profile on this host, so his everyday
sessions do not carry over.

To make a site permanently usable by the agent:

1. Launch the automation Chrome (Recovery steps above) and navigate the tab to
   the site's sign-in page.
2. Ask the user to sign in ONCE, in that window, with whatever method he
   already uses. This is the only credential step and it never passes through
   the agent.
3. Verify by reading an authenticated-only page, not by trusting the
   navigation. A redirect to a sign-in URL means not logged in; a real account
   page returns the sidebar plus the account's own handle.
4. Prove persistence instead of assuming it: kill the browser with the kill
   script, relaunch with the SAME `--user-data-dir`, and re-read the
   authenticated page. Cookies live on disk in the profile, so the login
   survives a full restart.
5. Close and verify shutdown as usual (see the section below).

**A live kill-and-relaunch is the proof step, not a formality.** Run the
sequence in that order and report the evidence: signed-out state first, then the
account identity read back from an auth-only page after the restart. Skipping
the restart proves nothing, because an in-memory session looks identical to a
persisted one until the process dies.

Rules that matter here:

- OAuth sign-in buttons (Google, X, Apple, Facebook, LinkedIn) cannot be
  vaulted; only an email plus password login can be saved with
  `browser_vault_save_login`. If the user wants the agent to enter credentials
  in future sessions, walk him to the email sign-in path rather than an OAuth
  button.
- Cookies expire. When a site logs itself out later, the fix is the same
  one-time sign-in in the automation profile, not a new capability. Say that
  up front so a future logout is not read as a broken setup.
- Never type, ask for, or repeat a password in chat, and never use
  `fill_input` for one. Passwords reach a page only through the vault tools.
- Concrete per-site verification patterns live in
  `references/persistent-site-logins.md`.

## Reading Trends through browser_navigate / browser_console (no browser_exec)

When the workflow is driven with `browser_navigate` / `browser_console` /
`browser_cdp` instead of `browser_exec`, these traps cost whole batches:

- **The internal widget API is the PREFERRED path from `browser_console`, not a
  last resort.** Verified repeatedly: one `browser_navigate` to any
  `trends.google.com/trends/explore?geo=US&q=<term>` URL, then one
  `browser_console` call that defines the `scripts/trends_api_extract.js`
  helpers, then every batch driven with
  `browser_console(expression='(async () => JSON.stringify(await globalThis.__trends([...])))()')`.
  Ten batches in one tab returned full data with zero 429s, zero waits, and
  zero failed batches, and the per-term payload includes the full 53-week `vals`
  array, which the rendered table is slower to give you. Reach for the DOM read
  only when the API path genuinely errors.
  The token-rotation failure (`widgetdata/multiline` returning HTTP 401 with an
  HTML body, so `JSON.parse` throws `Unexpected token '<'`) strikes when the
  helpers are defined in one call and driven from a LATER call that landed on a
  different tab or target, so the token no longer matches the page. Keep the
  definition and the batch calls on the same tab, redefining the helpers in the
  SAME call after any navigation, and the token stays valid.
- **A navigation wipes the globals.** `globalThis.__trends is not a function` after
  a `browser_navigate`, a timed-out call, or a fresh session means the tab object
  was replaced and the helper definitions went with it. Re-navigate to the Trends
  origin and redefine the helpers in one `browser_console` call, then continue.
  This is not an endpoint failure and does not need a diagnosis.
- **Read the right target, by id.** A `browser_console` read can land on the
  `chrome://newtab/` target and return a ~400-char body with none of your terms.
  When the body does not contain the terms you submitted, call `browser_cdp`
  method `Target.getTargets`, pick the page target whose `url` contains
  `trends.google.com`, and read
  `Runtime.evaluate` with `{expression: "document.body.innerText", returnByValue: true}`
  against that `targetId`. This is the reliable read path for Trends.
- **Two distinct "Oops! Something went wrong" states, told apart by body
  length.** If `innerText` returns the full table (thousands of chars,
  containing `Average` and the weekly rows), the page rendered before the
  overlay and the data is there. If it returns only the ~400-500 char header
  shell ending at "United States, Past 12 months", the batch genuinely did not
  render and the data is NOT in that DOM; reload the page (`Page.reload` with
  the tab's `targetId`) and wait 30-90 seconds before reading again. Trends
  frequently renders the full table on the retry, so an early read is what
  makes a recoverable batch look permanently lost.
- **Launching the automation Chrome from `terminal(background=true)` works on
  this host** when the port is not already bound: run chrome.exe with
  `--remote-debugging-port=9223 --user-data-dir="C:/Users/<user>/chrome-kw-profile"`
  (a path containing the literal `chrome-kw`, so the kill script can find it),
  then confirm with `curl -s --max-time 5 http://127.0.0.1:9223/json/version`
  before navigating. Do not start it with `nohup`/`&` inside a foreground call;
  the tool rejects shell-level background wrappers.

## Always close browser sessions when done

Vinny's standing rule (added Sep 2026): after any `browser_exec` work is
finished, close the browser/session instead of leaving it running. Closing
must be VERIFIED, not assumed. Do the close from the `terminal` tool using
the kill script (closes via browser_exec does NOT work — localhost targets
are blocked by the harness):

```bash
powershell -ExecutionPolicy Bypass -File "~/kill_chromekw.ps1"
sleep 3; curl -s --max-time 3 http://127.0.0.1:9223/json/version || echo "port 9223 dead"
```

The script kills every chrome-kw PID and prints `remaining: N`. Success
requires BOTH `remaining: 0` in the script output AND `port 9223 dead` from
the curl. One kill pass is NOT enough when multiple named `browser_exec`
sessions were used — each fresh named session (e.g. kw_b2, kw_b3) can spawn
extra Chrome children that survive a single Get-Process kill. **A pass can
also leave the port already dead while `remaining` is still nonzero** (helper
and crashpad children hold no port), so judge success on the FINAL pass: run
the script again until the last pass prints `remaining: 0`. The port probe
alone is not the whole condition. Session proof
(Sep 3 2026): a single kill left Chrome running and Vinny caught it. Never
report the browser closed without the verification output in hand.

**Close LAST: every browser read completes before the kill script runs.** Order
the phases so the close is the final browser step, not something done as soon as
the primary extraction lands. The reads that get forgotten are the secondary
ones: internal-link candidate verification, a source that needs a second read, a
related-query panel worth re-reading. A phase with an unknown target list does
not have to be a browser phase first — produce the targets with a non-browser
tool (a plain `curl` for a sitemap, a search index for a slug) and verify all of
them in the session that is already open. Finding a candidate after the close
costs a full relaunch (Chrome start plus helper redefinition) and invalidates
the close-then-verify sequence you already reported done. Check COMPLETENESS
before the kill, not just presence: a multi-item read phase (a related-query
pair, a sweep) is finished only when every requested item returned its own
record, so compare the returned keys against the requested items and re-read
whatever came back short. A phase that returned three of four records reads as
done in a skim and is discovered missing only after the port is dead.

## Notes

- The dedicated user-data-dir (`chrome-kw` here) is a persistent Chrome
  profile that already exists on the host — reuse it rather than creating a
  fresh one, so cookies/session state carry over. **The path MUST contain the
  literal token `chrome-kw`**: `kill_chromekw.ps1` matches that token against
  each Chrome process's command line, so a profile dir without it launches and
  browses fine but leaves the mandatory cleanup step with nothing to find, and
  the shutdown verification then fails with a live port. A path like
  `C:/Users/<user>/chrome-kw-profile` satisfies it. It is a SEPARATE profile from
  the user's everyday Chrome (`$LOCALAPPDATA/Google/Chrome/User Data`), so his
  existing site logins do not appear in it. Check the path exists before
  launching (`ls -d "$LOCALAPPDATA/chrome-kw"`); if it is missing, the harness
  Chrome will still start but as a brand-new profile.
- **A 429 from Trends is time-gated, not purely session-scoped.** A first 429 in
  a fresh named session often clears on the next fresh session; when TWO
  consecutive fresh sessions both return the 429 page, stop re-sessioning and
  wait 45 to 90 seconds before the next attempt. The block decays with elapsed
  time, and repeated retries inside the window keep it alive.
- **Put the cooldown INSIDE the browser_exec call, never between calls.**
  `time.sleep(60)` at the top of a batch call costs nothing but wall time; a
  separate call that only sleeps and retries costs a full round trip and is the
  difference between a run finishing in minutes and in tens of minutes. Same rule
  for a sequence of batches: loop the batches inside one call, writing each
  result to the run's JSON file as it lands, so the batch count does not set the
  tool-call count.
- **A Cloudflare `Just a moment...` interstitial is not a block until a second read says so.** The automation Chrome passes the check on its own after roughly 10 to 15 seconds: the first read returns title `Just a moment...` with body `Performing security verification` and only `cloudflare.com` links, and a re-read in the same tab after `time.sleep(12)` returns the real page with its title and anchors. Put the sleep and the second read inside the same `browser_exec` call, and only record a block when the interstitial survives that wait. This is distinct from the DataDome and Akamai pages, which do not clear on retry.
- This is a positive fix, not a "browser is broken" claim. The browser
  backend works once the automation Chrome is up.
- For Google Trends specifically, the manual-Chrome path is more reliable
  than scraping via Firecrawl (which returns HTTP 429 from Trends).
- **`browser_console` exists and is the primary driver when `browser_exec` is
  not in the toolset.** Earlier notes here called `browser_console` stale; that
  is wrong and the error wastes a session looking for a tool to replace it.
  `browser_console(expression=...)` evaluates JavaScript in the page and returns
  the value, which covers helper definition and API-driven reads in one call
  each. When `browser_exec` IS available its `js("document.body.innerText")`
  pattern still works for DOM reads; the accessibility snapshot
  (`page_info()`) often shows only the header, so read the body text instead.
- **Trends via the internal API beats DOM scraping when the Angular app will not
  hydrate (verified Sep 2026: 43 terms, 8 batches, zero 429s, zero waits).**  Symptom that sends you here: the page loads but
  `document.querySelectorAll('table').length` stays 0 and `innerText` is a
  ~470-char shell ending at "United States, Past 12 months", or you get the
  429 page, or the "Oops! Something went wrong" overlay. Do not poll, do not
  re-session, do not wait for a table that never renders. Instead:
  1. `new_tab("https://trends.google.com/trends/explore?geo=US&q=agent%20governance")`
     — the tab only needs to sit on the `trends.google.com` origin so the
     `fetch` calls carry the right cookies. It does not need to render.
  2. Define the helpers once per tab with `js(...)`, pasting
     `scripts/trends_api_extract.js` from this skill (`__trends` for the
     timeseries, `__related` for rising/top related queries).
  3. Read data with
     `js('(async () => JSON.stringify(await globalThis.__trends(["term one","term two"])))()')`,
     up to 5 terms per call. Each term returns `avg`, `peak`, `peakWeek`,
     `latest`, `first`.
  The `explore` endpoint returns a widget list; take the `TIMESERIES` widget's
  `request` plus `token` and post them to `widgetdata/multiline`.
  `RELATED_QUERIES` works the same way against `widgetdata/relatedsearches`,
  with one id trap: **the related-query widget id is SUFFIXED per term in a
  multi-term comparison** (`RELATED_QUERIES_0`, `_1`, `_2`), and is bare
  `RELATED_QUERIES` only for a single-term request. An exact-match `.find(x =>
  x.id === "RELATED_QUERIES")` therefore returns `no RELATED_QUERIES widget` on
  every batch of two or more terms while the widgets are all present, which
  reads as a broken endpoint. Match by prefix (`String(x.id).indexOf(
  "RELATED_QUERIES") === 0`) and iterate every match, pairing widget `i` with
  `terms[i]`; the widget does not carry its term name (`rankedList[].queryName`
  returns null), so the term comes from request ORDER, not the response. Keep
  related-query calls to TWO terms: three-term calls repeatedly returned
  `Runtime.evaluate timed out`, which leaves the helper undefined for the next
  call, while two-term calls returned on the first attempt.
  Both responses are JSON prefixed with a `)]}'` line followed by a comma and a
  newline. **Strip that with an anchored regex, not a literal string replace:**
  `.replace(")]}'", "")` leaves the trailing `,\n` in place and `JSON.parse`
  throws on every response, which looks like a broken endpoint when it is only
  a broken strip. Use
  `JSON.parse(String(s).replace(/^\)\]\}',?,?\s*/, ""))`.
  A ready-made helper pair (`__trends` for the timeseries, `__related` for
  rising/top related queries) lives in `scripts/trends_api_extract.js`; paste it
  into the tab with a single `js(...)` call, then drive it with
  `js('(async () => JSON.stringify(await globalThis.__trends(["term one","term two"])))()')`.
  **Batch failures return `[{error: "..."}]` rather than throwing.** Looping
  code that reads `x["term"]` from each entry prints a row of `None`s, which
  reads as a batch that ran and found nothing and invites recording zeros for
  live terms. Check for the `error` key before treating a batch as data, and
  re-run any batch that came back in that shape while its neighbours in the
  same session returned populated payloads.
- **`globalThis.__trends is not a function` means the tab was replaced, not that
  the helper is broken.** A fresh `browser_exec` session, a navigation, or a
  timed-out call gives you a new page object with none of the earlier globals.
  Re-navigate to any `trends.google.com/trends/explore?...` URL and redefine the
  helper in the SAME call, then continue. Same rule for `__related`.
- **A link-verification pass DESTROYS the Trends helpers, and only `related()`
  repairs itself.** `verify()` navigates the tab to the source and internal-link
  URLs, which moves it off the `trends.google.com` origin and wipes `__trends`
  and `__related` with it. The `related()` driver catches this, navigates back,
  redefines the helpers and retries once; the batch driver `run()` has no such
  recovery, so a `run()` issued after a `verify()`, or any other navigation, dies
  on its FIRST batch with `globalThis.__trends is not a function` and loses every
  batch it had not yet collected. Order the phases so all Trends work finishes
  before any link verification begins (`warm` -> `run` -> `related` -> `verify`),
  and when a Trends call genuinely has to follow a navigation, put the
  re-navigation and the `_helpers()` definition in the SAME `browser_exec` call
  ahead of it rather than assuming the prior call's globals survived.
- **A link that is refused has two distinct remedies, so classify before
  retrying: `Failed to fetch` is a cross-origin problem, a 429 page is a timeout
  problem.** A `fetch` that fails the moment the tab is off the Trends origin
  needs no cooldown at all: navigate back to a `trends.google.com` URL and
  redefine. A genuine 429 needs elapsed time, and re-running inside the window
  keeps the block alive. Spending a cooldown on the first case, or navigating on
  the second, both waste the window.
- See `references/trends-data-triage.md` for how to read Trends output once
  it is extracted: the header-only-vs-rate-limited-vs-error-overlay distinction,
  the rule that a 5-term batch failing twice needs shrinking to 3 terms rather
  than another fresh session, control-char stripping, the related-query pollution
  rules that disqualify a high-volume term from an H1 (including the
  the shared-consumer-product token collision and the non-AI-meaning collision, where
  a phrase coined for an AI mechanism is already owned by an unrelated established
  field), the relative-index caveat on the Average value AND the two ways it bites
  (a batch of four zeros inflating the survivor, and a single dominant anchor term
  crushing every batch-mate to a floor), the rule for reporting dual readings with
 the shape-versus-magnitude split AND the rule that a confirmation reading
 confirms magnitude only, never intent, so a term with an identical number in
 both reads plus an empty cluster on both lists is a body-use-only verdict,
 the empty-block verdict split between coined
  and plain-English terms, the partly-used-coinage case for a phrase with one or
  two lone spikes, the peak-week-before-launch inherited-meaning collision, the
  handling rule for when the article's own core metric returns an empty
  related-query block, the parsing anchors for the term-list and Average rows, the
  failed-batch-versus-zero-volume payload check AND the three related-query payload
  shapes (populated, genuine empty, and a missing key that must be re-read before
  the browser closes), the all-zero batch being the one zero-heavy shape with no
  inflation artifact, and the decay / news-entity /
  Breakout-query rules for writing recommendations.
- **Design batches so no mega-term shares a URL with technical terms.** A
  commodity, financial, or consumer term one order of magnitude above the rest
  rescales every batch-mate to a 1-to-3 flat line and makes healthy terms look
  dead. Keep an anchor term in its own batch or in a deliberate calibration
  batch, and when one has already contaminated a batch, re-run those terms
  before reading anything into their numbers.
- **One fresh named session per batch is the DOM-scraping design; the internal-API path does not need it.** When you read Trends through `__trends` / `__related`, ONE session carries ten or more batches with no rate-limiting and no waits — do not burn a named session per batch. The per-batch-session rule below applies when the Angular app itself must render and the daemon is throttling the table, which the API path bypasses entirely. What the API path DOES need is one **related-query confirmation pass** on the two or three top candidates: re-run just those terms to read their rising-query blocks before promoting any of them to a title or H1. In some runs `print(js(...))` DID return values in `output`, so the output-dropping issue is intermittent, not permanent — the write-to-file fallback remains the reliable pattern.
- **Header-only `innerText` on the first read is NOT a failed load (verified Sep 2026, six consecutive batches):** after `wait_for_load()`, the first `js("document.body.innerText")` can return only the nav and query-name list (a few hundred chars, ending at "United States, Past 12 months") because the Average row and weekly table render a few seconds later. Poll for the literal string `Average` (or Trends' `enough data` banner, which is the correct signal for an all-coined batch) in a short loop with `time.sleep(2)` before writing the file. Do not tear down the session or start a new one on a header-only read; it is a timing artifact, not a rate-limit. Distinguish the two: a rate-limited page has NO term names and is ~130 chars, while a header-only render lists every query you submitted.
- **Google Trends rate-limiting between batches (verified Aug 2026):** After batch 1 renders fine, batch 2/3 may load header + query names but never populate the Interest-over-time table or the Average row. `document.body.innerText` shows only top nav + term list, ending after "United States, Past 12 months". Do NOT keep retrying in the same session with longer sleeps — it stays empty after 10+ attempts. **The fix that works:** open a FRESH named session per batch (e.g. `session='kw_<article>_b2'`, then `_b3`). A fresh session returns the full table on first attempt after ~10s. The browser instance/daemon itself is rate-limiting, so new named sessions bypass it. Design batches so each can run in its own fresh session if the previous batch rate-limits.
- **The kill script prints Stop-Process 'Cannot find a process' errors for
  PIDs that already exited and still reports `remaining: 0` — this is a
  SUCCESS, not a failure.** The script enumerates chrome-kw PIDs and kills
  them in a loop; children that die mid-loop (or were reaped by their parent)
  throw and print a red error block. Judge the result ONLY by the final
  `remaining: N` line and the curl probe, never by the presence of those
  errors in the output. Reporting a failed shutdown because of benign
  Stop-Process noise wastes a cycle; reporting success without the
  `remaining: 0` line and `port 9223 dead` is the real violation.
- **A scripted `403`/`429` on a link under verification is NOT proof the link is dead; the browser read is the proof (verified Sep 2026).** Paywalled and WAF-fronted publishers (Axios, Bloomberg, WSJ and similar) refuse `urllib`/`curl` requests while serving the exact article fine to a real browser. When a bulk link-verification sweep flags a source with 403/429, do NOT drop or replace it on that evidence. Open it in the browser, read `document.title` plus the first few hundred characters of `document.body.innerText`, and confirm it resolves to the correct headline and byline. If it does, keep the link and record the caveat inline at that entry ("returns HTTP 403 to scripted clients; confirmed in a real browser on <date>, resolves to the correct article with headline, byline, and body intact — the link is valid for human readers"). The failure mode this rule prevents: reporting a perfectly good source as broken, or swapping it for a worse one, because a scripted client was refused.
- **When the browser is refused too, the link is UNVERIFIED — say exactly that, and pair it with a verified alternative (verified Sep 2026).** Hardened sites block the automation browser as well as scripted clients: a DataDome interstitial (`Iframe "DataDome Device Check"`, `Verifying the device...`, title `wsj.com`) and an Akamai `Access Denied` page are the two shapes seen, and neither is bypassable by retrying. Do not drop the source and do not call it verified. Record the caveat at that entry (name the block, state that headline/URL/date were confirmed through the search index rather than a page read, and that the link is valid for human readers), and when another outlet covers the same story, list its machine-verified URL directly beneath as the alternative. Distinguishing the two states matters: `HTTP 200` plus the right headline is verified, a block page is unverified, and an unverified real source reported as verified is the error the user will catch.
- **To find a site's real story URLs when the outlet blocks every automated read, search its site-scoped query on DuckDuckGo Lite.** `curl`/scrapling against `https://lite.duckduckgo.com/lite/?q=site%3A<domain>+<topic words>` returns the indexed URLs as plain text, which is enough to recover an exact article slug the outlet will not serve you. This is how a blocked newsroom's story URL gets resolved for a citation, and it also surfaces adjacent coverage on the same topic for a backlink section.

- See `references/site-link-verification.md` for the link-verification sweep:
  what does and does not count as a verified URL, the rule that a thin main
  sitemap usually means a separate content subdomain (PhantomByte articles live
  at `articles.phantom-byte.com/sitemap.xml`, not on the main domain's sitemap),
  the slug-triage heuristics, the requirement to read back each candidate
  page's `<title>` before recommending it, the host-form and PDF-header
  retry rules, the JavaScript-shell publisher that answers HTTP 200 on every
  path and the sibling-anchor and Wayback `<title>` reads that verify its
  specific story, and the four link jobs that run when auditing a DRAFT's own source
  list: resolving a bare-domain or truncated-slug citation to its story URL,
  recovering a blocked outlet's story URLs through a site-scoped DuckDuckGo Lite
  search when the outlet serves neither scripted clients nor the automation
  browser (and, when that thin index returns nothing, driving a full search
  engine in the automation browser and decoding the destination URL out of the
  `bing.com/ck/a?u=a1<base64>` redirect wrapper), resolving an entry that carries NO URL at all (or names an internal
  pipeline as a public source), and flagging a live URL whose on-page headline no
  longer matches the headline the draft quotes.
- **`browser_exec` blocks private/internal URLs.** Any code path that makes
  the harness fetch a localhost/127.x address (curl to the CDP port,
  `os.system` hitting 127.0.0.1, navigating to an internal URL) fails with
  "Blocked: URL targets a private or internal address". Do localhost probes
  and process shutdown from the `terminal` tool, not from inside browser_exec.
- **`browser_exec` may return `"output": null` / empty even when the code ran
  (verified on this host 2026-08).** The tab navigates and files get written,
  but printed/`js()` values are dropped from the `output` field. So
  `print(js("document.body.innerText"))` is NOT a reliable way to get page text
  back. **Reliable pattern:** write the extracted DOM text to a known absolute
  file path inside the code, then read that file back with `execute_code` /
  `read_file`. Use a real path in a controlled dir (e.g.
  `C:\Users\<user>\AppData\Local\hermes\cache\documents\`), NOT the
  `browser_exec` workspace dir (its paths can be transient/unstable). When
  regex-parsing Google Trends weekly rows, strip the Unicode control chars
  `\u202a`/`\u202c` from `document.body.innerText` first or parsing breaks.
