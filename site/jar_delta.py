"""Diferență reală de performanță și consum: fiecare motor măsurat, față de cum e acum live.

Sursele permise sunt exclusiv rapoartele commit-uite din `docs/`:
  * `ENGINE-NATIVE-RESULT.md`          — singurul duel echivalent (CUANTIC live vs CatServer oficial)
  * `ENGINE-TICKET-STEADY-RESULT.md`   — A/B stabil pentru candidat cu patch propriu
  * `ENGINE-FAMILY-RESULT.md`          — cine a pornit pack-ul 36/14 și cine nu
  * `CUANTIC-JAR-ATLAS-2026-10-12.md`  — de ce un candidat nu are scor
  * `analysis/BENCH-LIVE.md`           — arhiva „cum era înainte” (aceleași fișiere, sarcini declarate diferit)

Regula care guvernează tot fișierul: un număr se afișează DOAR dacă scrie în raportul brut.
Nu interpolăm, nu comparăm rânduri din rule diferite și nu numim câștigător un JAR care
nu a trecut pragul din `scripts/cuantic_tenx_gate.py`.
"""
from pathlib import Path
import json
import re

from jar_atlas import ATLAS, inline

DOCS = ATLAS.parent
ANALYSIS = DOCS.parent / "analysis"

FAMILY = DOCS / "ENGINE-FAMILY-RESULT.md"
BENCH = ANALYSIS / "BENCH-LIVE.md"
LADDER = DOCS / "CUANTIC-LADDER-RESULT.md"

# (document, cheia brațului de referință, cheia brațului candidat, metrici)
# Fiecare metrică: cheia din sumarul JSON al acelui raport.
PAIR_SPECS = (
    {
        "doc": "ENGINE-NATIVE-RESULT.md",
        "title": "CUANTIC live vs CatServer oficial",
        "task": "același pack 36/14, Java 17, 64 chunkuri forțate + 40 zombie, "
                "55 s încălzire + 75 s stabil, fără jucători și fără vehicule",
        "baseline": "branded", "candidate": "official",
        "labels": ("CUANTIC live", "CatServer oficial"),
        "metrics": (
            ("rss_steady_mib", "RAM stabilă", "MiB", "mai mic = mai bine"),
            ("cpu_steady_s", "CPU fereastră stabilă", "s", "mai mic = mai bine"),
            ("p95_steady_ms", "p95 MSPT", "ms", "bugetul unui tick e 50 ms"),
            ("boot_done_s", "Boot intern până la `Done`", "s", "nu include inițializarea din afară"),
            ("boot_wall_s", "Boot extern java → `Done`", "s", "cronometrat cu verificări la ~0,25 s"),
        ),
        "noise": True,
    },
    {
        "doc": "ENGINE-TICKET-STEADY-RESULT.md",
        "title": "CUANTIC live vs CUANTIC patch (cod scris de noi)",
        "task": "același pack intact, 64 chunkuri forțate + 40 zombie, ABBA pe aceeași mașină, "
                "75 s stabil după 55 s de încălzire, fără jucători",
        "baseline": "live", "candidate": "patched",
        "labels": ("CUANTIC live", "CUANTIC patch"),
        "metrics": (
            ("rss_mb_median_of_2", "RAM stabilă", "MiB", "mai mic = mai bine"),
            ("cpu_seconds_steady_median_of_2", "CPU fereastră stabilă", "s", "mai mic = mai bine"),
            ("p95_ms_median_of_2", "p95 MSPT", "ms", "bugetul unui tick e 50 ms"),
        ),
        "noise": False,
    },
)

# ordinea motoarelor în tabelul de diferență (cheile din ENGINE-FAMILY-RESULT.md)
ORDER = ("live-CatServer", "own-ticket-JAR", "Arclight", "Mist")

