# Source Extraction Recipes

Concrete, low-overhead ways to pull the authoritative text for each source type a
brief tends to name. None of these need a browser session.

## Preprint abstract pages (arXiv and similar)

Fetch the `/abs/<id>` form directly. The abstract page is the authority: it
carries the full abstract, the real title, the author list, and the submission
date in one document. Select the title element and the abstract blockquote and
you have every number the paper advertises, LaTeX escapes included (`\%` renders
in the raw text as a backslash-percent pair, so strip it before quoting a
percentage).

Do not go through a search results page. Search result pages truncate the
abstract behind an expansion control that is fragile to drive, while `/abs/`
renders everything immediately. Fall back to the PDF or HTML version only when
the abstract genuinely lacks the figure you need.

## Forum and listing pages

A submission listing (a Hacker News profile or search view, a subreddit listing)
is the cheapest confirmation that a product or story exists, and it carries the
submitted title, the posting handle, and a relative timestamp. That is enough to
justify a SOURCES entry when the product's own site is a client-rendered shell
that returns little extractable text.

## Product and vendor sites

Many marketing pages are client-rendered, so a raw fetch returns a title and
navigation with no body. When that happens, confirm the entity through its
submission listing or archived announcement, and cite the page you could
actually read. Do not present a title you scraped off a near-empty page as if
you had read its contents.

## Self-hosted article archives

Article slugs often live on a subdomain separate from the marketing site, and
the marketing site's `sitemap.xml` frequently lists only a handful of top-level
pages. Treat the stub as an index of nothing. Probe the article path itself, and
probe it in both forms: an extensionless path commonly 404s while the same path
with `.html` is the live canonical URL.

## Status probing without a browser

A redirect-aware fetch with a status code is the whole tool you need to decide
whether a link is live. Follow redirects, because a bare host often answers one
form of the URL with a redirect and a no-follow fetch reports that redirect
instead of the document. Read the final status and treat a 200 as proof the page
exists; that proof is what belongs in the SOURCES section rather than a note
somebody else wrote earlier.
