"""
Pilot engine for the AI Skill Ladder Control Tower.

The model is deliberately a transparent conversion funnel, not an ROI projection:
  entrants -> completed -> competent (independent assessment) -> transitioned (apprenticeship / project / deployment)
  -> verified (employer-validated workplace competency = VACR numerator) -> moved (job, promotion, redeployment at 6-12 mo)
Every rate is an input the user controls. Benefits are tested against a break-even, never assumed.
"""
import math
import random
from copy import deepcopy

from . import data as D

RATE_KEYS = ["completion", "competency", "uptake", "validation", "move"]
DEFAULT = {
    "entrants": 150000,
    "completion": 0.76, "competency": 0.73, "uptake": 0.86, "validation": 0.88, "move": 0.75,
    "employer_sat": 0.82,
    "women_entry": 0.48, "women_rel": 1.00, "tier_entry": 0.86, "tier_rel": 0.95,
    "cost_mult": 1.00,
    "earnings": 24434, "uplift": 0.10, "years": 2,
    "g1_pass": True,
    "lines": {},
}
LIMITS = {"entrants": (1000, 1000000), "completion": (0.05, 0.99), "competency": (0.05, 0.99), "uptake": (0.05, 0.99),
          "validation": (0.05, 0.99), "move": (0.05, 0.99), "employer_sat": (0.1, 1.0), "women_entry": (0.05, 0.95),
          "women_rel": (0.5, 1.5), "tier_entry": (0.05, 0.99), "tier_rel": (0.5, 1.5), "cost_mult": (0.5, 2.0),
          "earnings": (5000, 200000), "uplift": (0.0, 0.6), "years": (1, 5)}

PRESETS = {
    "operating_plan": {"name": "Operating plan with buffer", "note": "Stage rates that make the proposed targets add up with ≈2 pp headroom: VACR ≈42%, women-led cohorts lift women's entry share to 48%.",
                       "params": {}},
    "targets_at_floor": {"name": "Targets at their floors", "note": "Completion 70% and competency 60% exactly: shows VACR cannot reach 40% unless ≥95% of competent learners are workplace-validated.",
                         "params": {"completion": 0.70, "competency": 0.60}},
    "today_proxy": {"name": "Today's system (illustrative)", "note": "FSP completion 58% with assumed downstream rates; entry equity mix as reported. Illustrative only: downstream rates are not published.",
                    "params": {"completion": 0.583, "competency": 0.60, "uptake": 0.30, "validation": 0.70, "women_entry": 0.41, "employer_sat": 0.65}},
    "stretch": {"name": "Stretch plan", "note": "Upper-end rates if hubs, apprenticeships and outcome payments all land.",
                "params": {"completion": 0.80, "competency": 0.78, "uptake": 0.88, "validation": 0.90, "employer_sat": 0.86}},
}

# Plain-language explainers for the four planning scenarios above (see /scenarios).
SCENARIO_EXPLAINERS = {
    "operating_plan": {
        "plain": "The plan the team actually recommends running. Every stage rate is set a little above the bare minimum needed, so a normal amount of bad luck or slippage still lands on target.",
        "analogy": "Like leaving 15 minutes early for a train instead of timing it to the minute.",
        "seen_in": ["Pilot simulator: the default preset and the starting point for every guided demo",
                    "Strategy lab: the \"3.0 portfolio\" state selection",
                    "KPIs and gates: the baseline each gate is tested against"],
    },
    "targets_at_floor": {
        "plain": "What happens if every stage hits its published target exactly, with zero headroom. It is a stress test, not a plan: it shows the published floors don't add up to the 40% VACR goal on their own.",
        "analogy": "Like a bus schedule with no slack: one late connection and the whole trip fails.",
        "seen_in": ["Pilot simulator: the \"Targets at their floors\" preset and demo 2 (\"Do the targets add up?\")",
                    "KPIs and gates: the consistency-check alert on the floors"],
    },
    "today_proxy": {
        "plain": "An illustrative estimate of how today's system performs if you carry forward FSP's known completion rate and assume the weak, unpublished downstream numbers implied by the case. It is the \"do nothing new\" baseline.",
        "analogy": "The line you'd draw if you just extended what's already happening, with no new interventions.",
        "seen_in": ["Pilot simulator: the \"Today's system (illustrative)\" preset and the start of demo 1",
                    "Compare scenarios chart: shown alongside the other three plans"],
    },
    "stretch": {
        "plain": "The optimistic upper bound: every intervention lands, hubs and apprenticeships run at their best observed rates, and outcome payments work as designed. Useful as a ceiling, not a forecast.",
        "analogy": "The best-case finish time you'd only hit if every light turned green.",
        "seen_in": ["Pilot simulator: the \"Stretch plan\" preset",
                    "Compare scenarios chart: the upper line against the operating plan"],
    },
}