PRETTY = {
    "live-CatServer": ("CUANTIC live", "CatServer 1.16.5 adaptat + brand — binarul din producție"),
    "own-ticket-JAR": ("CUANTIC patch", "același CatServer cu patch-ul nostru de ticket/chunk"),
    "Arclight": ("Arclight 1.0.25", "hibrid Forge 1.16.5 + Bukkit, binar oficial"),
    "Mist": ("Mist 1.16.5-33", "hibrid cu mixin, fork Mohist arhivat"),
}

# arhiva „cum era înainte”, preluată din analysis/BENCH-LIVE.md + RAM-ALL.md (sarcini diferite)
ARCHIVE_ROWS = (
    ("RAM vârf (MiB)", "1.5.9: 2613", "1.7.7: 3335", 2613.0, 3335.0),
    ("p95 MSPT (ms)", "1.5.9: 4,9", "1.7.7: 2,0", 4.9, 2.0),
    ("Boot intern (s)", "1.5.9: 14,448", "1.7.7: 12,634", 14.448, 12.634),
)


def _read(path):
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return ""


def _json_block(text, section=0):
    blocks = re.findall(r"```json\s*(\{.*?\})\s*\```", text, re.S)
    try:
        return json.loads(blocks[section])
    except (IndexError, ValueError):
        return {}


def _num(value):
    return float(value) if isinstance(value, (int, float)) else None


def _ro(value, decimals=2):
    """Formatare românească, precizie fixă: 9.77 -> '9,77'."""
    return f"{value:.{decimals}f}".replace(".", ",")


def family_smokes():
    """Cine a ajuns la `Done` cu 36 moduri + 14 pluginuri, din rapoartele commit-uite."""
    data = _json_block(_read(FAMILY))
    out = {}
    for name, cand in (data.get("candidates") or {}).items():
        smoke = cand.get("smoke") or {}
        inventory = cand.get("candidate_pack_inventory") or {}
        done = smoke.get("done_seconds")
        out[name] = {
            "boot_s": _num(float(done)) if done else None,
            "plugins": smoke.get("enabled_plugins"),
            "mods": inventory.get("mods"),
            "passed": bool(smoke.get("passed_smoke")),
            "timed_out": bool(smoke.get("timed_out")),
            "sha": (cand.get("jar_sha256") or "")[:12],
            "qualified": bool(cand.get("qualified_for_performance_A_B")),
            "source": cand.get("source_engine"),
        }
    return out


def unmeasured_reasons():
    """Motivul pentru care un candidat nu are scor — textul atlasului, nu inventar al paginii."""
    reasons = {}
    try:
        from jar_atlas import rows
        text = ATLAS.read_text(encoding="utf-8")
        for name, _history, evidence, decision in rows(
                text, "## A. Duel echivalent posibil", "## B. Celelalte JAR-uri", 4):
            reasons[name.strip("*").strip()] = evidence + " " + decision
        for name, _context, reason in rows(text, "## B. Celelalte JAR-uri", "## Ce înseamnă 10×", 3):
            reasons[name.strip("*").strip()] = reason
    except Exception:  # noqa: BLE001 - atlas absent => randuri fara explicatie, nu cifre inventate
        pass
    return reasons


UNMEASURED_PREFIXES = ("Mohist", "LoliServer", "Magma")


def unmeasured_candidates():
    """Candidați din atlas care au sursă dar niciun fum 36/14 (tier C).

    Filtrul este pe NUME EXACT de motor, nu pe subșir: „Ketting / Magma Maintained”
    este alt ecosistem (tier D) și nu are ce căuta în randurile „NEAVĂGAT”.
    """
    names = []
    for name in unmeasured_reasons():
        if any(name == k or name.startswith(k + " ") for k in UNMEASURED_PREFIXES):
            names.append(name)
    return sorted(names)


