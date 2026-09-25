"""
Reference data for the AI Skill Ladder 3.0 Control Tower (Team Vertex, EY Young Leaders 2026).

Data discipline (from the team's evidence workbook):
  Observed         published statistic from an official / primary source
  Derived          calculated by us from Observed figures (formula shown)
  Benchmark        international programme or peer-reviewed research evidence
  Assumption       created by the team for the case; NOT a Government of India allocation
  Proposed target  future target proposed by the team
Figures checked against source on 25 Sep 2026. Re-check government figures on presentation day.
"""
import json
import os

_REF = os.path.join(os.path.dirname(__file__), "ref")


def _load(name):
    with open(os.path.join(_REF, name), encoding="utf-8") as fh:
        return json.load(fh)


CLASSES = {
    "obs": ("Observed", "#2E2E38", "#FFFFFF"),
    "der": ("Derived", "#747480", "#FFFFFF"),
    "ben": ("Benchmark", "#188CE5", "#FFFFFF"),
    "ass": ("Assumption", "#C4C4CD", "#2E2E38"),
    "tgt": ("Proposed target", "#FFE600", "#2E2E38"),
}

# --------------------------------------------------------------------------------------
# Sources (S01-S22 from the workbook, S23+ added in the 3.0 deck)
# --------------------------------------------------------------------------------------
SOURCES = _load("sources.json") + [
    {"id": "S23", "pub": "EY India", "title": "Unlocking productivity gains: GenAI to transform 38 million jobs by 2030 (The AIdea of India: 2025)", "date": "14 Jan 2025",
     "type": "Research (EY)", "supports": "38 mn jobs; 24% of tasks fully automatable; 42% significantly time-reduced; 8-10 hrs/week freed; 97% cite talent", "slides": "2",
     "url": "https://www.ey.com/en_in/newsroom/2025/01/unlocking-productivity-gains-gen-ai-to-transform-38-million-jobs-by-2030-ey-india", "status": "Verified via search extract"},
    {"id": "S24", "pub": "babl.ai (reporting EY AIdea of India 2025)", "title": "EY report on GenAI in India", "date": "29 Jan 2025", "type": "Secondary",
     "supports": "15% of enterprises with GenAI in production; 34% at proof of concept", "slides": "2", "url": "https://babl.ai/?p=6985", "status": "Secondary report"},
    {"id": "S25", "pub": "SBI Research", "title": "How India Works Today (PLFS 2025 unit-level analysis)", "date": "8 May 2026", "type": "Research (bank)",
     "supports": "Agriculture 43% of workforce; 14.5% in firms with 20+ workers; 42.3% in non-farm units with <19 workers", "slides": "2",
     "url": "https://sbi.bank.in/documents/13958/14472/08052026_PLFS_SBI+RESEARCH.pdf", "status": "Verified via search extract"},
    {"id": "S26", "pub": "Careers360 (reporting Lok Sabha reply)", "title": "PMKVY: only 17.7% youth placed, govt tells Lok Sabha", "date": "13 Mar 2023", "type": "Govt data, secondary",
     "supports": "17.7% of PMKVY candidates placed since inception; Rs 9,903.83 Cr utilised of Rs 11,880.50 Cr", "slides": "3, 5",
     "url": "https://news.careers360.com/pmkvy-only-17-7-percent-youth-under-pradhan-mantri-kaushal-vikas-yojana-placed-govt-tells-lok-sabha", "status": "Verified via search extract"},
    {"id": "S27", "pub": "Careers360 (reporting Parliamentary Standing Committee)", "title": "PMKVY 4.0: certification under 50%, placement data delinked", "date": "26 Apr 2025", "type": "Govt data, secondary",
     "supports": "PMKVY 4.0 delinked from placements; 19.17 lakh certified vs 45 lakh target", "slides": "3",
     "url": "https://news.careers360.com/pmkvy-4-0-under-50-pc-trainee-certification-placement-data-parliamentary-panel-skill-india-scheme-delay-kaushal-vikas-yojana-rti", "status": "Verified via search extract"},
    {"id": "S28", "pub": "British Asian Trust", "title": "Skill Impact Bond trains over 29,000 candidates", "date": "9 Oct 2024", "type": "Programme (official)",
     "supports": "29,000+ trained; 73% joined jobs; 74% women", "slides": "5, 8",
     "url": "https://www.britishasiantrust.org/latest-updates/news-events/skill-impact-bond-trains-over-29-000-candidates-empowering-women-in-the-workforce/", "status": "Verified via search extract"},
    {"id": "S29", "pub": "NSDC", "title": "Skill Impact Bond press release", "date": "2021", "type": "Primary (Govt body)",
     "supports": "USD 14.4 mn bond; target 50,000 youth, 60% women; only 10 of 100 women from skilling programmes stay in jobs for 3 months", "slides": "3, 5",
     "url": "https://www.nsdcindia.org/sites/all/modules/zibeespage/templates/images/howswork/sib.pdf", "status": "Verified via search extract"},
    {"id": "S30", "pub": "MoSPI (via PARI library)", "title": "Periodic Labour Force Survey Annual Report 2023-24", "date": "2024", "type": "Primary (Govt)",
     "supports": "Average monthly earnings of urban regular wage/salaried employees Rs 24,434 (Apr-Jun 2024)", "slides": "7",
     "url": "https://ruralindiaonline.org/ta/library/resource/periodic-labour-force-survey-plfs-annual-report-july-2023-june-2024/", "status": "Verified via search extract"},
    {"id": "S31", "pub": "Drishti IAS (MCA data)", "title": "CSR expenditure FY 2022-23", "date": "Aug 2024", "type": "Govt data, secondary",
     "supports": "Total CSR spend Rs 29,986.92 Cr in FY23; education about one-third", "slides": "7",
     "url": "https://www.drishtiias.com/daily-updates/daily-news-analysis/csir-expenditure-2023/print_manually", "status": "Verified via search extract"},
    {"id": "S32", "pub": "EY", "title": "Why CMOs should be central to every transformation (EY and Oxford Said research)", "date": "2023", "type": "Research (EY)",
     "supports": "Transformations that put humans at the centre are 2.6x more likely to succeed; six drivers", "slides": "6",
     "url": "https://www.ey.com/en_gl/consulting/why-cmos-should-be-central-to-every-transformation", "status": "Verified via search extract"},
]
SRC = {s["id"]: s for s in SOURCES}

