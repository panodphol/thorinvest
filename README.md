# ThorInvest v4 — one CIO agent loop

ThorInvest v4 folds three generations of KAsset Multi-Asset skills into one Claude Code plugin built
around a **single agent loop**, following Anthropic's guidance in
[*When to fold subagents into your main agent loop*](https://claude.com/resources/articles/building-agents-when-to-fold-subagents-into-your-main-agent-loop) (Oct 2026).

## What it replaces

| Before | Count | v4 |
|---|---|---|
| Standalone `thorinvest` orchestrator (v2.1) + `thorinvest-orchestrator` (v3.1) | 2 routers, conflicting skill IDs | 1 system prompt (`system/thor-system-prompt.md`), no router, no IDs |
| `thorinvest-core` + `thorinvest-extended` atomic skills | 119 | 13 folded skills + per-method reference files |
| Domain packages (macro, FS, alloc, PO, RM, PERF, GEO, IS, CI, mini-art, morning) | 12, 20–46 KB each | merged into the folded skills |
| Design skills (`kasset-ci`, `slide-mini-art`, CI-001…006, design_system) | 3 conflicting palettes | 1 token file, 2 explicit modes |
| `thor-interactive-presentation-designer` | 1 | kept as is (`thor-interactive-presentation`) |
| Gates written as prose | — | `thor-calc` MCP tools + `PreToolUse` write hook |

Skill text loaded up front fell from ~1.1 MB to ~43 KB; depth loads only when a method is used.

## Layout

```
.claude-plugin/plugin.json
system/thor-system-prompt.md        # the one prompt, injected by the SessionStart hook
hooks/                              # SessionStart prompt + write gate on email send / Drive writes
skills/                             # 14 skills, each SKILL.md <= ~5 KB
  macro-house-view  geopolitical-scenarios  portfolio-construction  risk
  performance-attribution  manager-research  product-origination  client-communication
  kasset-visual-system  thor-interactive-presentation
  workflow-morning-brief  workflow-ic-pack  workflow-event-response  workflow-monthly-review
  <skill>/references/procedures-index.md + procedures/<old-id>.md + knowledge files
agents/                             # only 3 subagents, each split by context, not by team
  research-fanout  client-output-verifier  ic-challenger
tools/thor_calc/                    # MCP server: 8 deterministic tools (maths + gates), unit-tested
knowledge/regulatory/               # SEC Thailand / BOT rulebook (shared)
evals/golden.jsonl                  # 10 end-to-end tasks (DRAFT), run twice each
docs/legacy-id-map.md               # old v2.1 / v3.1 IDs -> v4 skill (for audit trails only)
docs/migration.md                   # how to cut over and what to measure
```

## Design rules

- **Skills** hold how the team works (steps, rules, judgement). **Tools** hold actions, live data,
  fixed-shape maths and hard preconditions. **Subagents** exist only for parallel fan-out or a deliberately
  fresh context (verification, IC challenge).
- Domain teams own skills and their evals, not agents. The CIO office owns the system prompt and the
  end-to-end eval set.
- Keep the tool count under 30 and each SKILL.md short; put depth in `references/`.

## Regenerating internal content

The method files, knowledge base, design sources, `thor-interactive-presentation` and the legacy ID map are
KAsset-internal and are not in git. Rebuild them from the installed plugins:

```
python3 -I tools/migrate/fold.py <plugins_synced_dir> <skills_synced_dir> .
```

## Tests

```
python3 -m unittest discover -s tools/thor_calc/tests
```
Needs `numpy`; the server needs the `mcp` Python package (v1 or v2).