def ladder_rows():
    """Ultimele probe ale SCĂRII (CI pe runner). lipsa fișierului = randuri NEAVĂGATE, nu 0."""
    md = _read(LADDER)
    if not md:
        return []
    data = _json_block(md)
    rows = []
    for name, cand in (data.get("candidates") or {}).items():
        ab = cand.get("ab") or {}
        if isinstance(cand.get("error"), str):
            status = "ESUAT · " + cand["error"][:120]
        elif cand.get("smoke_passed"):
            status = "a pornit 36/14 · " + str(ab.get("verdict") or "A/B neîncercat")
        else:
            status = "nu a ajuns la `Done` · fără scor"
        rows.append({"name": name, "boot_s": cand.get("boot_done_s"),
                     "sha": (cand.get("sha256_actual") or cand.get("sha256_expected") or "")[:12],
                     "licence": cand.get("licence_declared") or "neverificată",
                     "plugins": cand.get("plugins_enabled"),
                     "status": status, "verdict": ab.get("verdict") or "NEAVĂGAT",
                     "reason": ab.get("reason") or cand.get("error") or ""})
    return rows


def same_run_pairs():
    """Doar perechile A/B rulate împreună, pe aceeași sarcină, din sumarele raportului."""
    pairs = []
    for spec in PAIR_SPECS:
        md = _read(DOCS / spec["doc"])
        if not md:
            continue
        summary = (_json_block(md).get("summary") or {})
        base, cand = summary.get(spec["baseline"]) or {}, summary.get(spec["candidate"]) or {}
        if not isinstance(base, dict) or not isinstance(cand, dict):
            continue
        rows = []
        for key, label, unit, note in spec["metrics"]:
            a_cell, b_cell = base.get(key), cand.get(key)
            # un sumar fie da o valoare simpla, fie un dict {median, within_arm_range}
            def val(cell):
                if isinstance(cell, dict):
                    return _num(cell.get("median"))
                return _num(cell)
            def rng(cell):
                return _num(cell.get("within_arm_range")) if isinstance(cell, dict) else None
            a, b = val(a_cell), val(b_cell)
            if a is None or b is None:
                continue
            noise = None
            if spec["noise"]:
                ranges = [v for v in (rng(a_cell), rng(b_cell)) if v is not None]
                noise = max(ranges) if ranges else None
            rows.append({"label": label, "unit": unit, "note": note, "a": a, "b": b,
                         "delta": b - a, "noise": noise})
        if not rows:
            continue
        verdict = (_json_block(md).get("verdict") or "").strip()
        if "NOT PROVEN BETTER" in verdict or "RESPINS" in verdict:
            state, why = "RESPINS", "verdictul raportului: „" + verdict + "”"
        elif "TWO-SAMPLE OBSERVATION ONLY" in verdict:
            state, why = "NECONCLUDENT", "două probe braț; variația internă acoperă diferența"
        else:
            state, why = "DE VERIFICAT", verdict or "verdictul nu e scris în raport"
        pairs.append({
            "title": spec["title"], "task": spec["task"], "labels": spec["labels"],
            "rows": rows, "state": state, "why": why, "source": "docs/" + spec["doc"],
            "runs": re.findall(r"actions/runs/(\d+)", md)[:1],
            "noise_reported": bool(spec["noise"]),
        })
    return pairs


def archive_deltas():
    """Ce s-a schimbat pe aceeași gazdă între 1.5.9 și pack-ul de azi (arhivist, nu A/B)."""
    out = []
    for label, before, after, a, b in ARCHIVE_ROWS:
        if not a:
            continue
        out.append({"label": label, "before": before, "after": after,
                    "delta": b - a, "pct": (b - a) / a * 100})
    return out


