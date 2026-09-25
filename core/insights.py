"""Analytics helpers: EY 3A exposure, Long-Term Value, change readiness, rules-based answers."""
import re

from . import data as D
from . import engine as E
from . import frameworks as F


def exposure(adoption=0.6, hours_week=45):
    adoption = min(max(float(adoption), 0.05), 1.0)
    rows, by_rung, by_sector = [], {1: 0.0, 2: 0.0, 3: 0.0, 4: 0.0}, {}
    tot = {"w": 0, "imp": 0, "hrs": 0, "fw": 0, "a": 0, "g": 0, "m": 0}
    for r in F.ROLES:
        impacted = r["workforce"] * min(1.0, (r["auto"] + r["aug"]) * 1.25) * adoption
        freed = hours_week * (r["auto"] * 0.34 + r["aug"] * 0.22 + r["amp"] * 0.05) * adoption / 0.6
        by_rung[r["rung"]] += impacted
        if r["rung"] >= 2:
            by_rung[1] += impacted * 0.35
        by_sector[r["sector"]] = by_sector.get(r["sector"], 0) + impacted
        posture = "Automate and redeploy" if r["auto"] > r["aug"] else "Augment and upskill" if r["aug"] >= r["amp"] * 2 else "Amplify and specialise"
        rows.append({**r, "impacted": round(impacted, 2), "hours_freed": round(freed, 1), "rung_code": f"L{r['rung']}",
                     "train_mn_hours": round(impacted * 1e5 * F.RUNG_HOURS[r["rung"]] / 1e6, 1), "posture": posture})
        tot["w"] += r["workforce"]; tot["imp"] += impacted; tot["hrs"] += impacted * 1e5 * F.RUNG_HOURS[r["rung"]]
        tot["fw"] += freed * r["workforce"]; tot["a"] += r["auto"] * r["workforce"]; tot["g"] += r["aug"] * r["workforce"]; tot["m"] += r["amp"] * r["workforce"]
    w = tot["w"]
    return {"rows": sorted(rows, key=lambda x: -x["impacted"]),
            "summary": {"workforce_lakh": round(w, 1), "impacted_lakh": round(tot["imp"], 1), "auto_pct": round(tot["a"] / w * 100, 1),
                        "aug_pct": round(tot["g"] / w * 100, 1), "amp_pct": round(tot["m"] / w * 100, 1),
                        "hours_freed_avg": round(tot["fw"] / w, 1), "training_bn_hours": round(tot["hrs"] / 1e9, 2), "adoption": adoption},
            "by_rung": {f"L{k}": round(v, 1) for k, v in by_rung.items()},
            "by_sector": {k: round(v, 1) for k, v in sorted(by_sector.items(), key=lambda kv: -kv[1])},
            "ey": D.DEMAND}


def ltv(sim):
    spend = {i["id"]: 0.0 for i in D.INTERVENTIONS}
    for l in sim["budget"]["lines"]:
        if l["int"]:
            spend[l["int"]] += l["amount"]
    tot = sum(spend.values()) or 1
    dims = [d["key"] for d in F.LTV_DIMS]
    agg = {k: 0.0 for k in dims}
    levers = []
    for i in D.INTERVENTIONS:
        sc = F.LTV_SCORES[i["id"]]
        w = spend[i["id"]] / tot
        for k in dims:
            agg[k] += sc[k] * w
        levers.append({"id": i["id"], "short": i["short"], "color": i["color"], "scores": {k: sc[k] for k in dims},
                       "metric": sc["metric"], "spend": round(spend[i["id"]], 1), "share": round(w * 100, 1), "total": sum(sc[k] for k in dims)})
    realised = {k: round(v, 2) for k, v in agg.items()}
    k = sim["kpi"]
    outcome = {
        "human": [f"{sim['verified']:,} verified converts in the pilot", f"VACR {k['vacr']}%"],
        "citizen": ["One portable Passport on existing rails", f"Completion {k['completion']}%"],
        "societal": [f"Women {k['women']}% and Tier-2/3 {k['tier23']}% of converts", "Two catch-up states incl. North-East"],
        "financial": [f"₹{(k['cost_per_convert'] or 0):,} per verified convert", "Loss capped at ₹290 Cr"],
    }
    return {"dims": F.LTV_DIMS, "levers": levers, "realised": realised, "outcome": outcome,
            "balance": round(min(realised.values()) / max(realised.values()) * 100, 1) if max(realised.values()) else 0}