_dv = _load("dv.json")
DATA_VERIFIED = _dv[1:] if _dv and _dv[0][0] == "ID" else _dv
_ex = _load("ex.json")
EXCLUDED = (_ex[1:] if _ex and _ex[0][0] == "Figure" else _ex) + [
    ["Rs 15,000 Cr reform model, '14x return', 'gap closes by 2030'", "Earlier versions of this tower", "Model outputs built on invented effect sizes; conflict with the no-manufactured-ROI rule", "Replaced with the pilot funnel, break-even test and Monte Carlo on stage rates"],
    ["'~12% of skilling support reaches 36-50 year olds'", "Earlier team estimate", "No published basis", "Removed; mid-career need argued from the absence of a dedicated AI credit"],
    ["Modelled state readiness index (ASRI)", "Earlier versions of this tower", "Invented pillar scores", "Replaced with PIB state-wise FutureSkills PRIME data"],
]
_qa = _load("qa.json")
QA = _qa[1:] if _qa and _qa[0][0] == "Judge question" else _qa

# --------------------------------------------------------------------------------------
# Headline figures
# --------------------------------------------------------------------------------------
HEADLINE = [
    {"key": "indiaai", "dv": "D01", "value": "₹10,371.92 Cr", "label": "IndiaAI Mission five-year outlay incl. FutureSkills pillar", "cls": "obs", "src": "S06", "asof": "7 Mar 2024"},
    {"key": "yuva", "dv": "D21", "value": "85.27 lakh", "label": "YUVA AI for ALL enrolments vs 1-crore goal", "cls": "obs", "src": "S09", "asof": "8 Jul 2026"},
    {"key": "sidh", "dv": "D20", "value": "1.5 crore+", "label": "candidates on Skill India Digital Hub", "cls": "obs", "src": "S02", "asof": "2 Feb 2026"},
    {"key": "apaar", "dv": "D19", "value": "35.27 crore", "label": "APAAR IDs; ABC live in 3,123 institutions", "cls": "obs", "src": "S05", "asof": "12 Aug 2026"},
    {"key": "naps", "dv": "D16", "value": "54.41 lakh", "label": "apprentices engaged under NAPS (all trades)", "cls": "obs", "src": "S05", "asof": "Mar 2026"},
    {"key": "pmsetu", "dv": "D17", "value": "₹60,000 Cr", "label": "PM-SETU: 1,000 govt ITIs via 200 hubs + 800 spokes", "cls": "obs", "src": "S05", "asof": "Oct 2025"},
    {"key": "naps_ai", "dv": "D15", "value": "1,480", "label": "apprentices trained in AI roles under NAPS-2 (FY23-FY26)", "cls": "obs", "src": "S04", "asof": "Jun 2025"},
    {"key": "soar", "dv": "D25", "value": "≈20%", "label": "SOAR learners certified (98,576 of 4,96,426)", "cls": "der", "src": "S02", "asof": "22 Jul 2026"},
    {"key": "labs", "dv": "D10", "value": "27", "label": "IndiaAI Data & AI Labs via NIELIT (56 centres, 9,000+ partners)", "cls": "obs", "src": "S01", "asof": "12 Aug 2026"},
    {"key": "msde", "dv": "D22", "value": "₹9,885.80 Cr", "label": "MSDE allocation FY 2026-27 (from ₹6,100 Cr)", "cls": "obs", "src": "S11", "asof": "FY27"},
]
H = {h["key"]: h for h in HEADLINE}

# Extra verified series from Data_Verified
FSP_FUNDING = {"labels": ["FY22-23", "FY23-24", "FY24-25", "FY25-26", "FY26-27"], "values": [26.59, 23.58, 55.97, 98.479, 137.17], "dv": "D08", "src": "S01"}
ITI_GROWTH = {"labels": ["2014", "2025"], "values": [9977, 14688], "dv": "D18", "src": "S05", "itots": 120}
SIDH_ECOSYSTEM = {"candidates": 15000000, "providers": 7000, "employers": 68000, "dv": "D20", "src": "S02"}
PMSETU_SANCTIONED = {"cr": 2171, "clusters": 9, "asof": "8 Sep 2026", "src": "S10", "dv": "D17"}
RC_TRAINING = {"officials": 32700, "trainers": 2367, "bootcamp_candidates": 40400, "bootcamps": 420, "rcs": 22, "dv": "D09", "src": "S01"}
PILOT_WB = {"TN": "Early adopter", "AP": "Early adopter", "KA": "Early adopter", "MH": "Early adopter", "KL": "Early adopter", "BR": "Catch-up", "AS": "Catch-up (North-East)"}
DV_REF = {"registered": "D02", "trained": "D03", "certified": "D04", "women": "D05", "tier": "D06", "fsp_rate": "D23", "soar_rate": "D25", "yuva": "D26"}