# Guided demo cases for the pilot simulator. Captions use live values: {vacr} {gates} {cpc} {months}
# {women} {total} {ceiling} {req}. Every rate is an illustrative assumption, not an estimate of real effects.
DEMOS = [
    {"id": "today_to_ladder", "title": "From today's system to the ladder",
     "question": "How much of the conversion gap does each intervention have to close?",
     "start": "today_proxy",
     "steps": [
         {"set": {}, "cap": "Today (illustrative): FSP-like completion of 58% and a weak link to work. Only <b>{vacr}%</b> of entrants reach verified work and each convert costs <b>₹{cpc}</b>."},
         {"set": {"completion": 0.76}, "cap": "I2 outcome-based pay and I5 Trainer Corps lift completion to 76%. VACR rises to <b>{vacr}%</b>."},
         {"set": {"competency": 0.73}, "cap": "Independent assessment with certified facilitators: 73% of completers validated. VACR <b>{vacr}%</b>."},
         {"set": {"uptake": 0.86}, "cap": "I3 AI Apprenticeship India and I7 Transition Exchange move 86% of competent learners into real projects. VACR <b>{vacr}%</b>."},
         {"set": {"validation": 0.88, "employer_sat": 0.82}, "cap": "Employers validate 88% at the workplace. VACR <b>{vacr}%</b>, <b>{gates}/6</b> gates."},
         {"set": {"women_entry": 0.48}, "cap": "Women-led cohorts lift women's entry share to 48%. Cost per convert falls to <b>₹{cpc}</b>, about <b>{months}</b> months of urban salaried earnings. <b>{gates}/6</b> gates pass."},
     ]},
    {"id": "targets_add_up", "title": "Do the targets add up?",
     "question": "Can completion ≥70% and competency ≥60% deliver VACR ≥40%?",
     "start": "operating_plan",
     "steps": [
         {"set": {}, "cap": "Operating plan: VACR <b>{vacr}%</b> and <b>{gates}/6</b> gates pass."},
         {"set": {"completion": 0.70, "competency": 0.60}, "cap": "Put completion and competency at their target floors. Only <b>{ceiling}%</b> of entrants are assessed competent, so VACR falls to <b>{vacr}%</b>."},
         {"set": {"uptake": 0.97, "validation": 0.98}, "cap": "To reach 40% from the floors, <b>{req}%</b> of competent learners must transition and be validated. Even 97% and 98% only gives <b>{vacr}%</b>."},
         {"set": {"completion": 0.76, "competency": 0.73, "uptake": 0.86, "validation": 0.88}, "cap": "Fix: manage to an operating plan of 76% and 73%; keep the published targets as gate floors. VACR <b>{vacr}%</b>, <b>{gates}/6</b> gates."},
     ]},
    {"id": "stress_test", "title": "Stress test: equity and cost shocks",
     "question": "Do the equity and economics gates catch what they should?",
     "start": "operating_plan",
     "steps": [
         {"set": {"women_entry": 0.41}, "cap": "Recruit the way FSP does today (41% women at entry). Women's share of converts falls to <b>{women}%</b>, below 45%: G6 fails."},
         {"set": {"women_rel": 1.19}, "cap": "Disadvantage-weighted outcome pay must lift women's relative conversion to about 1.19x before women reach <b>{women}%</b> of converts and G6 passes."},
         {"set": {"women_entry": 0.48, "women_rel": 1.0}, "cap": "Safer route: women-led cohorts (48% at entry) give <b>{women}%</b> without relying on differential conversion."},
         {"set": {"cost_mult": 1.05}, "cap": "Unit costs rise 5%. The ₹15 Cr contingency absorbs it and spend stays <b>₹{total} Cr</b>."},
         {"set": {"cost_mult": 1.12}, "cap": "At +12% the contingency is exhausted: spend <b>₹{total} Cr</b> breaches the ₹290 Cr cap and G5 fails. The gate forces redesign before scale."},
         {"set": {"cost_mult": 1.0}, "cap": "Back to plan: <b>{gates}/6</b> gates. Loss is capped at ₹290 Cr whatever happens."},
     ]},
]


