#!/usr/bin/env python3
"""
IONOS DNS manager (hosting API) — for phantom-byte.com / vincentsativa.com.

API base : https://api.hosting.ionos.com/dns/v1
Auth     : header  X-API-Key: <prefix>.<secret>
Key/zone : read from ../secrets.json (or env IONOS_API_KEY / IONOS_DNS_ZONE).

SAFETY: PUT replaces the ENTIRE record set for a zone, so every write
auto-backs-up first and requires --apply. Default is dry-run.

Commands:
  python ionos_dns.py zones
  python ionos_dns.py show    <domain>
  python ionos_dns.py backup  <domain>
  python ionos_dns.py set     <domain> <TYPE> <name> <content> [--prio N] [--ttl N] [--apply]
  python ionos_dns.py rm      <domain> <TYPE> <name> [<content>] [--apply]
"""
from __future__ import annotations
import json
import os
import sys
import urllib.request
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
BACKUP_DIR = Path.home() / "workspace" / "dns-backups"
BASE = "https://api.hosting.ionos.com/dns/v1"


def _secrets() -> dict:
    sec = ROOT / "secrets.json"
    return json.loads(sec.read_text(encoding="utf-8")) if sec.exists() else {}


def _key() -> str:
    if os.environ.get("IONOS_API_KEY"):
        return os.environ["IONOS_API_KEY"]
    s = _secrets()
    return f"{s['api_prefix']}.{s['api_secret']}"


def _zone_id(domain: str) -> str:
    if os.environ.get("IONOS_DNS_ZONE") and domain in ("", "-"):
        return os.environ["IONOS_DNS_ZONE"]
    s = _secrets()
    if domain in s.get("zones", {}):
        return s["zones"][domain]
    # look it up
    for z in api("GET", "/zones"):
        if z["name"] == domain:
            return z["id"]
    raise SystemExit(f"zone not found: {domain}")


def api(method: str, path: str, body: dict | None = None):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(BASE + path, data=data, method=method,
                                 headers={"X-API-Key": _key(), "Accept": "application/json",
                                          "Content-Type": "application/json"})
    with urllib.request.urlopen(req) as r:
        raw = r.read().decode()
    return json.loads(raw) if raw.strip() else {}


def cmd_zones():
    for z in api("GET", "/zones"):
        print(f"{z['name']:24} {z['id']}  ({z.get('type')})")


def cmd_show(domain):
    z = api("GET", f"/zones/{_zone_id(domain)}")
    for r in sorted(z.get("records", []), key=lambda x: (x.get("type", ""), x.get("name", ""))):
        prio = f" prio={r['prio']}" if r.get("prio") else ""
        ttl = f" ttl={r['ttl']}" if r.get("ttl") else ""
        print(f"{r['type']:7} {r['name']:45} {str(r.get('content',''))[:90]}{prio}{ttl}")


def cmd_backup(domain):
    zid = _zone_id(domain)
    z = api("GET", f"/zones/{zid}")
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    out = BACKUP_DIR / f"{domain}_dns_{ts}.json"
    out.write_text(json.dumps(z, indent=2), encoding="utf-8")
    print("backed up:", out)


def _upsert(domain, rtype, name, content, prio, ttl, apply_):
    zid = _zone_id(domain)
    z = api("GET", f"/zones/{zid}")
    recs = z.get("records", [])
    name = name.rstrip(".") if name.endswith(".") else name
    # remove any existing same type+name (IONOS keeps one record per name/type entry)
    recs = [r for r in recs if not (r.get("type", "").upper() == rtype.upper() and r.get("name") == name)]
    rec = {"name": name, "type": rtype.upper(), "content": content, "disabled": False}
    if prio is not None:
        rec["prio"] = prio
    if ttl is not None:
        rec["ttl"] = ttl
    recs.append(rec)
    print(f"WOULD set {rtype} {name} -> {content}" + (f" prio={prio}" if prio is not None else ""))
    if not apply_:
        print("(dry-run — add --apply to write)")
        return
    cmd_backup(domain)
    api("PUT", f"/zones/{zid}", {"name": z["name"], "type": z.get("type", "NATIVE"), "records": recs})
    print("APPLIED.")


def _rm(domain, rtype, name, content, apply_):
    zid = _zone_id(domain)
    z = api("GET", f"/zones/{zid}")
    keep, drop = [], []
    for r in z.get("records", []):
        match = r.get("type", "").upper() == rtype.upper() and r.get("name") == name
        if content:
            match = match and r.get("content") == content
        (drop if match else keep).append(r)
    for r in drop:
        print("WOULD remove", r["type"], r["name"], r.get("content"))
    if not drop:
        print("nothing matched")
        return
    if not apply_:
        print("(dry-run — add --apply to write)")
        return
    cmd_backup(domain)
    api("PUT", f"/zones/{zid}", {"name": z["name"], "type": z.get("type", "NATIVE"), "records": keep})
    print("APPLIED.")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return
    cmd = sys.argv[1]
    args = [a for a in sys.argv[2:] if not a.startswith("--")]
    flags = [a for a in sys.argv[2:] if a.startswith("--")]
    apply_ = "--apply" in flags
    prio = int(sys.argv[sys.argv.index("--prio") + 1]) if "--prio" in sys.argv else None
    ttl = int(sys.argv[sys.argv.index("--ttl") + 1]) if "--ttl" in sys.argv else None
    if cmd == "zones":
        cmd_zones()
    elif cmd == "show":
        cmd_show(args[0])
    elif cmd == "backup":
        cmd_backup(args[0])
    elif cmd == "set":
        _upsert(args[0], args[1], args[2], args[3], prio, ttl, apply_)
    elif cmd == "rm":
        _rm(args[0], args[1], args[2], args[3] if len(args) > 3 else None, apply_)
    else:
        print(__doc__)


if __name__ == "__main__":
    main()
