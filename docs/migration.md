# Migration: v2.1 / v3.1 → v4

Principle from the article: measure, change one thing at a time, keep what holds up.

## 1. Baseline (before uninstalling anything)
Run `evals/golden.jsonl` twice on the current setup (standalone `thorinvest` + `thorinvest-core` +
`thorinvest-extended` + domain packages). Record pass/fail per rubric line, skills/tools used, latency, cost.

## 2. Cut over
- Install this plugin; disable `thorinvest-core`, `thorinvest-extended` and the standalone `thorinvest`,
  `macro-research-monitoring`, `fund-selection`, `portfolio-allocation`, `portfolio-optimizer`,
  `risk-management`, `performance-analyst`, `geopolitical-intelligence`, `investment-strategist`,
  `kasset-ci`, `slide-mini-art`, `morning`, `thor-interactive-presentation-designer` skills.
  Running both generations at once brings back the ID collision (see `legacy-id-map.md`).
- Re-run the evals twice. Compare **which tasks flipped**, not just the total.

## 3. Keep, revert or split
- A folded skill that scores worse on its tasks → split it back out (as a skill, not an agent) and re-test.
- A subagent is justified only if (a) the single loop degrades from context bloat on that task,
  (b) the work is parallel and disposable, or (c) the task needs a fresh, unbiased context.

## Known gaps in this scaffold
- `thor-calc` covers VaR/CVaR, covariance, MVO/ERC, Brinson, Carino, pre-trade check, trade list and the
  compliance checklist. Black-Litterman, HRP, Monte Carlo, FI/FX attribution and stress P&L are still
  prose procedures; move them into tools by usage.
- `gates.classify_breach_trade` uses a conservative default (always FAIL) pending the CIO's policy.
- Mandate limits are the rulebook's operating baselines and carry `[COMPLIANCE-REVIEW]`; Compliance must
  verify them against current TorNor 87/2558 and BOT text.
- v3.1 context files (`/thorinvest/context/*.json`, `thor_launcher.py`) were never present; positions now
  come from the user or a Drive/LSEG tool call, stated in each output.
- Per-skill KPI tables from v3.1 were dropped; replace them with per-skill eval files.
