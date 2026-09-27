"""
AI Skill Ladder 3.0 Control Tower
EY Young Leaders 2026, Final Round (Team Vertex)

Run:  pip install -r requirements.txt  &&  python app.py   ->  http://127.0.0.1:5000
"""
import csv
import io
import json
import os
import secrets
import threading
import time
import uuid
from datetime import datetime

from flask import Flask, Response, abort, jsonify, redirect, render_template, request, session, url_for

from core import data as D
from core import engine as E
from core import frameworks as F
from core import insights as I
from core import pathway as P
from core import copilot as C

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STORE = os.path.join(BASE_DIR, "instance", "scenarios.json")
_lock = threading.Lock()

app = Flask(__name__)
# No hardcoded secret fallback: use TOWER_SECRET in any deployment where sessions must survive a
# restart, otherwise a fresh random key per process (sessions are non-sensitive: scenario choice
# and a copilot client id, so a restart-time reset is an acceptable trade for not shipping a secret).
app.config["SECRET_KEY"] = os.environ.get("TOWER_SECRET") or secrets.token_hex(32)
app.config["JSON_SORT_KEYS"] = False
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["SESSION_COOKIE_HTTPONLY"] = True

NAV_GROUPS = [
    ("Overview", [("command", "Command centre", "/")]),
    ("Diagnose", [("framing", "Problem framing", "/framing"), ("exposure", "Job exposure lab", "/exposure"), ("matrix", "Diagnosis matrix", "/matrix")]),
    ("Design", [("ladder", "Skill ladder", "/ladder"), ("interventions", "Seven interventions", "/interventions"),
                ("operating", "Operating model", "/operating"), ("value", "Long-term value", "/value")]),
    ("Decide", [("strategy", "Strategy lab", "/strategy"), ("simulator", "Pilot simulator", "/simulator"), ("stress", "Stress test", "/stress"), ("states", "State view", "/states")]),
    ("Deliver", [("roadmap", "Roadmap and risks", "/roadmap"), ("kpis", "KPIs and gates", "/kpis")]),
    ("Engage", [("navigator", "Pathway navigator", "/navigator"), ("ask", "Ask the Tower", "/ask")]),
    ("Evidence", [("sources", "Sources and data", "/sources"), ("brief", "Executive brief", "/brief")]),
]
NAV = [i for _, items in NAV_GROUPS for i in items]


def _build_search_index():
    idx = [{"label": label, "sub": grp, "href": href, "type": "page"} for grp, items in NAV_GROUPS for _, label, href in items]
    idx += [{"label": f"{i['id']} {i['title']}", "sub": "Intervention", "href": f"/interventions#{i['id']}", "type": "intervention"} for i in D.INTERVENTIONS]
    idx += [{"label": f"{l['code']} {l['name']}", "sub": "Ladder level", "href": f"/ladder#{l['code']}", "type": "ladder"} for l in D.LADDER]
    idx += [{"label": f"{g['id']} {g['name']}", "sub": "Evidence gate", "href": "/kpis", "type": "gate"} for g in D.GATES]
    idx += [{"label": s["name"], "sub": f"State, {s['rate']}% certified of {s['enrolled']:,}", "href": "/states", "type": "state"} for s in D.STATES if s.get("enrolled", 0) > 0]
    return idx


SEARCH_INDEX = _build_search_index()


# --------------------------------------------------------------------------------------
# CSRF: a per-session token, echoed in a meta tag and required as a header on every
# state-changing /api/ request. Defence in depth alongside the SameSite session cookie.
# --------------------------------------------------------------------------------------
def _csrf_token():
    if "csrf" not in session:
        session["csrf"] = uuid.uuid4().hex
    return session["csrf"]


@app.before_request
def _csrf_protect():
    if request.method in ("POST", "PUT", "PATCH", "DELETE") and request.path.startswith("/api/"):
        sent = request.headers.get("X-CSRF-Token", "")
        if not sent or sent != session.get("csrf"):
            return jsonify({"error": "Your session has expired. Reload the page and try again."}), 403


@app.before_request
def _apply_scenario_from_query():
    if request.method == "GET" and not request.path.startswith(("/api/", "/static/", "/export/")):
        sid = request.args.get("scenario")
        if sid and get_scenario(sid):
            session["scenario"] = sid
            session.pop("draft", None)