def _delta_bar(row):
    """Bara arată diferența și plaja de zgomot a aceluiași JAR, dacă raportul o dă."""
    if not row["noise"]:
        return '<span class="jd-bar jd-bar-empty" aria-hidden="true"><i class="jd-mid"></i>' \
               '<i class="jd-dot ' + ("up" if row["delta"] > 0 else "down") + '"></i></span>'
    spread = max(abs(row["delta"]), row["noise"], 1e-9) * 1.35
    def pct(v):
        return 50 + (v / spread) * 50
    left, right = pct(-row["noise"]), pct(row["noise"])
    return (f'<span class="jd-bar" aria-hidden="true"><i class="jd-noise" '
            f'style="left:{left:.2f}%;width:{max(right - left, 0.4):.2f}%"></i><i class="jd-mid"></i>'
            f'<i class="jd-dot {"up" if row["delta"] > 0 else "down"}" '
            f'style="left:{pct(row["delta"]):.2f}%"></i></span>')


def _pair_table(pair):
    body = []
    for row in pair["rows"]:
        sign = "+" if row["delta"] > 0 else "−"
        cls = "up" if row["delta"] > 0 else "down"
        if row["noise"] is None:
            inside_txt = "fără plajă de zgomot raportată în acest run"
        elif abs(row["delta"]) <= row["noise"]:
            inside_txt = "în interiorul zgomotului aceluiași JAR"
        else:
            inside_txt = "peste zgomotul măsurat — tot nu e dovadă"
        body.append(
            f'<tr><th scope="row">{row["label"]}<small>{row["note"]}</small></th>'
            f'<td class="jd-a">{_ro(row["a"])}<span>{pair["labels"][0]}</span></td>'
            f'<td class="jd-b">{_ro(row["b"])}<span>{pair["labels"][1]}</span></td>'
            f'<td class="jd-diff"><b class="{cls}">{sign}{_ro(abs(row["delta"]))} {row["unit"]}</b>'
            f'<small>{inside_txt}</small></td>'
            f'<td class="jd-visual">{_delta_bar(row)}</td></tr>')
    runs = "".join(
        f' <a href="https://github.com/iZentric/ServerRolePlayLite/actions/runs/{r}">run {r}</a>'
        for r in pair.get("runs") or [])
    return (f'<div class="jd-pair"><div class="jd-pair-head"><h3>{pair["title"]}</h3>'
            f'<span class="jd-chip {pair["state"].lower()}">{pair["state"]}</span></div>'
            f'<p class="jd-task">{pair["task"]} · {inline(pair["why"])} · '
            f'<a href="https://github.com/iZentric/ServerRolePlayLite/blob/main/{pair["source"]}">'
            f'{pair["source"].split("/")[-1]}</a>{runs}</p>'
            '<div class="jd-scroll" tabindex="0" role="region" '
            'aria-label="Diferențe de consum și performanță, aceeași sarcină">'
            '<table class="jd-table"><thead><tr><th scope="col">Măsură</th>'
            f'<th scope="col">{pair["labels"][0]}</th><th scope="col">{pair["labels"][1]}</th>'
            '<th scope="col">Diferență (candidat − live)</th><th scope="col">Față de zgomot</th>'
            '</tr></thead><tbody>' + "".join(body) + '</tbody></table></div></div>')


def _candidate_note(name, pairs, info):
    if name == "own-ticket-JAR":
        pair = next((p for p in pairs if "patch" in p["title"]), None)
        if not pair:
            return "A/B-ul stabil nu e disponibil; pagina nu afișează numere"
        bits = [f'{r["label"].split(" ")[0].lower()} {"+" if r["delta"] > 0 else "−"}'
                f'{_ro(abs(r["delta"]))} {r["unit"]}' for r in pair["rows"]]
        return (" " + " · ".join(bits) + " față de live în același run → " + pair["state"])
    if name in ("Arclight", "Mist"):
        return ("fără scor: nu a ajuns la `Done` cu pack-ul nostru, deci nu există ce compara. "
                "Nu e „mai lent”, e incompatibil.")
    return "— (baseline-ul live la care se raportează tot) · diferența cu oficialul e mai jos"


