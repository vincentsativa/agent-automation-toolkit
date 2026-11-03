#!/usr/bin/env python3
"""
Email recipient guard — run BEFORE any outbound send.

Blocks, in order:
  1. Suppression list  (data/suppression.txt)  — addresses that hard-bounced/unsubscribed.
  2. Role addresses    (data/role_prefixes.txt) — info@, service@, office@, sales@, support@...
  3. Bad syntax / disposable domains / free-mail domains / placeholder addresses.
Optionally checks MX and (with --smtp) does an SMTP RCPT probe.

Usage:
  python email_guard.py check  a@b.com c@d.com ...     # verdict per address
  python email_guard.py filter list.txt  > clean.txt   # keep only allowed addresses
  python email_guard.py suppress a@b.com ...           # append to suppression list
  python email_guard.py check --smtp a@b.com           # add live SMTP probe
"""
from __future__ import annotations
import re
import socket
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SUPPRESSION = ROOT / "data" / "suppression.txt"
ROLE = ROOT / "data" / "role_prefixes.txt"
FREE_MAIL = ROOT / "data" / "free_mail_domains.txt"

SYNTAX = re.compile(r"^[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}$")
# a couple of throwaway domain patterns; extend as needed
DISPOSABLE = ("mailinator.com", "guerrillamail.com", "10minutemail.com", "tempmail.com", "trashmail.com")

# Form-filler text published as if it were an address. Measured 2026-10-01:
# youcancreateanemailforthis@please.com came off an OpenStreetMap email tag
# and hard-bounced 5.0.0.
PLACEHOLDER_MARKERS = (
    "youcancreate", "createanemail", "youremail", "your.email", "your-email",
    "your_email", "yourname", "your.name", "your-name", "your_name",
    "enteryour", "enter-your", "enter_your", "emailaddress", "email.address",
    "email_address", "yourdomain", "your-domain", "placeholder", "changeme",
    "somename", "someone", "someoneelse", "firstname", "lastname",
    "fullname", "johndoe", "janedoe", "testemail", "test-email",
)


def _lines(path: Path) -> set[str]:
    if not path.exists():
        return set()
    return {l.strip().lower() for l in path.read_text(encoding="utf-8").splitlines()
            if l.strip() and not l.startswith("#")}


def load_suppression() -> set[str]:
    return _lines(SUPPRESSION)


def load_roles() -> set[str]:
    return _lines(ROLE)


def load_free_mail() -> set[str]:
    return _lines(FREE_MAIL)


def _role_shaped(local: str, roles: set[str]) -> bool:
    """True when a local part names a shared/function mailbox.

    Mirrors find_contacts.address_shape in the WSL pipeline so the two
    blocklists behave identically: an exact word, a word fused with a separator
    (info-uk@), a plural (teams@), or a role word at the END of a fused token
    (churchadmin@, smartcenter@) all count. Suffix matching uses role words of
    length >= 4 only, so a real name is never dropped on a fragment ("chris"
    does not end in "hr").
    """
    local = (local or "").strip().lower()
    if not local:
        return True
    if local in roles:
        return True
    for p in roles:
        if local.startswith(p + ".") or local.startswith(p + "-") or local.startswith(p + "_"):
            return True
    strong = tuple(p for p in roles if len(p) >= 4)
    for tok in re.split(r"[._\-]+", local):
        if tok in roles or (tok.endswith("s") and tok[:-1] in roles):
            return True
        for p in strong:
            if tok.endswith(p) or tok == p + "s":
                return True
    # 2026-10-09 (Vinny): a role word fused to the FRONT of a token slipped the
    # end-match above. infoboston@ (a shared front-desk box) went out on the
    # Oct 9 send. "info" is the only front-fused role word that is safe: no
    # common given or family name begins with it, so a real person is never
    # dropped on the guess.
    if local.startswith("info") and len(local) > 4:
        return True
    return False


