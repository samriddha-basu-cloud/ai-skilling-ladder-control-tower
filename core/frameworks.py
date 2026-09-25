"""
Framework layer. EY frameworks used (public sources):
  - The AIdea of India 2025 (EY India): 3A task lens (automation, augmentation, amplification)  [S23]
  - Long-Term Value: human, consumer (citizen/learner), societal, financial value
  - Humans@Center (EY and Oxford Said): Lead, Inspire, Care, Empower, Build, Collaborate  [S32]
Plus standard consulting tools: MECE issue tree, PESTLE, power-interest grid, Kirkpatrick-Phillips.
All scores in this file are team judgements (class: Assumption) unless a source ID is given.
"""

ISSUE_TREE = {
    "question": "How can India turn AI-skilling access into verified capability and work outcomes, for every age group, at national scale?",
    "branches": [
        {"id": "B1", "name": "Demand: what capability does work need?", "color": "#188CE5", "nodes": [
            {"q": "How much work will GenAI change?", "h": "38 mn organised-sector jobs; 24% of task time automatable, 42% sharply reduced.", "status": "supported", "ev": "EY AIdea of India 2025 [S23]", "link": "FM4"},
            {"q": "Where are the gains largest?", "h": "Among novices and thin-skill workers.", "status": "supported", "ev": "+34% for novice agents vs +14% average [S17]", "link": "FM4"},
            {"q": "Is demand signalled to providers?", "h": "No common jobs → tasks → skills taxonomy exists.", "status": "supported", "ev": "500+ FSP and 50 SOAR courses on no common scale [S01, S03]", "link": "FM2"},
        ]},
        {"id": "B2", "name": "Supply: do the rails exist?", "color": "#27ACAA", "nodes": [
            {"q": "Is access the constraint?", "h": "No: access is at scale.", "status": "supported", "ev": "85.27 lakh YUVA, 34 lakh+ FSP, 1.5 crore+ SIDH [S09, S01, S02]", "link": "FM5"},
            {"q": "Is the plumbing for an outcome layer in place?", "h": "Yes: APAAR/ABC, DigiLocker, BHASHINI, NCS, NAPS.", "status": "supported", "ev": "35.27 crore APAAR IDs; SIDH integrations [S05, S02]", "link": "I1"},
            {"q": "Are trainers ready for AI?", "h": "Trainer shortage with AI + sector expertise.", "status": "partial", "ev": "UK SKAI names trainer shortage [S16]; no Indian measure", "link": "FM1"},
        ]},
        {"id": "B3", "name": "Conversion: does learning become work?", "color": "#FFE600", "nodes": [
            {"q": "Do learners complete?", "h": "Partly: FSP 58%, SOAR ≈20%.", "status": "supported", "ev": "13,90,145 ÷ 23,85,414; 98,576 ÷ 4,96,426 [S01, S02]", "link": "FM1"},
            {"q": "Is competence verified?", "h": "Not reported in any public release.", "status": "supported", "ev": "FSP release has no competency or placement field [S01]", "link": "FM1"},
            {"q": "Do learners reach AI work?", "h": "Rarely through apprenticeships.", "status": "supported", "ev": "1,480 AI-role apprentices under NAPS-2 [S04]", "link": "FM3"},
        ]},
        {"id": "B4", "name": "Incentives: what are providers paid for?", "color": "#FF6D00", "nodes": [
            {"q": "Does per-seat funding deliver jobs?", "h": "No.", "status": "supported", "ev": "PMKVY 17.7% placed; 4.0 delinked from placement [S26, S27]", "link": "I2"},
            {"q": "Does outcome funding work in India?", "h": "Yes, directionally.", "status": "supported", "ev": "Skill Impact Bond: 73% joined jobs, 74% women [S28]", "link": "I2"},
            {"q": "Will outcome pay push providers to cherry-pick?", "h": "Risk exists; disadvantage weighting mitigates.", "status": "test", "ev": "Test in Phase 1 with equity gate G6", "link": "G6"},
        ]},
        {"id": "B5", "name": "Equity: who is left behind?", "color": "#B14891", "nodes": [
            {"q": "Who must be reached?", "h": "Most workers have no employer L&D.", "status": "supported", "ev": "43% in agriculture; 14.5% in 20+ worker firms [S25]", "link": "FM5"},
            {"q": "Do women convert to work?", "h": "Entry is broad; retention historically weak.", "status": "partial", "ev": "41% FSP women [S01]; 10 in 100 stay 3 months [S29]", "link": "FM5"},
            {"q": "Is there mid-career support?", "h": "No dedicated AI credit exists.", "status": "supported", "ev": "Contrast: Singapore S$4,000 at 40+ [S12]", "link": "I4"},
        ]},
    ],
}

