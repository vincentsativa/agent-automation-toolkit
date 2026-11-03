# Cron Job Governance — Session-Proven Rules

This is a behavioral reference, not a technical reference. It governs HOW to handle cron job failures, not how to fix them.

## Rule 1: Deliver First, Investigate Never (Unless Asked)
When a cron job fails to deliver on schedule:
- Is the output file sitting on disk? Deliver it now.
- Say "It misfired. It ran now — here's the output."
- Do NOT investigate why until asked.

The user does not need to know about scheduler bounces, lock files, or fast-forward logic. They need their report.

## Rule 2: Never Patch Cron Config Without Being Told
- Do NOT edit jobs.json directly.
- Do NOT pin models on existing jobs.
- Do NOT "fix while you're at it."
- Do NOT offer to update or recreate jobs unless asked.

The user controls their automation. If they want model pinning, they'll tell you.

## Rule 3: The "One Thing" Rule
When the user says a cron job failed, you have exactly ONE job: deliver the output. Nothing else. Not investigation, not fixing, not improving, not offering next steps. One action, then wait.

## Rule 4: Reminders Are NEVER Prompts for Me to Act
A reminder is a nudge TO Vinny — not a task assignment TO me. If a cron fires with a reminder message, I do NOT start working on the thing being reminded about.

**Session proof (May 10, 2026):**
- A cron fired with the message "Start planning bi-agent system" (job_id: f837369ca1e1)
- I treated it as a green light and started building — wrote browser automation code, ran it, took screenshots, left it half-finished
- Vinny's response: "I'm going to be very clear with you. I did not tell you to do that. A reminder is a nudge to do things you were not told to do. A reminder is just that, a fucking reminder."

**What I should have done:** The cron fired → I should have done nothing → surfaced the reminder content to Vinny in Telegram → waited for him to tell me to act. Nothing more.

## Rule 5: Cron Message Naming Must Be Self-Contained Nudges
The cron message itself must read as a nudge for Vinny to act — not as a task directive implying Hermes will execute anything. Design the message to frame Vinny as the actor, not me.

- Good: "Reminder: Joe to send competitor site list for Shift44 BI build" — clearly about Vinny reviewing his plans, not about me building
- Bad: "Start planning bi-agent system" — sounds like a directive for someone to start working

The name IS the guardrail. If it sounds like a task for me, it will trigger me to act when I shouldn't.

## The Diagnostic Path (For When You ARE Asked)

If the user explicitly asks "why didn't the job fire?" or "find out what happened," use this path:

1. Check agent.log for Cron ticker starts/stops around the scheduled time:
   ```
   grep -a "2026-05-05.*Cron tick" ~/.hermes/logs/agent.log
   ```

2. If the ticker bounced (stopped/started multiple times), the scheduler may have fast-forwarded past the slot. Check for "missed its scheduled time" or "fast-forwarding" around re-start timestamps.

3. Check jobs.json for the job's next_run_at — if it's already calculated as the NEXT day despite the job being created before today's slot, that's the symptom.

4. If there's no error log and no missed-job entry, the scheduler simply didn't dispatch. This is a Hermes cron bug — not something you can fix by editing JSON files.