# --------------------------------------------------------------------------------------
# Simple in-memory rate limiting for /api/ask (per browser session)
# --------------------------------------------------------------------------------------
_ask_hits = {}
_ASK_LIMIT, _ASK_WINDOW = 20, 60


def _rate_limited(key, limit=_ASK_LIMIT, window=_ASK_WINDOW):
    now = time.time()
    with _lock:
        hits = [t for t in _ask_hits.get(key, []) if now - t < window]
        hits.append(now)
        _ask_hits[key] = hits
        return len(hits) > limit


# --------------------------------------------------------------------------------------
# Scenarios
# --------------------------------------------------------------------------------------
def _load_store():
    try:
        with open(STORE, encoding="utf-8") as fh:
            return json.load(fh)
    except (OSError, ValueError):
        return {}


def _save_store(store):
    os.makedirs(os.path.dirname(STORE), exist_ok=True)
    tmp = STORE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(store, fh, indent=2)
    os.replace(tmp, STORE)


def all_scenarios():
    out = [{"id": k, "name": v["name"], "note": v["note"], "params": E.preset(k), "preset": True} for k, v in E.PRESETS.items()]
    for sid, s in _load_store().items():
        out.append({**s, "id": sid, "preset": False, "params": E.clean(s.get("params"))})
    return out


def get_scenario(sid):
    return next((s for s in all_scenarios() if s["id"] == sid), None)


def active():
    sc = get_scenario(session.get("scenario", "operating_plan")) or get_scenario("operating_plan")
    if session.get("draft"):
        sc = {**sc, "params": E.clean(session["draft"]), "draft": True}
    return sc


def active_sim():
    sc = active()
    return sc, E.simulate(sc["params"])


def _logo():
    folder = os.path.join(BASE_DIR, "static", "img")
    for n in ("logo_dark.png", "logo.svg", "logo.png"):
        if os.path.exists(os.path.join(folder, n)):
            return url_for("static", filename="img/" + n)
    return None


@app.context_processor
def inject():
    cid = _cid()
    scs = all_scenarios()
    for s in scs:
        s["owned"] = s["preset"] or not s.get("owner") or s["owner"] == cid
    return {"NAV_GROUPS": NAV_GROUPS, "NAV": NAV, "active_scenario": active(), "scenarios": scs,
            "now": datetime.now().strftime("%d %b %Y, %H:%M"), "CLASSES": D.CLASSES, "SRC": D.SRC,
            "LOGO": _logo(), "INTS": D.INTERVENTIONS, "CSRF": _csrf_token(), "SEARCH_INDEX": SEARCH_INDEX}


def page(name, **kw):
    title = next(label for key, label, _ in NAV if key == name)
    return render_template(f"{name}.html", page=name, title=title, **kw)


# --------------------------------------------------------------------------------------
# Pages
# --------------------------------------------------------------------------------------
@app.route("/")
def command():
    sc, sim = active_sim()
    top_states = sorted([s for s in D.STATES if s["enrolled"] >= 20000], key=lambda s: -s["rate"])
    return render_template("command.html", page="command", title="Command centre", sim=sim, H=D.H, fsp=D.FSP_FUNNEL, soar=D.SOAR,
                           signals=E.signals(sim), env=E.envelope(), states=top_states, nat=D.FSP_STATE_TOTAL, demand=D.DEMAND,
                           workforce=D.WORKFORCE, chg=I.change_index(), ltv=I.ltv(sim), fund=D.FSP_FUNDING, iti=D.ITI_GROWTH,
                           decision=E.decision(sim), bottleneck=E.bottleneck(sim))


@app.route("/framing")
def framing():
    return page("framing", tree=F.ISSUE_TREE, pestle=F.PESTLE, smap=F.STAKEHOLDER_MAP)


@app.route("/exposure")
def exposure():
    return page("exposure", ex=I.exposure(), ladder=D.LADDER)


@app.route("/matrix")
def matrix():
    return page("matrix", priorities=D.PRIORITIES, fms=D.FAILURE_MODES, inc=D.INCENTIVE_EVIDENCE)