PESTLE = [
    {"dim": "Political", "items": [
        {"f": "IndiaAI Mission ₹10,371.92 Cr with a FutureSkills pillar [S06]", "dir": "tail", "w": 5},
        {"f": "AI skilling spread across MeitY, MSDE and MoE schemes", "dir": "head", "w": 4},
        {"f": "MSDE allocation up to ₹9,885.80 Cr in FY27 from ₹6,100 Cr [S11]", "dir": "tail", "w": 4}]},
    {"dim": "Economic", "items": [
        {"f": "GenAI could transform 38 mn organised jobs by 2030 [S23]", "dir": "tail", "w": 5},
        {"f": "Only 14.5% of workers are in firms with 20+ workers: thin employer L&D [S25]", "dir": "head", "w": 4},
        {"f": "PM-SETU ₹60,000 Cr ITI upgrade creates hub sites [S05]", "dir": "tail", "w": 4}]},
    {"dim": "Social", "items": [
        {"f": "Broad entry: 41% women, 86% Tier-2/3 FSP candidates [S01]", "dir": "tail", "w": 4},
        {"f": "Women's job retention after skilling historically low (10 in 100 at 3 months) [S29]", "dir": "head", "w": 4},
        {"f": "43% of workers in agriculture need voice-first, assisted delivery [S25]", "dir": "head", "w": 3}]},
    {"dim": "Technological", "items": [
        {"f": "DPI rails ready: APAAR 35.27 crore IDs, DigiLocker, BHASHINI, SIDH [S05, S02]", "dir": "tail", "w": 5},
        {"f": "Jagged AI frontier makes curricula age fast [S19]", "dir": "head", "w": 4},
        {"f": "27 IndiaAI Data & AI Labs via NIELIT [S01]", "dir": "tail", "w": 3}]},
    {"dim": "Legal", "items": [
        {"f": "DPDP Act 2023 requires consent-based learner data [S22]", "dir": "head", "w": 3},
        {"f": "NSQF / NCrF and ABC allow stackable, credit-linked micro-credentials [S03, S05]", "dir": "tail", "w": 4},
        {"f": "NAPS rails allow AI apprenticeship tracks [S05]", "dir": "tail", "w": 3}]},
    {"dim": "Environmental", "items": [
        {"f": "Shared hub labs avoid duplicated compute and hardware", "dir": "tail", "w": 2},
        {"f": "AI skills for agriculture and climate-resilient livelihoods at L1-L2", "dir": "tail", "w": 2}]},
]

STAKEHOLDER_MAP = [
    {"name": "National AI Skills Council", "power": 9.4, "interest": 9.2, "stance": "Champion"},
    {"name": "MeitY / IndiaAI", "power": 8.8, "interest": 9.0, "stance": "Champion"},
    {"name": "MSDE / NCVET / NSDC", "power": 8.6, "interest": 9.2, "stance": "Champion"},
    {"name": "MoE / AICTE", "power": 7.8, "interest": 7.0, "stance": "Supportive"},
    {"name": "Ministry of Finance", "power": 9.0, "interest": 4.4, "stance": "Neutral"},
    {"name": "Pilot states (7)", "power": 7.0, "interest": 8.4, "stance": "Supportive"},
    {"name": "Other states", "power": 6.6, "interest": 5.0, "stance": "Neutral"},
    {"name": "Industry & MSMEs", "power": 6.6, "interest": 7.8, "stance": "Supportive"},
    {"name": "Training providers", "power": 4.4, "interest": 9.0, "stance": "Mixed"},
    {"name": "Independent assessors", "power": 4.0, "interest": 7.6, "stance": "Supportive"},
    {"name": "Faculty and trainers", "power": 3.8, "interest": 6.8, "stance": "Mixed"},
    {"name": "Learners", "power": 2.8, "interest": 9.0, "stance": "Supportive"},
    {"name": "Media and civil society", "power": 5.0, "interest": 3.6, "stance": "Neutral"},
]

