"""Fold ThorInvest v3.1 atomic skills + knowledge base into the v4 single-loop plugin layout.

The generated content is KAsset-internal and is NOT committed (see .gitignore). Regenerate it locally:

    python3 -I tools/migrate/fold.py <plugins_synced_dir> <skills_synced_dir> .

<plugins_synced_dir> holds thorinvest-core/ and thorinvest-extended/;
<skills_synced_dir> holds the standalone kasset-ci, slide-mini-art, thor-interactive-presentation-designer
and domain packages.
"""
import re, shutil, sys
from pathlib import Path

SRC = Path(sys.argv[1])          # dir containing thorinvest-core / thorinvest-extended
MONO = Path(sys.argv[2])         # synced standalone skills dir (v2.1 monoliths)
OUT = Path(sys.argv[3])          # plugin root

# atomic skill dir-name prefix -> folded skill (explicit overrides first)
OVERRIDE = {
    "macro-001": "workflow-morning-brief", "macro-007": "workflow-morning-brief",
    "macro-012": "geopolitical-scenarios",
    "is-001": "macro-house-view", "is-009": "macro-house-view",
    "alloc-009": "portfolio-construction", "rm-017": "portfolio-construction", "perf-009": "portfolio-construction",  # FX trio
    "alloc-008": "portfolio-construction", "rm-012": "portfolio-construction",  # DV01 pair
    "rm-008": "workflow-ic-pack", "perf-006": "workflow-monthly-review", "perf-014": "workflow-monthly-review",
    "geo-010": "workflow-event-response",
}
PREFIX = {"macro": "macro-house-view", "geo": "geopolitical-scenarios", "alloc": "portfolio-construction",
          "po": "portfolio-construction", "rm": "risk", "perf": "performance-attribution",
          "fs": "manager-research", "prod": "product-origination", "is": "client-communication",
          "ci": "kasset-visual-system"}
KB = {  # knowledge-base folder -> owning folded skill
    "macro": "macro-house-view", "geo": "geopolitical-scenarios", "alloc": "portfolio-construction",
    "po": "portfolio-construction", "ltcma": "portfolio-construction", "rm": "risk",
    "perf": "performance-attribution", "fs": "manager-research", "prod": "product-origination",
    "is": "client-communication", "regulatory": "_shared",
}
KEEP = ["Purpose", "Methodology", "Output Specification", "Regulatory Constraints", "Failure Modes"]

def sections(md):
    body = re.split(r"^---\s*$", md, maxsplit=2, flags=re.M)[-1]
    out, cur = {}, None
    for line in body.splitlines():
        m = re.match(r"^## (.+)", line)
        if m:
            cur = m.group(1).strip(); out[cur] = []; continue
        if cur: out[cur].append(line)
    return {k: "\n".join(v).strip() for k, v in out.items()}

def fm(md, key):
    m = re.search(rf"^{key}:\s*(.+)$", md, flags=re.M)
    return m.group(1).strip() if m else ""

procs, idmap = {}, []
for pkg in ("thorinvest-core", "thorinvest-extended"):
    for d in sorted((SRC / pkg / "skills").iterdir()):
        md = (d / "SKILL.md").read_text()
        key = "-".join(d.name.split("-")[:2])
        target = OVERRIDE.get(key) or PREFIX[d.name.split("-")[0]]
        sid, name = fm(md, "skill_id"), fm(md, "skill_name")
        sec = sections(md)
        block = [f"## {sid} — {name}", f"_Folded from `{pkg}/{d.name}` (v3.1)._", ""]
        for k in KEEP:
            if sec.get(k):
                block += [f"### {k}", sec[k], ""]
        procs.setdefault(target, []).append("\n".join(block))
        idmap.append((sid, name, pkg, target))

for target, blocks in procs.items():
    ref = OUT / "skills" / target / "references" / "procedures"; ref.mkdir(parents=True, exist_ok=True)
    idx = []
    for b in blocks:
        title = b.splitlines()[0][3:]
        sid = title.split(" ")[0].lower()
        (ref / f"{sid}.md").write_text(b + "\n")
        idx.append(f"| `procedures/{sid}.md` | {title.split(' — ',1)[1]} |")
    (OUT / "skills" / target / "references" / "procedures-index.md").write_text(
        "| File | Procedure |\n|---|---|\n" + "\n".join(idx) + "\n")
