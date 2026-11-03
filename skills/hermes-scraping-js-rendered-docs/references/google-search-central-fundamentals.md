# Google Search Fundamentals, distilled reference (worked example)

Fetched the three Search Central fundamentals pages via StealthyFetcher + `get_all_text` directly on the response. This is the deliverable produced and is kept as a condensed knowledge bank.

## How Google Search Works (3 stages; no payment for crawling/ranking/position)

1. **Crawling**, Googlebot discovers URLs via links, sitemaps, and prior visits. Renders JS with recent Chrome. Throttles itself (slows on HTTP 500s). Does not crawl everything (robots.txt, login-gated pages blocked).
2. **Indexing**, analyzes text, `<title>`, `alt`, images, video. Picks a **canonical** per cluster of similar pages. Collects signals (language, country, usability). Not guaranteed, fails on low-quality content, `noindex` robots meta, or hard-to-index design.
3. **Serving**, matches query against index, ranks programmatically using hundreds of relevance signals (location, language, device). Search features vary by query type.

A page can be indexed yet absent from results if content is irrelevant, quality is low, or `robots meta` prevents serving.

## SEO Starter Guide essentials

- **Timeline:** changes take hours to months; wait a few weeks before judging; iterate.
- **Discovery:** verify indexing with `site:yourdomain.com`; earn links; submit sitemap (optional, CMS often auto); ensure CSS/JS/images not blocked; use URL Inspection Tool.
- **Organization:** descriptive URLs (words become breadcrumbs); group similar pages in directories (Google learns per-directory change frequency); reduce duplicate content via 301 or `rel="canonical"` (one URL per piece of content).
- **Content quality (biggest ranking driver):** easy-to-read, unique, up-to-date, helpful/people-first.
- **Keywords:** anticipate reader terminology variations ("charcuterie" vs "cheese board").
- **Links:** descriptive anchor text; `nofollow` untrusted outbound and ALL user-generated links.
- **Search appearance:** title links (unique, concise, accurate, sourced from `<title>` + headings); snippets (from page content or meta description, short, unique, relevant points).
- **Images/video:** high-quality images near relevant text; descriptive alt text; video on standalone page near relevant text with descriptive title/description.
- **Don't focus on:** meta keywords, keyword stuffing, domain/URL keywords, content length, subdomain-vs-subdir, PageRank alone, duplicate-content "penalty", heading order/count, "E-E-A-T is a ranking factor" (it isn't).

## Get Started / Technical SEO

- **robots.txt:** block crawling (dupes, icons/logos), NOT indexing (use noindex/login for that).
- **Sitemaps:** signal important pages, prioritize crawling, esp. for non-textual content and fast-changing sites.
- **Migrations:** 301 permanent, 302 temporary, true 404 for removed (not soft 404), custom 404 page; tell Google about whole-site moves.
- **hreflang** for multilingual/multiregional pages.
- **Crawl budget:** only matters for very large sites (hundreds of millions of pages).
- **Crawlable links:** `nofollow` paid/login/untrusted; next/prev for multi-page articles; paginated version for infinite-scroll; block state-changing URLs via robots.txt.
- **UX is a ranking factor:** HTTPS, fast pages (Core Web Vitals / PageSpeed Insights), mobile-friendly (mobile crawler is default).
- **Structured data** for rich results; key info in text not graphics.
- **Content-specific:** News sitemap for news sites; adult tagging for SafeSearch; child-directed tagging for COPPA.
- **Search Console** reports for monitoring: URL Inspection, Page Indexing, Core Web Vitals.
