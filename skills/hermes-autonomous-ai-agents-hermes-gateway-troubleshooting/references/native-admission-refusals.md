# Native admission refusals

Depth for `invalid_params: <clause>` warnings from `gateway/session_envelope.py`. The gate refuses an inbound event before the agent sees it, logs one line, and answers the chat with a warning. The turn is not queued, so the content must be resent.

## Clause table

`_media_clause()` evaluates in this order and returns the first failure, so a control case can trip an earlier clause than the one being fixed.

| Clause | Meaning |
|---|---|
| `media_urls` | not a list of `str` |
| `media_types` | not a list of `str` |
| `media_text_inlined` | not a list, or an element that is neither `None` nor a real `bool` |
| `media_types_length` | length is neither `0` nor `len(media_urls)` |
| `media_text_inlined_length` | length is neither `0` nor `len(media_urls)` |

Other clauses in `_event_clause()` name structural problems instead: `source`, `text`, `message_type`, `command`, `internal`, `metadata`, `prompt_response`, relay and profile-route provenance mismatches. Those are not list-alignment bugs and must not be "fixed" by padding anything.

## Merge lanes to audit together

Every one of these concatenates media, so each needs the same alignment treatment:

- `gateway/platforms/base.py` `merge_pending_message_event()`: the general pending-event merger with photo bursts, text follow-ups, and caption merging.
- `gateway/platforms/base.py` `_enqueue_text_event()`: the text-batch lane, which extends media when a buffered text chunk carries an attachment.
- `plugins/platforms/telegram/adapter.py` `_merge_into_pending()`: the album and photo-burst merger behind `_queue_media_group_event()` and `_enqueue_photo_event()`.

An adapter that sets `event.media_urls = [path]` also has to set the flag, and a lane that REPLACES the URLs must reset the flags or they end up longer than the list.

## Recovering what was dropped

The adapter logs the cache path for every attachment immediately before the refusal line:

```bash
sed -n '/<timestamp of refusal>/' ...   # or grep the surrounding 20 lines of the refusal
```

Those files still exist under `~/.hermes/cache/documents/`, `documents/`, `audio/`, `images/`. Quote the paths to the user so the send can be repeated or the files read directly.

## Verifying a fix here

Drive the real merger and the real `_media_clause()` in one script: merge N events, assert the clause is `None`, then hand it the pre-fix shape and assert it still returns the length clause. That pair is the difference between a test and a decoration. The install-tree recipe lives in `hermes-install-patch-durability/references/verify-a-live-patch.md`.
