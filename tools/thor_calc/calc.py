"""Deterministic portfolio maths for ThorInvest. Pure numpy; no I/O.

Every function returns plain dicts/lists so the MCP layer can pass results straight to the model.
"""
from __future__ import annotations

import math
from statistics import NormalDist

import numpy as np


# ---------------------------------------------------------------- risk
def risk_metrics(returns: list[float], confidence: float = 0.95, horizon_periods: int = 1,
                 periods_per_year: int = 252) -> dict:
    """Historical and parametric VaR/CVaR, volatility and max drawdown from a return series (decimals)."""
    r = np.asarray(returns, dtype=float)
    if r.size < 20:
        raise ValueError("need at least 20 observations")
    if not 0.5 < confidence < 1:
        raise ValueError("confidence must be in (0.5, 1)")
    scale = math.sqrt(horizon_periods)
    q = np.quantile(r, 1 - confidence)
    hist_var = -q * scale
    tail = r[r <= q]
    hist_cvar = -tail.mean() * scale
    mu, sd = r.mean(), r.std(ddof=1)
    z = NormalDist().inv_cdf(1 - confidence)
    para_var = -(mu * horizon_periods + z * sd * scale)
    para_cvar = -(mu * horizon_periods - sd * scale * NormalDist().pdf(z) / (1 - confidence))
    wealth = np.cumprod(1 + r)
    dd = wealth / np.maximum.accumulate(wealth) - 1
    trough = int(dd.argmin())
    return {
        "n_obs": int(r.size), "confidence": confidence, "horizon_periods": horizon_periods,
        "var_historical": float(hist_var), "cvar_historical": float(hist_cvar),
        "var_parametric": float(para_var), "cvar_parametric": float(para_cvar),
        "vol_annualised": float(sd * math.sqrt(periods_per_year)),
        "max_drawdown": float(dd.min()), "max_drawdown_trough_index": trough,
        "current_drawdown": float(dd[-1]),
        "note": "Losses reported as positive numbers. Historical VaR uses sqrt-time scaling.",
    }


def estimate_covariance(returns: list[list[float]], method: str = "ledoit_wolf") -> dict:
    """Covariance from a T x N return matrix. ledoit_wolf shrinks to scaled identity (LW 2004)."""
    X = np.asarray(returns, dtype=float)
    t, n = X.shape
    if t <= n:
        raise ValueError("need more observations than assets")
    Xc = X - X.mean(axis=0)
    S = Xc.T @ Xc / t
    if method == "sample":
        return {"cov": S.tolist(), "shrinkage": 0.0, "method": "sample"}
    if method != "ledoit_wolf":
        raise ValueError("method must be 'sample' or 'ledoit_wolf'")
    m = np.trace(S) / n
    F = m * np.eye(n)
    d2 = np.sum((S - F) ** 2)
    b2_bar = sum(np.sum((np.outer(x, x) - S) ** 2) for x in Xc) / t**2
    b2 = min(b2_bar, d2)
    delta = b2 / d2 if d2 > 0 else 1.0
    return {"cov": (delta * F + (1 - delta) * S).tolist(), "shrinkage": float(delta), "method": method}


# ---------------------------------------------------------------- optimisation
def _project_box_simplex(v: np.ndarray, lo: np.ndarray, hi: np.ndarray) -> np.ndarray:
    """Euclidean projection onto {w : sum w = 1, lo <= w <= hi} by bisection on the shift."""
    a, b = (lo - v).min() - 1, (hi - v).max() + 1
    for _ in range(200):
        tau = (a + b) / 2
        if np.clip(v + tau, lo, hi).sum() > 1:
            b = tau
        else:
            a = tau
    return np.clip(v + (a + b) / 2, lo, hi)


