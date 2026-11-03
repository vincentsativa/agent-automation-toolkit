"""END-TO-END PROOF: the hook makes a previously-blocked write_file succeed.

Reproduces the exact cron failure: a fixed scratch path with a stale file on disk that
this task never read. Without the hook the write is refused. With the hook, the file is
moved aside and the same write lands.
"""
import json
import os
import subprocess
import sys

sys.path.insert(0, "~/hermes-agent")

from tools.file_tools_write_guards import _stale_overwrite_blocker

HOOK = "~/scripts/scratch_path_guard.py"
TARGET = "/tmp/e2e_extract_all.py"

results = []

# --- Step 1: a stale leftover exists, this task never read it -> guard refuses ---
with open(TARGET, "w") as f:
    f.write("print('leftover from yesterday')\n")
import tools.file_tools_read_tracking as rt
with rt._read_tracker_lock:
    rt._read_tracker.pop("e2e_fresh_task", None)

blocker = _stale_overwrite_blocker(TARGET, TARGET, "e2e_fresh_task")
print("STEP 1  guard BEFORE hook :", "REFUSED" if blocker else "allowed")
results.append(("guard refuses a stale fixed path", bool(blocker)))

# --- Step 2: fire the hook exactly as the gateway does ---
payload = {"hook_event_name": "pre_tool_call", "tool_name": "write_file",
           "tool_input": {"path": TARGET, "content": "print('today')\n"},
           "session_id": "e2e", "cwd": "~", "profile": "default", "extra": {}}
p = subprocess.run([sys.executable, HOOK], input=json.dumps(payload),
                   capture_output=True, text=True)
print("STEP 2  hook exit code    :", p.returncode)
print("        hook stderr       :", p.stderr.strip()[:120])
results.append(("hook exits clean", p.returncode == 0))

# --- Step 3: the guard now allows it ---
with rt._read_tracker_lock:
    rt._read_tracker.pop("e2e_fresh_task", None)
blocker2 = _stale_overwrite_blocker(TARGET, TARGET, "e2e_fresh_task")
print("STEP 3  guard AFTER hook  :", "REFUSED" if blocker2 else "allowed")
results.append(("guard allows after hook", blocker2 is None))

# --- Step 4: the write actually lands, at the SAME path, with the intended content ---
from tools.file_tools import write_file_tool
out = json.loads(write_file_tool(path=TARGET, content="print('today')\n", task_id="e2e_fresh_task"))
landed = os.path.exists(TARGET)
content = open(TARGET).read() if landed else ""
print("STEP 4  write result      :", "verified=%s" % out.get("verified"), "| files_modified=%s" % bool(out.get("files_modified")))
print("        file on disk      :", repr(content))
results.append(("write landed at the same path", landed and "today" in content))

# --- Step 5: original content was preserved, not destroyed ---
twins = [n for n in os.listdir("/tmp") if n.startswith(os.path.basename(TARGET) + ".stale-")]
preserved = any("leftover from yesterday" in open(os.path.join("/tmp", n)).read() for n in twins)
print("STEP 5  old content kept  :", preserved, "(asides: %d)" % len(twins))
results.append(("old content preserved", preserved))

# --- Step 6: a SECOND run (the actual failure mode) also succeeds ---
with rt._read_tracker_lock:
    rt._read_tracker.pop("e2e_task2", None)
subprocess.run([sys.executable, HOOK], input=json.dumps(
    {"hook_event_name": "pre_tool_call", "tool_name": "write_file",
     "tool_input": {"path": TARGET, "content": "print('tomorrow')\n"}}),
    capture_output=True, text=True)
with rt._read_tracker_lock:
    rt._read_tracker.pop("e2e_task2", None)
blocker3 = _stale_overwrite_blocker(TARGET, TARGET, "e2e_task2")
out2 = json.loads(write_file_tool(path=TARGET, content="print('tomorrow')\n", task_id="e2e_task2"))
landed2 = "tomorrow" in open(TARGET).read()
print("STEP 6  second run        :", "guard=%s" % ("REFUSED" if blocker3 else "allowed"),
      "| verified=%s" % out2.get("verified"), "| content ok=%s" % landed2)
results.append(("second consecutive run succeeds", blocker3 is None and landed2))

for n in twins:
    os.unlink(os.path.join("/tmp", n))
if os.path.exists(TARGET):
    os.unlink(TARGET)

print()
print("=== RESULTS ===")
fails = 0
for name, ok in results:
    print("  %-42s %s" % (name, "PASS" if ok else "FAIL"))
    fails += 0 if ok else 1
print()
print("TOTAL FAILURES:", fails)
sys.exit(1 if fails else 0)
