"""Learner Pathway Navigator on the L0-L5 AI Skill Ladder (illustrative placement rules; team design)."""
from datetime import date, timedelta

from . import data as D

PACE = {
    "standard": (1.0, "Standard", "Blended with work or study, a few hours a week"),
    "accelerated": (0.65, "Accelerated", "Near full-time intensity, fastest route to target"),
    "extended": (1.5, "Extended", "Part-time evenings and weekends, lighter weekly load"),
}

EDUCATION = {
    "none": ("Primary schooling or less", 0), "school": ("School (Class 6 to 12)", 1), "iti": ("ITI / Diploma / Polytechnic", 1),
    "ug_nontech": ("Graduate, non-technical", 2), "ug_tech": ("Graduate, engineering or science", 2), "pg": ("Postgraduate", 3), "phd": ("PhD / research", 4),
}
OCCUPATION = {
    "student": {"label": "Student", "target": 3}, "iti_grad": {"label": "ITI or polytechnic graduate", "target": 3},
    "it_pro": {"label": "IT professional", "target": 4}, "non_it_pro": {"label": "Non-IT professional (finance, ops, sales, HR)", "target": 2},
    "govt": {"label": "Government employee", "target": 2}, "teacher": {"label": "Teacher or faculty", "target": 2},
    "msme": {"label": "MSME owner", "target": 2}, "farmer": {"label": "Farmer or informal worker", "target": 1},
    "gig": {"label": "Gig or platform worker", "target": 1}, "returner": {"label": "Returning to work after a break", "target": 2},
    "leader": {"label": "Senior leader, civil servant or regulator", "target": 5}, "researcher": {"label": "Researcher or advanced engineer", "target": 4},
}
QUESTIONS = [
    {"id": "q1", "text": "I use AI tools such as ChatGPT, Gemini or Copilot for real tasks.", "options": ["Never", "Sometimes", "Every week"]},
    {"id": "q2", "text": "I know when not to trust an AI answer and how to check it.", "options": ["No", "Roughly", "Confidently"]},
    {"id": "q3", "text": "I have used AI inside my job's workflow and measured the result.", "options": ["No", "Once", "Regularly"]},
    {"id": "q4", "text": "I have built, deployed or evaluated an AI application.", "options": ["No", "In a course", "In production"]},
    {"id": "q5", "text": "I have led AI strategy, governance or risk decisions.", "options": ["No", "Contributed", "Led"]},
]
LANGUAGES = ["English", "Hindi", "Bengali", "Marathi", "Telugu", "Tamil", "Gujarati", "Kannada", "Malayalam", "Odia", "Punjabi", "Assamese", "Urdu"]

STEP = {
    0: {"weeks": 1, "how": "Free YUVA AI for ALL (4.5 hours) or SOAR awareness module; assisted at a CSC or hub", "proof": "Assisted, voice or vernacular assessment"},
    1: {"weeks": 3, "how": "SOAR micro-credential or iGOT Karmayogi path; task-based practice", "proof": "Task-based assessment"},
    2: {"weeks": 10, "how": "Role pathway on FSP + 8-12-week workplace project (AI Apprenticeship India, L2 track)", "proof": "Employer-validated project"},
    3: {"weeks": 26, "how": "FSP / NIELIT build track + ≈6-month apprenticeship at a hub or employer", "proof": "Apprenticeship + portfolio"},
    4: {"weeks": 48, "how": "9-12-month specialist track with academia or employer CoE; IndiaAI compute", "proof": "Production system or published work"},
    5: {"weeks": 12, "how": "Council-accredited leadership programme; governance case", "proof": "Peer or board review"},
}
FULL_LADDER_WEEKS = sum(s["weeks"] for s in STEP.values())


def _current(answers):
    a = [int(answers.get(q["id"], 0) or 0) for q in QUESTIONS]
    lvl = 0
    if a[0] >= 1:
        lvl = 1
    if a[0] >= 1 and a[1] >= 1 and a[2] >= 1:
        lvl = 2
    if a[3] >= 1 and a[1] >= 1:
        lvl = 3
    if a[3] == 2 and a[1] == 2:
        lvl = 4
    if a[4] >= 1 and a[1] >= 1 and a[2] >= 1:
        lvl = max(lvl, 5 if a[4] == 2 else lvl)
    return lvl, sum(a)


