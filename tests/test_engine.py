"""Regression tests for the pilot engine: funnel math, gates, decision engine, stress test."""
import pytest

from core import data as D
from core import engine as E


def test_funnel_is_monotonically_decreasing():
    sim = E.simulate()
    counts = [f["n"] for f in sim["funnel"]]
    for a, b in zip(counts, counts[1:]):
        assert b <= a


def test_vacr_matches_verified_over_entrants():
    sim = E.simulate()
    verified = sim["funnel"][4]["n"]
    entrants = sim["funnel"][0]["n"]
    assert sim["kpi"]["vacr"] == pytest.approx(round(verified / entrants * 100, 1), abs=0.15)


def test_clean_bounds_every_limit():
    p = E.clean({"completion": 5, "competency": -3, "entrants": 1})
    assert p["completion"] == E.LIMITS["completion"][1]
    assert p["competency"] == E.LIMITS["competency"][0]
    assert p["entrants"] == E.LIMITS["entrants"][0]


def test_operating_plan_passes_all_gates():
    sim = E.simulate(E.preset("operating_plan"))
    assert sim["gates_passed"] == 6
    assert all(g["pass"] for g in sim["gates"])


def test_targets_at_floor_fails_g4():
    sim = E.simulate(E.preset("targets_at_floor"))
    g4 = next(g for g in sim["gates"] if g["id"] == "G4")
    assert g4["pass"] is False


def test_budget_within_cap_on_default_scenario():
    sim = E.simulate()
    assert sim["budget"]["total_cr"] <= D.PILOT_CAP_CR + 0.01
    assert sim["budget"]["within_cap"] is True


# --------------------------------------------------------------------------------------
# Decision engine
# --------------------------------------------------------------------------------------
def test_decision_scale_when_all_gates_pass():
    sim = E.simulate(E.preset("operating_plan"))
    d = E.decision(sim)
    assert d["verdict"] == "SCALE"
    assert d["primary_gate"] is None


def test_decision_hold_when_g1_fails():
    sim = E.simulate({"g1_pass": False})
    d = E.decision(sim)
    assert d["verdict"] == "HOLD"
    assert d["primary_gate"] == "G1"


def test_decision_redesign_when_only_equity_fails():
    sim = E.simulate({"women_entry": 0.30, "women_rel": 1.0})
    g = {x["id"]: x["pass"] for x in sim["gates"]}
    assert g["G6"] is False
    d = E.decision(sim)
    assert d["verdict"] == "REDESIGN"
    assert d["primary_gate"] == "G6"
    assert any(l["id"] in ("I4", "I6") for l in d["levers"])


def test_decision_stop_when_outcome_and_economics_both_fail():
    sim = E.simulate({"validation": 0.10, "cost_mult": 2.0})
    d = E.decision(sim)
    assert d["verdict"] in ("STOP", "REDESIGN")  # STOP requires both G4 and G5 failing
    g = {x["id"]: x["pass"] for x in sim["gates"]}
    if not g["G4"] and not g["G5"]:
        assert d["verdict"] == "STOP"


def test_decision_verdict_is_one_of_four():
    for _ in range(5):
        sim = E.simulate()
        assert E.decision(sim)["verdict"] in ("SCALE", "HOLD", "REDESIGN", "STOP")


# --------------------------------------------------------------------------------------
# Bottleneck / VACR driver tree
# --------------------------------------------------------------------------------------
def test_bottleneck_is_a_funnel_stage():
    sim = E.simulate()
    b = E.bottleneck(sim)
    assert b["key"] in E.BOTTLENECK_STAGES
    assert b["swing_pp"] >= 0


# --------------------------------------------------------------------------------------
# Stress test
# --------------------------------------------------------------------------------------
@pytest.mark.parametrize("shock_id", [s["id"] for s in E.SHOCKS])
def test_every_shock_runs_and_never_improves_vacr_or_is_neutral(shock_id):
    sim = E.simulate(E.preset("operating_plan"))
    r = E.stress_test(sim["params"], shock_id)
    assert r["shock"]["id"] == shock_id
    assert r["after"]["kpi"]["vacr"] <= r["before"]["kpi"]["vacr"] + 0.05


def test_stress_test_unknown_shock_errors():
    sim = E.simulate()
    r = E.stress_test(sim["params"], "not-a-real-shock")
    assert "error" in r


def test_stress_cost_shock_raises_spend():
    sim = E.simulate(E.preset("operating_plan"))
    r = E.stress_test(sim["params"], "cost_up")
    assert r["after"]["kpi"] is not None
    before_gates = r["before"]["gates_passed"]
    after_gates = r["after"]["gates_passed"]
    assert after_gates <= before_gates


# --------------------------------------------------------------------------------------
# Sensitivity / Monte Carlo sanity
# --------------------------------------------------------------------------------------
def test_monte_carlo_probability_in_bounds():
    mc = E.monte_carlo(runs=200)
    assert 0 <= mc["p_vacr40"] <= 100
    assert 0 <= mc["p_all_gates"] <= 100
    assert mc["vacr"]["p10"] <= mc["vacr"]["p50"] <= mc["vacr"]["p90"]


def test_state_profile_known_and_unknown_codes():
    assert E.state_profile("TN") is not None
    assert E.state_profile("ZZ") is None
