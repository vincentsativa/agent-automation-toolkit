# Getting Text Out of a Publisher Page, and His Voice Out of His Site

Depth for the Web Research step. Load when a scrape comes back looking like menu links, when the outlet that broke the story will not serve the fetch, or when the instruction is to match his voice from the live site.

## Search engines are the failure point, discovery is not

`web_search` is for discovery only. Scrape the publisher URL it returns with scrapling and read the actual text.

- DuckDuckGo HTML serves a bot challenge, Google serves a verification interstitial, Mojeek returns 403, and Bing returns unrelated or generic results. Do not burn calls re-trying search engines through the fetcher; the search tool already does that job.
- Disqualify SEO counter and character-counter pages on sight. No named human author means no citation, however confident the number looks.

## When the publisher is paywalled, go to the primary source's own page

A paper whose `p` nodes return one paragraph is paywalled, and syndication desks often answer 403. The organization that published the study usually has its own report page and press release, and those repeat every figure in the source's own words, which is also the correct entity to attribute and the correct date to quote.

- Reach for the report page first when the story is a survey, a benchmark or a funding round. Trade coverage then confirms the figure instead of carrying it alone.
- Quote the publisher's own sentence for a share or a split rather than the aggregator's paraphrase, and check the release date there: a report can be dated a day earlier at the source than in the aggregation.

## A publisher URL from the data file 404s

A link aggregated into a data file is a lead, and its slug can be stale or truncated even when the story is live. Do not conclude the outlet did not publish it, and do not fall back to quoting the aggregation.

- Read the 404 body. Publisher 404 pages carry a most-read or favourites module built from real URLs, and the headline you were chasing is often sitting in it with the working slug. `p.css("a")`, then match on the words of the headline rather than on the article id.
- The stable half of the URL is the numeric article id plus the site's section path. Anything after that is a slug the outlet rewrites freely, so a link whose id resolves can still 404 until the current slug is found.
- Try the id alone (`/tech/big-tech/article/3373757/`) before giving up: the redirect or the 404 module usually hands back the live address.
- Once open, grep the body for the exact figures (`"92 trillion"`) and read the sentence around them, because the date and the attribution you need usually sit in the same paragraph.

## Article body off a publisher page

`Fetcher.get(url).get_all_text()` on a news site returns the article wrapped in navigation, topic chips, newsletter promos and footer link farms, so the paragraph you need can sit past the first few thousand characters of junk. Do not conclude the page is empty or the fetch failed when the head of the text looks like menu links.

- Extract paragraphs directly and drop the short ones: `p.css("p")` then keep only nodes whose `get_all_text().strip()` is longer than about 40 characters, joined with newlines. Nav and promo links are almost always shorter than a real sentence, so the length filter removes them without a selector per site.
- This works unchanged on Business Insider, TechCrunch and MIT Technology Review; expect each publisher to differ in chrome, not in structure, so reach for the paragraph filter before writing per site selectors.
- arXiv `/abs/` pages are the exception: the abstract lives in `blockquote.abstract`, and the `p` filter returns footer boilerplate. Use `page.css("blockquote.abstract")[0].get_all_text().strip()`.
- Print one URL per clearly labelled block, and fetch the batch in a loop that prints as it goes. A single `print(t[:4500])` per URL inside a loop means the last page scrolls the earlier ones out of view in the tool result, which then reads as a fetch failure for the pages that worked.
- The byline, the date and the author's name sit in that extracted text; take them from there for the report rather than reconstructing attribution from memory.
- Grep the fetched text for the few figures the post will use (`grep -Ei "89|72.8|1.5 percent"`) instead of reading every paragraph. A paywalled page can return one real paragraph, so a thin result is a page limit, not a failed fetch.

## Capturing his voice from the live site

When the instruction is to match his voice, read the site rather than working from the style skill alone. `https://articles.phantom-byte.com/sitemap.xml` returns the whole archive as dated URLs, newest first, so pick two recent notes from the same category as the topic and read them whole.

- The article body begins after the `// field note NNN` marker in `get_all_text()`. Everything before it is navigation, archive lists and promo blocks, so slice from that marker and print the first few thousand characters of each note.
- Read two notes, not one. The first gives the rhythm, the second confirms it is the house style and not one piece's mood.
- Read the opening paragraphs and the section transitions. That is where the short declarative sentences, the one line definition and the blunt thesis live.
- Do not copy site furniture into the post: the promo blocks, the article index, the share row and the field note number are page chrome, not voice.
