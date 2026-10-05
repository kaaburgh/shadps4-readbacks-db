# Game records

Each `CUSA#####.json` file is a canonical game record.

Keep claims narrow and evidence-backed. Prefer multiple scoped claims over a single broad statement such as "this game requires Precise".

Important distinctions:

- `required`: weaker modes are explicitly insufficient, or the source explicitly says the mode is required.
- `sufficient`: the mode is shown to work, but weaker modes have not all been excluded.
- `beneficial`: the mode improves the behavior but does not fully fix it.
- `no_benefit`: tested without an observable benefit for the scope.

Comparison outcomes describe only what the cited evidence supports:

- `not_tested`: the source explicitly establishes that this mode was not tested.
- `not_reported`: the source does not tell us the result for this mode. Do not silently turn this into `not_tested`.
- `fails`: the target scope cannot be reached.
- `incorrect`: the target is reached but the scoped behavior is incorrect.
- `partial`: some of the scoped behavior works.
- `works`: the scoped target is achieved.
- `improves`: better than the comparison mode, but not fully correct.
- `no_change`: no meaningful change for this scope.

Never infer a missing shadPS4 version from the issue date. Use `null`.

If another experimental option is necessary for the observation, record it in `co_requirements` rather than attributing the whole result to readbacks.
