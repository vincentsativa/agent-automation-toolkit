# Social Posts Are a Required Deliverable

Session proof (Aug 18, 2026): a prior session finished the article body but left the
X post, Pinterest title/description, and keywords unfinished (stuck trimming the X post
char count). Vinny had to demand them: "you better make sure it has the social media
posts and they are good."

## Rule
The X post, Pinterest title/description, and keywords are NOT optional extras. They are
part of the article deliverable and MUST be present in the emailed file, verified for
char counts, before you send. Do not email the article without the social section.

## Write the X post in one pass
Target ~180 chars (under the 190 limit) on the first attempt. Do NOT iterate on trims —
the trim loop is what stalled the prior session. A strong pattern that fits under 190:

> Your GPU scheduler is leaving 33 points of utilization on the table. Same hardware,
> same workloads, only the allocation order changed. No new GPUs. Is your scheduler the
> bottleneck?  (181 chars)

Structure: hook with the concrete number, "same hardware, same workloads, only the
allocation order changed," then a reply-hook question ("Is your scheduler the
bottleneck?"). This satisfies the x-algorithm-post-optimization signals: hook earns the
second line (dwell), ends on a reply question (reply × 15 mutual boost), self-contained
for a stranger (retweet/quote), uses the topic's actual vocabulary (out-of-network
retrieval).

## Verify all three char ranges before sending
- X post: ≤ 190 chars
- Pinterest title: 60-80 chars
- Pinterest description: 150-300 chars

Check with a quick `len()` in Python before appending to the file and emailing.
