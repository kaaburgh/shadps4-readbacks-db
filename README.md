# shadPS4 Readbacks DB

Evidence-backed observations about which shadPS4 GPU readback mode is needed for specific games and specific correctness scopes.

This is **not** a generic compatibility list and it does not assume that a game has one timeless "correct setting". Readback behavior can change with shadPS4 versions, drivers, hardware, and other experimental settings.

## Current shadPS4 modes

Current upstream exposes three `GpuReadbacksMode` values:

- `Disabled`
- `Relaxed`
- `Precise`

`Disabled` is currently the default. The database stores mode names rather than numeric enum values.

Upstream source: https://github.com/shadps4-emu/shadPS4/blob/main/src/core/emulator_settings.h

## Quick view

See [SUMMARY.md](SUMMARY.md) for the generated human-readable table.

Canonical records live under [data/games](data/games).

## Evidence rules

A record is scoped to a concrete observed behavior, for example `reach_ingame`, `geometry_rendering`, or `vertex_integrity`.

`finding` has deliberately strict semantics:

- **required** — the evidence explicitly says the mode is needed/requires it, or demonstrates that weaker modes fail for the same scope.
- **sufficient** — this mode is shown to achieve the stated result, but the evidence does not rule out every weaker mode.
- **beneficial** — this mode improves the stated behavior but does not fully correct it.
- **no_benefit** — the mode was tested and provided no observable benefit for the stated scope.

Do not promote "Precise works" into "Precise required" without evidence about Relaxed.

Each claim records the shadPS4 version when the source states it. `null` means the source does not pin the version; it must not be silently inferred from issue dates or milestones.

Other experimental requirements belong in `co_requirements`. A result that needs Direct Memory Access or Readback Linear Images should not be represented as a readbacks-only result.

## Repository layout

- `data/games/*.json` — canonical per-title records.
- `schema/game.schema.json` — JSON Schema for editors and external tooling.
- `tools/validate.py` — dependency-free semantic validation.
- `tools/generate_summary.py` — regenerates `SUMMARY.md`.
- `.github/workflows/validate.yml` — validates data and checks generated output.

Validate locally:

~~~sh
python3 tools/validate.py
python3 tools/generate_summary.py --check
~~~

Regenerate the summary after editing data:

~~~sh
python3 tools/generate_summary.py
~~~

## Scope and limitations

The initial seed is intentionally small and conservative. It is sourced primarily from the official shadPS4 compatibility repository and prefers reports that explicitly compare readback modes.

A claim is an observation tied to its evidence, not a guarantee that the same result holds on every GPU or every later shadPS4 build.