FSP_FUNNEL = {"registered": 3400000, "trained": 2300000, "certified": 1300000, "women": 0.41, "tier23": 0.86, "courses": 500, "rate_headline": 56.5, "rate_registered": 38.2,
              "src": "S01", "note": "All emerging-tech courses, not AI only. Headline figures rounded ('34 lakh+', '23 lakh+', '13 lakh+')."}
SOAR = {"enrolled": 496426, "certified": 98576, "src": "S02", "asof": "22 Jul 2026"}

DEMAND = {"jobs_mn": 38, "auto": 24, "aug": 42, "talent": 97, "prod": 15, "hours": "8-10", "src": "S23"}
WORKFORCE = {"agri": 43, "small": 42, "large": 15, "src": "S25",
             "note": "Agriculture 43% and firms with 20+ workers 14.5% (SBI Research on PLFS 2025); non-farm units under 19 workers 42.3%. Rounded to 43/42/15."}
INCENTIVE_EVIDENCE = {
    "pmkvy_placed": 17.7, "pmkvy_spent_cr": 9903.83, "sib_joined": 73, "sib_trained": 29000, "sib_women": 74, "sib_usd_mn": 14.4, "women_retained_3m": 10,
    "srcs": ["S26", "S27", "S28", "S29"],
    "caveat": "Different cohorts, sectors and definitions: directional, not a controlled comparison.",
}

# --------------------------------------------------------------------------------------
# FSP state-wise data (PIB/MeitY, 14 Aug 2026); tile = (col,row) on an 8x7 cartogram
# --------------------------------------------------------------------------------------
_TILES = {
    "Jammu and Kashmir": ("JK", 2, 0), "Ladakh": ("LA", 3, 0), "Punjab": ("PB", 2, 1), "Himachal Pradesh": ("HP", 3, 1),
    "Uttarakhand": ("UK", 4, 1), "Chandigarh": ("CH", 1, 1), "Rajasthan": ("RJ", 1, 2), "Haryana": ("HR", 2, 2),
    "NCT of Delhi": ("DL", 3, 2), "Uttar Pradesh": ("UP", 4, 2), "Bihar": ("BR", 5, 2), "Sikkim": ("SK", 6, 2),
    "Arunachal Pradesh": ("AR", 7, 2), "Gujarat": ("GJ", 1, 3), "Madhya Pradesh": ("MP", 2, 3), "Chhattisgarh": ("CG", 3, 3),
    "Jharkhand": ("JH", 4, 3), "West Bengal": ("WB", 5, 3), "Assam": ("AS", 6, 3), "Nagaland": ("NL", 7, 3),
    "Dadra & Nagar Haveli & Daman & Diu": ("DN", 1, 4), "Maharashtra": ("MH", 2, 4), "Telangana": ("TG", 3, 4),
    "Odisha": ("OD", 4, 4), "Meghalaya": ("ML", 6, 4), "Manipur": ("MN", 7, 4), "Goa": ("GA", 1, 5), "Karnataka": ("KA", 2, 5),
    "Andhra Pradesh": ("AP", 3, 5), "Puducherry": ("PY", 4, 5), "Tripura": ("TR", 6, 5), "Mizoram": ("MZ", 7, 5),
    "Lakshadweep": ("LD", 1, 6), "Kerala": ("KL", 2, 6), "Tamil Nadu": ("TN", 3, 6), "Andaman and Nicobar": ("AN", 6, 6),
}
NORTH_EAST = {"AS", "AR", "NL", "ML", "MN", "MZ", "TR", "SK"}
PILOT = {
    "TN": ("Volume leader", "Highest FSP certifications (3,61,336)"),
    "AP": ("Volume leader", "Second-highest certifications (2,44,096)"),
    "KA": ("Conversion leader", "72.2% certification rate on 2.1 lakh enrolled"),
    "OD": ("Conversion leader, East", "72.3% certification rate; eastern representation"),
    "UP": ("Scale, North", "Most populous state; 1.25 lakh enrolled at 58.4%"),
    "BR": ("Catch-up", "45,402 enrolled at 52.3%; large under-served workforce"),
    "AS": ("Catch-up, North-East", "6,074 enrolled at 47.3%; North-East representation"),
}

STATES_ALL = _load("states.json")
STATES = []
_others = None
for _name, _enr, _cert in STATES_ALL:
    if _name == "Others":
        _others = (_enr, _cert)
        continue
    _code, _col, _row = _TILES.get(_name, (_name[:2].upper(), None, None))
    STATES.append({"name": _name, "code": _code, "col": _col, "row": _row, "enrolled": _enr, "certified": _cert,
                   "rate": round(_cert / _enr * 100, 1) if _enr else 0.0, "ne": _code in NORTH_EAST,
                   "pilot": PILOT.get(_code, (None, None))[0], "pilot_why": PILOT.get(_code, (None, None))[1], "pilot_wb": PILOT_WB.get(_code)})
FSP_STATE_TOTAL = {"enrolled": sum(r[1] for r in STATES_ALL), "certified": sum(r[2] for r in STATES_ALL), "others": _others, "src": "S01"}
FSP_STATE_TOTAL["rate"] = round(FSP_STATE_TOTAL["certified"] / FSP_STATE_TOTAL["enrolled"] * 100, 1)

