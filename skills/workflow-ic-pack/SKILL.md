---
name: workflow-ic-pack
description: Build the Investment Committee pack (weekly/bi-weekly IC or risk committee) — macro and house view refresh, TAA update, risk dashboard and stress, performance summary, decision items with authority labels, assembled as a 15–20 slide KAsset deck. Use for "prep the IC pack", "IC prep", "risk committee pack", "weekly CIO pack".
---

# IC Pack

Plan once, then run in one loop — you hold all components in context, so check them against each other
as you go (that is the reason this is not a chain of agents).

1. **Macro & house view** (`macro-house-view`) — regime, changes vs last IC.
2. **Portfolio** (`portfolio-construction`) — current vs SAA/TAA, proposed tilts, TE budget check.
3. **Risk** (`risk`) — dashboard, VaR/TE vs limits, stress on the house-view bear case. Run the
   `thor-calc` tools; no numbers without tool output or source.
4. **Performance** (`performance-attribution`) — period attribution, linked YTD.
5. **Consistency gate** — same numbers across sections; house view ↔ tilts ↔ risk all agree. Fix or flag.
6. **Decisions** — table of items with `[RECOMMEND]` / `[CIO DECISION]` / `[IC REQUIRED]`.
7. **Challenge** — run `ic-challenger` on the draft; add its three strongest objections and our answers.
8. **Assemble** — `kasset-visual-system` Corporate Teal; stale component (> 5 business days) → refresh
   or a gap slide, never silent.

Risk-committee variant: `references/procedures/rm-008.md`.