def optimize_weights(cov: list[list[float]], expected_returns: list[float] | None = None,
                     method: str = "mvo", risk_aversion: float = 3.0,
                     lower: list[float] | None = None, upper: list[float] | None = None) -> dict:
    """Fully-invested weights. mvo: max mu'w - (lambda/2) w'Sw with box bounds. erc: equal risk contribution."""
    S = np.asarray(cov, dtype=float)
    n = S.shape[0]
    lo = np.zeros(n) if lower is None else np.asarray(lower, float)
    hi = np.ones(n) if upper is None else np.asarray(upper, float)
    if lo.sum() > 1 + 1e-9 or hi.sum() < 1 - 1e-9:
        raise ValueError("bounds are infeasible for a fully invested portfolio")
    if method == "mvo":
        if expected_returns is None:
            raise ValueError("mvo needs expected_returns")
        mu = np.asarray(expected_returns, float)
        w = _project_box_simplex(np.full(n, 1 / n), lo, hi)
        step = 1 / (risk_aversion * np.linalg.eigvalsh(S).max() + 1e-12)
        for _ in range(5000):
            w_new = _project_box_simplex(w + step * (mu - risk_aversion * S @ w), lo, hi)
            if np.abs(w_new - w).max() < 1e-10:
                break
            w = w_new
        w = w_new
    elif method == "erc":
        w = np.full(n, 1 / n)
        for _ in range(10000):
            rc = w * (S @ w)
            w_new = w * (rc.mean() / rc) ** 0.5
            w_new /= w_new.sum()
            if np.abs(w_new - w).max() < 1e-12:
                break
            w = w_new
        w = w_new
        if (w < lo - 1e-9).any() or (w > hi + 1e-9).any():
            w = _project_box_simplex(w, lo, hi)
    else:
        raise ValueError("method must be 'mvo' or 'erc'")
    vol = float(math.sqrt(w @ S @ w))
    rc = w * (S @ w) / vol
    at_bound = [i for i in range(n) if abs(w[i] - lo[i]) < 1e-6 or abs(w[i] - hi[i]) < 1e-6]
    return {
        "weights": w.tolist(), "vol": vol,
        "risk_contribution_pct": (rc / vol).round(6).tolist(),
        "expected_return": None if expected_returns is None else float(np.dot(w, expected_returns)),
        "assets_at_bound": at_bound,
        "corner_solution_warning": len(at_bound) >= n - 1,
        "method": method,
    }


# ---------------------------------------------------------------- attribution
def performance_attribution(wp: list[float], wb: list[float], rp: list[float], rb: list[float],
                            segments: list[str] | None = None, method: str = "BF") -> dict:
    """Single-period Brinson. BF (Brinson-Fachler, default) or BHB. Returns per-segment and totals."""
    wp_, wb_, rp_, rb_ = (np.asarray(x, float) for x in (wp, wb, rp, rb))
    Rb = float(wb_ @ rb_)
    Rp = float(wp_ @ rp_)
    if method == "BF":
        alloc = (wp_ - wb_) * (rb_ - Rb)
    elif method == "BHB":
        alloc = (wp_ - wb_) * rb_
    else:
        raise ValueError("method must be 'BF' or 'BHB'")
    sel = wb_ * (rp_ - rb_)
    inter = (wp_ - wb_) * (rp_ - rb_)
    segs = segments or [f"seg{i}" for i in range(len(wp_))]
    total = alloc.sum() + sel.sum() + inter.sum()
    return {
        "portfolio_return": Rp, "benchmark_return": Rb, "active_return": Rp - Rb,
        "allocation": float(alloc.sum()), "selection": float(sel.sum()), "interaction": float(inter.sum()),
        "residual": float(Rp - Rb - total),
        "by_segment": [{"segment": s, "allocation": float(a), "selection": float(b), "interaction": float(c)}
                       for s, a, b, c in zip(segs, alloc, sel, inter)],
        "method": method,
    }


def link_attribution(periods: list[dict]) -> dict:
    """Carino-link single-period effects. Each period: portfolio_return, benchmark_return, allocation, selection, interaction."""
    def k(rp, rb):
        return 1.0 if abs(rp - rb) < 1e-12 else (math.log1p(rp) - math.log1p(rb)) / (rp - rb)
    Rp = math.prod(1 + p["portfolio_return"] for p in periods) - 1
    Rb = math.prod(1 + p["benchmark_return"] for p in periods) - 1
    K = k(Rp, Rb)
    out = {"allocation": 0.0, "selection": 0.0, "interaction": 0.0}
    for p in periods:
        f = k(p["portfolio_return"], p["benchmark_return"]) / K
        for e in out:
            out[e] += f * p[e]
    linked = sum(out.values())
    return {"portfolio_return": Rp, "benchmark_return": Rb, "active_return": Rp - Rb, **out,
            "residual": Rp - Rb - linked, "method": "Carino"}


# ---------------------------------------------------------------- implementation
def rebalance_trade_list(current: dict[str, float], target: dict[str, float], aum: float,
                         min_trade_pct: float = 0.0025) -> dict:
    """Trades (in currency units) to move current -> target weights, skipping trades below min_trade_pct of AUM."""
    names = sorted(set(current) | set(target))
    lines, skipped = [], []
    for n in names:
        dw = target.get(n, 0.0) - current.get(n, 0.0)
        row = {"asset": n, "from": current.get(n, 0.0), "to": target.get(n, 0.0),
               "delta_weight": round(dw, 6), "amount": round(dw * aum, 2),
               "side": "BUY" if dw > 0 else "SELL"}
        (lines if abs(dw) >= min_trade_pct else skipped).append(row)
    return {"aum": aum, "trades": lines, "below_threshold": skipped,
            "turnover_one_way": round(sum(abs(r["delta_weight"]) for r in lines) / 2, 6)}
