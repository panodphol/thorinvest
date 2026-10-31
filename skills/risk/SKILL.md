---
name: risk
description: Investment risk for multi-asset portfolios — RAG risk dashboard, VaR/CVaR/ES, tracking error, stress tests (historical and hypothetical), drawdown and recovery, risk-budget slack, liquidity, counterparty, concentration, factor risk, model risk/backtesting, tail risk, operational flags and SEC Thailand (TorNor 87/2558) limit compliance reporting. Use for any risk number, limit, breach, stress or risk committee question.
---

# Risk

## Steps
1. **Measure with tools.** `thor-calc.risk_metrics` for VaR/CVaR/vol/drawdown; never estimate by eye.
   State method, confidence, horizon and data window.
2. **Against limits.** Compare with the mandate template and binding layer
   (`${CLAUDE_PLUGIN_ROOT}/knowledge/regulatory/sec_thailand_rulebook.md` §1, §4). RAG: GREEN < 90%
   utilisation ≤ AMBER < 100% ≤ RED.
3. **Stress.** Historical (GFC, COVID, Taper Tantrum, 2022 rates) and hypothetical from the house view /
   geopolitical branches. Report P&L, limit hits and liquidity under stress.
4. **So what.** Breaches → remediation options with size; slack → where risk budget is under-used.
5. DV01 and FX risk views come from `portfolio-construction` (single source).

## Procedures (`references/procedures-index.md`)
Dashboard · VaR/CVaR/ES · TE · pre-trade checker · stress engine · drawdown · risk partner advisory ·
liquidity · counterparty · concentration · factor risk · model risk · tail risk · op-risk flags ·
regulatory compliance reporter.

## Knowledge
`references/rm/` — governance, measurement, budgeting, stress testing, monitoring & control.

## Authority
Measurement `[AUTO]` · remediation `[RECOMMEND]` · limit changes `[CIO DECISION]` / `[IC REQUIRED]`.
