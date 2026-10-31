---
name: manager-research
description: Fund selection and manager due diligence for the Foreign Fund team — screening and ranking managers, quantitative DD (rolling returns, drawdown forensics, factor exposure), qualitative DD (team, process, ops), factsheet extraction, style drift, fee analysis, DD memos, watchlist monitoring, feeder-fund (SEC Thailand) compliance, onboarding, pipeline and RFP/DDQ responses. Use for any manager, fund, DD, factsheet or watchlist task.
---

# Manager Research & DD

## Steps
1. **Universe & screen.** Criteria first (mandate fit, track record length, AUM, fees, vehicle eligibility
   for feeder/FIF). Rank with explicit weights.
2. **Factsheets in bulk.** More than ~5 documents → delegate parsing to `research-fanout` (one document
   per worker, compact table back). Keep the judgment here.
3. **Quant DD.** Rolling returns, drawdown forensics, up/down capture, factor exposure, style drift,
   using `thor-calc.risk_metrics`. **Qual DD.** Team stability, process evidence, ops, alignment.
4. **Feeder/FIF check.** Master-fund eligibility and look-through per the rulebook §3/§5;
   `thor-calc.compliance_precheck` with `fund_type="feeder"`.
5. **Memo.** Recommendation, conviction, key risks, monitoring triggers. Manager approval is `[IC REQUIRED]`.

## Procedures (`references/procedures-index.md`)
Screening/ranking · DD memo · monitoring watchlist · quant DD · qual DD · factsheet parser · style drift ·
fees · RFP/DDQ · feeder compliance · onboarding · pipeline.

## Knowledge
`references/fs/dd_methodology.md` · `references/fs/monitoring_framework.md`.
