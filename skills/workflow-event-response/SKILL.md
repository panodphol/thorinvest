---
name: workflow-event-response
description: Market or geopolitical event response — triage, scenario tree, portfolio impact, stress, pre-committed CIO gameplan and internal/client communication. Use for "[event] — assess impact", "what do we do", shock days, war/sanctions/tariff headlines, or a sharp cross-asset move.
---

# Event Response

1. **Triage** (minutes) — what happened, verified sources, severity GREEN/AMBER/RED. GREEN → 5-bullet note.
2. **Scenarios** (`geopolitical-scenarios` or `macro-house-view`) — branches, probabilities, signposts.
3. **Impact** (`risk`) — stress each branch on current positions with `thor-calc`; limit hits; liquidity.
4. **Gameplan** — per trigger: pre-committed action, size, authority level. No trade list without
   `pretrade_check`.
5. **Comms** (`client-communication`) — internal alert first; RM talking points; client note only after
   `compliance_precheck` and CIO sign-off.

Gameplan method: `references/procedures/geo-010.md`.
