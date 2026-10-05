#!/usr/bin/env python3
import json
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "games"

MODES = {"disabled", "relaxed", "precise"}
FINDINGS = {"required", "sufficient", "beneficial", "no_benefit"}
CONFIDENCE = {"high", "medium", "low"}
OUTCOMES = {"fails", "incorrect", "partial", "works", "improves", "no_change", "not_tested", "not_reported"}
KINDS = {"compatibility_issue", "compatibility_issue_comment", "upstream_issue", "upstream_pr", "other"}
SERIAL_RE = re.compile(r"^CUSA\d{5}$")
SCOPE_RE = re.compile(r"^[a-z0-9_]+$")

errors = []
seen_serials = set()

def err(path, message):
    errors.append(f"{path}: {message}")

files = sorted(DATA.glob("*.json"))
if not files:
    err(DATA, "no game records found")

for path in files:
    try:
        record = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        err(path, f"invalid JSON: {exc}")
        continue

    serial = record.get("serial")
    if not isinstance(serial, str) or not SERIAL_RE.fullmatch(serial):
        err(path, "serial must match CUSA#####")
    else:
        if path.stem != serial:
            err(path, f"filename must be {serial}.json")
        if serial in seen_serials:
            err(path, f"duplicate serial {serial}")
        seen_serials.add(serial)

    if record.get("schema_version") != 1:
        err(path, "schema_version must be 1")
    if not isinstance(record.get("title"), str) or not record["title"].strip():
        err(path, "title must be a non-empty string")
    if not isinstance(record.get("last_reviewed"), str):
        err(path, "last_reviewed must be a date string")

    claims = record.get("claims")
    if not isinstance(claims, list) or not claims:
        err(path, "claims must be a non-empty list")
        continue

    for idx, claim in enumerate(claims):
        where = f"{path}: claim[{idx}]"
        if claim.get("mode") not in MODES:
            err(where, "invalid mode")
        if claim.get("finding") not in FINDINGS:
            err(where, "invalid finding")
        if claim.get("confidence") not in CONFIDENCE:
            err(where, "invalid confidence")
        scope = claim.get("scope")
        if not isinstance(scope, str) or not SCOPE_RE.fullmatch(scope):
            err(where, "scope must be lower-case snake_case")

        comparison = claim.get("comparison")
        if not isinstance(comparison, dict) or not comparison:
            err(where, "comparison must be a non-empty object")
        else:
            for mode, outcome in comparison.items():
                if mode not in MODES:
                    err(where, f"invalid comparison mode {mode!r}")
                if outcome not in OUTCOMES:
                    err(where, f"invalid comparison outcome {outcome!r}")

        evidence = claim.get("evidence")
        if not isinstance(evidence, list) or not evidence:
            err(where, "evidence must be a non-empty list")
        else:
            for eidx, item in enumerate(evidence):
                ewhere = f"{where}.evidence[{eidx}]"
                if item.get("kind") not in KINDS:
                    err(ewhere, "invalid evidence kind")
                url = item.get("url")
                parsed = urlparse(url) if isinstance(url, str) else None
                if not parsed or parsed.scheme != "https" or not parsed.netloc:
                    err(ewhere, "evidence URL must be absolute https")
                if not isinstance(item.get("note"), str) or not item["note"].strip():
                    err(ewhere, "evidence note must be non-empty")

        if not isinstance(claim.get("co_requirements"), list):
            err(where, "co_requirements must be a list")
        if not isinstance(claim.get("summary"), str) or not claim["summary"].strip():
            err(where, "summary must be non-empty")

if errors:
    print("\n".join(errors), file=sys.stderr)
    sys.exit(1)

claim_count = sum(
    len(json.loads(path.read_text(encoding="utf-8"))["claims"])
    for path in files
)
print(f"OK: {len(files)} game records, {claim_count} claims")
