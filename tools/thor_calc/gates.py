"""Hard gates for ThorInvest: pre-trade limit check and compliance pre-check.

These are in code, not prose, because a skill instruction can be skipped and a tool precondition cannot.

Limits below are the *operating baselines* from knowledge/regulatory/sec_thailand_rulebook.md §4
(reviewed 2026-06-10). That file carries a [COMPLIANCE-REVIEW] warning: KAsset Compliance must verify
every figure against current TorNor 87/2558 and BOT notifications before client or regulatory use.
"""
from __future__ import annotations

import datetime as dt
import hashlib
import json

RULEBOOK_REVIEWED = dt.date(2026, 6, 10)
RULEBOOK_MAX_AGE_DAYS = 183

# metric -> (kind, limit). kind "max": value must be <= limit; "min": value must be >= limit.
MANDATE_LIMITS: dict[str, dict[str, tuple[str, float]]] = {
    "core_balanced_domestic": {"var95_1m": ("max", 0.03), "te": ("max", 0.025),
                               "single_issuer": ("max", 0.08), "cash": ("min", 0.03)},
    "fif_equity": {"var95_1m": ("max", 0.06), "te": ("max", 0.05), "cash": ("min", 0.02),
                   "single_country": ("max", 0.40), "single_sector": ("max", 0.30)},
    "fif_fixed_income": {"var95_1m": ("max", 0.02), "te": ("max", 0.015),
                         "single_issuer": ("max", 0.05), "cash": ("min", 0.05)},
    "private_fund": {"var95_1m": ("max", 0.07), "te": ("max", 0.06)},
}
FLAG_UTILISATION = 0.90  # RM-004: >90% utilisation post-trade -> FLAG

_SIGNOFFS: dict[str, dict] = {}


def _utilisation(kind: str, limit: float, value: float) -> float:
    if kind == "max":
        return value / limit
    return float("inf") if value <= 0 else limit / value


def classify_breach_trade(pre_util: float, post_util: float) -> str:
    """Verdict for a limit that is in breach AFTER the trade (post_util > 1.0).

    The policy question: if the portfolio was already in breach before the trade (pre_util > 1.0) and the
    trade REDUCES the breach (post_util < pre_util), is that trade allowed?

    TODO(Tor): replace the conservative default below with KAsset's policy. Options to weigh:
      - "FAIL" always: simplest, but blocks remediation trades that move toward compliance.
      - "FLAG" when post_util < pre_util: lets remediation through with a human sign-off.
      - "FLAG" only if the reduction is material (e.g. closes >= X% of the gap), else "FAIL".
    Return one of "FAIL" or "FLAG".
    """
    return "FAIL"


def pretrade_check(mandate: str, pre: dict[str, float], post: dict[str, float]) -> dict:
    """Check post-trade exposures against the mandate template. Returns verdicts and, unless FAIL, a sign-off id."""
    if mandate not in MANDATE_LIMITS:
        raise ValueError(f"unknown mandate '{mandate}'; known: {sorted(MANDATE_LIMITS)}")
    rows, worst = [], "PASS"
    order = {"PASS": 0, "FLAG": 1, "FAIL": 2}
    for metric, (kind, limit) in MANDATE_LIMITS[mandate].items():
        if metric not in post:
            verdict, u_pre, u_post = "FLAG", None, None
            note = "NOT PROVIDED — manual review required"
        else:
            u_post = _utilisation(kind, limit, post[metric])
            u_pre = _utilisation(kind, limit, pre[metric]) if metric in pre else None
            if u_post > 1.0:
                verdict = classify_breach_trade(u_pre if u_pre is not None else u_post, u_post)
                note = "breach after trade"
            elif u_post > FLAG_UTILISATION:
                verdict, note = "FLAG", f"utilisation > {FLAG_UTILISATION:.0%}"
            else:
                verdict, note = "PASS", ""
        worst = max(worst, verdict, key=order.get)
        rows.append({"metric": metric, "kind": kind, "limit": limit, "pre": pre.get(metric),
                     "post": post.get(metric), "utilisation_pre": u_pre, "utilisation_post": u_post,
                     "verdict": verdict, "note": note})
    result = {"mandate": mandate, "verdict": worst, "checks": rows,
              "binding_layer": "rulebook §4 operating baseline — confirm prospectus/IPS/internal/CIO overlay",
              "compliance_note": "[COMPLIANCE-REVIEW] limits are operating baselines, not verified regulatory text"}
    if worst != "FAIL":
        payload = json.dumps({"mandate": mandate, "post": post}, sort_keys=True)
        sid = hashlib.sha256(payload.encode()).hexdigest()[:12]
        _SIGNOFFS[sid] = {"mandate": mandate, "verdict": worst, "ts": dt.datetime.now().isoformat()}
        result["signoff_id"] = sid
    return result


def require_signoff(signoff_id: str | None) -> dict:
    """Precondition used by the trade-list tool."""
    if not signoff_id or signoff_id not in _SIGNOFFS:
        raise PermissionError("No valid pretrade_check sign-off. Run pretrade_check on the post-trade "
                              "exposures first; a trade list cannot be produced without it.")
    return _SIGNOFFS[signoff_id]


# output_type -> checks (from subsystems/compliance_filter.md gate triggers, v3.1)
GATE_TRIGGERS = {
    "client_letter": ["disclosure language", "suitability", "SEC retail communication rules"],
    "retail": ["plain-language risk statement", "SEC risk level 1-8 disclosure", "suitability"],
    "rm_brief": ["internal-only marking or full disclosures if forwarded", "no performance promises"],
    "social": ["SEC social media disclosure rules", "no performance promises", "balanced risk statement"],
    "video": ["disclosure on screen and in script", "no performance promises"],
    "allocation_change": ["mandate limits", "TorNor investment limits (run pretrade_check)"],
    "provident": ["TorNor provident-fund hard constraints", "member-level suitability"],
    "feeder": ["master-fund eligibility", "look-through", "BOT FX / foreign investment quota headroom"],
    "fx_hedge": ["BOT FX regulations", "hedge ratio within prospectus range"],
}


def compliance_precheck(output_type: str, audience: str, fund_type: str,
                        today: str | None = None) -> dict:
    """Return the checks that must be satisfied before this output is delivered, plus rulebook freshness."""
    if output_type not in GATE_TRIGGERS:
        raise ValueError(f"unknown output_type; known: {sorted(GATE_TRIGGERS)}")
    d = dt.date.fromisoformat(today) if today else dt.date.today()
    age = (d - RULEBOOK_REVIEWED).days
    checks = list(GATE_TRIGGERS[output_type])
    if audience in {"retail", "bancassurance"} and "suitability" not in checks:
        checks.append("suitability")
    if fund_type in {"feeder", "fif"} and output_type != "feeder":
        checks.append("FIF disclosures and FX risk statement")
    status = "CHECKLIST"  # the model/verifier must tick every item; this tool cannot read the draft's meaning
    flags = []
    if age > RULEBOOK_MAX_AGE_DAYS:
        flags.append(f"Rulebook last reviewed {RULEBOOK_REVIEWED} ({age} days) — refresh before client use")
        status = "FLAG"
    return {"status": status, "required_checks": checks, "flags": flags,
            "next_step": "Run the client-output-verifier subagent on the draft; deliver only on PASS.",
            "rulebook": "knowledge/regulatory/sec_thailand_rulebook.md"}
