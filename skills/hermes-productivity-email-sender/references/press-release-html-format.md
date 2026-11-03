# Press Release HTML Format for PR Log / Distribution

## When to use HTML instead of plain text

When Vinny says "this is a FREE prlog campaign" or mentions any press release distribution platform (PR Log, PRWeb, Newswire, EIN Presswire, 24-7 Press Release, etc.), the attachment **must be HTML**, not `.txt`.

Plain text files cannot contain clickable hyperlinks. Press release distribution platforms ingest HTML and render the links as live URLs. A `.txt` file with a URL in parentheses is not a clickable link, it's dead text.

## The correction (July 14, 2026)

Session proof: Vinny said "make (Daily field notes: https://...) the clickable link. this is a FREE prlog campaign." I sent a `.txt` file. He replied "that is not what the instructions said to do" and made me redo it as HTML.

## HTML template for press release emails

```html
<!DOCTYPE html>
<html>
<body style="font-family: Arial, sans-serif; max-width: 600px; line-height: 1.5;">

<p><strong>HEADLINE</strong></p>

<p>Body text with <a href="https://example.com">clickable links</a> inline.</p>

<p><strong>Links:</strong><br>
Description: <a href="https://example.com">https://example.com</a></p>

<p><strong>About:</strong> About text.</p>

<p><strong>Media Contact:</strong><br>
Name<br>
email@example.com</p>

</body>
</html>
```

## Rules

1. **Every URL in the body must be an `<a href>` tag.** Plain text URLs in parentheses are not acceptable for PR Log.
2. **Inline links**, when Vinny says "make (X: URL) the clickable link," the anchor text is the label (e.g. "Daily field notes"), not the raw URL.
3. **Link list at bottom**, also include a separate link list section with full clickable URLs for every property.
4. **Shorten by X%**, count the original body text chars (excluding the instruction line), count the new HTML body text (strip tags, collapse whitespace), verify the reduction is at or above the target. If under, cut more.
5. **Attach the .html file** via SMTP attachment. Do not paste HTML into the email body, attach it as a file.
