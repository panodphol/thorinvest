import sys
import unittest
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import calc  # noqa: E402
import gates  # noqa: E402


class RiskTests(unittest.TestCase):
    def test_var_ordering_and_drawdown(self):
        r = np.random.default_rng(0).normal(0.0003, 0.01, 1000).tolist()
        m = calc.risk_metrics(r)
        self.assertGreater(m["cvar_historical"], m["var_historical"])
        self.assertAlmostEqual(m["var_parametric"], 0.01 * 1.645 - 0.0003, delta=0.002)
        self.assertLess(m["max_drawdown"], 0)

    def test_short_series_rejected(self):
        with self.assertRaises(ValueError):
            calc.risk_metrics([0.01] * 5)

    def test_ledoit_wolf_shrinks(self):
        X = np.random.default_rng(1).normal(0, 0.01, (60, 10)).tolist()
        out = calc.estimate_covariance(X)
        self.assertTrue(0 < out["shrinkage"] <= 1)


class OptimiserTests(unittest.TestCase):
    cov = [[0.04, 0.006, 0.0], [0.006, 0.01, 0.0], [0.0, 0.0, 0.0225]]

    def test_erc_equalises_risk(self):
        out = calc.optimize_weights(self.cov, method="erc")
        self.assertAlmostEqual(sum(out["weights"]), 1, places=6)
        for rc in out["risk_contribution_pct"]:
            self.assertAlmostEqual(rc, 1 / 3, places=4)

    def test_mvo_respects_bounds(self):
        out = calc.optimize_weights(self.cov, [0.08, 0.03, 0.05], upper=[0.5, 0.6, 0.5])
        w = out["weights"]
        self.assertAlmostEqual(sum(w), 1, places=6)
        self.assertTrue(all(0 <= x <= u + 1e-6 for x, u in zip(w, [0.5, 0.6, 0.5])))

    def test_mvo_matches_unconstrained_closed_form(self):
        # with loose bounds the solution equals the analytic budget-constrained optimum
        S, mu, lam = np.array(self.cov), np.array([0.08, 0.03, 0.05]), 3.0
        Si = np.linalg.inv(S); one = np.ones(3)
        gamma = (one @ Si @ mu - lam) / (one @ Si @ one)
        w_star = Si @ (mu - gamma * one) / lam
        self.assertTrue((w_star > 0).all())
        out = calc.optimize_weights(self.cov, mu.tolist(), risk_aversion=lam)
        np.testing.assert_allclose(out["weights"], w_star, atol=1e-4)


class AttributionTests(unittest.TestCase):
    def test_brinson_reconciles(self):
        a = calc.performance_attribution([0.6, 0.4], [0.5, 0.5], [0.05, 0.01], [0.04, 0.02], ["Eq", "FI"])
        self.assertAlmostEqual(a["residual"], 0, places=12)
        self.assertAlmostEqual(a["active_return"], 0.034 - 0.03, places=12)

    def test_carino_reconciles(self):
        p1 = calc.performance_attribution([0.6, 0.4], [0.5, 0.5], [0.05, 0.01], [0.04, 0.02])
        p2 = calc.performance_attribution([0.55, 0.45], [0.5, 0.5], [-0.02, 0.015], [-0.03, 0.01])
        linked = calc.link_attribution([p1, p2])
        self.assertAlmostEqual(linked["residual"], 0, places=10)


class GateTests(unittest.TestCase):
    pre = {"var95_1m": 0.02, "te": 0.01, "single_issuer": 0.05, "cash": 0.05}

    def test_pass_issues_signoff_and_unlocks_trade_list(self):
        r = gates.pretrade_check("core_balanced_domestic", self.pre, dict(self.pre, var95_1m=0.025))
        self.assertEqual(r["verdict"], "PASS")
        self.assertIn("signoff_id", r)
        self.assertEqual(gates.require_signoff(r["signoff_id"])["verdict"], "PASS")

    def test_flag_above_90pct(self):
        r = gates.pretrade_check("core_balanced_domestic", self.pre, dict(self.pre, var95_1m=0.028))
        self.assertEqual(r["verdict"], "FLAG")

    def test_breach_fails_without_signoff(self):
        r = gates.pretrade_check("core_balanced_domestic", self.pre, dict(self.pre, single_issuer=0.09))
        self.assertEqual(r["verdict"], "FAIL")
        self.assertNotIn("signoff_id", r)

    def test_min_limit_cash(self):
        r = gates.pretrade_check("core_balanced_domestic", self.pre, dict(self.pre, cash=0.02))
        self.assertEqual(r["verdict"], "FAIL")

    def test_missing_metric_flags(self):
        r = gates.pretrade_check("core_balanced_domestic", {}, {"var95_1m": 0.01})
        self.assertEqual(r["verdict"], "FLAG")

    def test_trade_list_requires_signoff(self):
        with self.assertRaises(PermissionError):
            gates.require_signoff("nope")

    def test_compliance_rulebook_staleness(self):
        fresh = gates.compliance_precheck("client_letter", "institutional", "mutual", today="2026-10-31")
        stale = gates.compliance_precheck("client_letter", "retail", "feeder", today="2027-03-01")
        self.assertEqual(fresh["status"], "CHECKLIST")
        self.assertEqual(stale["status"], "FLAG")
        self.assertIn("FIF disclosures and FX risk statement", stale["required_checks"])


if __name__ == "__main__":
    unittest.main()
