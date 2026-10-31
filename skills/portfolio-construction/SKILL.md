---
name: portfolio-construction
description: Portfolio construction end to end — SAA from capital market assumptions (JPMAM LTCMA, BlackRock, KAsset CMA, multi-source blend), TAA overlay, scenario-weighted and core-satellite design, hierarchical decomposition, risk budgeting, optimisation (MVO, Black-Litterman, shrinkage, risk parity/ERC, HRP, Monte Carlo, robust, regime-conditional), duration/DV01 targeting, FX hedge ratio, alternatives, provident/feeder/fund-structure constraints, rebalancing, trade lists, pre-trade TCA and the allocation change log. Use for any weights, allocation, optimisation, rebalance or implementation task.
---

# Portfolio Construction

## Steps
1. **Mandate & constraints.** Fund type (retail / private / provident / feeder-FIF), benchmark, risk
   template and binding-limit cascade from `${CLAUDE_PLUGIN_ROOT}/knowledge/regulatory/sec_thailand_rulebook.md`.
2. **Inputs.** CMAs (state provider and vintage), house view from `macro-house-view`, covariance via
   `thor-calc.estimate_covariance` (Ledoit-Wolf default).
3. **Construct.** Pick the method that fits the question, say why, and run it in `thor-calc.optimize_weights`.
   Check for corner solutions; if one appears, explain it and constrain or switch to ERC/robust.
4. **Translate.** Asset class → region → country → sector/factor → duration/DV01/curve → FX hedge.
   The FX and DV01 views here are the single source for risk and attribution (no duplicate versions).
5. **Implement.** `thor-calc.pretrade_check` → only on PASS/FLAG with sign-off, `thor-calc.rebalance_trade_list`.
   Then log the decision (prior → new weights, rationale, authority level).

## Procedures (`references/procedures-index.md`)
30 methods: SAA/LTCMA, TAA, hierarchy, scenario allocator, risk budget, drift, core-satellite, DV01,
FX overlay/risk/decomposition, change log, alternatives, trade list, TCA, provident, fund structure,
MVO, BL, shrinkage, ERC, HRP, Monte Carlo, frontier, corner solutions, ML forecasts, regime-conditional,
robust, multi-source LTCMA.

## Knowledge
`references/alloc/` (hierarchy, scenarios, constraints, execution, templates) ·
`references/po/` (MVO, BL, covariance, simulation, ML, constraint library) · `references/ltcma/`.

## Authority
Calculations `[AUTO]` · TAA tilts `[RECOMMEND]` · SAA, limits `[CIO DECISION]` · mandate changes `[IC REQUIRED]`.