def clean(params):
    p = deepcopy(DEFAULT)
    for k, v in (params or {}).items():
        if k == "lines" and isinstance(v, dict):
            p["lines"] = {lk: {kk: float(vv) for kk, vv in lv.items() if kk in ("qty", "unit", "lump") and vv is not None}
                          for lk, lv in v.items() if isinstance(lv, dict)}
        elif k == "g1_pass":
            p[k] = bool(v)
        elif k in LIMITS:
            try:
                lo, hi = LIMITS[k]
                p[k] = min(max(float(v), lo), hi)
            except (TypeError, ValueError):
                pass
    p["entrants"] = int(round(p["entrants"]))
    p["years"] = int(round(p["years"]))
    return p


def preset(pid):
    pr = PRESETS.get(pid)
    return clean(pr["params"]) if pr else clean({})


def budget(p):
    rows, base_nc, cont = [], 0.0, 0.0
    for L in D.PILOT_LINES:
        o = p["lines"].get(L["key"], {})
        if L["lump"] is not None:
            amt = o.get("lump", L["lump"])
            qty, unit = None, None
        else:
            qty = o.get("qty", L["qty"])
            unit = o.get("unit", L["unit"])
            amt = qty * unit / 1e7
        if L["key"] == "cont":
            cont = amt
        else:
            amt *= p["cost_mult"]
            base_nc += amt
        rows.append({"key": L["key"], "line": L["line"], "qty": qty, "unit": unit, "amount": amt, "basis": L["basis"], "int": L["int"]})
    overrun = base_nc - base_nc / p["cost_mult"] if p["cost_mult"] else 0
    used = min(cont, max(0.0, overrun))
    for r in rows:
        if r["key"] == "cont":
            r["amount"] = cont - used
            r["basis"] = f"≈5% of pilot; ₹{used:,.1f} Cr absorbed by unit-cost overrun" if used > 0 else "≈5% of pilot"
    total = sum(r["amount"] for r in rows)
    for r in rows:
        r["amount"] = round(r["amount"], 2)
        r["share"] = round(r["amount"] / total * 100, 1) if total else 0
    return rows, round(total, 2)


def _share(entry, rel):
    num = entry * rel
    return num / (num + (1 - entry)) if (num + (1 - entry)) > 0 else 0