@app.route("/ladder")
def ladder():
    sc, sim = active_sim()
    return page("ladder", ladder=D.LADDER, dims=D.DIMENSIONS, sim=sim, refresh=D.REFRESH_RULE, fsp=D.FSP_FUNNEL, soar=D.SOAR)


@app.route("/interventions")
def interventions():
    sc, sim = active_sim()
    return page("interventions", ints=D.INTERVENTIONS, fms=D.FAILURE_MODES, sim=sim, bench=D.BENCHMARKS, inc=D.INCENTIVE_EVIDENCE)


@app.route("/recommendations")
def _old_recs():
    return redirect("/interventions")


@app.route("/operating")
def operating():
    return page("operating", actors=D.ACTORS, hc=F.HUMANS_AT_CENTER, c3=F.CONFIDENCE_3C, idx=I.change_index(), smap=F.STAKEHOLDER_MAP)


@app.route("/value")
def value():
    sc, sim = active_sim()
    return page("value", ltv=I.ltv(sim), sim=sim)


@app.route("/strategy")
def strategy():
    sc, sim = active_sim()
    return page("strategy", sim=sim, sens=E.sensitivity(sim["params"]), env=E.envelope(), states=D.STATES, nat=D.FSP_STATE_TOTAL, cfg=pilot_cfg())


def pilot_cfg():
    d = {k: v for k, v in E.DEFAULT.items() if k != "lines"}
    band = D.PILOT_CAP_CR * 1e7 / (D.ECON["pilot_entrants"] * D.ECON["vacr_target"]) * 1.25
    return {"defaults": d, "lines": D.PILOT_LINES, "gates": D.GATES, "cap": D.PILOT_CAP_CR, "plan_entrants": D.ECON["pilot_entrants"],
            "vacr_target": D.ECON["vacr_target"], "band": band, "presets": {k: E.preset(k) for k in E.PRESETS}}


@app.route("/simulator")
def simulator():
    sc, sim = active_sim()
    return page("simulator", sim=sim, lines=D.PILOT_LINES, presets=E.PRESETS, demos=E.DEMOS, cfg=pilot_cfg())


@app.route("/states")
def states():
    return page("states", states=D.STATES, nat=D.FSP_STATE_TOTAL)


@app.route("/roadmap")
def roadmap():
    sc, sim = active_sim()
    return page("roadmap", phases=D.PHASES, workstreams=D.WORKSTREAMS, gates=D.GATES, risks=D.RISKS, raci=D.RACI,
                raci_cols=D.RACI_COLS, sim=sim, env=E.envelope())


@app.route("/kpis")
def kpis():
    sc, sim = active_sim()
    return page("kpis", rows=E.kpi_scorecard(sim), sim=sim, kirk=F.KIRKPATRICK, sdgs=D.SDGS, decision=E.decision(sim))


@app.route("/stress")
def stress():
    sc, sim = active_sim()
    return page("stress", sim=sim, shocks=E.SHOCKS, decision=E.decision(sim))


@app.route("/navigator")
def navigator():
    return page("navigator", education=P.EDUCATION, occupation=P.OCCUPATION, questions=P.QUESTIONS, languages=P.LANGUAGES,
                states=sorted(D.STATES, key=lambda s: s["name"]))


@app.route("/ask")
def ask():
    return page("ask", cstat=C.status(_cid()))


@app.route("/sources")
def sources():
    return page("sources", sources=D.SOURCES, dv=D.DATA_VERIFIED, excluded=D.EXCLUDED, qa=D.QA, bench=D.BENCHMARKS)


@app.route("/assumptions")
def _old_assumptions():
    return redirect("/sources")


@app.route("/brief")
def brief():
    sc, sim = active_sim()
    return page("brief", sim=sim, env=E.envelope(), fms=D.FAILURE_MODES, ints=D.INTERVENTIONS, rows=E.kpi_scorecard(sim), fsp=D.FSP_FUNNEL, H=D.H)


# --------------------------------------------------------------------------------------
# API
# --------------------------------------------------------------------------------------
def _body():
    return request.get_json(silent=True) or {}


@app.post("/api/simulate")
def api_simulate():
    return jsonify(E.simulate(_body().get("params")))


