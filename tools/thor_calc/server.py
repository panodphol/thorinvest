"""thor-calc MCP server — intent-grouped tools for ThorInvest (8 tools; keep the total under 30)."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import calc  # noqa: E402
import gates  # noqa: E402

try:  # mcp >= 2
    from mcp.server.mcpserver import MCPServer as _Server
except ImportError:  # mcp 1.x
    from mcp.server.fastmcp import FastMCP as _Server

mcp = _Server("thor-calc", instructions="Deterministic maths and hard gates for ThorInvest. "
              "Use these instead of computing risk, optimisation, attribution or trade lists by hand.")


@mcp.tool()
def risk_metrics(returns: list[float], confidence: float = 0.95, horizon_periods: int = 1,
                 periods_per_year: int = 252) -> dict:
    """VaR/CVaR (historical + parametric), annualised vol, max and current drawdown from a decimal return series."""
    return calc.risk_metrics(returns, confidence, horizon_periods, periods_per_year)


@mcp.tool()
def estimate_covariance(returns: list[list[float]], method: str = "ledoit_wolf") -> dict:
    """Covariance from a T x N return matrix; method 'ledoit_wolf' (default) or 'sample'."""
    return calc.estimate_covariance(returns, method)


@mcp.tool()
def optimize_weights(cov: list[list[float]], expected_returns: list[float] | None = None,
                     method: str = "mvo", risk_aversion: float = 3.0,
                     lower: list[float] | None = None, upper: list[float] | None = None) -> dict:
    """Fully invested weights by 'mvo' (needs expected_returns) or 'erc'; flags corner solutions."""
    return calc.optimize_weights(cov, expected_returns, method, risk_aversion, lower, upper)


@mcp.tool()
def performance_attribution(wp: list[float], wb: list[float], rp: list[float], rb: list[float],
                            segments: list[str] | None = None, method: str = "BF") -> dict:
    """Single-period Brinson attribution (BF default, or BHB) with per-segment effects and residual."""
    return calc.performance_attribution(wp, wb, rp, rb, segments, method)


@mcp.tool()
def link_attribution(periods: list[dict]) -> dict:
    """Carino-linked multi-period attribution from per-period results of performance_attribution."""
    return calc.link_attribution(periods)


@mcp.tool()
def pretrade_check(mandate: str, pre: dict[str, float], post: dict[str, float]) -> dict:
    """Check post-trade exposures (var95_1m, te, single_issuer, cash, single_country, single_sector) vs the
    mandate template. Returns PASS/FLAG/FAIL per limit and a signoff_id unless FAIL."""
    return gates.pretrade_check(mandate, pre, post)


@mcp.tool()
def rebalance_trade_list(current: dict[str, float], target: dict[str, float], aum: float,
                         signoff_id: str, min_trade_pct: float = 0.0025) -> dict:
    """Trade list from current to target weights. Requires a signoff_id from pretrade_check."""
    signoff = gates.require_signoff(signoff_id)
    return {"signoff": signoff, **calc.rebalance_trade_list(current, target, aum, min_trade_pct)}


@mcp.tool()
def compliance_precheck(output_type: str, audience: str, fund_type: str) -> dict:
    """Checks required before delivering an output (client_letter, retail, rm_brief, social, video,
    allocation_change, provident, feeder, fx_hedge) plus rulebook freshness."""
    return gates.compliance_precheck(output_type, audience, fund_type)


if __name__ == "__main__":
    mcp.run()