def change_index(scores=None, conf=None):
    scores = scores or {d["driver"]: d["baseline"] for d in F.HUMANS_AT_CENTER}
    conf = conf or {c["c"]: c["baseline"] for c in F.CONFIDENCE_3C}
    hc = sum(scores.values()) / len(scores)
    c3 = sum(conf.values()) / len(conf)
    readiness = round((hc * 0.6 + c3 * 0.4) / 5 * 100, 1)
    weakest = [w[0] for w in sorted(scores.items(), key=lambda kv: kv[1])[:2]]
    band = "Ready to scale" if readiness >= 75 else "Pilot-ready" if readiness >= 55 else "Mobilise first"
    return {"readiness": readiness, "band": band, "humans": round(hc, 2), "c3": round(c3, 2), "weakest": weakest}


def ask(question, sim):
    q = (question or "").strip()
    ql = q.lower()
    k, e = sim["kpi"], sim["econ"]
    if not q:
        return {"answer": "Ask about VACR, gates, the ₹290 Cr pilot, a state, an intervention (I1 to I7), failure modes, benchmarks or SDGs.", "source": "rules", "links": []}
    for s in D.STATES:
        if s["name"].lower() in ql or re.search(r"\b" + re.escape(s["code"]) + r"\b", q):
            p = E.state_profile(s["code"])
            em = "; ".join(f"{x['id']} {x['title']}" for x in p["emphasis"])
            role = f" Pilot role: {p['pilot']} ({p['pilot_why']})." if p["pilot"] else " Not in the 7-state pilot."
            return {"answer": f"{s['name']}: {s['enrolled']:,} enrolled and {s['certified']:,} certified on FutureSkills PRIME, a {s['rate']}% certification rate "
                              f"({p['gap']:+} pp vs the national {p['national_rate']}%), rank {p['rank_enrolled']} of {p['of']} by enrolment.{role} Suggested emphasis: {em}. "
                              f"(PIB/MeitY, 14 Aug 2026; emphasis is a team rule of thumb.)", "source": "rules", "links": [{"label": "Open state view", "href": "/states"}]}
    m = re.search(r"\bi([1-7])\b", ql)
    iv = D.INT_INDEX.get(f"I{m.group(1)}") if m else next((i for i in D.INTERVENTIONS if i["short"].lower() in ql or i["title"].lower() in ql), None)
    if iv:
        line = next((l for l in sim["budget"]["lines"] if l["int"] == iv["id"]), None)
        return {"answer": f"{iv['id']} {iv['title']}: {iv['mechanism']} Fixes {', '.join(iv['fixes'])}. Rides on {', '.join(iv['rails'])}. Owner: {iv['owner']}."
                          + (f" Pilot line: {line['line']} ₹{line['amount']} Cr." if line else ""), "source": "rules",
                "links": [{"label": f"Open {iv['id']}", "href": f"/interventions#{iv['id']}"}]}
    if any(w in ql for w in ["probab", "risk", "confiden", "monte", "odds", "chance"]):
        mc = E.monte_carlo(sim["params"], runs=800)
        return {"answer": f"Across {mc['runs']} simulated pilots, VACR reaches 40% in {mc['p_vacr40']}% of runs (P10 {mc['vacr']['p10']}%, median {mc['vacr']['p50']}%, P90 {mc['vacr']['p90']}%). "
                          f"All quantitative gates pass together in {mc['p_all_gates']}%. The biggest driver is {mc['drivers'][0]['label'].lower()}.", "source": "rules",
                "links": [{"label": "Open simulator", "href": "/simulator#mc"}]}
    if any(w in ql for w in ["vacr", "north star", "conversion"]):
        c = sim["consistency"]
        return {"answer": f"VACR = learners reaching verified workplace competency ÷ learners entering. Active scenario: {k['vacr']}% ({sim['verified']:,} of {sim['params']['entrants']:,}). "
                          f"Note: at the target floors (completion 70% × competency 60%) VACR is capped at {c['floor_ceiling']}%, so every downstream step would need ≥{c['floor_required']}%.",
                "source": "rules", "links": [{"label": "Open strategy lab", "href": "/strategy#consistency"}]}
    if any(w in ql for w in ["gate", "scale"]):
        return {"answer": "Gates: " + "; ".join(f"{g['id']} {g['name']}: {'pass' if g['pass'] else 'FAIL'} ({g['detail']})" for g in sim["gates"]),
                "source": "rules", "links": [{"label": "Open KPI scorecard", "href": "/kpis"}]}
    if any(w in ql for w in ["budget", "cost", "290", "6,500", "6500", "money", "crore", "break", "afford", "roi"]):
        env = E.envelope()
        return {"answer": f"Pilot ₹{sim['budget']['total_cr']} Cr (cap ₹290 Cr), built bottom-up; largest line apprenticeships ₹70 Cr. Cost per verified convert ₹{(e['cost_per_convert'] or 0):,}, "
                          f"about {e['months_of_earnings']} months of average urban salaried earnings (₹24,434/month, PLFS). Five-year envelope ₹6,500 Cr: ≈₹{env['per_role_ready']:,} per role-ready learner, "
                          f"≈₹{env['per_advanced']:,} per advanced practitioner; central share ₹800 Cr/yr = {env['central_pct_msde']}% of MSDE FY27. We claim no ROI: benefits are measured against comparison districts.",
                "source": "rules", "links": [{"label": "Open strategy lab", "href": "/strategy"}]}
    if any(w in ql for w in ["failure", "problem", "challenge", "fm"]):
        return {"answer": " ".join(f"{f['id']} {f['name']}: {f['evidence']}" for f in D.FAILURE_MODES), "source": "rules",
                "links": [{"label": "Open diagnosis", "href": "/matrix"}]}
    if any(w in ql for w in ["benchmark", "singapore", "uk", "peer", "impact bond", "pmkvy"]):
        return {"answer": " ".join(f"{b['where']}, {b['what']}: {b['facts']}." for b in D.BENCHMARKS[:6]), "source": "rules",
                "links": [{"label": "Open interventions", "href": "/interventions"}]}
    if any(w in ql for w in ["women", "gender", "equity", "inclusion", "tier"]):
        return {"answer": f"Women are 41% of FSP candidates and Tier-2/3 86% (entry). Targets are measured at conversion: women ≥45%, Tier-2/3 ≥70%. Active scenario: women {k['women']}%, Tier-2/3 {k['tier23']}%. "
                          "At 41% entry, women must convert about 1.18x as often as men to reach 45%; women-led cohorts that raise entry share are the more reliable route.",
                "source": "rules", "links": [{"label": "Open simulator", "href": "/simulator"}]}
    if any(w in ql for w in ["sdg"]):
        return {"answer": "SDG targets: " + "; ".join(f"{a} {b}" for a, b, _ in D.SDGS), "source": "rules", "links": []}
    if any(w in ql for w in ["job", "genai", "automat", "exposure", "role"]):
        x = exposure()
        return {"answer": f"EY's AIdea of India 2025: GenAI could transform 38 mn organised-sector jobs by 2030; 24% of task time fully automatable, 42% significantly reduced. "
                          f"Our role-level estimate (assumption) suggests ≈{x['summary']['impacted_lakh']} lakh workers need an upgrade, most at L2.", "source": "rules",
                "links": [{"label": "Open job exposure lab", "href": "/exposure"}]}
    return {"answer": "I can answer on VACR, gates, budget and break-even, states, interventions I1 to I7, failure modes, benchmarks, equity, SDGs and job exposure. "
                      "Connect Claude for open-ended questions.", "source": "rules", "links": []}