def simulate(params=None):
    p = clean(params)
    n = p["entrants"]
    completed = n * p["completion"]
    competent = completed * p["competency"]
    transitioned = competent * p["uptake"]
    verified = transitioned * p["validation"]
    moved = verified * p["move"]
    vacr = verified / n
    transition = transitioned / n
    women = _share(p["women_entry"], p["women_rel"])
    tier = _share(p["tier_entry"], p["tier_rel"])
    lines, total_cr = budget(p)
    cost_per_convert = total_cr * 1e7 / verified if verified else None
    cost_per_entrant = total_cr * 1e7 / n
    breakeven = cost_per_convert
    months = breakeven / p["earnings"] if breakeven else None
    test_benefit = p["uplift"] * p["earnings"] * 12 * p["years"]
    ceiling = p["completion"] * p["competency"]
    required_downstream = D.ECON["vacr_target"] / ceiling if ceiling else None

    band = D.PILOT_CAP_CR * 1e7 / (D.ECON["pilot_entrants"] * D.ECON["vacr_target"]) * 1.25
    gates = [
        {"id": "G1", "pass": p["g1_pass"], "detail": "Passport issues and verifies across rails" if p["g1_pass"] else "Technical integration not yet verified"},
        {"id": "G2", "pass": p["completion"] >= 0.70 and n >= 0.9 * D.ECON["pilot_entrants"],
         "detail": f"Completion {p['completion'] * 100:.1f}% (≥70%); entrants {n:,} (≥{int(0.9 * D.ECON['pilot_entrants']):,})"},
        {"id": "G3", "pass": p["competency"] >= 0.60, "detail": f"Competency {p['competency'] * 100:.1f}% of completers (≥60%)"},
        {"id": "G4", "pass": vacr >= 0.40 and transition >= 0.40 and p["employer_sat"] >= 0.80,
         "detail": f"VACR {vacr * 100:.1f}% (≥40%); transition {transition * 100:.1f}% (≥40%); employer satisfaction {p['employer_sat'] * 100:.0f}% (≥80%)"},
        {"id": "G5", "pass": bool(cost_per_convert) and cost_per_convert <= band and total_cr <= D.PILOT_CAP_CR + 0.01,
         "detail": f"₹{cost_per_convert:,.0f} per convert (≤₹{band:,.0f}); spend ₹{total_cr:,.1f} Cr (≤₹{D.PILOT_CAP_CR} Cr)" if cost_per_convert else "No verified converts"},
        {"id": "G6", "pass": women >= 0.45 and tier >= 0.70, "detail": f"Women {women * 100:.1f}% (≥45%); Tier-2/3 {tier * 100:.1f}% (≥70%) of converts"},
    ]
    for g in gates:
        g.update({k: v for k, v in next(x for x in D.GATES if x["id"] == g["id"]).items() if k in ("name", "test", "month")})

    return {
        "params": p,
        "funnel": [
            {"stage": "Entered", "n": n, "rate": 1.0, "step": None},
            {"stage": "Completed", "n": round(completed), "rate": p["completion"], "step": "completion"},
            {"stage": "Competency validated", "n": round(competent), "rate": p["competency"], "step": "competency"},
            {"stage": "Transitioned to apprenticeship / project", "n": round(transitioned), "rate": p["uptake"], "step": "uptake"},
            {"stage": "Workplace competency verified (VACR)", "n": round(verified), "rate": p["validation"], "step": "validation"},
            {"stage": "Moved to job / promotion / redeployment", "n": round(moved), "rate": p["move"], "step": "move"},
        ],
        "kpi": {"vacr": round(vacr * 100, 1), "completion": round(p["completion"] * 100, 1), "competency": round(p["competency"] * 100, 1),
                "transition": round(transition * 100, 1), "employer_sat": round(p["employer_sat"] * 100, 1),
                "women": round(women * 100, 1), "tier23": round(tier * 100, 1),
                "cost_per_convert": round(cost_per_convert) if cost_per_convert else None, "relevance": None},
        "verified": round(verified), "moved": round(moved),
        "budget": {"lines": lines, "total_cr": total_cr, "cap_cr": D.PILOT_CAP_CR, "within_cap": total_cr <= D.PILOT_CAP_CR + 0.01},
        "econ": {"cost_per_entrant": round(cost_per_entrant), "cost_per_convert": round(cost_per_convert) if cost_per_convert else None,
                 "breakeven": round(breakeven) if breakeven else None, "months_of_earnings": round(months, 2) if months else None,
                 "test_benefit": round(test_benefit), "test_pass": bool(breakeven) and test_benefit >= breakeven, "band": round(band)},
        "consistency": {"ceiling": round(ceiling * 100, 1), "required_downstream": round(required_downstream * 100, 1) if required_downstream else None,
                        "floor_ceiling": round(0.70 * 0.60 * 100, 1), "floor_required": round(0.40 / (0.70 * 0.60) * 100, 1)},
        "gates": gates, "gates_passed": sum(1 for g in gates if g["pass"]),
    }


def envelope():
    E = D.ECON
    role = dict(D.ENVELOPE)["Role-ready learners"] * 1e7 / E["role_ready_target"]
    adv = dict(D.ENVELOPE)["Advanced practitioners"] * 1e7 / E["advanced_target"]
    central_yr = dict(D.FINANCING)["Central Government"] / E["years"]
    csr_yr = dict(D.FINANCING)["CSR / philanthropy"] / E["years"]
    return {"lines": D.ENVELOPE, "financing": D.FINANCING, "total": sum(v for _, v in D.ENVELOPE),
            "per_role_ready": round(role), "per_advanced": round(adv), "central_per_year": central_yr,
            "central_pct_msde": round(central_yr / E["msde_fy27_cr"] * 100, 1), "csr_per_year": csr_yr,
            "csr_pct": round(csr_yr / E["csr_fy23_cr"] * 100, 2)}


# --------------------------------------------------------------------------------------
# Sensitivity and Monte Carlo
# --------------------------------------------------------------------------------------
LABELS = {"completion": "Completion", "competency": "Competency validation", "uptake": "Transition uptake",
          "validation": "Workplace validation", "move": "Move to job", "cost_mult": "Unit-cost overrun",
          "employer_sat": "Employer satisfaction", "women_rel": "Women relative conversion"}


