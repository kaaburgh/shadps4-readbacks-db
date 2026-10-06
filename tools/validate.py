#!/usr/bin/env python3
import json
import sys
from pathlib import Path
from urllib.parse import urlparse

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "games"
SCHEMA_PATH = ROOT / "schema" / "game.schema.json"

FINDING_OUTCOMES = {
    "required": {"works", "partial"},
    "sufficient": {"works", "partial"},
    "beneficial": {"improves"},
    "no_benefit": {"no_change"},
}

errors = []
seen_serials = set()


def err(path, message):
    errors.append(f"{path}: {message}")


def location(error):
    if not error.absolute_path:
        return "<root>"
    return ".".join(str(part) for part in error.absolute_path)


try:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
except Exception as exc:
    print(f"{SCHEMA_PATH}: invalid JSON Schema: {exc}", file=sys.stderr)
    raise SystemExit(1)

schema_validator = Draft202012Validator(schema, format_checker=FormatChecker())

files = sorted(DATA.glob("*.json"))
if not files:
    err(DATA, "no game records found")

claim_count = 0

for path in files:
    try:
        record = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        err(path, f"invalid JSON: {exc}")
        continue

    schema_errors = sorted(
        schema_validator.iter_errors(record),
        key=lambda item: [str(part) for part in item.absolute_path],
    )
    for item in schema_errors:
        err(path, f"{location(item)}: {item.message}")
    if schema_errors:
        continue

    serial = record["serial"]
    if path.stem != serial:
        err(path, f"filename must be {serial}.json")
    if serial in seen_serials:
        err(path, f"duplicate serial {serial}")
    seen_serials.add(serial)

    seen_claims = set()
    for idx, claim in enumerate(record["claims"]):
        claim_count += 1
        where = f"{path}: claim[{idx}]"

        selected_outcome = claim["comparison"].get(claim["mode"])
        if selected_outcome is None:
            err(where, f"comparison must contain the selected mode {claim['mode']!r}")
        elif selected_outcome not in FINDING_OUTCOMES[claim["finding"]]:
            allowed = ", ".join(sorted(FINDING_OUTCOMES[claim["finding"]]))
            err(
                where,
                f"{claim['finding']} requires selected-mode outcome in {{{allowed}}}, "
                f"got {selected_outcome!r}",
            )

        evidence_urls = [item["url"] for item in claim["evidence"]]
        if len(evidence_urls) != len(set(evidence_urls)):
            err(where, "duplicate evidence URL in one claim")
        for eidx, url in enumerate(evidence_urls):
            parsed = urlparse(url)
            if parsed.scheme != "https" or not parsed.netloc:
                err(f"{where}.evidence[{eidx}]", "evidence URL must be absolute https")

        claim_key = (
            claim["scope"],
            claim["mode"],
            claim["finding"],
            claim["shadps4_version"],
            claim["game_version"],
            tuple(sorted(claim["co_requirements"])),
        )
        if claim_key in seen_claims:
            err(where, "duplicate claim; merge its evidence into the existing claim")
        seen_claims.add(claim_key)

if errors:
    print("\n".join(errors), file=sys.stderr)
    raise SystemExit(1)

print(f"OK: {len(files)} game records, {claim_count} claims")