# --------------------------------------------------------------------------------------
# The ladder (L0-L5) and three assessment dimensions
# --------------------------------------------------------------------------------------
DIMENSIONS = [("Technical AI", "#2E2E38", "#FFFFFF"), ("Non-technical AI", "#747480", "#FFFFFF"), ("Responsible AI", "#FFE600", "#2E2E38")]
LADDER = [
    {"code": "L0", "name": "AI Awareness", "who": "Citizens, students, informal workers", "what": "Digital literacy and AI fundamentals, safe use, spotting scams and deepfakes",
     "proof": "Assisted, voice or vernacular assessment", "channels": ["YUVA AI for ALL", "SOAR", "CSCs", "BHASHINI voice"], "color": "#FFF8CC", "ink": "#2E2E38"},
    {"code": "L1", "name": "AI User", "who": "All employees, MSME owners, gig workers", "what": "Uses AI tools effectively for everyday tasks",
     "proof": "Task-based assessment", "channels": ["SOAR micro-credentials", "iGOT Karmayogi", "Regional hubs"], "color": "#FFF19A", "ink": "#2E2E38"},
    {"code": "L2", "name": "AI-Enabled Professional", "who": "Teachers, bankers, nurses, agri and govt officers", "what": "Embeds AI into a specific role and its workflows",
     "proof": "8-12-week workplace project, employer-validated", "channels": ["FSP", "AI Apprenticeship India (8-12 wks)", "AI Skill Credit"], "color": "#FFE600", "ink": "#2E2E38"},
    {"code": "L3", "name": "AI Practitioner", "who": "Builders and deployers of AI applications", "what": "Builds, deploys and evaluates AI applications",
     "proof": "≈6-month apprenticeship + portfolio", "channels": ["FSP", "NIELIT", "AI Apprenticeship India (≈6 mo)", "IndiaAI Data & AI Labs"], "color": "#747480", "ink": "#FFFFFF"},
    {"code": "L4", "name": "AI Specialist", "who": "Researchers, advanced engineers", "what": "Advanced technical or domain AI expertise",
     "proof": "9-12-month track; production system or published work", "channels": ["Academia", "AI Apprenticeship India (9-12 mo)", "IndiaAI compute"], "color": "#4A4A58", "ink": "#FFFFFF"},
    {"code": "L5", "name": "AI Leader / Governor", "who": "CXOs, senior civil servants, regulators", "what": "Strategy, transformation, risk, governance, responsible AI",
     "proof": "Governance case + peer or board review", "channels": ["iGOT Karmayogi leadership", "Council-accredited programmes"], "color": "#2E2E38", "ink": "#FFFFFF"},
]
REFRESH_RULE = "Reassess every 24 months at L2+, or sooner when skill relevance falls below 80% (proposed)."

# --------------------------------------------------------------------------------------
# Failure modes and prioritised issues
# --------------------------------------------------------------------------------------
FAILURE_MODES = [
    {"id": "FM1", "name": "Course ≠ Capability", "hurts": "Fresh graduates, employers", "cls": "der",
     "evidence": "FSP certifies 58% of enrolees (13,90,145 ÷ 23,85,414, state table) but publishes no competency or job validation; state certification rates run from 43% (Gujarat) to 72% (Karnataka, Odisha) among states with 20k+ enrolled.", "srcs": ["S01"]},
    {"id": "FM2", "name": "Certificate ≠ Signal", "hurts": "Employers, MSMEs", "cls": "obs",
     "evidence": "500+ FSP courses, 50 SOAR courses (35 micro-credentials), YUVA and vendor certificates sit on no common competency scale; UK employers name missing AI skills frameworks (35%).", "srcs": ["S01", "S03", "S16"]},
    {"id": "FM3", "name": "Training ≠ Work", "hurts": "Fresh talent, ITI and polytechnic students", "cls": "obs",
     "evidence": "Only 1,480 apprentices trained in AI roles under NAPS-2 (FY23-FY26, as of Jun 2025), inside a system that engaged 54.41 lakh apprentices overall (to Mar 2026; different period).", "srcs": ["S04", "S05"]},
    {"id": "FM4", "name": "Supply ≠ Demand", "hurts": "Mid-career workers, faculty", "cls": "ben",
     "evidence": "AI's frontier is jagged: consultants using GPT-4 were 19 pp less likely to be correct on a task outside it (758 consultants). Curricula must refresh by task, not syllabus cycle.", "srcs": ["S19"]},
    {"id": "FM5", "name": "Access ≠ Equity", "hurts": "Women, PwD, rural, informal, 40+", "cls": "obs",
     "evidence": "Entry is broad (FSP: 41% women, 86% Tier-2/3), but outcomes by gender, region, disability or language are not reported; no dedicated mid-career AI credit exists.", "srcs": ["S01"]},
]
FM_INDEX = {f["id"]: f for f in FAILURE_MODES}