def sensitivity(params=None, delta=0.05):
    base = simulate(params)
    p = base["params"]
    rows = []
    for k in ["completion", "competency", "uptake", "validation"]:
        lo, hi = dict(p), dict(p)
        lo[k] = max(0.05, p[k] - delta)
        hi[k] = min(0.99, p[k] + delta)
        a, b = simulate(lo), simulate(hi)
        rows.append({"key": k, "label": LABELS[k], "vacr_lo": round(a["kpi"]["vacr"] - base["kpi"]["vacr"], 2),
                     "vacr_hi": round(b["kpi"]["vacr"] - base["kpi"]["vacr"], 2),
                     "cost_lo": (a["econ"]["cost_per_convert"] or 0) - (base["econ"]["cost_per_convert"] or 0),
                     "cost_hi": (b["econ"]["cost_per_convert"] or 0) - (base["econ"]["cost_per_convert"] or 0)})
    lo, hi = dict(p), dict(p)
    lo["cost_mult"], hi["cost_mult"] = p["cost_mult"] * 0.9, p["cost_mult"] * 1.1
    a, b = simulate(lo), simulate(hi)
    rows.append({"key": "cost_mult", "label": "Unit costs ±10%", "vacr_lo": 0, "vacr_hi": 0,
                 "cost_lo": (a["econ"]["cost_per_convert"] or 0) - (base["econ"]["cost_per_convert"] or 0),
                 "cost_hi": (b["econ"]["cost_per_convert"] or 0) - (base["econ"]["cost_per_convert"] or 0)})
    return {"base_vacr": base["kpi"]["vacr"], "base_cost": base["econ"]["cost_per_convert"], "delta_pp": delta * 100, "rows": rows}


UNCERTAIN = [("completion", 0.92, 1.08), ("competency", 0.92, 1.08), ("uptake", 0.90, 1.08), ("validation", 0.93, 1.06),
             ("employer_sat", 0.94, 1.06), ("women_rel", 0.92, 1.08), ("cost_mult", 0.95, 1.15)]


def _pct(v, q):
    s = sorted(v)
    k = (len(s) - 1) * q
    f, c = math.floor(k), math.ceil(k)
    return s[f] if f == c else s[f] + (s[c] - s[f]) * (k - f)


def _rank(x):
    o = sorted(range(len(x)), key=lambda i: x[i])
    r = [0] * len(x)
    for pos, i in enumerate(o):
        r[i] = pos
    return r


def _spearman(x, y):
    rx, ry = _rank(x), _rank(y)
    n = len(x)
    mx, my = sum(rx) / n, sum(ry) / n
    cov = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    vx = math.sqrt(sum((a - mx) ** 2 for a in rx))
    vy = math.sqrt(sum((b - my) ** 2 for b in ry))
    return cov / (vx * vy) if vx and vy else 0.0


