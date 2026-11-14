# Primary-Source Verification for Fact-Checking

When fact-checking claims against named sources during article writing, fetch the primary page directly and read it. Abstracts and blog posts render as plain text with no expansion step.

## Scrapling First
Per the constitution, web retrieval starts with scrapling via `terminal()`, not the browser. One call gets the full text of a Hugging Face blog post, an arXiv abstract page, or a named tech-journalism article:

```python
from scrapling.fetchers import Fetcher
r = Fetcher.get('https://arxiv.org/abs/<id>', timeout=60)
t = r.get_all_text()
print(t[:6000])
```

`get_all_text()` returns the whole page, so you can locate a named section by string search inside Python instead of scrolling a rendered page. Fall back to the browser only when scrapling returns nothing usable.

**Check `get_all_text()`, never `page.text`, before calling a fetch failed.** A Hugging Face blog post can return status 200 with `len(page.text) == 0` and still hold the entire 21,000-character article in `get_all_text()` (verified against the Microsoft/Hugging Face ThinkingBox post). Score the fetch on the parsed text, and pull from `get_all_text()` or `markdown()`. A zero-length `page.text` is a scrapling quirk, not a block and not a dead URL.

**Confirm which interpreter has scrapling before writing the fetch script.** Hermes's default `python3` is its bundled 3.14 build, while scrapling is installed under `~/.local/lib/python3.12/site-packages`, so a bare `python3 script.py` fails with `ModuleNotFoundError: No module named 'scrapling'` even though the package is right there. Confirm the interpreter once, then use that explicit path for every fetch in the run:

```bash
/usr/bin/python3 -c "import scrapling; print(scrapling.__version__)"
```

If a fetch script still cannot import it, add the packages directory to the path at the top of the script before importing: `sys.path.insert(0, '~/.local/lib/python3.12/site-packages')`. Do not treat an import error as a block and do not fall back to curl; it is the interpreter, not the site.

**Never run `scrapling extract get` when you want the text.** That CLI subcommand converts through scrapling's markdown path and dies with `ModuleNotFoundError: No module named 'markdownify'`, writing a 0-byte file while the log still shows `Fetched (200)` and the shell exits 0. Use the Python `Fetcher` plus `page.get_all_text()`, which needs no markdown dependency. If you use a CLI subcommand for any other reason, verify the output file is non-empty, never trust the exit code alone.

## arXiv: Find the Paper Through the API, Not a Search Engine

When an outline names a benchmark or paper without an arXiv ID, a general web search returns SEO mirrors, blog summaries, and AI content farms ahead of the paper itself, and citing one of those violates the credible-sources rule. Query the API instead, which returns the canonical link, exact title, authors, and submission date in one call:

```python
from scrapling.fetchers import Fetcher
p = Fetcher().get('http://export.arxiv.org/api/query?search_query=ti:%22TALENT%22+AND+abs:%22tabular%22&max_results=5', timeout=40)
print(p.get_all_text())
```

The response is plain text you can read directly; each hit carries `http://arxiv.org/abs/<id>`, the title, and the date, which is everything a SOURCES line needs. Use the paper's own `/abs/` page for the finding and the API only to discover the paper's name and ID. Note that keyword searches over arXiv titles surface near-miss papers (a title containing the query word but on an unrelated topic), so confirm the abstract matches the outline's description before citing.

## Hugging Face Repo Names: Take Them From the Post, Never Guess

Model repo names are chosen by the publisher and variant suffixes are invented as often as they are real. `nvidia/Kumo-Tabular` resolves while a plausible `nvidia/Kumo-Tabular-215M` variant returns 401. Fetch the vendor's announcement post first and lift the weights link, the library link, and the license link out of that text verbatim. Treat a 401 on a Hugging Face URL as evidence the guess is wrong rather than as a gated model, and never cite a URL you constructed yourself.

## Hugging Face Blog URLs: The Org Slug Is Case-Sensitive, Fix It With One Title Search

