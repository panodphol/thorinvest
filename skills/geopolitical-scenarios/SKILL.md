---
name: geopolitical-scenarios
description: Geopolitical risk for portfolios — risk assessment, probability-weighted scenario trees, SITREPs, escalation ladders, signpost/trigger tracking, expert-opinion calibration, sanctions and trade-war analysis, historical analogs, geopolitics-to-macro transmission and portfolio impact mapping. Use for any conflict, sanctions, tariff, election shock or "what happens to the portfolio if…" question.
---

# Geopolitical Scenarios

## Steps
1. **Severity triage** (GREEN/AMBER/RED) with the reason; GREEN → short note, stop.
2. **Scenario tree.** Base / escalation / de-escalation (add tails if material). Probabilities sum to 100%,
   calibrated per `references/geo/probability_calibration.md`; show the calibration, not just the number.
3. **Transmission.** Supply-shock channel, safe-haven FX, energy, rates, risk premia → asset-class P&L per
   branch. Use `thor-calc.risk_metrics` / stress inputs for the numbers.
4. **Signposts.** For each branch: observable triggers that would move probabilities, with thresholds.
5. **Output.** SITREP format (Situation, Background, Assessment, Implications, Signposts) or the CIO
   gameplan (pre-committed actions per trigger — see `workflow-event-response`).

## Procedures (`references/procedures-index.md`)
Risk assessor · scenario tree · SITREP · portfolio impact mapper · escalation ladder · expert synthesis ·
signpost tracker · sanctions/trade war · historical analogs · geopolitical–macro integration.

## Knowledge
`references/geo/` — theater profiles, historical analogs, quantitative indicators, expert synthesis,
probability calibration.

## Subagent
For broad source gathering (many think-tanks, news, expert views) delegate to `research-fanout` and
synthesise here — keep the scenario judgment in the main loop.