def monte_carlo(params=None, runs=1000, seed=2026):
    base = clean(params)
    rng = random.Random(seed)
    runs = int(min(max(runs, 200), 5000))
    vacrs, costs, gate_pass = [], [], {g["id"]: 0 for g in D.GATES}
    all_quant, draws = 0, []
    for _ in range(runs):
        q = dict(base)
        d = {}
        for k, lo, hi in UNCERTAIN:
            m = rng.triangular(lo, hi, 1.0)
            d[k] = m
            q[k] = base[k] * m
        for k in ["completion", "competency", "uptake", "validation", "employer_sat"]:
            q[k] = min(q[k], 0.98)
        r = simulate(q)
        vacrs.append(r["kpi"]["vacr"])
        costs.append(r["econ"]["cost_per_convert"] or 0)
        ok = True
        for g in r["gates"]:
            if g["pass"]:
                gate_pass[g["id"]] += 1
            elif g["id"] != "G1":
                ok = False
        all_quant += ok
        d["vacr"] = r["kpi"]["vacr"]
        draws.append(d)
    bins = list(range(20, 62, 3))
    hist = [0] * (len(bins) - 1)
    for v in vacrs:
        v2 = min(max(v, bins[0]), bins[-1] - 0.01)
        hist[int((v2 - bins[0]) // 3)] += 1
    drivers = [{"key": k, "label": LABELS[k], "corr": round(_spearman([x[k] for x in draws], [x["vacr"] for x in draws]), 3)}
               for k, _, _ in UNCERTAIN if k != "cost_mult"]
    drivers.sort(key=lambda x: -abs(x["corr"]))
    return {"runs": runs,
            "p_vacr40": round(sum(v >= 40 for v in vacrs) / runs * 100, 1),
            "p_all_gates": round(all_quant / runs * 100, 1),
            "p_gate": {k: round(v / runs * 100, 1) for k, v in gate_pass.items()},
            "vacr": {"p10": round(_pct(vacrs, .1), 1), "p50": round(_pct(vacrs, .5), 1), "p90": round(_pct(vacrs, .9), 1)},
            "cost": {"p10": round(_pct(costs, .1)), "p50": round(_pct(costs, .5)), "p90": round(_pct(costs, .9))},
            "hist": {"labels": [f"{b}-{b + 3}%" for b in bins[:-1]], "counts": hist, "starts": bins[:-1]},
            "drivers": drivers,
            "ranges": [{"key": k, "label": LABELS[k], "lo": lo, "hi": hi} for k, lo, hi in UNCERTAIN]}


# --------------------------------------------------------------------------------------
# States, KPIs, signals
# --------------------------------------------------------------------------------------
def state_profile(code):
    s = next((x for x in D.STATES if x["code"] == str(code).upper()), None)
    if not s:
        return None
    by_enr = sorted(D.STATES, key=lambda x: -x["enrolled"])
    by_rate = sorted([x for x in D.STATES if x["enrolled"] >= 20000], key=lambda x: -x["rate"])
    nat = D.FSP_STATE_TOTAL["rate"]
    share = s["enrolled"] / D.FSP_STATE_TOTAL["enrolled"] * 100
    emphasis = []
    if s["rate"] < nat - 5:
        emphasis.append(("I2", "Certification rate is below the national 58%: outcome-based provider contracts and independent assessment first."))
        emphasis.append(("I5", "Trainer Corps cohort to lift delivery quality."))
    if share < 1.0:
        emphasis.append(("I6", "Low enrolment base: regional hub on a PM-SETU ITI or NIELIT centre, assisted and vernacular delivery."))
        emphasis.append(("I4", "AI Skill Credit top-ups to seed demand."))
    if s["ne"]:
        emphasis.append(("I6", "North-East: IndiaAI Data & AI Labs and BHASHINI voice delivery."))
    if s["rate"] >= nat + 8 and s["enrolled"] >= 20000:
        emphasis.append(("I3", "Strong conversion: add AI apprenticeships and employer validation to prove workplace outcomes."))
    if s["enrolled"] >= 150000:
        emphasis.append(("I7", "Scale base: AI Transition Exchange with state employers."))
    if not emphasis:
        emphasis.append(("I1", "Adopt the Skill Graph and Passport; measure outcomes before adding spend."))
    seen, emph = set(), []
    for i, t in emphasis:
        key = (i, t)
        if key not in seen:
            seen.add(key)
            emph.append({"id": i, "title": D.INT_INDEX[i]["title"], "why": t})
    return {**s, "rank_enrolled": [x["code"] for x in by_enr].index(s["code"]) + 1, "of": len(D.STATES),
            "rank_rate": ([x["code"] for x in by_rate].index(s["code"]) + 1) if s in by_rate else None, "of_rate": len(by_rate),
            "share": round(share, 2), "national_rate": nat, "gap": round(s["rate"] - nat, 1), "emphasis": emph,
            "rule_note": "Emphasis is a team rule of thumb from FSP data, not an official assessment."}


def kpi_scorecard(sim):
    rows = []
    for k in D.KPIS:
        r = dict(k)
        v = sim["kpi"].get(k["key"])
        r["projected"] = v
        if v is None:
            r["status"] = "grey"
        else:
            ok = v >= k["target"] if k["cmp"] == ">=" else v <= k["target"]
            near = (v >= k["target"] * 0.9) if k["cmp"] == ">=" else (v <= k["target"] * 1.1)
            r["status"] = "green" if ok else ("amber" if near else "red")
        rows.append(r)
    return rows


# --------------------------------------------------------------------------------------
# Decision engine (deterministic, rule-based on the six gates; never an opaque model)
# --------------------------------------------------------------------------------------
GATE_LEVERS = {
    "G1": [], "G2": ["I2", "I5"], "G3": ["I2", "I5"], "G4": ["I3", "I7"], "G5": [], "G6": ["I4", "I6"],
}
DECISIONS = {
    "SCALE": "All six evidence gates pass in the active scenario.",
    "HOLD": "Foundational gates have not yet had time to clear; hold before judging outcome or economics.",
    "REDESIGN": "A core outcome, cost or equity gate fails. Fix the design before adding spend or entrants.",
    "STOP": "Workforce outcome and economic viability both fail: the pilot is not converting learners to affordable, verified work.",
}


def decision(sim):
    """Deterministic SCALE / HOLD / REDESIGN / STOP call from the six gates. Never an opaque model (RULE 8/9)."""
    g = {x["id"]: x for x in sim["gates"]}
    if not g["G1"]["pass"]:
        verdict, why = "HOLD", "Technical feasibility (G1) is not verified: the Passport does not yet issue and verify across SIDH/APAAR/DigiLocker. Nothing downstream can be trusted until this clears."
        primary = "G1"
    elif not g["G4"]["pass"] and not g["G5"]["pass"]:
        verdict, why = "STOP", "Workforce outcome (G4) and economic viability (G5) both fail: the pilot is neither converting learners to verified work nor within its cost band."
        primary = "G4" if abs(sim["kpi"]["vacr"] - 40) >= abs((sim["econ"]["cost_per_convert"] or 0) - sim["econ"]["band"]) / 1000 else "G5"
    elif not g["G4"]["pass"]:
        verdict, why = "REDESIGN", "Workforce outcome (G4) fails: VACR, transition or employer satisfaction is short of target."
        primary = "G4"
    elif not g["G5"]["pass"]:
        verdict, why = "REDESIGN", "Economic viability (G5) fails: cost per verified convert or total spend breaches its cap."
        primary = "G5"
    elif not g["G6"]["pass"]:
        verdict, why = "REDESIGN", "Equity (G6) fails: women or Tier-2/3 share of verified converts is below target."
        primary = "G6"
    elif not g["G2"]["pass"] or not g["G3"]["pass"]:
        verdict, why = "HOLD", "Learner adoption (G2) or competency validation (G3) has not reached its threshold; give the pilot time before judging outcome and economics."
        primary = "G2" if not g["G2"]["pass"] else "G3"
    else:
        verdict, why = "SCALE", DECISIONS["SCALE"]
        primary = None
    levers = [{"id": i, "title": D.INT_INDEX[i]["title"]} for i in GATE_LEVERS.get(primary, [])] if primary else []
    action = ("Strengthen " + " and ".join(l["title"] for l in levers) + "." if levers else
              ("Hold spend and entrants at plan until the gate clears; no design change is indicated yet." if verdict == "HOLD" else
               "Redesign unit costs or the budget mix before scaling." if primary == "G5" else
               "Ready to recommend scale to the next pilot wave." if verdict == "SCALE" else
               "Stop and redesign before committing further spend."))
    return {"verdict": verdict, "reason": why, "primary_gate": primary,
            "gates": [{"id": x["id"], "name": x["name"], "pass": x["pass"]} for x in sim["gates"]],
            "levers": levers, "recommended_action": action}


BOTTLENECK_STAGES = {"completion": "Completion", "competency": "Competency validation", "uptake": "Transition to apprenticeship/project", "validation": "Workplace validation"}


def bottleneck(sim):
    """Which funnel stage would move VACR the most, per the model's own sensitivity (never manually labelled, RULE 6)."""
    sens = sensitivity(sim["params"], delta=0.05)
    rows = [r for r in sens["rows"] if r["key"] in BOTTLENECK_STAGES]
    top = max(rows, key=lambda r: r["vacr_hi"] - r["vacr_lo"])
    return {"key": top["key"], "label": BOTTLENECK_STAGES[top["key"]],
            "swing_pp": round(top["vacr_hi"] - top["vacr_lo"], 2),
            "statement": f"Improving {BOTTLENECK_STAGES[top['key']].lower()} produces the largest direct improvement in VACR under the current scenario "
                         f"(±5 pp there moves VACR by {round(top['vacr_hi'] - top['vacr_lo'], 1)} pp, vs less for the other stages)."}


# --------------------------------------------------------------------------------------
# Stress test: apply a named shock to the active scenario and show the cascade
# --------------------------------------------------------------------------------------
SHOCKS = [
    {"id": "completion_down", "label": "Completion -10%", "param": "completion", "rel": -0.10, "kpi_hit": "Fewer learners complete the programme"},
    {"id": "competency_down", "label": "Competency -10%", "param": "competency", "rel": -0.10, "kpi_hit": "Fewer completers pass independent assessment"},
    {"id": "employer_down", "label": "Employer participation -15%", "param": "employer_sat", "rel": -0.15, "kpi_hit": "Workplace validation and employer satisfaction fall"},
    {"id": "cost_up", "label": "Training cost +10%", "param": "cost_mult", "rel": 0.10, "kpi_hit": "Unit costs rise across every budget line"},
    {"id": "uptake_down", "label": "Apprenticeship uptake -15%", "param": "uptake", "rel": -0.15, "kpi_hit": "Fewer competent learners transition to a workplace"},
    {"id": "women_conv_down", "label": "Women conversion -10%", "param": "women_rel", "rel": -0.10, "kpi_hit": "Women convert less often relative to men"},
    {"id": "tier_conv_down", "label": "Tier-2/3 conversion -10%", "param": "tier_rel", "rel": -0.10, "kpi_hit": "Tier-2/3 learners convert less often relative to metros"},
]
SHOCK_INDEX = {s["id"]: s for s in SHOCKS}


def apply_shock(params, shock_id):
    s = SHOCK_INDEX.get(shock_id)
    if not s:
        return dict(params)
    p = dict(params)
    p[s["param"]] = p.get(s["param"], DEFAULT[s["param"]]) * (1 + s["rel"])
    return p


def stress_test(params, shock_id):
    s = SHOCK_INDEX.get(shock_id)
    before = simulate(params)
    if not s:
        return {"error": "Unknown shock id."}
    after = simulate(apply_shock(before["params"], shock_id))
    db, da = decision(before), decision(after)
    flips = [g["id"] for g in after["gates"] if not g["pass"] and next(x for x in before["gates"] if x["id"] == g["id"])["pass"]]
    return {"shock": s, "before": {"kpi": before["kpi"], "gates_passed": before["gates_passed"], "decision": db},
            "after": {"kpi": after["kpi"], "gates_passed": after["gates_passed"], "decision": da},
            "gate_flips": flips, "vacr_delta": round(after["kpi"]["vacr"] - before["kpi"]["vacr"], 1),
            "decision_changed": db["verdict"] != da["verdict"]}


def signals(sim):
    out = []
    c = sim["consistency"]
    out.append({"level": "amber", "title": "Targets at their floors cannot deliver VACR 40%",
                "body": f"Completion 70% × competency 60% caps VACR at {c['floor_ceiling']}%; every downstream step would need ≥{c['floor_required']}%. Run completion ≥75% and competency ≥72%.",
                "link": "/strategy#consistency"})
    failed = [g["id"] for g in sim["gates"] if not g["pass"]]
    out.insert(0, {"level": "green" if not failed else "red",
                   "title": f"{sim['gates_passed']} of 6 gates pass in the active scenario",
                   "body": ("Ready to recommend scale." if not failed else "Failing: " + ", ".join(failed) + ". Open the simulator to see why."),
                   "link": "/simulator"})
    out.append({"level": "red", "title": "AI is barely on the apprenticeship rail",
                "body": "Only 1,480 AI-role apprentices under NAPS-2 (FY23-FY26) in a system that engaged 54.41 lakh apprentices.", "link": "/matrix"})
    out.append({"level": "amber", "title": "SOAR certifies about 1 in 5 enrolees",
                "body": "98,576 certified of 4,96,426 enrolled (22 Jul 2026). Completion is the first leak.", "link": "/ladder"})
    low = [s for s in D.STATES if s["enrolled"] >= 20000 and s["rate"] < 46]
    out.append({"level": "amber", "title": f"{len(low)} large states certify under 46% of enrolees",
                "body": ", ".join(f"{s['name']} {s['rate']}%" for s in sorted(low, key=lambda x: x['rate'])) + ". Provider quality varies by state.", "link": "/states"})
    if sim["kpi"]["women"] < 45:
        out.append({"level": "amber", "title": "Women's share of converts below 45%",
                    "body": f"At {sim['params']['women_entry'] * 100:.0f}% entry share, women must convert {0.45 / (1 - 0.45) * (1 - sim['params']['women_entry']) / sim['params']['women_entry']:.2f}x as often as men, or entry must rise via women-led cohorts.",
                    "link": "/simulator"})
    return out
