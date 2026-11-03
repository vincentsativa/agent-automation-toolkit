# Fetching Pages with Scrapling: Reliable Accessors and CLI Reality

Depth for the scrapling fetch path. See the `scrapling` skill for the full API surface (packaged with the environment; this file is the portable subset).

## Which accessor holds the page

| Accessor | What it returns | When it is empty |
|---|---|---|
| `.html_content` | full document text | almost never on a 200 |
| `.body` | raw bytes, not a string | only on a real failure |
| `.text` | frequently empty | on plenty of clean 200s |
| `.get_all_text(strip=True)` | the words, callable on the response itself | only if the page genuinely has no text |

The failure this causes: a `page.text[:500]` check prints nothing, the fetch reads as blank, and the next step is a pointless retry through a different tool. Read `.html_content` for markup and `get_all_text()` for words, then save both to disk and read the files in slices.

```python
from scrapling.fetchers import Fetcher
p = Fetcher().get("https://example.com/page")
print(p.status, len(str(p.html_content)))
open("page.html", "w").write(str(p.html_content))
open("page.txt", "w").write(p.get_all_text(strip=True) or "")
```

## CLI surface

`scrapling --help` lists four subcommands: `extract`, `install`, `mcp`, `shell`. There is no `fetch`. `scrapling fetch <url>` exits 2 with `No such command 'fetch'` and writes a zero-byte output file, which reads like a blank page rather than a usage error. Use the Python fetchers, or read `scrapling extract --help` before scripting the CLI.

## Fetcher before StealthyFetcher

For a page that is not bot-walled, `Fetcher` is faster and more reliable than a browser fetch, and it avoids the browser-fetch timeout failure mode entirely. A `StealthyFetcher` navigation can raise `Page.goto: Timeout` with a value that looked reasonable, and each attempt costs a retry cycle. Escalate to stealth on an actual refusal (403, 429, CAPTCHA), not in advance.

A timeout passed to `StealthyFetcher.fetch()` is in milliseconds, so `timeout=90` means 90ms and fails immediately. Use `timeout=40000` for real navigation.

## Truncated URL slugs need a trailing slash

Search results and outline files routinely carry a news slug cut off mid-word (a headline slug that ends in the middle of a token). That URL returns 301 and then resolves only after a redirect retry cycle, which costs an extra navigation per page. Append a trailing slash before fetching: the same slug with `/` resolves in one navigation. If a URL looks truncated, add the slash first rather than paying the redirect.

## `network_idle=True` costs about a minute per page on news sites

On news and blog pages with heavy analytics and ad scripts, `network_idle=True` waits for the network to settle and takes roughly 60 to 80 seconds per URL. That is fine for one page and ruinous for six. Use `network_idle=True` only when the content is genuinely JS-rendered; for ordinary article pages a plain fetch returns the text, and `p.css("p::text").getall()` gives you the article body without the nav, cookie banner, and comment sludge that `get_all_text()` includes.

```python
paras = p.css("p::text").getall()
body = "\n".join(x.strip() for x in paras if len(x.strip()) > 60)
open("article.txt", "w").write(body)
```

## Working directory

Never run a fetch script from a directory containing a file named after a stdlib module you import (`inspect.py`, `email.py`, `json.py`). The shadowing file breaks the import and the traceback names some other package, sending you after a cause that does not exist. `mktemp -d` a scratch directory and run from there.
