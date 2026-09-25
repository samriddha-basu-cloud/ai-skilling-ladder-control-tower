/* Client-side mirror of core/engine.simulate(). Same formulas; used for instant, animated updates.
   The server remains the source of truth for Monte Carlo, saving and exports. */
(function () {
  const LIM = {
    entrants: [1000, 1000000], completion: [0.05, 0.99], competency: [0.05, 0.99], uptake: [0.05, 0.99], validation: [0.05, 0.99],
    move: [0.05, 0.99], employer_sat: [0.1, 1], women_entry: [0.05, 0.95], women_rel: [0.5, 1.5], tier_entry: [0.05, 0.99],
    tier_rel: [0.5, 1.5], cost_mult: [0.5, 2], earnings: [5000, 200000], uplift: [0, 0.6], years: [1, 5]
  };
  const clamp = (v, k) => Math.min(Math.max(+v, LIM[k][0]), LIM[k][1]);
  const share = (e, r) => { const n = e * r; return n / (n + (1 - e)); };

  function budget(p, CFG) {
    let baseNc = 0, cont = 0;
    const rows = CFG.lines.map(L => {
      const o = (p.lines || {})[L.key] || {};
      let amt, qty = null, unit = null;
      if (L.lump !== null) amt = o.lump !== undefined ? +o.lump : L.lump;
      else { qty = o.qty !== undefined ? +o.qty : L.qty; unit = o.unit !== undefined ? +o.unit : L.unit; amt = qty * unit / 1e7; }
      if (L.key === "cont") cont = amt; else { amt *= p.cost_mult; baseNc += amt; }
      return { key: L.key, line: L.line, qty, unit, amount: amt, basis: L.basis, int: L.int };
    });
    const overrun = p.cost_mult ? baseNc - baseNc / p.cost_mult : 0;
    const used = Math.min(cont, Math.max(0, overrun));
    rows.forEach(r => { if (r.key === "cont") { r.amount = cont - used; r.absorbed = used; } });
    const total = rows.reduce((a, r) => a + r.amount, 0);
    rows.forEach(r => { r.amount = Math.round(r.amount * 100) / 100; r.share = total ? Math.round(r.amount / total * 1000) / 10 : 0; });
    return { rows, total: Math.round(total * 100) / 100, used };
  }

  function simulate(params, CFG) {
    const p = Object.assign({}, CFG.defaults, params || {});
    Object.keys(LIM).forEach(k => { if (p[k] !== undefined) p[k] = clamp(p[k], k); });
    p.entrants = Math.round(p.entrants);
    const n = p.entrants;
    const completed = n * p.completion, competent = completed * p.competency, transitioned = competent * p.uptake;
    const verified = transitioned * p.validation, moved = verified * p.move;
    const vacr = verified / n, transition = transitioned / n;
    const women = share(p.women_entry, p.women_rel), tier = share(p.tier_entry, p.tier_rel);
    const b = budget(p, CFG);
    const cpc = verified ? b.total * 1e7 / verified : null;
    const months = cpc ? cpc / p.earnings : null;
    const band = CFG.band;
    const ceiling = p.completion * p.competency;
    const gates = [
      { id: "G1", pass: !!p.g1_pass, detail: p.g1_pass ? "Passport issues and verifies across rails" : "Technical integration not yet verified" },
      { id: "G2", pass: p.completion >= 0.70 && n >= 0.9 * CFG.plan_entrants, detail: `Completion ${(p.completion * 100).toFixed(1)}% (≥70%); entrants ${n.toLocaleString("en-IN")}` },
      { id: "G3", pass: p.competency >= 0.60, detail: `Competency ${(p.competency * 100).toFixed(1)}% of completers (≥60%)` },
      { id: "G4", pass: vacr >= 0.40 && transition >= 0.40 && p.employer_sat >= 0.80, detail: `VACR ${(vacr * 100).toFixed(1)}%; transition ${(transition * 100).toFixed(1)}%; employer satisfaction ${Math.round(p.employer_sat * 100)}%` },
      { id: "G5", pass: !!cpc && cpc <= band && b.total <= CFG.cap + 0.01, detail: cpc ? `₹${Math.round(cpc).toLocaleString("en-IN")} per convert (≤₹${Math.round(band).toLocaleString("en-IN")}); spend ₹${b.total.toFixed(1)} Cr (≤₹${CFG.cap} Cr)` : "No verified converts" },
      { id: "G6", pass: women >= 0.45 && tier >= 0.70, detail: `Women ${(women * 100).toFixed(1)}%; Tier-2/3 ${(tier * 100).toFixed(1)}% of converts` },
    ];
    gates.forEach(g => Object.assign(g, CFG.gates.find(x => x.id === g.id)));
    const r1 = v => Math.round(v * 1000) / 10;
    return {
      params: p,
      funnel: [
        { stage: "Entered", n: n, rate: 1, step: null },
        { stage: "Completed", n: Math.round(completed), rate: p.completion, step: "completion" },
        { stage: "Competency validated", n: Math.round(competent), rate: p.competency, step: "competency" },
        { stage: "Transitioned to apprenticeship / project", n: Math.round(transitioned), rate: p.uptake, step: "uptake" },
        { stage: "Workplace competency verified (VACR)", n: Math.round(verified), rate: p.validation, step: "validation" },
        { stage: "Moved to job / promotion / redeployment", n: Math.round(moved), rate: p.move, step: "move" },
      ],
      kpi: { vacr: r1(vacr), completion: r1(p.completion), competency: r1(p.competency), transition: r1(transition),
             employer_sat: r1(p.employer_sat), women: r1(women), tier23: r1(tier), cost_per_convert: cpc ? Math.round(cpc) : null },
      verified: Math.round(verified), moved: Math.round(moved),
      women_converts: Math.round(verified * women), tier_converts: Math.round(verified * tier),
      budget: { lines: b.rows, total_cr: b.total, cap_cr: CFG.cap, within_cap: b.total <= CFG.cap + 0.01, contingency_used: b.used },
      econ: { cost_per_convert: cpc ? Math.round(cpc) : null, months_of_earnings: months ? Math.round(months * 100) / 100 : null, band: Math.round(band),
              test_benefit: Math.round(p.uplift * p.earnings * 12 * p.years) },
      consistency: { ceiling: r1(ceiling), required_downstream: ceiling ? r1(CFG.vacr_target / ceiling) : null },
      gates, gates_passed: gates.filter(g => g.pass).length,
    };
  }
  window.Pilot = { simulate };
})();
