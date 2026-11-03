# Handing this pipeline to Pi (or any agent on the Windows side)

Vinny's coding harness is Pi, on his Windows machine, WSL running under it. This is the shape of a handoff prompt for this project, and the boundary rules it has to carry.

## The deliverable

One complete prompt file, written to disk, emailed to him as an attachment. Not chat text, not a chat message plus an addendum. A useful prompt for this pipeline runs to several thousand words, which is longer than a chat reply survives, and he will end up asking for the file by email after it truncates. Write the file first, then email it.

Where to write it: the `PROMPTS I USE DAILY` folder on his Desktop, next to his existing Pi prompts. Read one of his existing Pi prompts first and match the blunt imperative register he uses there: state the rule, state why it matters, do not pad it.

## What the prompt must contain

1. An order to read the skill before writing any code, with the skill's full path and every reference file listed, plus a line saying the prompt is a summary and the skill is the authority where they differ.
2. The file and script inventory it will touch, with both the WSL path and the Windows path for each crossing point.
3. The goal in plain terms: what is being sold, who qualifies as a prospect, the send volume, the money.
4. Its concrete work list, quoting the skill's own open items rather than inventing new ones.
5. The proof requirements, so it cannot hand back a claim: the known-answer test, the rendered messages, the send-and-read-back, every refusal path.
6. The work that is only its to ship, which for this project is deployment of the offer page and the contact form backend, because the WSL agent is barred from deploying and from inspecting the cloud accounts.
7. The hard boundaries: no automation of sending, never remove the postal-address or opt-out check, SendGrid records stay, IONOS DNS through the API and never the web panel, no Gumroad.
8. The report format it must answer in, including that a script is never reported as working on the strength of a past session.

## Boundary rules the prompt must state, in the prompt's own words

- Run the Python and shell inside WSL, never under Windows Python. The send path needs the env file at `~/.config/phantombyte/mailer.env`, and the scanner reaches DNS over HTTPS, so a copy on a Windows drive is a broken copy.
- Windows into WSL:
  `wsl.exe -d Ubuntu bash -lc "cd ~/money_ideas && source ~/.config/phantombyte/mailer.env && python3 test_email_scan.py"`
- Anything WSL will execute must be written with LF line endings. A `.py` or `.sh` saved with CRLF fails inside WSL with an error that reads like a syntax problem on line 1 and costs an hour.
- Path translation, both directions: inside WSL `/mnt/c/Users/<user>/` is `C:\Users\<user>\`; from Windows `\\wsl.localhost\Ubuntu\home\vincent\` is `~/`. `~/` is not a Windows path and cannot be read as one.
- A UNC path as the current directory makes `cmd.exe`, `reg.exe`, and other Windows tools fail with “UNC paths are not supported”. Change to a drive-letter path first.
- WSL-resident Hermes state is out of bounds: `~/` config, crons, memories, and the venv.

## Verify the prompt file before sending it

Three checks, all of them mechanical, because this is a document he reads:

```bash
awk '{ if (length($0) > m) m = length($0) } END { print m }' "$FILE"   # long is right; a short longest line means it is hard-wrapped
grep -c $'\u2014\|\u2013' "$FILE"                                        # must be 0
grep -n ' - ' "$FILE"                                                   # must be empty; no dash as a separator
grep -c $'\r' "$FILE"                                                   # must be 0, the file keeps LF
```

## Then email it, and read it back

Use the `email-sender` skill: attachment, never a pasted body, and confirm delivery by reading the message back out of the mailbox rather than trusting the SMTP reply. Confirm the attachment's byte count and its first and last lines match the on-disk file, which is what proves nothing was truncated in transit.

## The revert prompt: handing back a change that should not exist

When the WSL agent has changed something Vinny did not authorize, Pi is the one who undoes it. The prompt shape is different from a build handoff, and the difference is what makes it safe.

- **Inventory every touched artifact, exhaustively, by path and line number.** A file created, a config block inserted, an allowlist entry appended, a scratch directory left behind. State the exact current line range and the exact text at that range, so Pi removes what is there rather than what a summary described. "I changed the config" is not a handoff; "four lines at 605 to 608, reading exactly this" is.
- **Carry a DO NOT TOUCH section, and put it in a named part of its own.** The authorized work from the same session sits in the same tree as the mess, and a reverting agent will happily clean up both. List every authorized artifact by path with the reason it must survive, including the exact things not to restore (deleted dictionaries, removed branches). Without this section the revert destroys the work he actually ordered.
- **Do not tell Pi to restore a backup file.** A dated backup of a long-lived config is older than many later legitimate edits. Prescribe the targeted removal, and forbid restoring the backup by name, or the revert silently discards weeks of unrelated changes.
- **Every step carries a proof command with the expected output.** Same rule as a build handoff: no claim without the pasted output. Include the negative checks (grep for the artifact returning nothing, the file no longer existing).
- **Name the pre-existing warnings so Pi does not "fix" them.** A unrelated drift or warning that already existed will surface in the verification output; call it out as pre-existing and off-limits, or the revert turns into unrequested repairs.
- **State the rule at the top: revert exactly this and nothing more.** Then repeat the boundary inside each step. A reverting agent with no boundary wanders into improvement, and an unauthorized cleanup of his machine on top of an unauthorized change does not survive the conversation.
- **Also give it in chat when he asks, and know where the file is.** He may want to hand the path to Pi himself rather than wait for the email. Have both ready. When he asks what it says, answer with the path and the byte count, not a summary of its contents.