HUMANS_AT_CENTER = [
    {"driver": "Lead", "question": "Is one owner visibly accountable for outcomes?", "baseline": 2.2, "target": 4.2, "owner": "National AI Skills Council",
     "actions": ["Joint Council of MeitY, MSDE and MoE with one mission director", "VACR and six gates reviewed quarterly", "Pilot-state secretaries sign outcome compacts"]},
    {"driver": "Inspire", "question": "Do learners see where the ladder leads?", "baseline": 2.6, "target": 4.4, "owner": "Council + MyGov",
     "actions": ["Every level shown as a job and wage path", "Passport stories from pilot districts", "Employer pledges published"]},
    {"driver": "Care", "question": "Are fears about AI and job loss addressed?", "baseline": 1.8, "target": 4.0, "owner": "Regional hubs",
     "actions": ["Counsellors at hubs and CSCs", "Apprentice stipends and flexible timing", "Mid-career credit framed as income protection"]},
    {"driver": "Empower", "question": "Do learners and states control their choices?", "baseline": 2.4, "target": 4.1, "owner": "MSDE + States",
     "actions": ["Learner-owned Passport and credit", "Any accredited provider, any assessed pathway", "States choose hub sites"]},
    {"driver": "Build", "question": "Are platforms and processes ready?", "baseline": 3.0, "target": 4.3, "owner": "MeitY + NCVET",
     "actions": ["Reuse SIDH, APAAR, DigiLocker, BHASHINI", "Independent assessment item bank", "Convergence dashboard"]},
    {"driver": "Collaborate", "question": "Do government, academia and industry work as one?", "baseline": 2.5, "target": 4.2, "owner": "Council + industry bodies",
     "actions": ["Employers co-write competency standards", "Challenge fund for MSME problem statements", "Public departments as employer of first resort"]},
]
CONFIDENCE_3C = [
    {"c": "Capabilities", "q": "Are the right structures, processes, tools and skills in place?", "baseline": 2.7},
    {"c": "Content", "q": "Does the roadmap prioritise value-generating, human-centred journeys?", "baseline": 3.5},
    {"c": "Culture", "q": "Do leaders and the delivery team model outcome-first behaviour?", "baseline": 2.3},
]

KIRKPATRICK = [
    {"level": 1, "name": "Reaction", "measure": "Learner relevance and satisfaction per module", "tool": "In-app pulse", "kpi": "Tracked, not gated", "cadence": "Continuous"},
    {"level": 2, "name": "Learning", "measure": "Completion and independent competency validation", "tool": "NCVET awarding bodies, Passport", "kpi": "Completion ≥70%; competency ≥60%", "cadence": "Monthly"},
    {"level": 3, "name": "Behaviour", "measure": "Applied project or apprenticeship; employer-validated workplace competency", "tool": "Workplace mentor + employer validation", "kpi": "Transition ≥40%; VACR ≥40%", "cadence": "Quarterly"},
    {"level": 4, "name": "Results", "measure": "Jobs, internal moves, wages, productivity; equity of converts", "tool": "Passport outcome at 6 and 12 months; comparison districts", "kpi": "Employer satisfaction ≥80%; women ≥45%; Tier-2/3 ≥70%", "cadence": "6 and 12 months, to year 3"},
    {"level": 5, "name": "ROI (Phillips)", "measure": "Measured benefit vs cost per verified convert", "tool": "Independent evaluation with comparison districts", "kpi": "Cost per convert within band; break-even trajectory", "cadence": "Month 18 and year 3"},
]

