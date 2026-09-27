"""Ask the Tower: Claude-powered analyst with live tools over the tower's model."""
import json
import os
import threading
import urllib.error
import urllib.request

from . import data as D
from . import engine as E
from . import insights as I
from . import knowledge as K
from . import pathway as P

API_URL = "https://api.anthropic.com/v1/messages"
MODELS = [
    ("claude-sonnet-5", "Claude Sonnet 5"),
    ("claude-opus-5-5", "Claude Opus 5.5"),
    ("claude-haiku-4-5-20251001", "Claude Haiku 4.5"),
    ("claude-fable-5-1", "Claude Fable 5.1"),
]
DEFAULT_MODEL = os.environ.get("TOWER_MODEL", "claude-sonnet-5")

_lock = threading.Lock()
_keys = {}  # client id -> {"key":..., "model":...}


def _persist_path(base_dir):
    return os.path.join(base_dir, "instance", "copilot.json")


def load_persisted(base_dir):
    try:
        with open(_persist_path(base_dir), "r", encoding="utf-8") as fh:
            d = json.load(fh)
        if d.get("key"):
            with _lock:
                _keys["__persisted__"] = {"key": d["key"], "model": d.get("model", DEFAULT_MODEL)}
    except (OSError, ValueError):
        pass


def set_key(cid, key, model, remember, base_dir):
    with _lock:
        _keys[cid] = {"key": key, "model": model}
    path = _persist_path(base_dir)
    if remember:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as fh:
            json.dump({"key": key, "model": model}, fh)
        try:
            os.chmod(path, 0o600)
        except OSError:
            pass
        with _lock:
            _keys["__persisted__"] = {"key": key, "model": model}


def clear_key(cid, base_dir):
    with _lock:
        _keys.pop(cid, None)
        _keys.pop("__persisted__", None)
    try:
        os.remove(_persist_path(base_dir))
    except OSError:
        pass


def get_cfg(cid):
    with _lock:
        c = _keys.get(cid) or _keys.get("__persisted__")
    if c:
        return dict(c)
    env = os.environ.get("ANTHROPIC_API_KEY")
    if env:
        return {"key": env, "model": DEFAULT_MODEL, "env": True}
    return None


def status(cid):
    c = get_cfg(cid)
    if not c:
        return {"connected": False, "model": DEFAULT_MODEL, "models": MODELS}
    k = c["key"]
    return {"connected": True, "model": c["model"], "models": MODELS, "source": "environment" if c.get("env") else "saved",
            "masked": k[:7] + "…" + k[-4:] if len(k) > 12 else "…"}


class ApiError(Exception):
    def __init__(self, msg, code=None):
        super().__init__(msg)
        self.code = code