def navigate(payload, cost_per_entrant=None):
    age = int(payload.get("age", 30) or 30)
    edu = payload.get("education", "ug_nontech")
    occ = payload.get("occupation", "non_it_pro")
    state = (payload.get("state") or "MH").upper()
    lang = payload.get("language", "English")
    pace = payload.get("pace") if payload.get("pace") in PACE else "standard"
    answers = payload.get("answers", {}) or {}
    cur, score = _current(answers)
    target = OCCUPATION.get(occ, OCCUPATION["non_it_pro"])["target"]
    if edu in ("ug_tech", "pg") and occ == "student":
        target = 3
    if edu == "phd":
        target = max(target, 4)
    target = max(target, min(cur + 1, 5)) if cur < 5 else 5

    base_steps = []
    for lvl in range(cur + 1 if cur < target else cur, target + 1):
        L = D.LADDER[lvl]
        base_steps.append({"code": L["code"], "name": L["name"], "what": L["what"], "color": L["color"], "ink": L["ink"],
                            **STEP[lvl], "channels": L["channels"]})
    base_weeks = sum(s["weeks"] for s in base_steps)

    mult = PACE[pace][0]
    steps = []
    cursor = 0
    for s in base_steps:
        wk = max(1, round(s["weeks"] * mult))
        steps.append({**s, "weeks": wk, "start_week": cursor, "end_week": cursor + wk})
        cursor += wk
    weeks = sum(s["weeks"] for s in steps)
    eta = (date.today() + timedelta(weeks=weeks)).strftime("%b %Y") if weeks else None
    pace_options = {}
    for key, (m, label, note) in PACE.items():
        w = sum(max(1, round(s["weeks"] * m)) for s in base_steps)
        pace_options[key] = {"label": label, "note": note, "weeks": w,
                              "eta": (date.today() + timedelta(weeks=w)).strftime("%b %Y") if w else None}

    credit = None
    if age >= 40 and target >= 2:
        credit = ("Mid-career band", "₹15,000-25,000", 20000)
    elif occ in ("student", "iti_grad") or age < 25:
        credit = ("Youth band", "₹2,000-3,000", 2500)
    elif target >= 2:
        credit = ("Professional band", "₹5,000-10,000", 7500)

    cost = None
    if cost_per_entrant and weeks:
        programme_cost = round(cost_per_entrant * weeks / FULL_LADDER_WEEKS)
        credit_value = credit[2] if credit else 0
        cost = {"programme": programme_cost, "credit": credit_value, "net": max(0, programme_cost - credit_value)}

    topups = []
    if occ == "returner":
        topups.append("Priority top-up and a women-led or returner cohort with flexible timing")
    if occ in ("farmer", "gig"):
        topups.append("Assisted learning at a CSC or regional hub; eShram-linked outreach")
    if lang != "English":
        topups.append(f"Voice and vernacular delivery in {lang} via BHASHINI")
    if occ == "govt":
        topups.append("iGOT Karmayogi path; counts toward capacity-building hours")
    if occ == "teacher":
        topups.append("Eligible for the National AI Trainer Corps after L2")
    if occ == "msme":
        topups.append("Bring a real business problem to the hub's MSME challenge fund")

    st = next((s for s in D.STATES if s["code"] == state), None)

    risk = None
    if cur == 0 and (age >= 45 or occ in ("farmer", "gig") or lang != "English"):
        drivers = []
        if age >= 45:
            drivers.append("age band with lower historical digital-learning completion")
        if occ in ("farmer", "gig"):
            drivers.append("informal-work cohort, harder to reach with standard delivery")
        if lang != "English":
            drivers.append(f"{lang}-first learner; needs vernacular content from day one")
        risk = {"level": "Elevated first-mile drop-off risk", "drivers": drivers,
                "mitigation": "Route through an assisted CSC or hub with vernacular support rather than self-serve online"}
    elif st and isinstance(st.get("rate"), (int, float)) and st["rate"] < 50 and target >= 2:
        risk = {"level": f"{st['name']} certifies below the national pace ({st['rate']}%)",
                "drivers": ["State-level FSP certification rate is on the lower half"],
                "mitigation": "Build in the buffer months shown above rather than the standard timeline"}

    return {
        "profile": {"age": age, "education": EDUCATION.get(edu, EDUCATION["ug_nontech"])[0], "occupation": OCCUPATION.get(occ, OCCUPATION["non_it_pro"])["label"],
                    "state": st["name"] if st else state, "language": lang},
        "score": score, "current": {k: D.LADDER[cur][k] for k in ("code", "name", "color", "ink")},
        "target": {k: D.LADDER[target][k] for k in ("code", "name", "color", "ink")},
        "steps": steps, "weeks": weeks, "eta": eta, "pace": pace, "pace_options": pace_options,
        "credit": credit, "cost": cost, "risk": risk, "topups": topups,
        "passport": [f"{s['code']}: {s['proof']}" for s in steps] + ["Outcome recorded at 6 and 12 months", "Reassess every 24 months at L2+"],
        "state_ctx": {"name": st["name"], "rate": st["rate"], "pilot": st["pilot"]} if st else None,
        "note": "Illustrative placement rules (team design); a certified assessor makes the real placement.",
    }