@app.post("/api/montecarlo")
def api_mc():
    b = _body()
    return jsonify(E.monte_carlo(b.get("params"), runs=int(b.get("runs", 1000) or 1000)))


@app.post("/api/sensitivity")
def api_sens():
    return jsonify(E.sensitivity(_body().get("params")))


@app.post("/api/stress")
def api_stress():
    b = _body()
    sc, sim = active_sim()
    params = E.clean(b.get("params")) if b.get("params") else sim["params"]
    if b.get("all"):
        return jsonify({"shocks": [E.stress_test(params, s["id"]) for s in E.SHOCKS]})
    shock = str(b.get("shock", ""))
    if shock not in E.SHOCK_INDEX:
        return jsonify({"error": "Unknown shock id."}), 400
    return jsonify(E.stress_test(params, shock))


@app.post("/api/compare")
def api_compare():
    out = []
    for sid in (_body().get("ids") or [])[:5]:
        sc = get_scenario(sid)
        if sc:
            r = E.simulate(sc["params"])
            out.append({"id": sid, "name": sc["name"], "kpi": r["kpi"], "funnel": [f["n"] for f in r["funnel"]], "gates_passed": r["gates_passed"]})
    return jsonify({"stages": [f["stage"] for f in E.simulate()["funnel"]], "scenarios": out})


@app.get("/api/scenarios")
def api_scenarios():
    return jsonify(all_scenarios())


@app.post("/api/scenarios")
def api_save():
    b = _body()
    name = (b.get("name") or "").strip()[:60]
    if not name:
        return jsonify({"error": "Give the scenario a name before saving."}), 400
    sid = "sc-" + uuid.uuid4().hex[:8]
    rec = {"name": name, "note": (b.get("note") or "Saved from simulator")[:160], "params": E.clean(b.get("params")),
           "created": datetime.now().isoformat(timespec="seconds"), "owner": _cid()}
    with _lock:
        st = _load_store()
        st[sid] = rec
        _save_store(st)
    session["scenario"] = sid
    session.pop("draft", None)
    return jsonify({"id": sid, **rec})


@app.delete("/api/scenarios/<sid>")
def api_delete(sid):
    if sid in E.PRESETS:
        return jsonify({"error": "Preset scenarios cannot be deleted."}), 400
    with _lock:
        st = _load_store()
        if sid not in st:
            return jsonify({"error": "Scenario not found."}), 404
        owner = st[sid].get("owner")
        if owner and owner != _cid():
            return jsonify({"error": "You can only delete scenarios you created on this browser."}), 403
        st.pop(sid)
        _save_store(st)
    if session.get("scenario") == sid:
        session["scenario"] = "operating_plan"
    return jsonify({"deleted": sid})


@app.post("/api/active")
def api_active():
    b = _body()
    if b.get("id"):
        if not get_scenario(b["id"]):
            return jsonify({"error": "Scenario not found."}), 404
        session["scenario"] = b["id"]
        session.pop("draft", None)
    if b.get("draft"):
        session["draft"] = E.clean(b["draft"])
    return jsonify({"active": active()})


@app.get("/api/state/<code>")
def api_state(code):
    p = E.state_profile(code)
    if not p:
        abort(404)
    return jsonify(p)


@app.post("/api/pathway")
def api_pathway():
    return jsonify(P.navigate(_body()))


@app.post("/api/exposure")
def api_exposure():
    b = _body()
    return jsonify(I.exposure(b.get("adoption", 0.6), b.get("hours_week", 45)))


@app.post("/api/change")
def api_change():
    b = _body()
    return jsonify(I.change_index(b.get("scores"), b.get("conf")))


# ---------------- copilot ----------------
def _cid():
    if "cid" not in session:
        session["cid"] = uuid.uuid4().hex
    return session["cid"]


C.load_persisted(BASE_DIR)


@app.get("/api/copilot/status")
def api_cstatus():
    return jsonify(C.status(_cid()))


