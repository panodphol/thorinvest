---
name: kasset-visual-system
description: The single KAsset visual system — design tokens, typography, layout grammar and chart rules for every formatted ThorInvest output (PPTX IC packs, client decks, A4 memos and reports, HTML dashboards, infographics and visual cards). Two modes: Corporate Teal (default, KAsset CI 2026) and Mini-Art Dark-Gold (executive visual cards, CIO personal brand). Use whenever a ThorInvest output is formatted, rendered or styled.
---

# KAsset Visual System

One token file, two modes. Do not mix modes in one deliverable.

## Pick the mode
| Output | Mode |
|---|---|
| IC pack, risk committee, client deck, A4 memo/report, factsheet, dashboard | **Corporate Teal** (default) |
| Executive visual card, CIO keynote/personal-brand visual, "black and gold", "mini art" | **Mini-Art Dark-Gold** |
| Interactive stage deck | Either — chosen in `thor-interactive-presentation` art direction |

## Tokens
Canonical values: `references/tokens.css` (CSS custom properties) and `references/tokens.md` (PPTX/DOCX).
Never hard-code hex values elsewhere.

## Rules that apply in both modes
- Arial only. No gradients, drop shadows or 3D.
- Max 3 non-neutral colours per slide/section. White space is deliberate.
- Charts: one highlighted series, others muted; sources and as-of date on every exhibit.
- Corporate Teal: teal family dominates; the only warm colour is RAG red `--k-rag-red`, for status only.
- Mini-Art: gold is for titles and hero numbers only; body text is off-white.

## Sizes
Projected / stage: KAsset minimums (title ≥ 36pt, body ≥ 22pt, footnote ≥ 13pt).
On-screen cards (Mini-Art): 800×450 base, body 13–16px. When in doubt, cut content, not font size.

## Sources (read only when a detail is not covered above)
`references/source-kasset-ci-2026.md` (slide archetypes, grid) ·
`references/source-slide-mini-art.md` + `mini-art-demo_slide.html` · `references/source-design-system-v3.1.md` ·
`references/procedures-index.md` (IC deck templates, client library, infographics, A4 formatter).
