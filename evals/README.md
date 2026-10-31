# ThorInvest evals

`golden.jsonl` is the shared end-to-end set (owned by the CIO office). It is a **draft**: confirm or replace
each task before it is used to accept or reject a fold.

Per task, grade three things and run each task **twice** (one-run passes hide flaky process breaks):
1. Final answer against `rubric` (pass/fail per line).
2. Process: did Thor load `expected_skills` and call `expected_tools`? Missing a gate tool is a fail even if
   the prose looks right.
3. Latency and cost per task, to compare against the old multi-package setup.

Domain owners may add a small per-skill set next to their skill (`skills/<name>/evals.jsonl`). Changes to a
skill ship with its evals.