# Urgency / impact are qualitative team scores (1-10) used only to place items in quadrants.
PRIORITIES = [
    {"id": "P1", "name": "Learning → work disconnect", "urgency": 9.0, "impact": 9.0, "fm": ["FM1", "FM3"], "levers": ["I2", "I3"]},
    {"id": "P2", "name": "Practical workplace exposure", "urgency": 8.6, "impact": 8.8, "fm": ["FM3"], "levers": ["I3", "I6"]},
    {"id": "P3", "name": "Fragmented skill taxonomy", "urgency": 8.2, "impact": 8.0, "fm": ["FM2"], "levers": ["I1"]},
    {"id": "P4", "name": "Mid-career transition", "urgency": 7.8, "impact": 8.4, "fm": ["FM4", "FM5"], "levers": ["I4", "I7"]},
    {"id": "P5", "name": "Provider incentives", "urgency": 8.8, "impact": 8.6, "fm": ["FM1"], "levers": ["I2"]},
    {"id": "P6", "name": "Advanced research talent", "urgency": 5.8, "impact": 8.2, "fm": ["FM4"], "levers": ["I3", "I6"]},
    {"id": "P7", "name": "Trainer readiness", "urgency": 6.6, "impact": 8.0, "fm": ["FM1", "FM4"], "levers": ["I5"]},
    {"id": "P8", "name": "Responsible AI competence", "urgency": 6.2, "impact": 7.6, "fm": ["FM4"], "levers": ["I1", "I5"]},
    {"id": "P9", "name": "Inclusion by design", "urgency": 6.8, "impact": 8.8, "fm": ["FM5"], "levers": ["I4", "I6"]},
    {"id": "P10", "name": "Language access via BHASHINI", "urgency": 7.4, "impact": 6.4, "fm": ["FM5"], "levers": ["I6"]},
    {"id": "P11", "name": "Scheme duplication", "urgency": 7.2, "impact": 6.2, "fm": ["FM2"], "levers": ["I1"]},
    {"id": "P12", "name": "Basic AI awareness", "urgency": 5.0, "impact": 5.5, "fm": [], "levers": [],
     "note": "Already at scale via YUVA AI for ALL and SOAR: sustain, do not add spend."},
]

# --------------------------------------------------------------------------------------
# Seven interventions
# --------------------------------------------------------------------------------------
INTERVENTIONS = [
    {"id": "I1", "short": "Skill Graph + Passport", "title": "Skill Graph + AI Skill Passport", "color": "#FFE600",
     "mechanism": "One national taxonomy: jobs → tasks → skills → assessments. The Passport is a verifiable record on APAAR/ABC, DigiLocker and SIDH; no new ID.",
     "outcome": "Employers read verified depth, not course names", "fixes": ["FM2", "FM4"], "rails": ["APAAR/ABC", "DigiLocker", "SIDH"],
     "owner": "National AI Skills Council (MeitY, MSDE-NCVET, MoE-AICTE)", "pilot_line": "Skill Graph + Passport"},
    {"id": "I2", "short": "Outcome marketplace", "title": "Outcome-based Training Marketplace", "color": "#2DB757",
     "mechanism": "Accredited providers paid in milestones 15/20/25/20/20 (enrolment, completion, competency, applied project, work outcome): 65% only after evidence. Disadvantage-weighted to stop cherry-picking.",
     "outcome": "Pay for capability, not seat counts", "fixes": ["FM1", "FM2"], "rails": ["FSP", "SOAR", "NCVET awarding bodies"],
     "owner": "Council with MSDE/NSDC", "pilot_line": "Assessment infrastructure"},
    {"id": "I3", "short": "AI Apprenticeship India", "title": "AI Apprenticeship India", "color": "#188CE5",
     "mechanism": "Three tracks on NAPS rails: 8-12 weeks (L2), ≈6 months (L3), 9-12 months (L4). Learn → apply → employer-validate → transition.",
     "outcome": "Workplace evidence enters the Passport", "fixes": ["FM1", "FM3"], "rails": ["NAPS"],
     "owner": "MSDE (NAPS) with industry", "pilot_line": "Apprenticeships"},
    {"id": "I4", "short": "AI Skill Credit", "title": "Targeted AI Skill Credit", "color": "#B14891",
     "mechanism": "₹2-3k youth, ₹5-10k professionals, ₹15-25k mid-career, plus top-ups for priority groups. Redeemable only on accredited, assessed pathways.",
     "outcome": "Funded mid-career moves, no certificate inflation", "fixes": ["FM5"], "rails": ["SIDH", "DBT"],
     "owner": "MSDE", "pilot_line": "AI Skill Credits"},
    {"id": "I5", "short": "Trainer Corps", "title": "National AI Trainer Corps", "color": "#27ACAA",
     "mechanism": "Master → regional → local facilitators. Train → teach → audit → renew. Builds on 120 IToTs and NIELIT resource centres.",
     "outcome": "Trainers certified on AI, pedagogy, assessment and ethics", "fixes": ["FM1", "FM4", "FM5"], "rails": ["120 IToTs", "NIELIT RCs"],
     "owner": "MSDE (DGT) with MoE and NIELIT", "pilot_line": "Trainer network"},
    {"id": "I6", "short": "Regional hubs", "title": "Regional AI Workforce Hubs", "color": "#FF6D00",
     "mechanism": "AI layer on PM-SETU ITI hubs, 27 IndiaAI Data & AI Labs and NIELIT centres: labs, assessment, MSME problem statements, local language.",
     "outcome": "Digital-first, not digital-only", "fixes": ["FM3", "FM5"], "rails": ["PM-SETU", "IndiaAI labs", "NIELIT"],
     "owner": "States with MSDE and MeitY", "pilot_line": "Regional hub enablement"},
    {"id": "I7", "short": "Transition Exchange", "title": "AI Transition Exchange", "color": "#FF4136",
     "mechanism": "Employer demand → AI task extraction → skill gap → pathway → assessment → apprenticeship → job or internal move; runs on SIDH + NCS.",
     "outcome": "Demand pulls supply; reskilling becomes continuous", "fixes": ["FM3", "FM4"], "rails": ["SIDH", "NCS"],
     "owner": "Council with industry bodies", "pilot_line": "Employer challenge fund"},
]
INT_INDEX = {i["id"]: i for i in INTERVENTIONS}