def _call(key, body, timeout=90):
    req = urllib.request.Request(API_URL, data=json.dumps(body).encode("utf-8"), method="POST",
                                 headers={"content-type": "application/json", "x-api-key": key,
                                          "anthropic-version": "2023-06-01"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        try:
            detail = json.loads(e.read()).get("error", {}).get("message", "")
        except Exception:
            detail = ""
        msgs = {401: "The API key was rejected. Check it and save again.",
                403: "This key is not allowed to use that model.",
                404: "The selected model is not available for this key. Choose another model.",
                429: "Rate limit reached. Wait a moment and ask again.",
                529: "The API is overloaded. Try again shortly."}
        raise ApiError(msgs.get(e.code, f"API error {e.code}") + (f" ({detail})" if detail else ""), e.code)
    except urllib.error.URLError as e:
        raise ApiError(f"Could not reach the Anthropic API: {e.reason}")
    except TimeoutError:
        raise ApiError("The API took too long to respond. Try again.")


def test_key(key, model):
    _call(key, {"model": model, "max_tokens": 8, "messages": [{"role": "user", "content": "Reply OK"}]}, timeout=30)


# --------------------------------------------------------------------------------------
# Tools
# --------------------------------------------------------------------------------------
PARAM_SCHEMA = {"type": "object", "description": "Pilot parameters; omitted keys use the active scenario. Rates are fractions 0-1.",
                "properties": {"entrants": {"type": "number"}, "completion": {"type": "number"}, "competency": {"type": "number"},
                               "uptake": {"type": "number", "description": "share of competent learners who transition to apprenticeship/project/deployment"},
                               "validation": {"type": "number", "description": "share of transitioned learners whose workplace competency is employer-verified"},
                               "move": {"type": "number"}, "employer_sat": {"type": "number"}, "women_entry": {"type": "number"},
                               "women_rel": {"type": "number"}, "tier_entry": {"type": "number"}, "tier_rel": {"type": "number"},
                               "cost_mult": {"type": "number"}, "uplift": {"type": "number"}, "years": {"type": "number"}}}
TOOLS = [
    {"name": "simulate_pilot", "description": "Run the pilot conversion funnel: VACR, transition, completion, competency, equity shares, budget, cost per verified convert, break-even and the six gates. Use preset or params (merged over the active scenario).",
     "input_schema": {"type": "object", "properties": {"preset": {"type": "string", "enum": list(E.PRESETS.keys())}, "params": PARAM_SCHEMA}}},
    {"name": "monte_carlo", "description": "Risk view: probability VACR ≥40% and all gates pass, P10/P50/P90 VACR and cost per convert, top uncertainty drivers.",
     "input_schema": {"type": "object", "properties": {"params": PARAM_SCHEMA, "runs": {"type": "integer"}}}},
    {"name": "sensitivity", "description": "Change in VACR (pp) and cost per convert when each stage rate moves ±5 pp, and unit costs ±10%.",
     "input_schema": {"type": "object", "properties": {"params": PARAM_SCHEMA}}},
    {"name": "state_data", "description": "FutureSkills PRIME state data (enrolled, certified, rate), ranks, gap to national 58.3%, pilot role and suggested intervention emphasis. Two-letter code e.g. BR, TN, UP, OD.",
     "input_schema": {"type": "object", "properties": {"code": {"type": "string"}}, "required": ["code"]}},
    {"name": "envelope_economics", "description": "₹6,500 Cr five-year envelope: lines, financing, cost per role-ready learner and advanced practitioner, central share vs MSDE, CSR share.",
     "input_schema": {"type": "object", "properties": {}}},
    {"name": "job_exposure", "description": "EY 3A lens (S23) with team role-level estimates: reskilling need by ladder level and sector at an adoption share (0.15-1).",
     "input_schema": {"type": "object", "properties": {"adoption": {"type": "number"}}}},
    {"name": "place_learner", "description": "Place a person on the L0-L5 ladder and build a pathway with credit band and Passport evidence.",
     "input_schema": {"type": "object", "properties": {"age": {"type": "integer"}, "education": {"type": "string", "enum": list(P.EDUCATION.keys())},
                                                      "occupation": {"type": "string", "enum": list(P.OCCUPATION.keys())}, "state": {"type": "string"},
                                                      "language": {"type": "string"}, "answers": {"type": "object", "description": "q1..q5 each 0,1,2"}},
                      "required": ["age", "education", "occupation"]}},
]


def _params(inp, active):
    base = dict(active)
    if inp.get("preset") in E.PRESETS:
        base = dict(E.preset(inp["preset"]))
    base.update(inp.get("params") or {})
    return base


def run_tool(name, inp, active):
    if name == "simulate_pilot":
        r = E.simulate(_params(inp, active))
        return {k: r[k] for k in ("params", "funnel", "kpi", "verified", "moved", "budget", "econ", "consistency", "gates", "gates_passed")}
    if name == "monte_carlo":
        return E.monte_carlo(_params(inp, active), runs=int(inp.get("runs") or 1000))
    if name == "sensitivity":
        return E.sensitivity(_params(inp, active))
    if name == "state_data":
        return E.state_profile(inp.get("code", "")) or {"error": "Unknown code. Use e.g. TN, AP, KA, OD, UP, BR, AS."}
    if name == "envelope_economics":
        return E.envelope()
    if name == "job_exposure":
        x = I.exposure(inp.get("adoption", 0.6))
        return {"summary": x["summary"], "by_rung": x["by_rung"], "by_sector": x["by_sector"], "note": "Role-level shares are team estimates calibrated to EY averages"}
    if name == "place_learner":
        return P.navigate(inp)
    return {"error": f"Unknown tool {name}"}


SYSTEM = """You are "Ask the Tower", the senior analyst inside the AI Skill Ladder Control Tower built by Team Vertex (EY Young Leaders 2026 final round) for the Government of India.

Rules:
- Answer anything about the case, India's AI-skilling landscape, the L0-L5 ladder, the seven interventions (I1-I7), VACR and the six gates, the ₹290 Cr pilot and ₹6,500 Cr envelope, states, benchmarks, risks, SDGs, the deck and panel questions.
- Ground every number in the KNOWLEDGE PACK or a tool result, and tag it as Observed, Derived, Benchmark, Assumption or Proposed target. Cite source IDs (e.g. S01) for observed figures.
- Never cite anything in EXCLUDED FIGURES. Never invent statistics, ROI, salaries or placement rates. If a number is not available, say so and say how Phase 0 would measure it.
- For any what-if, probability, state or budget question, call the tools.
- Consultant style: answer first in one or two sentences, then evidence, then a recommendation. Use lakh/crore and ₹. Short paragraphs; a compact table only for comparisons.
- If asked to rehearse, play a tough EY panelist, then give a model answer.
- Keep answers under about 350 words unless asked for depth."""


def ask(cid, question, history, scenario_name, sim):
    cfg = get_cfg(cid)
    if not cfg:
        raise ApiError("No API key saved. Add your Anthropic API key in the panel on the right.", 401)
    system = [{"type": "text", "text": SYSTEM}, {"type": "text", "text": "KNOWLEDGE PACK\n" + K.build(sim, scenario_name), "cache_control": {"type": "ephemeral"}}]
    msgs = []
    for h in (history or [])[-12:]:
        if h.get("role") in ("user", "assistant") and isinstance(h.get("content"), str) and h["content"].strip():
            msgs.append({"role": h["role"], "content": h["content"][:6000]})
    while msgs and msgs[0]["role"] != "user":
        msgs.pop(0)
    merged = []
    for m in msgs:
        if merged and merged[-1]["role"] == m["role"]:
            merged[-1]["content"] += "\n\n" + m["content"]
        else:
            merged.append(m)
    if merged and merged[-1]["role"] == "user":
        merged[-1]["content"] += "\n\n" + question
    else:
        merged.append({"role": "user", "content": question})
    msgs = merged
    active = sim["params"]
    trace = []
    for _ in range(8):
        out = _call(cfg["key"], {"model": cfg["model"], "max_tokens": 2000, "system": system, "tools": TOOLS, "messages": msgs})
        content = out.get("content", [])
        uses = [b for b in content if b.get("type") == "tool_use"]
        if out.get("stop_reason") != "tool_use" or not uses:
            text = "".join(b.get("text", "") for b in content if b.get("type") == "text").strip()
            return {"answer": text or "No answer returned. Try rephrasing.", "source": "claude", "model": cfg["model"], "tools": trace}
        msgs.append({"role": "assistant", "content": content})
        results = []
        for u in uses:
            try:
                res = run_tool(u["name"], u.get("input") or {}, active)
                is_err = isinstance(res, dict) and "error" in res
            except Exception as ex:
                res, is_err = {"error": str(ex)}, True
            trace.append({"name": u["name"], "input": u.get("input") or {}})
            results.append({"type": "tool_result", "tool_use_id": u["id"], "content": json.dumps(res, default=str)[:60000], "is_error": is_err})
        msgs.append({"role": "user", "content": results})
    return {"answer": "The analysis needed more steps than allowed. Ask a narrower question.", "source": "claude", "model": cfg["model"], "tools": trace}