for folder, target in KB.items():
    src = SRC / "thorinvest-core" / "knowledge-base" / folder
    dst = (OUT / "knowledge" / "regulatory") if target == "_shared" else (OUT / "skills" / target / "references" / folder)
    dst.mkdir(parents=True, exist_ok=True)
    for f in src.glob("*.md"):
        shutil.copy(f, dst / f.name)

# design sources -> kasset-visual-system references
vis = OUT / "skills" / "kasset-visual-system" / "references"; vis.mkdir(parents=True, exist_ok=True)
shutil.copy(MONO / "kasset-ci" / "SKILL.md", vis / "source-kasset-ci-2026.md")
shutil.copy(MONO / "slide-mini-art" / "SKILL.md", vis / "source-slide-mini-art.md")
shutil.copy(SRC / "thorinvest-core" / "design_system" / "kasset_ci.md", vis / "source-design-system-v3.1.md")
for f in (MONO / "slide-mini-art").rglob("*"):
    if f.is_file() and f.name != "SKILL.md":
        shutil.copy(f, vis / f"mini-art-{f.name}")

# thor-interactive-presentation: kept as-is (already a single-loop workflow skill)
tip = OUT / "skills" / "thor-interactive-presentation"; tip.mkdir(parents=True, exist_ok=True)
txt = (MONO / "thor-interactive-presentation-designer" / "SKILL.md").read_text()
txt = txt.replace("name: thor-interactive-presentation-designer", "name: thor-interactive-presentation", 1)
anchor = "### Phase 3 — Art direction\n"
txt = txt.replace(anchor, anchor + "\n> **ThorInvest:** start art direction from `kasset-visual-system` tokens "
                  "(`references/tokens.css`). Pick Corporate Teal or Mini-Art Dark-Gold; add a new palette only "
                  "with a stated reason.\n", 1)
(tip / "SKILL.md").write_text(txt)

# legacy ID map: v3.1 atomic + v2.1 monolith IDs (which collide)
rows = ["| v3.1 ID | v3.1 name | Source package | Folded into |", "|---|---|---|---|"]
rows += [f"| {a} | {b} | {c} | `{t}` |" for a, b, c, t in sorted(idmap)]
mono_rows = ["| v2.1 ID | v2.1 function | v2.1 package |", "|---|---|---|"]
for pkg in ["macro-research-monitoring", "fund-selection", "portfolio-allocation", "portfolio-optimizer",
            "risk-management", "performance-analyst", "geopolitical-intelligence", "investment-strategist"]:
    seen = set()
    for m in re.finditer(r"\b((?:MACRO|ALLOC|RM|FS|IS|GEO|PERF|PO)-\d{3}):\s*`?([A-Za-z_ ][^`|\n]{2,60})`?", (MONO / pkg / "SKILL.md").read_text()):
        if m.group(1) not in seen:
            seen.add(m.group(1)); mono_rows.append(f"| {m.group(1)} | {m.group(2).strip().strip('*')} | {pkg} |")
(OUT / "docs").mkdir(exist_ok=True)
(OUT / "docs" / "legacy-id-map.md").write_text(
    "# Legacy ID map\n\nSkill IDs are retired in v4. Route by intent, not by ID. This map exists only so old "
    "prompts, IC minutes and audit logs can be traced.\n\n**Warning:** v2.1 and v3.1 reuse the same IDs for "
    "different functions (e.g. MACRO-001 = FOMC summary in v2.1, morning brief in v3.1). Never resolve an old ID "
    "without knowing which generation produced it.\n\n## v3.1 atomic skills (thorinvest-core / -extended)\n\n"
    + "\n".join(rows) + "\n\n## v2.1 monolith functions (standalone packages)\n\n" + "\n".join(mono_rows) + "\n")
print({k: len(v) for k, v in procs.items()}, len(idmap))
