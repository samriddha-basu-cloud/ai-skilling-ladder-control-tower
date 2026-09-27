# AI Skill Ladder Control Tower

EY Young Leaders 2026, Final Round. Team Vertex.

A Flask decision tool aligned to the AI Skill Ladder deck and the team's evidence workbook. The thesis: India has built the AI-learning rails; build the bridge from learning to verified work. It is a conversion problem, not an access problem.

## Run it

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate    macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Open http://127.0.0.1:5000. Works offline (Chart.js is bundled). Production style: `gunicorn -w 2 -b 0.0.0.0:8000 app:app`

## Data discipline

Every figure carries one of five tags: Observed, Derived, Benchmark, Assumption, Proposed target. Sources S01 to S22 come from the workbook; S23 to S32 were added for the 3.0 deck (EY AIdea of India 2025, SBI Research on PLFS, PMKVY, Skill Impact Bond, PLFS earnings, CSR, EY Humans@Center). Excluded figures (prelim NASSCOM numbers, earlier ROI and ₹15,000 Cr model outputs, the modelled state index) are listed on the Sources page and never used. Figures were checked on 25 Sep 2026; re-check government figures on presentation day.

## Pages

| Group | Page | What it does |
|---|---|---|
| Overview | Command centre | FSP conversion gap, VACR, verified converts, cost per convert, gates, signals, state certification rates, workforce structure, FSP funding trend (D08), YUVA progress (D26), SOAR (D12, D13), ITI growth (D18) |
| Diagnose | Problem framing | MECE issue tree with source IDs, PESTLE, stakeholder grid |
| | Job exposure lab | EY 3A lens (S23) with role-level team estimates mapped to ladder levels |
| | Diagnosis matrix | Urgency × impact (qualitative), five failure modes, root cause (PMKVY vs Skill Impact Bond) |
| Design | Skill ladder | L0 to L5, three assessment dimensions, the six-step journey, programme vs pilot funnels |
| | Seven interventions | I1 to I7, MECE coverage, outcome payment split, benchmarks |
| | Operating model | Six actors, three units, human-in-the-loop, guardrails, inclusion, Humans@Center change plan |
| | Long-term value | EY LTV scoring weighted by pilot budget share |
| Decide | Strategy lab | VACR driver tree what-if, target consistency check, sensitivity, budget and envelope, break-even test, pilot portfolio on real FSP data |
| | Pilot simulator | Edit entrants, stage rates, equity, unit costs and budget lines; funnel, six gates, Monte Carlo, save and compare scenarios |
| | Stress test | Apply one of seven shocks to the active scenario (completion, competency, employer participation, cost, uptake, women/Tier-2/3 relative conversion) and see the cascade: shock → KPI hit → VACR → gates → decision |
| | State view | Cartogram and table of PIB state-wise FSP data; drawer with ranks, gap to national 58.3% and suggested emphasis |
| Deliver | Roadmap and risks | 60-month stage-gated Gantt, gate status, ₹290 Cr resources, risk register, RACI |
| | KPIs and gates | VACR and pilot targets vs baseline and projection, results chain, Kirkpatrick-Phillips, SDG targets |
| Engage | Pathway navigator | Places a learner on L0 to L5 with pathway, credit band, top-ups and Passport evidence |
| | Ask the Tower | Rules engine offline; with an Anthropic API key, Claude with live tools |
| Evidence | Sources and data | Sources with links, Data_Verified, Excluded, panel Q&A |
| | Executive brief | One-page printable brief for the active scenario |

## Animation and sources

Charts morph in place: when a slider, preset, demo or toggle changes a value, bars, doughnuts and scatter points move from their old to their new position instead of redrawing (Tower.chart in static/js/tower.js). Headline numbers count up or down, funnel bars slide, and gates flip when they change state. The simulator runs a client-side copy of the engine (static/js/pilot.js, tested to match core/engine.py) so every frame is instant; Monte Carlo, saving and exports still use the server.

Every chart carries a source caption: source ID, publisher and date, plus the workbook sheet or Data_Verified row (D01 to D26) it comes from. Assumption-based charts say so.