# --------------------------------------------------------------------------------------
# Budget model (internal assumptions; mirrors the workbook's Budget_Model sheet)
# --------------------------------------------------------------------------------------
PILOT_LINES = [
    {"key": "appr", "line": "Apprenticeships", "qty": 10000, "unit": 70000, "lump": None, "basis": "≈10,000 AI apprentices × ≈₹70,000 (stipend top-up, mentoring, assessment)", "int": "I3"},
    {"key": "hubs", "line": "Regional hub enablement", "qty": 35, "unit": 11428571, "lump": None, "basis": "≈35 hubs (5 per pilot state) × ≈₹1.14 Cr AI-lab layer on existing ITI/NIELIT sites", "int": "I6"},
    {"key": "graph", "line": "Skill Graph + Passport", "qty": None, "unit": None, "lump": 35, "basis": "Taxonomy, graph, credential schema and APIs on SIDH/APAAR/DigiLocker", "int": "I1"},
    {"key": "trainers", "line": "Trainer network", "qty": None, "unit": None, "lump": 35, "basis": "≈5,000 facilitators + ≈250 master trainers certified", "int": "I5"},
    {"key": "assess", "line": "Assessment infrastructure", "qty": 150000, "unit": 2000, "lump": None, "basis": "≈1.5 lakh competency assessments × ≈₹2,000 incl. item bank and proctoring", "int": "I2"},
    {"key": "challenge", "line": "Employer challenge fund", "qty": 300, "unit": 1000000, "lump": None, "basis": "≈300 employer/MSME projects × ≈₹10 lakh matched grant", "int": "I7"},
    {"key": "credits", "line": "AI Skill Credits", "qty": 50000, "unit": 5000, "lump": None, "basis": "≈50,000 credits × ≈₹5,000 average", "int": "I4"},
    {"key": "eval", "line": "Independent evaluation", "qty": None, "unit": None, "lump": 10, "basis": "Third-party evaluation incl. baseline and comparison districts", "int": None},
    {"key": "cont", "line": "Contingency", "qty": None, "unit": None, "lump": 15, "basis": "≈5% of pilot", "int": None},
]
PILOT_CAP_CR = 290
ENVELOPE = [("Role-ready learners", 2100), ("Advanced practitioners", 2000), ("Apprenticeship / industry challenge", 600), ("Contingency", 400),
            ("Skill Graph + Passport", 350), ("Foundation assessment / conversion", 350), ("Trainer / faculty corps", 300),
            ("Regional / inclusion", 250), ("Governance / evaluation", 150)]
FINANCING = [("Central Government", 4000), ("Industry", 1250), ("States", 750), ("CSR / philanthropy", 500)]
ECON = {"role_ready_target": 3000000, "advanced_target": 100000, "years": 5, "msde_fy27_cr": 9885.80, "csr_fy23_cr": 29986.92,
        "urban_monthly_earnings": 24434, "pilot_entrants": 150000, "vacr_target": 0.40}