LTV_DIMS = [
    {"key": "human", "name": "Human value", "desc": "Verified capability, employability and wages", "color": "#FFE600"},
    {"key": "citizen", "name": "Citizen & learner value", "desc": "Access, portability, trust and choice", "color": "#27ACAA"},
    {"key": "societal", "name": "Societal value", "desc": "Inclusion across gender, region, age; responsible AI", "color": "#B14891"},
    {"key": "financial", "name": "Financial value", "desc": "Cost per verified outcome; less training waste", "color": "#2DB757"},
]
LTV_SCORES = {
    "I1": {"human": 3, "citizen": 5, "societal": 3, "financial": 4, "metric": "Passports verified by employers"},
    "I2": {"human": 5, "citizen": 3, "societal": 4, "financial": 5, "metric": "Share of fees paid after evidence; cost per convert"},
    "I3": {"human": 5, "citizen": 3, "societal": 3, "financial": 3, "metric": "Transition and VACR"},
    "I4": {"human": 4, "citizen": 5, "societal": 5, "financial": 2, "metric": "Mid-career and priority-group converts"},
    "I5": {"human": 4, "citizen": 3, "societal": 3, "financial": 3, "metric": "Certified trainers; competency pass rates by trainer"},
    "I6": {"human": 4, "citizen": 4, "societal": 5, "financial": 2, "metric": "Tier-2/3, rural and vernacular converts"},
    "I7": {"human": 5, "citizen": 3, "societal": 3, "financial": 4, "metric": "Internal moves and employer repeat demand"},
}

# EY 3A lens (S23). Role-level shares and workforce split are TEAM ESTIMATES calibrated to EY's
# averages (24% automatable, 42% augmentable, 38 mn jobs). rung = ladder level needed.
ROLES = [
    {"role": "Software developer", "sector": "IT/ITeS", "workforce": 42, "auto": 0.22, "aug": 0.54, "amp": 0.14, "rung": 3},
    {"role": "Contact centre and BPO agent", "sector": "IT/ITeS", "workforce": 32, "auto": 0.46, "aug": 0.36, "amp": 0.06, "rung": 2},
    {"role": "Bank and insurance operations", "sector": "Financial services", "workforce": 30, "auto": 0.34, "aug": 0.46, "amp": 0.08, "rung": 2},
    {"role": "Accountant and financial analyst", "sector": "Financial services", "workforce": 24, "auto": 0.30, "aug": 0.48, "amp": 0.10, "rung": 2},
    {"role": "Teacher and faculty", "sector": "Education", "workforce": 48, "auto": 0.12, "aug": 0.46, "amp": 0.20, "rung": 2},
    {"role": "Retail sales and store staff", "sector": "Retail", "workforce": 40, "auto": 0.18, "aug": 0.32, "amp": 0.08, "rung": 1},
    {"role": "Nurse and health administrator", "sector": "Healthcare", "workforce": 26, "auto": 0.14, "aug": 0.40, "amp": 0.12, "rung": 2},
    {"role": "Manufacturing supervisor and technician", "sector": "Manufacturing", "workforce": 44, "auto": 0.16, "aug": 0.30, "amp": 0.10, "rung": 2},
    {"role": "Government clerk and case officer", "sector": "Public services", "workforce": 30, "auto": 0.38, "aug": 0.42, "amp": 0.06, "rung": 1},
    {"role": "Marketing and content creator", "sector": "Business services", "workforce": 14, "auto": 0.28, "aug": 0.50, "amp": 0.14, "rung": 2},
    {"role": "HR and recruitment executive", "sector": "Business services", "workforce": 12, "auto": 0.30, "aug": 0.46, "amp": 0.10, "rung": 2},
    {"role": "Logistics and supply coordinator", "sector": "Logistics", "workforce": 22, "auto": 0.26, "aug": 0.38, "amp": 0.10, "rung": 2},
    {"role": "Legal associate and paralegal", "sector": "Business services", "workforce": 6, "auto": 0.32, "aug": 0.48, "amp": 0.10, "rung": 2},
    {"role": "Data and AI engineer", "sector": "IT/ITeS", "workforce": 10, "auto": 0.14, "aug": 0.50, "amp": 0.28, "rung": 4},
]
RUNG_HOURS = {1: 20, 2: 90, 3: 400, 4: 900}
