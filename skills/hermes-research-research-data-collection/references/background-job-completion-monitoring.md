# Monitoring a Long Collection Run to Completion

The job shape: a collection script runs for tens of minutes over hundreds or thousands
of inputs, the user says "just let me know when it's done," and the deliverable is ONE
completion notice carrying the final count. Interim progress reports are not wanted.

## 1. Arm a watcher, do not poll by hand

Run the watcher loop AS the background command:

```
terminal(background=true, notify=true, timeout=600,
  command="/tmp/hermes-watch-XXXX/watch.sh")
```

Never write the watcher as `nohup bash -c '...' &` inside a `background=true` call. The
backgrounded shell returns immediately, so the completion notification fires for the
shell that launched the watcher, not for the job. You get a "process completed" event
seconds in and the real finish never notifies.

Do not sit in a foreground sleep loop sampling the row count in your own turn either:
it burns the turn budget and still misses the real end of the job.

## 2. Poll by process NAME, never a captured PID

```bash
alive=$(pgrep -f "find_contacts.py" | wc -l)
```

A captured PID is fragile in exactly the way that produces a false completion. A long
runner relaunched with a different shape (the same script split across N parallel part
files) has a new parent PID, so `kill -0 <old_pid>` returns false while the work is
still going and the watcher announces done with a fraction of the rows written.
Declare completion only when the live process count is 0.

`ps aux | grep <script>` alongside the count tells you whether the run changed shape
(one process became four), which is worth knowing before you interpret progress.

## 3. Use the output file as the progress signal, and sum every output file

A collector that appends and flushes row by row makes the output file line count a free
progress meter:

```bash
rows=0
for f in "$OUT"/contacts_2000_part*.csv "$OUT"/contacts_2000.csv; do
  [ -f "$f" ] && rows=$((rows + $(wc -l < "$f")))
Done
```

Sum the glob, not one hardcoded filename. A run that splits into `part1.csv`,
`part2.csv`, ... leaves the original single-file path frozen at a stale count, and a
final total read from it will be wrong.

## 4. Give the watcher its own stall contingency

Every watcher gets a no-progress cap before it launches, per the failure-contingency
rule. Sample the progress signal each cycle: unchanged for the cap means report STALLED
with the live process count, rows so far, and the no-progress duration, then exit
non-zero. A watcher with only a completion condition waits forever on a hung job and
notifies nobody.

Pick the cap well above the slowest observed row interval. Measured on a contact
harvest: the first rows landed about 3 minutes after start, then roughly a row every
few seconds, so a 15 minute no-progress cap was safe and a 60 second one would have
fired on startup.

## 5. Validate the watcher before launching it

```bash
bash -n "$SCRATCH/watch.sh"
```

A syntax error in a background watcher fails silently. No notification of any kind
arrives and the job finishes unobserved. Write the script to a fresh `mktemp -d`
directory for the run, syntax-check it, and only then launch it.

## 6. Verify completion against the artifact, not the notification

At completion, report all three:

- live process count is 0
- total rows across every output file
- finish time

An exit code of 0 from the watcher means the watcher loop ended, not that the collector
succeeded. Check the output file for the row count and read the tail of it before
claiming the harvest produced usable rows.

## 7. Report shape

One line: done, the count, and anything that failed. "Harvest complete: 1,204 of 2,000
with a contact address, finished 09:42." No interim chatter, no narration of the
watching itself.
