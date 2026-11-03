# Vinny's Tutorial Outline Format

When Vinny says "write me this tutorial," his request follows a specific structure. Parse it carefully.

## The Fields

**Title:** The tutorial title. Use this as-is.

**Primary Source:** Which agent narrates. "FRANK #2" means write from that agent's perspective in first person ("I am FRANK #2"). This is a credibility signal, not a blueprint — do not expose the actual system.

**Overlap Check:** "None in KARMA" means the content does not conflict with anything else in the pipeline. Do not worry about overlap. Write the tutorial as specified.

**Why it leads / Why it matters:** The positioning. This is the hook. Use it to frame the tutorial's value.

**What it covers:** The bullet list of topics. This is the tutorial's table of contents. Cover each one.

**Why now:** The timing argument. Use it to close the tutorial or as the urgency signal.

## Example

```
Tutorial:

Your First Agent Cron Job: Automate Anything While You Sleep
  Primary Source: FRANK #2
  Overlap Check: None in KARMA
  Why it leads: Automation is the killer app beginners don't know exists.

  What it covers:
   - What cron is
   - Setting up a daily briefing agent
   - Chaining jobs
   - Watchdog patterns
   - Cron syntax
   - Real example

  Why now: Automation is the killer app of agents.
```

## What NOT to Do

- Do not turn the "What it covers" bullets into a table of contents that gives away the implementation. Cover each topic at the concept level.
- Do not use the "Real example" section to describe Vinny's actual system. Use a generic example or describe the concept in action.
- Do not name FRANK #2 as the narrator in the tutorial body unless Vinny explicitly says to. The Primary Source field is instruction for you, not publication copy.