An outline's `huggingface.co/blog/<org>/<slug>` path 404s when the org segment is wrong, and the segment is neither lowercase nor predictable: `huggingface.co/blog/servicenow/autosynthdata` is dead while `huggingface.co/blog/ServiceNow-AI/autosynthdata` is live. Do not permute the slug or try casing variants by hand. Run ONE `web_search` on the exact post title, take the canonical `huggingface.co/blog/<Org>/<slug>` URL from the top hit, then fetch that URL to verify the numbers before citing. The daily data files (TensorFeed, blogwatcher) usually carry the correct title too, which is enough for the search that surfaces the real link.

## Vendor Newsroom Slugs: Extract, Do Not Guess

Vendor press-release slugs are long and non-obvious, so a guessed path 404s while the release exists. Do not burn attempts on guessed slugs and do not fall back to an aggregator for a vendor claim. Fetch the newsroom listing page and pull the real hrefs out of its HTML:

```python
import re
from scrapling.fetchers import Fetcher
f = Fetcher()
p = f.get('https://www.marvell.com/company/newsroom.html', follow_redirects=True)
for l in sorted(set(re.findall(r'href="([^"]*newsroom[^"]*)"', p.html_content))):
    print(l)
```

The listing page carries the headline, the date, and the canonical slug side by side, so you can match the release by headline and fetch its exact URL. The vendor's own release is also worth reading in full rather than stopping at the outline's summary: it usually carries product specifics the outline omitted (named DSPs, a co-packaged optics platform at a stated Tbps figure), which are exactly the citable details an authority piece wants.

## Read the Whole Primary, Not Just the Headline Stat
Pull enough of the source to cover the mechanics the outline references. A post's later sections usually carry the exact cost profile, the worked examples, and the per-difficulty breakdown the outline assumed you already knew. Fetching only the first screen leaves the mechanism sections of the article thin.

## Workflow

1. **Fetch the abstract or article page directly**
   `https://arxiv.org/abs/[id]` for papers. Do not go through a search result page first; the abstract page renders the full text immediately, including the author block and submission history you can cite from.

2. **Confirm the source is the one named in the outline**
   Verify title, ID, authors, and date match.

   A URL that resolves to a real page is not a verified source. Open it and confirm the page actually contains the claim. An outline can pair a true claim with a real URL for an unrelated article, and a 200 status hides it. When the named page does not carry the claim, do not drop the claim and do not cite that page: trace the claim to the true primary source and cite that instead. Worked shape: an outline sourced "AI data centers could reach one percent of global electricity demand by 2030" to a Nature link that loaded fine but was a story about AI drug discovery. The claim itself was real and lived in the IEA's Energy and AI report, which supplied the precise figures (about 1.5 percent of world electricity in 2024, around 415 TWh, projecting roughly 945 TWh by 2030). The fix is to re-source the claim, then update the SOURCES entry so the citation matches the page that actually carries the number. Report the substitution to Vinny in the delivery note; he asked for accuracy and wants to see it was caught.

3. **Verify key claims against the abstract**
   - Check specific numbers (variance, overhead reduction, call reduction, evidence rates)
   - Compare outline claims with the abstract's own wording, including any scope caveat the authors state

4. **Handle discrepancies**
   - If a claim is not in the abstract, open the PDF or HTML version
   - If unreachable after 2-3 attempts, mark unverifiable and omit

5. **Respect the outline's traceability list**
   Verify against the source and against the list of permitted numbers. Extra true figures from the source still do not go in the article.

## When the Browser Is Still the Right Tool

A rendered search page, a JS-only page, or a site that blocks plain fetches. For bulk search results and batch metadata, the arXiv API (`curl export.arxiv.org`) beats both.

## Verified arXiv IDs from Previous Sessions
- Phionyx: 2607.18246
- SAAG: 2607.18245
- BatchDAG: 2607.18241
- CPSAINT: 2607.18243

## Checklist Before Using Claims in an Article
- [ ] Paper exists at expected arXiv ID
- [ ] Title matches the source that cited it
- [ ] Authors are consistent
- [ ] Submitted date is reasonable
- [ ] Key numbers appear in abstract or full paper
- [ ] No contradictory claims in the abstract
