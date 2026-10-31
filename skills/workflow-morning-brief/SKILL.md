---
name: workflow-morning-brief
description: The daily pre-IC morning market brief — overnight Asia/Europe/US moves across equities, rates, FX (incl. USD/THB), commodities, today's data calendar and the top 3 themes with positioning implications, one page. Use for "morning brief", "daily brief", "overnight summary", "market update", or a scheduled weekday run.
---

# Morning Brief

1. **Context** — date (BKK), regime from the latest house view in session, open IC items.
2. **Overnight** — pull from LSEG (fallback: web, with staleness disclaimer): US close, Asia, Europe open;
   indices, UST 2Y/10Y, Bund/JGB, DXY, USD/THB, Brent/WTI, gold. Flag moves > 1σ. As-of on every line.
3. **Calendar** — today's releases with consensus/prior and sensitivity.
4. **Top 3 themes** — ranked by surprise × policy relevance × relevance to our positioning; each ends with
   a positioning implication.
5. **Format** — one page, `kasset-visual-system` Corporate Teal. Holiday → say so; do not pad.

Detail: `references/procedures/macro-001.md`, `references/procedures/macro-007.md`.