def _matrix_rows(pairs):
    smokes = family_smokes()
    reasons = unmeasured_reasons()
    out = []
    for name in ORDER:
        info = smokes.get(name)
        if not info:
            continue
        pretty, sub = PRETTY.get(name, (name, ""))
        boot = f"{_ro(info['boot_s'], 3)} s" if info["boot_s"] else "—"
        plugins = f"{info['plugins']}/14" if info["plugins"] is not None else "—"
        mods = f"{info['mods']}/36" if info["mods"] else ("36 (identic)" if info["passed"] else "—")
        if info["passed"]:
            state, chip = "a pornit pack-ul intact", "ok"
        elif info["timed_out"]:
            state, chip = "nu a ajuns la `Done`", "bad"
        else:
            state, chip = "nu a pornit cu pack-ul nostru", "bad"
        out.append(
            f'<tr data-delta-row data-engine="{name}"><th scope="row"><b>{pretty}</b>'
            f'<small>{sub} · SHA {info["sha"] or "—"}</small></th>'
            f'<td><span class="jd-badge {chip}">{inline(state)}</span></td>'
            f'<td>{mods}</td><td>{plugins}</td><td class="jd-num"><b>{boot}</b></td>'
            f'<td>{inline(_candidate_note(name, pairs, info))}</td></tr>')
    tried = {r["name"].split(" ")[0].lower() for r in ladder_rows()}
    for cand in ladder_rows():
        cand["name"] = cand["name"].replace(" 1.16.5", " ").split(" (")[0].strip()
        boot = f"{_ro(cand['boot_s'], 3)} s" if isinstance(cand["boot_s"], (int, float)) else "—"
        if cand["status"].startswith("ESUAT"):
            # fără binar descărcat nu am atins nici pack-ul: niciun „36” de afișat
            chip, mods, plugins, boot = "none", "—", "—", "—"
        elif "a pornit" in cand["status"]:
            chip, mods = "ok", "36 (neschimbat)"
            plugins = f"{cand['plugins']}/14" if isinstance(cand["plugins"], int) else "—"
        else:
            chip, mods, plugins = "bad", "—", (f"{cand['plugins']}/14" if isinstance(cand["plugins"], int) else "—")
        out.append(
            f'<tr data-delta-row data-engine="{re.sub(r"[^a-z0-9-]", "-", cand["name"].lower())}">'
            f'<th scope="row"><b>{inline(cand["name"])}</b>'
            f'<small>scara CUANTIC pe runner · SHA {cand["sha"] or "—"} · licență {inline(cand["licence"])}</small></th>'
            f'<td><span class="jd-badge {chip}">{inline(cand["status"])}</span></td>'
            f'<td>{mods}</td><td>{plugins}</td><td class="jd-num"><b>{boot}</b></td>'
            f'<td>{inline(cand["reason"] or cand["verdict"])}</td></tr>')
        tried.add(cand["name"].split(" ")[0].lower())
    for name in unmeasured_candidates():
        short = name.replace(" 1.16.5", "").strip()
        if short.lower().split(" ")[0] in tried:
            continue
        reason = unmeasured_reasons().get(name, "nu a fost rulat cu pack-ul nostru în această rundă")
        out.append(
            f'<tr data-delta-row data-engine="{re.sub(r"[^a-z0-9-]", "-", short.lower())}">'
            f'<th scope="row"><b>{inline(short)}</b>'
            f'<small>candidat neevaluat pe 36/14</small></th>'
            '<td><span class="jd-badge none">NEAVĂGAT</span></td><td>—</td><td>—</td>'
            f'<td class="jd-num"><b>—</b></td><td>{inline(reason)}</td></tr>')
    return "".join(out)