@app.post("/api/copilot/key")
def api_ckey():
    b = _body()
    key = str(b.get("key", "")).strip()
    model = str(b.get("model") or C.DEFAULT_MODEL)
    if model not in [m[0] for m in C.MODELS]:
        return jsonify({"error": "Choose a model from the list."}), 400
    cid = _cid()
    if not key:
        cfg = C.get_cfg(cid)
        if not cfg:
            return jsonify({"error": "Paste your Anthropic API key first."}), 400
        key = cfg["key"]
    if not key.startswith("sk-"):
        return jsonify({"error": "That does not look like an Anthropic API key (it should start with sk-)."}), 400
    try:
        C.test_key(key, model)
    except C.ApiError as e:
        return jsonify({"error": str(e)}), 400
    C.set_key(cid, key, model, bool(b.get("remember")), BASE_DIR)
    return jsonify(C.status(cid))


@app.delete("/api/copilot/key")
def api_cclear():
    C.clear_key(_cid(), BASE_DIR)
    return jsonify(C.status(_cid()))


@app.post("/api/ask")
def api_ask():
    b = _body()
    q = str(b.get("q", "")).strip()[:4000]
    if not q:
        return jsonify({"error": "Type a question first."}), 400
    cid = _cid()
    if _rate_limited(cid):
        return jsonify({"error": "Too many questions in a short time. Wait a moment and try again."}), 429
    sc, sim = active_sim()
    if C.get_cfg(cid):
        try:
            return jsonify(C.ask(cid, q, b.get("history") or [], sc["name"], sim))
        except C.ApiError as e:
            return jsonify({"error": str(e), "fallback": I.ask(q, sim)}), 502
    return jsonify(I.ask(q, sim))


# ---------------- exports ----------------
@app.get("/export/scenario.csv")
def export_csv():
    sc, sim = active_sim()
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(["Scenario", sc["name"]])
    w.writerow(["Generated", datetime.now().isoformat(timespec="seconds")])
    w.writerow([])
    w.writerow(["Parameter", "Value"])
    for k, v in sim["params"].items():
        if k != "lines":
            w.writerow([k, v])
    w.writerow([])
    w.writerow(["Funnel stage", "Learners", "Stage rate"])
    for f in sim["funnel"]:
        w.writerow([f["stage"], f["n"], f["rate"]])
    w.writerow([])
    w.writerow(["KPI", "Value"])
    for k, v in sim["kpi"].items():
        w.writerow([k, v])
    w.writerow([])
    w.writerow(["Budget line", "Rs Cr", "Basis"])
    for l in sim["budget"]["lines"]:
        w.writerow([l["line"], l["amount"], l["basis"]])
    w.writerow(["TOTAL", sim["budget"]["total_cr"], ""])
    w.writerow([])
    w.writerow(["Gate", "Pass", "Detail"])
    for g in sim["gates"]:
        w.writerow([g["id"] + " " + g["name"], g["pass"], g["detail"]])
    w.writerow([])
    w.writerow(["Note", "All budgets and rates are internal case assumptions or proposed targets, not Government of India allocations."])
    return Response(buf.getvalue(), mimetype="text/csv", headers={"Content-Disposition": "attachment; filename=ai_skill_ladder_scenario.csv"})


@app.get("/export/scenario.json")
def export_json():
    sc, sim = active_sim()
    return Response(json.dumps({"scenario": sc["name"], "generated": datetime.now().isoformat(timespec="seconds"), **sim}, indent=2, default=str),
                    mimetype="application/json", headers={"Content-Disposition": "attachment; filename=ai_skill_ladder_scenario.json"})


@app.get("/health")
def health():
    return jsonify({"status": "ok", "states": len(D.STATES), "interventions": len(D.INTERVENTIONS), "sources": len(D.SOURCES)})


@app.errorhandler(404)
def nf(_):
    if request.path.startswith("/api/"):
        return jsonify({"error": "Not found"}), 404
    return render_template("error.html", page=None, title="Not found", code=404,
                           message="This view does not exist. Use the navigation to return to the control tower."), 404


@app.errorhandler(500)
def server_error(e):
    app.logger.exception("Unhandled server error")
    if request.path.startswith("/api/"):
        return jsonify({"error": "Something went wrong processing that request."}), 500
    return render_template("error.html", page=None, title="Error", code=500,
                           message="Something went wrong. Use the navigation to return to the control tower."), 500


if __name__ == "__main__":
    app.run(debug=os.environ.get("FLASK_DEBUG") == "1", host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
