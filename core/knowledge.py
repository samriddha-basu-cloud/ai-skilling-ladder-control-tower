"""Knowledge pack that grounds Ask the Tower in the case, the 3.0 solution and the evidence workbook."""
import json

from . import data as D
from . import engine as E
from . import frameworks as F

CASE = """EY Young Leaders 2026 business case competition, final round. Topic: "AI Skilling Ladder: Creating a Future-Ready Indian Workforce".
Brief: as EY consultants appointed by the Government of India, build an "AI skilling reform framework for India": a blueprint that equips the current workforce with AI expertise and ensures lifelong proficiency across all age groups.
Final round: max 8 slides, 10 MB, 12 min + 5 min Q&A; executive summary of prelim; challenges on an urgency vs impact matrix; 5-7 recommendations deployable nationally from basic digital literacy to advanced AI, with infrastructure and ecosystem implications; phased implementation plan with timelines, resources, stakeholders and challenges; KPIs. Assumptions must be reasoned. Judged on contextualisation, depth of research, storyboarding, creativity; EY values human perspective.
Team Vertex: Samriddha Basu, Souraj Roy.

THE SOLUTION (AI Skill Ladder): India has built the AI-learning rails; build the outcome bridge. It is a conversion problem, not an access problem.
Journey: Diagnose → Learn → Demonstrate → Apply → Recognise → Move (work) → Refresh. Each step writes evidence to the AI Skill Passport. AI runs the system; humans make every high-stakes call.
North Star: VACR = learners achieving verified workplace competency ÷ learners entering × 100; pilot target ≥40%.
Money: ₹290 Cr 12-18-month proof of value in 7 states (TN, AP volume; KA, OD conversion; UP scale; Bihar, Assam catch-up incl. North-East), each paired with a comparison district. ₹6,500 Cr five-year convergence envelope. All budgets are internal case assumptions, not GoI allocations. No manufactured ROI: break-even test only.
Decisions requested: approve the ₹290 Cr pilot; launch taxonomy, Skill Graph and Passport on existing rails; fund AI apprenticeships and outcome-linked provider contracts; make independent evaluation (VACR + six gates) the only route to scale.
Data discipline: every figure is Observed, Derived, Benchmark, Assumption or Proposed target. Never mix them; never cite excluded figures."""


def _c(o):
    return json.dumps(o, ensure_ascii=False, separators=(",", ":"))


def build(sim, scenario_name):
    env = E.envelope()
    parts = [
        "# CASE AND SOLUTION\n" + CASE,
        "# HEADLINE (class, source)\n" + _c(D.HEADLINE),
        "# FSP FUNNEL\n" + _c(D.FSP_FUNNEL) + "\nSOAR " + _c(D.SOAR) + f"\nFSP state-table totals: {_c(D.FSP_STATE_TOTAL)}",
        "# DEMAND (EY AIdea 2025) AND WORKFORCE (SBI Research on PLFS 2025)\n" + _c(D.DEMAND) + "\n" + _c(D.WORKFORCE),
        "# INCENTIVE EVIDENCE\n" + _c(D.INCENTIVE_EVIDENCE),
        "# LADDER L0-L5 (assessed on Technical, Non-technical and Responsible AI)\n" + _c([{k: l[k] for k in ("code", "name", "who", "what", "proof", "channels")} for l in D.LADDER]) + "\n" + D.REFRESH_RULE,
        "# FAILURE MODES\n" + _c(D.FAILURE_MODES),
        "# PRIORITY MATRIX (qualitative team scores)\n" + _c(D.PRIORITIES),
        "# SEVEN INTERVENTIONS\n" + _c(D.INTERVENTIONS),
        "# PILOT BUDGET LINES (assumptions)\n" + _c(D.PILOT_LINES),
        "# ENVELOPE AND FINANCING\n" + _c(env),
        "# KPIs\n" + _c(D.KPIS), "# GATES\n" + _c(D.GATES), "# PHASES\n" + _c(D.PHASES), "# RISKS\n" + _c(D.RISKS),
        "# ACTORS\n" + _c(D.ACTORS), "# BENCHMARKS\n" + _c(D.BENCHMARKS), "# SDGs\n" + _c(D.SDGS),
        "# HUMANS@CENTER CHANGE PLAN\n" + _c(F.HUMANS_AT_CENTER), "# KIRKPATRICK\n" + _c(F.KIRKPATRICK),
        "# STATES (FSP enrolled, certified, rate %, pilot role)\n" + _c([{k: s[k] for k in ("code", "name", "enrolled", "certified", "rate", "pilot")} for s in D.STATES]),
        "# SOURCES\n" + _c([{k: s[k] for k in ("id", "pub", "title", "date", "url")} for s in D.SOURCES]),
        "# EXCLUDED FIGURES (never cite)\n" + _c(D.EXCLUDED),
        "# BOARDROOM Q&A (team answers)\n" + _c(D.QA),
        f"# ACTIVE SCENARIO: {scenario_name}\n" + _c({k: sim[k] for k in ("params", "kpi", "verified", "econ", "consistency", "gates_passed")}),
    ]
    return "\n\n".join(parts)