## Demo cases (Pilot simulator)

1. From today's system to the ladder: starts at the illustrative today proxy (VACR ≈7%) and adds each intervention's effect step by step to reach the operating plan.
2. Do the targets add up?: shows that completion 70% × competency 60% caps VACR at 42%, and how the operating plan fixes it.
3. Stress test: women's entry share at 41% fails G6; disadvantage weighting or women-led cohorts fix it; a 5% cost overrun is absorbed by contingency, 12% breaches the ₹290 Cr cap and fails G5.

Each demo animates the sliders, updates every chart and writes a caption with live numbers. Play, pause, next step and exit are on the demo bar; /simulator?demo=2 opens a demo directly.

## The pilot model

A transparent funnel, not an ROI projection: entrants → completed → competency validated → transitioned (apprenticeship or project) → workplace-verified (VACR numerator) → moved to work. Budget lines follow the workbook's Budget_Model. Contingency absorbs unit-cost overruns before the ₹290 Cr cap is breached. Gates G1 to G6 are evaluated on every run.

Presets: Operating plan with buffer (default, VACR ≈42%), Targets at their floors, Today's system (illustrative), Stretch plan.

Key finding built into the tool: at the proposed target floors (completion 70% × competency 60%) VACR is capped at 42%, so reaching 40% needs about 95% downstream conversion. The operating plan runs completion ≈76% and competency ≈73% to make the targets consistent.

## Decision engine

`core/engine.decision(sim)` turns the six gates into one deterministic call — SCALE, HOLD, REDESIGN or STOP — never an opaque model: G1 (technical) failing holds everything; G4+G5 both failing stops; either failing alone, or G6 failing, redesigns; G2/G3 not yet clearing holds; all six passing scales. Each call carries a plain-English reason, the primary gate at fault, and (where one exists) which of the seven interventions addresses it. It is shown on the Command Centre and the KPI scorecard, and can be driven with `core/engine.bottleneck(sim)` (which funnel stage's ±5pp move swings VACR the most, from the model's own sensitivity, never hand-labelled) and stress-tested per shock below.

## Testing

```bash
pip install -r requirements-dev.txt
python -m pytest
```

`tests/test_engine.py` covers the funnel maths, gate logic, decision engine (all four verdicts), the stress shocks and Monte Carlo bounds. `tests/test_app.py` smoke-tests every page and API endpoint, including malformed and out-of-range input, scenario CRUD, and that no hardcoded Flask secret ships.

## API

| Method | Endpoint | Purpose |
|---|---|---|
| POST | /api/simulate | Run the pilot model on `{"params": {...}}` |
| POST | /api/montecarlo | Probability of VACR ≥40% and of all gates passing |
| POST | /api/sensitivity | ±5 pp stage-rate sensitivity |
| POST | /api/stress | Apply a named shock (`{"shock": "cost_up"}`) or all seven (`{"all": true}`) to the active scenario; returns before/after KPI, gates and decision |
| POST | /api/compare | Compare saved or preset scenarios by id |
| GET/POST/DELETE | /api/scenarios | List, save, delete scenarios (stored in instance/scenarios.json) |
| POST | /api/active | Set active scenario or apply a draft |
| GET | /api/state/<code> | State profile, e.g. /api/state/BR |
| POST | /api/pathway | Learner placement |
| POST | /api/exposure, /api/change | 3A exposure, change readiness |
| POST | /api/ask | Ask the Tower |
| GET | /export/scenario.csv, /export/scenario.json | Export the active scenario |

## Ask the Tower with Claude

Paste an Anthropic API key on the Ask page (optionally remembered in instance/). Claude is grounded in a knowledge pack built from the case, the deck, the workbook and the active scenario, and can call simulate_pilot, monte_carlo, sensitivity, state_data, envelope_economics, job_exposure and place_learner. It is instructed never to cite excluded figures.

## Branding

The EY logo in static/img/logo_dark.png is taken from the team's prelim deck asset. Budgets and targets are internal case assumptions, not Government of India allocations.