def panel():
    pairs = same_run_pairs()
    rows = _matrix_rows(pairs)
    arch = "".join(
        f'<tr><th scope="row">{a["label"]}</th><td>{inline(a["before"])}</td>'
        f'<td>{inline(a["after"])}</td><td class="jd-diff"><b class="{"up" if a["pct"] > 0 else "down"}">'
        f'{"+" if a["pct"] > 0 else "−"}{_ro(abs(a["pct"]), 1)}%</b>'
        f'<small>{("+" if a["pct"] > 0 else "−")}{_ro(abs(a["delta"]), 1)} față de 1.5.9</small></td></tr>'
        for a in archive_deltas())
    measured = sum(1 for info in family_smokes().values() if info["passed"])
    untried = [n for n in unmeasured_candidates()
               if n.split(" ")[0].lower() not in {r["name"].split(" ")[0].lower() for r in ladder_rows()}]
    total = len(family_smokes()) + len(unmeasured_candidates())
    return f'''<section id="diferente" class="jd-section" aria-labelledby="jd-title">
<div class="jd-overline"><span aria-hidden="true">⇄</span> DIFERENȚA MĂSURATĂ <span class="jd-rule"></span> 12 OCT 2026</div>
<h2 id="jd-title">Ce aduce Cuantic față de cum era.<br><span>Cifrele care contează, restul — marcat „nu avem”.</span></h2>
<p class="jd-lead"><b>{measured} din {total}</b> motoare au pornit pack-ul intact (36 moduri Forge + 14 pluginuri Bukkit).
Doar perechile măsurate <b>în același run, pe aceeași sarcină</b> primesc diferență. Orice altă comparație ar fi între
două jocuri diferite, deci afișăm motivul, nu un număr.</p>
<div class="jd-matrix-wrap"><table class="jd-matrix">
<thead><tr><th scope="col">Motor</th><th scope="col">Cu pack-ul Cuantic</th><th scope="col">Moduri</th>
<th scope="col">Pluginuri</th><th scope="col">Boot</th><th scope="col">Diferență față de cum e acum</th></tr></thead>
<tbody>{rows}</tbody></table></div>
{"".join(_pair_table(p) for p in pairs) if pairs else
 '<p class="jd-empty">Nu există încă un A/B complet commit-uit; pagina nu afișează numere.</p>'}
<div class="jd-legend"><span><i class="jd-noise-demo"></i> fâșia gri = cât variază <b>același JAR</b> între două porniri;
dacă punctul cade înăuntru, diferența nu e dovadă</span>
<span><i class="jd-dot down demo"></i> candidat mai mic (bine)</span>
<span><i class="jd-dot up demo"></i> candidat mai mare (rău)</span></div>
<details class="jd-archive"><summary><b>Arhiva „cum era înainte” — aceeași gazdă, sarcini declarate diferit</b></summary>
<p>Cifrele de mai jos vin din runde diferite ale aceluiași proiect (<code>analysis/BENCH-LIVE.md</code>,
<code>analysis/RAM-ALL.md</code>). Le păstrăm ca istoric, <b>nu</b> ca benchmark: lumea, seed-ul, sarcina
și momentul diferă, deci procentul de mai jos nu e un câștig de motor.</p>
<div class="jd-scroll"><table class="jd-table jd-old">
<thead><tr><th scope="col">Metric</th><th scope="col">Cum era</th><th scope="col">Cum e</th>
<th scope="col">Diferență</th></tr></thead><tbody>{arch}</tbody></table></div>
</details>
<div class="jd-next"><div><strong>Ce ar mișca rândurile de „NEAVĂGAT”</strong>
<p>Build 1.16.5 autentic cu SHA și licență verificate, pornire cu 36/14, apoi minimum <b>3 repetări reale
pe braț</b> cu clienți Forge confirmați în <code>/list</code>. Până atunci pagina nu primește niciun număr
pentru ele — <code>scripts/cuantic_tenx_gate.py</code> întoarce <code>NEMĂSURAT</code>, niciodată un număr favorabil.</p></div>
<a href="#tier">Înapoi la tier list ↑</a></div>
</section>'''


