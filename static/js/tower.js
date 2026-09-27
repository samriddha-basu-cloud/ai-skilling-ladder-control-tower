/* AI Skill Ladder Control Tower: shared client runtime */
(function () {
  const root = document.documentElement;
  const saved = (() => { try { return localStorage.getItem("tower-theme"); } catch (e) { return null; } })();
  if (saved) root.setAttribute("data-theme", saved);

  window.Tower = {
    palette: { beam: "#FFE600", blue: "#188CE5", teal: "#27ACAA", green: "#2DB757", orange: "#FF6D00",
               magenta: "#B14891", red: "#FF4136", lilac: "#9C82D4", grey: "#747480", silver: "#C4C4CD" },
    charts: {},
    css(name) { return getComputedStyle(root).getPropertyValue(name).trim(); },
    fmt(n, d = 1) { if (n === null || n === undefined || isNaN(n)) return "–"; return Number(n).toLocaleString("en-IN", { maximumFractionDigits: d, minimumFractionDigits: 0 }); },
    inr(n) { return "₹" + Number(n).toLocaleString("en-IN", { maximumFractionDigits: 0 }); },
    async api(url, body, method) {
      const opt = { method: method || (body ? "POST" : "GET"), headers: { "Content-Type": "application/json" } };
      if (body) opt.body = JSON.stringify(body);
      const r = await fetch(url, opt);
      const j = await r.json().catch(() => ({}));
      if (!r.ok) throw new Error(j.error || ("Request failed: " + r.status));
      return j;
    },
    toast(msg) {
      let t = document.querySelector(".toast");
      if (!t) { t = document.createElement("div"); t.className = "toast"; t.setAttribute("role", "status"); document.body.appendChild(t); }
      t.textContent = msg; t.classList.add("show");
      clearTimeout(t._h); t._h = setTimeout(() => t.classList.remove("show"), 2600);
    },
    applyChartTheme() {
      if (!window.Chart) return;
      const text = this.css("--text-2"), grid = this.css("--line-soft");
      Chart.defaults.color = text;
      Chart.defaults.borderColor = grid;
      Chart.defaults.font.family = getComputedStyle(document.body).fontFamily;
      Chart.defaults.font.size = 12;
      Chart.defaults.plugins.legend.labels.boxWidth = 10;
      Chart.defaults.plugins.legend.labels.boxHeight = 10;
      Chart.defaults.plugins.tooltip.backgroundColor = "#1A1A24";
      Chart.defaults.plugins.tooltip.borderColor = "#3A3A4A";
      Chart.defaults.plugins.tooltip.borderWidth = 1;
      Chart.defaults.plugins.tooltip.padding = 10;
      Chart.defaults.plugins.tooltip.titleColor = "#FFE600";
      Chart.defaults.maintainAspectRatio = false;
      Chart.defaults.animation.duration = window.matchMedia("(prefers-reduced-motion: reduce)").matches ? 0 : 700;
      Chart.defaults.animation.easing = "easeOutQuart";
      Chart.defaults.transitions.active = { animation: { duration: 250 } };
    },
    /* Create a chart, or morph an existing one in place so values animate from old to new. */
    chart(id, cfg) {
      const el = document.getElementById(id);
      if (!el || !window.Chart) return null;
      const ex = this.charts[id];
      const sameShape = ex && ex.canvas === el && ex.config.type === cfg.type &&
        ex.data.datasets.length === (cfg.data.datasets || []).length &&
        ex.data.datasets.every((d, i) => (d.type || null) === (cfg.data.datasets[i].type || null));
      if (sameShape) {
        ex.data.labels = cfg.data.labels;
        cfg.data.datasets.forEach((nd, i) => {
          const od = ex.data.datasets[i];
          Object.keys(nd).forEach(k => { if (k !== "data") od[k] = nd[k]; });
          if (Array.isArray(od.data) && od.data.length === nd.data.length) nd.data.forEach((v, j) => { od.data[j] = v; });
          else od.data = nd.data;
        });
        if (cfg.options) ex.options = cfg.options;
        ex.update();
        return ex;
      }
      if (ex) ex.destroy();
      this.charts[id] = new Chart(el, cfg);
      return this.charts[id];
    },
    /* Count a number from its previous value to a new one. fmt(v) returns the display string. */
    tween(el, to, fmt, dur) {
      if (!el) return;
      if (typeof el === "string") el = document.getElementById(el);
      if (!el) return;
      fmt = fmt || (v => Math.round(v).toLocaleString("en-IN"));
      const reduce = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
      const from = (typeof el._tv === "number" && isFinite(el._tv)) ? el._tv : to;
      el._tv = to;
      cancelAnimationFrame(el._raf);
      if (reduce || from === to || !isFinite(to)) { el.innerHTML = fmt(to); return; }
      const t0 = performance.now(), d = dur || 650;
      const step = now => {
        const k = Math.min(1, (now - t0) / d), e = 1 - Math.pow(1 - k, 3);
        el.innerHTML = fmt(from + (to - from) * e);
        if (k < 1) el._raf = requestAnimationFrame(step);
      };
      el._raf = requestAnimationFrame(step);
    },
    pulse(el) { if (!el) return; el.classList.remove("pulse"); void el.offsetWidth; el.classList.add("pulse"); },
    /* Paint a range input's filled portion up to the thumb (Chrome/Edge/Safari; Firefox uses ::-moz-range-progress natively). */
    paintRange(el) {
      if (!el) return;
      const min = parseFloat(el.min) || 0, max = parseFloat(el.max) || 100, val = parseFloat(el.value);
      const pct = max > min ? Math.min(100, Math.max(0, (val - min) / (max - min) * 100)) : 0;
      el.style.setProperty("--fill", pct + "%");
    },
    refreshCharts() {
      this.applyChartTheme();
      Object.values(this.charts).forEach(c => {
        if (c.options.scales) Object.values(c.options.scales).forEach(s => {
          if (s.grid) s.grid.color = this.css("--line-soft");
          if (s.ticks) s.ticks.color = this.css("--text-2");
          if (s.title) s.title.color = this.css("--text-3");
        });
        if (c.options.plugins && c.options.plugins.legend && c.options.plugins.legend.labels) c.options.plugins.legend.labels.color = this.css("--text-2");
        c.update("none");
      });
    },
    spark(id, data, color) {
      const el = document.getElementById(id);
      if (!el || !data || !data.length) return;
      const w = 200, h = 30, pad = 3;
      const min = Math.min(...data), max = Math.max(...data);
      const flat = max - min < 1e-9;
      const pts = data.map((v, i) => {
        const x = data.length === 1 ? w / 2 : (i / (data.length - 1)) * w;
        const y = flat ? h / 2 : h - pad - ((v - min) / (max - min)) * (h - pad * 2);
        return [x, y];
      });
      const line = pts.map(p => p[0].toFixed(1) + "," + p[1].toFixed(1)).join(" ");
      const area = "0," + h + " " + line + " " + w + "," + h;
      const c = color || "#FFE600";
      const last = pts[pts.length - 1];
      el.innerHTML = `<svg viewBox="0 0 ${w} ${h}" preserveAspectRatio="none" role="img" aria-label="Trend">
        <polygon points="${area}" fill="${c}" opacity="${flat ? 0 : 0.12}"></polygon>
        <polyline points="${line}" fill="none" stroke="${c}" stroke-width="2" vector-effect="non-scaling-stroke" stroke-linejoin="round" stroke-linecap="round" ${flat ? 'stroke-dasharray="4 4" opacity="0.6"' : ""}></polyline>
        <circle cx="${last[0]}" cy="${last[1]}" r="2.5" fill="${c}"></circle></svg>`;
      el.title = flat ? "No change across 2026 to 2031" : "2026 to 2031 trend";
    },
    sortable(table) {
      table.querySelectorAll("th.sortable").forEach((th, idx) => {
        if (!th.title) th.title = `Sort by ${th.textContent.trim()}`;
        th.addEventListener("click", () => {
          const col = [...th.parentNode.children].indexOf(th);
          const dir = th.dataset.dir === "asc" ? "desc" : "asc";
          table.querySelectorAll("th").forEach(h => delete h.dataset.dir);
          th.dataset.dir = dir;
          const rows = [...table.tBodies[0].rows];
          rows.sort((a, b) => {
            const av = a.cells[col].dataset.v ?? a.cells[col].textContent.trim();
            const bv = b.cells[col].dataset.v ?? b.cells[col].textContent.trim();
            const an = parseFloat(av), bn = parseFloat(bv);
            const cmp = (!isNaN(an) && !isNaN(bn)) ? an - bn : String(av).localeCompare(String(bv));
            return dir === "asc" ? cmp : -cmp;
          });
          rows.forEach(r => table.tBodies[0].appendChild(r));
        });
      });
    },
    drawer: {
      open(html) {
        const d = document.getElementById("drawer"), b = document.getElementById("drawerBack");
        d.querySelector(".drawer-body").innerHTML = html;
        d.classList.add("open"); b.classList.add("open");
        d.setAttribute("aria-hidden", "false");
        d.querySelector(".close").focus();
      },
      close() {
        document.getElementById("drawer").classList.remove("open");
        document.getElementById("drawerBack").classList.remove("open");
        document.getElementById("drawer").setAttribute("aria-hidden", "true");
      }
    }
  };

  document.addEventListener("DOMContentLoaded", () => {
    Tower.applyChartTheme();

    const tbtn = document.getElementById("themeToggle");
    if (tbtn) tbtn.addEventListener("click", () => {
      const next = root.getAttribute("data-theme") === "light" ? "dark" : "light";
      root.setAttribute("data-theme", next);
      try { localStorage.setItem("tower-theme", next); } catch (e) {}
      Tower.refreshCharts();
    });

    const mbtn = document.getElementById("menuBtn");
    const navb = document.querySelector(".drawer-back.navb");
    const mobile = () => window.matchMedia("(max-width: 1024px)").matches;
    const setExpanded = () => {
      const open = mobile() ? document.body.classList.contains("nav-open") : !document.body.classList.contains("nav-collapsed");
      if (mbtn) mbtn.setAttribute("aria-expanded", String(open));
    };
    try { if (localStorage.getItem("tower-nav") === "collapsed") document.body.classList.add("nav-collapsed"); } catch (e) {}
    if (mbtn) mbtn.addEventListener("click", e => {
      e.preventDefault(); e.stopPropagation();
      if (mobile()) {
        document.body.classList.toggle("nav-open");
      } else {
        document.body.classList.toggle("nav-collapsed");
        try { localStorage.setItem("tower-nav", document.body.classList.contains("nav-collapsed") ? "collapsed" : "open"); } catch (err) {}
        setTimeout(() => Object.values(Tower.charts).forEach(c => { try { c.resize(); } catch (err) {} }), 260);
      }
      setExpanded();
    });
    if (navb) navb.addEventListener("click", () => { document.body.classList.remove("nav-open"); setExpanded(); });
    document.querySelectorAll(".side .nav a").forEach(a => a.addEventListener("click", () => { if (mobile()) document.body.classList.remove("nav-open"); }));
    window.addEventListener("resize", () => { if (!mobile()) document.body.classList.remove("nav-open"); setExpanded(); });
    setExpanded();

    const sel = document.getElementById("scenarioSelect");
    if (sel) sel.addEventListener("change", async () => {
      try { await Tower.api("/api/active", { id: sel.value }); location.reload(); }
      catch (e) { Tower.toast(e.message); }
    });

    const db = document.getElementById("drawerBack");
    if (db && !db.classList.contains("navb")) db.addEventListener("click", Tower.drawer.close);
    document.querySelectorAll("#drawer .close").forEach(b => b.addEventListener("click", Tower.drawer.close));
    document.addEventListener("keydown", e => { if (e.key === "Escape") { Tower.drawer.close(); document.body.classList.remove("nav-open"); } });

    document.querySelectorAll("table.tbl").forEach(t => Tower.sortable(t));

    document.querySelectorAll(".form-row input[type=range]").forEach(inp => {
      if (inp.title) return;
      const label = inp.closest(".form-row").querySelector("label");
      if (label) inp.title = label.textContent.trim();
    });
    document.querySelectorAll('input[type=range]').forEach(el => {
      Tower.paintRange(el);
      el.addEventListener("input", () => Tower.paintRange(el));
    });
    document.querySelectorAll("[data-p], .preset").forEach(el => { if (!el.title && el.dataset.p) el.title = "Apply the " + el.textContent.trim() + " preset"; });
  });
})();