# --------------------------------------------------------------------------------------
# KPIs, gates, roadmap, risks
# --------------------------------------------------------------------------------------
KPIS = [
    {"key": "vacr", "type": "North Star", "name": "Verified AI Workforce Conversion Rate (VACR)", "formula": "Learners achieving verified workplace competency ÷ learners entering × 100",
     "baseline": "Not measured today", "target": 40, "unit": "%", "cmp": ">=", "gate": "G4", "kirk": "L3 Behaviour"},
    {"key": "completion", "type": "Pilot target", "name": "Completion rate", "formula": "Completed ÷ enrolled", "baseline": "FSP ≈57% of enrolled certified (headline, D23); 58.3% on the state table; SOAR ≈20% (D25)",
     "target": 70, "unit": "%", "cmp": ">=", "gate": "G2", "kirk": "L2 Learning"},
    {"key": "competency", "type": "Pilot target", "name": "Competency validation", "formula": "Passed independent assessment ÷ completed", "baseline": "Not measured; set in Phase 0",
     "target": 60, "unit": "%", "cmp": ">=", "gate": "G3", "kirk": "L2 Learning"},
    {"key": "transition", "type": "Pilot target", "name": "Transition to apprenticeship / job / deployment", "formula": "Transitioned ÷ entered", "baseline": "Not publicly reported",
     "target": 40, "unit": "%", "cmp": ">=", "gate": "G4", "kirk": "L3 Behaviour"},
    {"key": "employer_sat", "type": "Pilot target", "name": "Employer satisfaction", "formula": "Employers rating converts ≥4/5 ÷ employers surveyed", "baseline": "No national measure",
     "target": 80, "unit": "%", "cmp": ">=", "gate": "G4", "kirk": "L4 Results"},
    {"key": "women", "type": "Pilot target", "name": "Women share of verified converts", "formula": "Women converts ÷ all converts", "baseline": "41% of FSP candidates (entry, not outcome; D05)",
     "target": 45, "unit": "%", "cmp": ">=", "gate": "G6", "kirk": "L4 Results"},
    {"key": "tier23", "type": "Pilot target", "name": "Tier-2/3 share of verified converts", "formula": "Tier-2/3 converts ÷ all converts", "baseline": "86% of FSP candidates (entry, not outcome; D06)",
     "target": 70, "unit": "%", "cmp": ">=", "gate": "G6", "kirk": "L4 Results"},
    {"key": "relevance", "type": "Novel KPI", "name": "Skill relevance", "formula": "Currently valid competencies ÷ previously certified competencies", "baseline": "New metric",
     "target": 80, "unit": "%", "cmp": ">=", "gate": None, "kirk": "L4 Results"},
    {"key": "cost_per_convert", "type": "Economics", "name": "Cost per verified convert", "formula": "Pilot spend ÷ verified converts", "baseline": "Not measured",
     "target": 60417, "unit": "₹", "cmp": "<=", "gate": "G5", "kirk": "L5 ROI"},
]
GATES = [
    {"id": "G1", "name": "Technical feasibility", "test": "Passport issues and verifies across SIDH / APAAR / DigiLocker", "month": 6},
    {"id": "G2", "name": "Learner adoption", "test": "Entrants at plan and completion ≥70%", "month": 10},
    {"id": "G3", "name": "Competency validation", "test": "≥60% of completers validated; integrity audit clean", "month": 14},
    {"id": "G4", "name": "Workforce outcome", "test": "VACR ≥40%; transition ≥40%; employer satisfaction ≥80%", "month": 18},
    {"id": "G5", "name": "Economic viability", "test": "Cost per verified convert ≤₹60,417 (plan +25%); spend within ₹290 Cr", "month": 18},
    {"id": "G6", "name": "Equity", "test": "Women ≥45% and Tier-2/3 ≥70% of verified converts", "month": 18},
]
PHASES = [
    {"id": "P0", "name": "Design", "start": 0, "end": 6, "goal": "Council, taxonomy v1, programme inventory, baseline, standards, comparison districts, pilot design"},
    {"id": "P1", "name": "Pilot", "start": 6, "end": 18, "goal": "7 states, each with a university cluster, ITI/polytechnic, MSME cluster, govt department, employer consortium and rural district"},
    {"id": "P2", "name": "Scale", "start": 18, "end": 36, "goal": "15-20 states; 1,000+ employers; 3M role-ready; 100K advanced (proposed)"},
    {"id": "P3", "name": "Institutionalise", "start": 36, "end": 60, "goal": "National rollout, employer co-funding, refresh cycles, independent impact evaluation"},
]
WORKSTREAMS = [
    {"name": "Standards & Skill Graph", "bars": [(0, 6, "Taxonomy", "Taxonomy v1 + Passport schema"), (6, 60, "Graph live; quarterly skill refresh")]},
    {"name": "Delivery: hubs, trainers, credits", "bars": [(6, 18, "35 hubs, 5,000 trainers, credits"), (18, 60, "Scale via PM-SETU hubs and NIELIT")]},
    {"name": "Apprenticeships & employers", "bars": [(6, 18, "10,000 AI apprentices"), (18, 60, "1,000+ employers; industry co-funding rises")]},
    {"name": "Evaluation & gates", "bars": [(0, 6, "Baseline", "Baseline + comparison districts"), (18, 60, "Independent evaluation; 2-3-year outcome tracking")]},
]
RISKS = [
    ("Course / credential inflation", "High", "Provider accreditation + independent assessment", "NCVET / Council", "G3"),
    ("Low completion", "High", "Modular learning + milestone funding", "Providers", "G2"),
    ("Providers cherry-pick easy learners", "Medium", "Disadvantage-weighted outcome payments", "Council", "G6"),
    ("Weak practical capability", "High", "Mandatory applied projects / apprenticeships", "Industry + providers", "G3/G4"),
    ("Industry disengagement / no apprenticeships", "Medium", "Co-funding, challenge fund, demand commitments; public departments as employer of first resort", "Industry + Council", "G4"),
    ("AI hallucination / misinformation in content", "Medium", "Expert verification before release; grounded tutors; human high-stakes assessment", "Delivery unit", "G1/G3"),
    ("Data / privacy risk", "Medium", "Consent-based Passport, learner-controlled sharing (DPDP Act 2023)", "Council", "G1"),
    ("Cybersecurity", "Medium", "CERT-In-aligned controls; independent audit", "Tech partner", "G1"),
    ("Regional exclusion", "High", "Assisted learning at hubs/CSCs; voice and vernacular (BHASHINI); offline modules", "Hubs", "G6"),
    ("Faculty / trainer shortage", "High", "National AI Trainer Corps", "Delivery unit", "G2"),
    ("Skill obsolescence", "High", "Skill-relevance KPI triggers refresh", "Skills Intelligence", "Ongoing"),
    ("Programme duplication", "Medium", "National convergence dashboard", "Council", "G5"),
    ("Cost overrun", "Medium", "Stage gates; capped ₹290 Cr pilot", "Council", "G5"),
    ("Employer mismatch", "Medium", "Employer-defined competency standards", "Industry", "G4"),
    ("Pilot fails a gate", "-", "Redesign or stop; loss capped at ₹290 Cr; baseline data still gained", "Council", "All"),
]
ACTORS = [
    ("National AI Skills Council", "MeitY (IndiaAI) + MSDE (NCVET) + MoE (AICTE): policy, taxonomy, standards, interoperability, funding, QA, equity, responsible AI", "One accountable owner"),
    ("Industry & MSMEs", "Demand signals, task definitions, projects, apprenticeships, validation, co-funding", "Pre-verified talent, co-funded projects"),
    ("Training providers", "Delivery, mentoring, local implementation", "Higher pay for better outcomes"),
    ("Academia", "Advanced curriculum, research, faculty development, L4 specialists", "Research pipeline, faculty upgrade"),
    ("Independent assessors", "NCVET-recognised awarding bodies: competency validation, integrity, credential verification", "Portable-signal market"),
    ("Learners", "Build Passport and portfolio; refresh on cadence", "Portable signal + skill credit"),
]
RACI_COLS = ["Council", "MSDE / NCVET", "MeitY / IndiaAI", "MoE / AICTE", "States", "Industry", "Assessors"]
RACI = [
    ("Taxonomy, Skill Graph, Passport", ["A", "R", "R", "C", "I", "C", "C"]),
    ("Outcome-based provider contracts", ["A", "R", "C", "I", "C", "I", "C"]),
    ("AI Apprenticeship India", ["A", "R", "I", "C", "C", "R", "C"]),
    ("AI Skill Credit", ["A", "R", "I", "I", "C", "I", "I"]),
    ("Trainer Corps", ["A", "R", "C", "R", "C", "C", "C"]),
    ("Regional hubs", ["A", "C", "R", "I", "R", "C", "I"]),
    ("Transition Exchange", ["A", "R", "C", "I", "C", "R", "I"]),
    ("Independent evaluation and gates", ["A", "C", "C", "C", "I", "I", "R"]),
]
BENCHMARKS = [  # rows 1-8 mirror the workbook sheet Benchmarks_Research; rows marked added=True come from the 3.0 deck sources
    {"where": "Singapore", "what": "SkillsFuture Credit (base)", "facts": "S$500 opening credit for all citizens 25+; no expiry (since 2015)", "lesson": "Individual learning account builds ownership of lifelong learning", "use": "AI Skill Credit bands for youth/professionals", "src": ["S13"]},
    {"where": "Singapore", "what": "SkillsFuture Credit (Mid-Career)", "facts": "S$4,000 for citizens 40+ from 1 May 2024; only for selected industry/employment-oriented courses", "lesson": "Money follows employability, targeted at those facing skill obsolescence", "use": "Mid-career band ₹15-25k, redeemable only on accredited, assessed pathways", "src": ["S12", "S13"]},
    {"where": "Singapore", "what": "AI Apprenticeship Programme (AIAP)", "facts": "6- or 9-month track; real industry projects; S$4,000/month stipend; >90% placed in AI roles within 6 months (programme-reported)", "lesson": "Employer-linked projects convert learning into workplace capability", "use": "AI Apprenticeship India tracks: 8-12 wks (L2), ≈6 mo (L3), 9-12 mo (L4)", "src": ["S14"]},
    {"where": "United Kingdom", "what": "Skills England SKAI / PRIMES", "facts": "PRIMES: Practical, Reachable, Integrated, Modular, Expandable, Sustainable; 23 workshops, ≈150 orgs, survey n=536", "lesson": "AI training must be role-based, modular, accessible and continuously refreshed", "use": "Ladder design; modular pathways; refresh cycle", "src": ["S15"]},
    {"where": "United Kingdom", "what": "SKAI insight briefing", "facts": "Most-missing features: flexible/accessible delivery 51%; clear AI skills frameworks 35%; practical learning 34%; trainer shortage", "lesson": "The gap is quality and relevance, not just access", "use": "National competency taxonomy + Trainer Corps", "src": ["S16"]},
    {"where": "Research", "what": "Brynjolfsson, Li & Raymond: Generative AI at Work", "facts": "5,179 agents: +14% productivity avg, +34% novice/low-skilled, minimal for experienced (WP); ≈15% avg in QJE 2025 (5,172 agents)", "lesson": "Gains are heterogeneous and largest where skills are thinnest: one field study, not a universal effect", "use": "Prioritise novices, mid-career and L1-L2 workers", "src": ["S17", "S18"]},
    {"where": "Research", "what": "Dell'Acqua et al.: Jagged Technological Frontier", "facts": "758 BCG consultants: inside frontier +12.2% tasks, 25.1% faster, >40% quality; outside frontier 19 pp less likely correct", "lesson": "Knowing when NOT to trust AI is a skill", "use": "Responsible AI assessed at every ladder level; human-in-the-loop", "src": ["S19"]},
    {"where": "Research", "what": "Card, Kluve & Weber: ALMP meta-analysis", "facts": "200+ studies: impacts ≈0 short-run, positive after 2-3 yrs; larger for human-capital programmes and women", "lesson": "Judge training programmes over years, not months", "use": "Track outcomes to year 3; independent evaluation as scale gate", "src": ["S20", "S21"]},
    {"where": "India", "what": "Skill Impact Bond (outcome-funded)", "facts": "29,000+ trained; 73% joined jobs; 74% women; USD 14.4 mn", "lesson": "Paying for outcomes changes provider behaviour", "use": "Outcome-based Training Marketplace", "src": ["S28", "S29"], "added": True},
    {"where": "India", "what": "PMKVY (largely paid per trainee)", "facts": "17.7% of candidates placed since inception; ₹9,903.83 Cr utilised; PMKVY 4.0 delinked from placement", "lesson": "Paying for seats measures seats", "use": "Why milestone payments", "src": ["S26", "S27"], "added": True},
]
SDGS = [("4.4", "Skills for employment", "#C5192D"), ("4.c", "Qualified teachers (Trainer Corps)", "#C5192D"), ("5.5", "Women's participation", "#FF3A21"),
        ("8.2", "Productivity via technology", "#A21942"), ("8.5", "Decent work", "#A21942"), ("8.6", "Youth in employment or training", "#A21942"),
        ("9.5", "Research capacity (L4)", "#FD6925"), ("10.2", "Inclusion by age, sex, location, disability", "#DD1367"),
        ("16.6", "Accountable institutions (dashboard, evaluation)", "#00689D"), ("17.17", "Public-private partnerships", "#19486A")]