STYLE = r'''
/* Diferenta masurata: aceeasi sarcina sau nimic. */
.jd-section{margin:44px 0 8px;padding:34px 28px 26px;border:1px solid rgba(127,176,255,.22);border-radius:24px;
 background:radial-gradient(circle at 92% 4%,rgba(95,240,192,.1),transparent 42%),
 radial-gradient(circle at 4% 60%,rgba(127,176,255,.12),transparent 46%),#0b1120;position:relative;overflow:hidden}
.jd-section:before{content:"";position:absolute;left:0;right:0;top:0;height:2px;background:linear-gradient(90deg,#7fb0ff,#5ff0c0,#ff9093)}
.jd-overline{display:flex;align-items:center;gap:10px;color:#a6c6f5;letter-spacing:.16em;font-weight:800;font-size:11px}
.jd-rule{height:1px;background:rgba(166,198,245,.26);width:34px}
.jd-section h2{font-size:clamp(27px,4.1vw,44px);line-height:1.13;letter-spacing:-.04em;margin:14px 0}
.jd-section h2 span{color:#7fb0ff}
.jd-lead{max-width:920px;color:#a8b8d2;font-size:15px;line-height:1.7}
.jd-matrix-wrap{overflow-x:auto;margin-top:22px;border:1px solid rgba(127,176,255,.2);border-radius:14px}
.jd-matrix{width:100%;min-width:880px;border-collapse:separate;border-spacing:0;font-size:13px}
.jd-matrix th[scope=col]{position:sticky;top:0;background:#131d33;color:#a9c3ea;font-size:10.5px;letter-spacing:.09em;
 text-transform:uppercase;padding:12px 13px;text-align:left;font-weight:750}
.jd-matrix td,.jd-matrix th[scope=row]{padding:13px;border-top:1px solid rgba(127,176,255,.13);background:rgba(14,22,38,.86);
 text-align:left;font-weight:400;color:#b9c6dd;vertical-align:top}
.jd-matrix th[scope=row] b{display:block;color:#f1f6ff;font-size:13.5px}
.jd-matrix th[scope=row] small{display:block;margin-top:4px;color:#7f8cab;font-size:11px;line-height:1.45}
.jd-matrix .jd-num{font-variant-numeric:tabular-nums;color:#e8eefb}
.jd-badge{display:inline-block;border-radius:20px;padding:4px 9px;font-size:11px;font-weight:750;white-space:nowrap}
.jd-badge.ok{background:rgba(95,240,192,.13);color:#9cf3d4}
.jd-badge.bad{background:rgba(255,144,147,.12);color:#ffb8b8}
.jd-badge.none{background:rgba(246,199,106,.13);color:#f6d69e}
.jd-pair{margin-top:26px;border:1px solid rgba(127,176,255,.18);border-radius:16px;padding:18px;background:rgba(255,255,255,.02)}
.jd-pair-head{display:flex;align-items:center;justify-content:space-between;gap:14px;flex-wrap:wrap}
.jd-pair-head h3{margin:0;font-size:17px;letter-spacing:-.02em;color:#eef4ff}
.jd-chip{border-radius:20px;padding:5px 11px;font-size:11px;font-weight:800;letter-spacing:.05em;
 background:rgba(148,163,184,.14);color:#cbd6e8}
.jd-chip.neconcludent{background:rgba(246,199,106,.15);color:#f7dda9}
.jd-chip.respins{background:rgba(255,144,147,.14);color:#ffbcbe}
.jd-chip.de,.jd-chip.verificat{background:rgba(127,176,255,.14);color:#bcd8ff}
.jd-task{margin:8px 0 4px;color:#8d9bb8;font-size:12.5px;line-height:1.6}
.jd-task a{color:#8fd8c9}
.jd-scroll{overflow-x:auto;margin-top:10px}
.jd-table{width:100%;min-width:780px;border-collapse:separate;border-spacing:0;font-size:13px}
.jd-table th[scope=col]{text-align:left;color:#9db3d6;font-size:10.5px;letter-spacing:.09em;text-transform:uppercase;
 padding:10px 12px;border-bottom:1px solid rgba(127,176,255,.2);background:transparent}
.jd-table td,.jd-table th[scope=row]{padding:12px;border-bottom:1px solid rgba(127,176,255,.1);text-align:left;
 font-weight:400;color:#bcc9de;vertical-align:middle}
.jd-table tbody tr:last-child td,.jd-table tbody tr:last-child th{border-bottom:0}
.jd-table th[scope=row]{color:#eaf1fb;font-weight:650;width:236px}
.jd-table th[scope=row] small,.jd-table td small{display:block;margin-top:4px;color:#7d89a6;font-size:11px;font-weight:400}
.jd-a,.jd-b{font-variant-numeric:tabular-nums;font-weight:750;color:#e8eefb}
.jd-a span,.jd-b span{display:block;font-size:10.5px;font-weight:500;color:#7d89a6;margin-top:2px}
.jd-diff b{font-size:14px;font-variant-numeric:tabular-nums}
.jd-diff b.up{color:#ff9ba0}.jd-diff b.down{color:#7ff0c6}
.jd-visual{width:200px}
.jd-bar{position:relative;display:block;height:26px;border-radius:8px;background:rgba(255,255,255,.035);overflow:hidden}
.jd-bar-empty{background:rgba(255,255,255,.02)}
.jd-noise{position:absolute;top:0;bottom:0;background:rgba(148,163,184,.22)}
.jd-mid{position:absolute;left:50%;top:3px;bottom:3px;width:1px;background:rgba(203,213,225,.45)}
.jd-dot{position:absolute;top:50%;left:50%;width:11px;height:11px;margin:-5.5px 0 0 -5.5px;border-radius:50%;
 box-shadow:0 0 0 2px rgba(6,10,18,.9)}
.jd-dot.down{background:#5ff0c0}.jd-dot.up{background:#ff9093}
.jd-legend{display:flex;flex-wrap:wrap;gap:16px;margin-top:16px;color:#8593b0;font-size:12px;align-items:center}
.jd-legend span{display:flex;align-items:center;gap:7px}
.jd-noise-demo{width:22px;height:11px;border-radius:3px;background:rgba(148,163,184,.35);display:inline-block}
.jd-dot.demo{position:static;margin:0;display:inline-block}
.jd-archive{margin-top:24px;border:1px solid rgba(148,163,184,.18);border-radius:14px;padding:14px 16px;background:rgba(255,255,255,.015)}
.jd-archive summary{cursor:pointer;font-size:13.5px;color:#cfdcef}
.jd-archive p{color:#8d9bb8;font-size:12.5px;line-height:1.65;margin:10px 0 4px}
.jd-archive code{color:#cfe0f7;background:rgba(127,176,255,.1);padding:1px 4px;border-radius:3px;font-size:11px}
.jd-old{min-width:660px}
.jd-empty{margin-top:22px;color:#f6d69e;font-size:13px}
.jd-next{display:flex;justify-content:space-between;gap:20px;align-items:center;margin-top:24px;padding:18px;
 border:1px solid rgba(127,176,255,.24);border-radius:14px;background:linear-gradient(100deg,rgba(127,176,255,.09),rgba(95,240,192,.05))}
.jd-next strong{color:#f1f6ff;font-size:14px}
.jd-next p{color:#a3aecb;font-size:12px;line-height:1.6;margin:6px 0 0;max-width:800px}
.jd-next a{font-size:12px;color:#9fc4f5;white-space:nowrap}
.jd-next code{color:#cfe0f7;background:rgba(127,176,255,.12);padding:1px 4px;border-radius:3px;font-size:11px}
@media(max-width:740px){.jd-section{padding:24px 14px}.jd-next{flex-direction:column;align-items:flex-start}}
'''