def verdict(addr: str, smtp: bool = False) -> tuple[str, str]:
    """Return (decision, reason). decision in {allow, block, verify}."""
    a = addr.strip().lower()
    if not SYNTAX.match(a):
        return "block", "bad syntax"
    if a in load_suppression():
        return "block", "suppressed (previous hard bounce/unsub)"
    local, domain = a.rsplit("@", 1)
    roles = load_roles()
    if _role_shaped(local, roles) or _role_shaped(local.split("+")[0], roles):
        return "block", f"role address ({local}@)"
    # Numbered store/branch boxes ("store002@", "shop14@") are shared, not a
    # person. Measured 2026-10-06: user@example.com was sent.
    if re.match(r"^(store|shop|branch|location)\d+$", local):
        return "block", f"numbered {local}@ (chain store/branch box)"
    if any(domain == d or domain.endswith("." + d) for d in DISPOSABLE):
        return "block", "disposable domain"
    if any(domain == d or domain.endswith("." + d) for d in load_free_mail()):
        return "block", "free-mail/consumer mailbox (no domain of their own to fix)"
    if any(m in local for m in PLACEHOLDER_MARKERS):
        return "block", "placeholder address (form-filler text)"
    if smtp:
        ok, why = smtp_probe(a)
        return ("allow" if ok else "block"), why
    return "allow", "ok"


def _mx(domain: str) -> bool:
    try:
        import subprocess
        # nslookup is available in this MSYS env; fall back to socket
        out = subprocess.run(["nslookup", "-type=MX", domain], capture_output=True, text=True, timeout=10).stdout
        return "mail exchanger" in out.lower() or "MX preference" in out
    except Exception:
        return True  # don't block on lookup failure


def smtp_probe(addr: str) -> tuple[bool, str]:
    domain = addr.rsplit("@", 1)[1]
    if not _mx(domain):
        return False, "no MX record"
    # NOTE: many providers (Gmail/MS) accept all at RCPT and bounce later.
    # A 550 at RCPT is a reliable hard-block; anything else is 'verify'.
    try:
        import smtplib
        # find an MX host via nslookup parse
        import subprocess
        out = subprocess.run(["nslookup", "-type=MX", domain], capture_output=True, text=True, timeout=10).stdout
        mx = re.findall(r"mail exchanger = ([^\s]+)", out, re.I)
        if not mx:
            return True, "MX found (host parse failed)"
        host = mx[0].rstrip(".")
        s = smtplib.SMTP(host, 25, timeout=12)
        s.helo("phantom-byte.com")
        s.mail("hello@example.com")
        code, _ = s.rcpt(addr)
        s.quit()
        if code and 500 <= code < 600:
            return False, f"SMTP {code} at RCPT"
        return True, f"SMTP {code} (accept/verify)"
    except Exception as e:
        return True, f"probe inconclusive ({type(e).__name__})"


def cmd_check(args):
    smtp = "--smtp" in args
    addrs = [a for a in args if a != "--smtp"]
    blocked = 0
    for a in addrs:
        d, r = verdict(a, smtp)
        if d == "block":
            blocked += 1
        print(f"{d.upper():6} {a:40} {r}")
    print(f"\n{blocked}/{len(addrs)} would be blocked", file=sys.stderr)


def cmd_filter(path):
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        a = line.strip().lower()
        if a and verdict(a)[0] != "block":
            print(a)


def cmd_suppress(addrs):
    SUPPRESSION.parent.mkdir(parents=True, exist_ok=True)
    cur = load_suppression()
    with SUPPRESSION.open("a", encoding="utf-8") as f:
        for a in addrs:
            a = a.strip().lower()
            if a and a not in cur:
                f.write(a + "\n")
                cur.add(a)
                print("suppressed:", a)


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return
    cmd, rest = sys.argv[1], sys.argv[2:]
    if cmd == "check":
        cmd_check(rest)
    elif cmd == "filter":
        cmd_filter(rest[0])
    elif cmd == "suppress":
        cmd_suppress(rest)
    else:
        print(__doc__)


if __name__ == "__main__":
    main()
