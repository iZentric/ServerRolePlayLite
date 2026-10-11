"""Measured engine results and a clearly labelled RP/survival strategy for the site."""
from datetime import datetime, timezone
from html import escape
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
REPO_DOCS = "https://github.com/iZentric/ServerRolePlayLite/blob/arena/a29b4ef4-serverroleplaylite/docs/"
JAR_URL = "https://github.com/iZentric/ServerRolePlayLite/releases/download/lite/CUANTIC-Engine-Validated-Live-1.16.5.jar"
PACK_URL = "https://github.com/iZentric/ServerRolePlayLite/releases/tag/lite"


def result(name, section=0):
    try:
        text = (DOCS / name).read_text(encoding="utf-8")
        blocks = re.findall(r"```json\s*(\{.*?\})\s*```", text, re.S)
        return json.loads(blocks[section])
    except (OSError, IndexError, ValueError):
        return {}


def latest_status():
    """A static page can only show a timestamped observation, never live presence."""
    try:
        text = (ROOT / "analysis/ALIVE.md").read_text(encoding="utf-8")
        stamp = re.search(r"ALIVE CUANTIC — (\d{4}-\d\d-\d\d \d\d:\d\d:\d\d) UTC", text)
        observation = re.search(r"```\s*(.+?)\s*```", text, re.S)
        if not stamp or not observation:
            return "Status public neconfirmat", "var(--mut)"
        dt = datetime.strptime(stamp.group(1), "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
        age = (datetime.now(timezone.utc) - dt).total_seconds()
        if age < 0 or age > 30 * 60:
            return "Status neconfirmat acum · ultima probă " + dt.strftime("%d.%m %H:%M UTC"), "var(--mut)"
        if observation.group(1).startswith("SUS public"):
            return "SUS la ultima probă publică " + dt.strftime("%d.%m %H:%M UTC") + " (ping)", "var(--mint)"
        return "Status public neconfirmat " + dt.strftime("%H:%M UTC"), "var(--amber)"
    except (OSError, ValueError):
        return "Status public neconfirmat", "var(--mut)"


def _metric(data, key, unit):
    try:
        return f"{float(data[key]):.2f}".rstrip("0").rstrip(".").replace(".", ",") + unit
    except (KeyError, TypeError, ValueError):
        return "—"


def panel():
    """The winner and the numbers come from committed, reproducible reports."""
    family = result("ENGINE-FAMILY-RESULT.md")
    player = result("ENGINE-PLAYER-RESULT.md")
    steady = result("ENGINE-TICKET-STEADY-RESULT.md")
    filled = result("ENGINE-CURRENT-RESULT.md", section=1).get("summary", {})
    empty = result("ENGINE-EMPTY-RESULT.md", section=1).get("summary", {})
    mist_j11 = result("ENGINE-MIST-J11-RESULT.md")
    candidates = family.get("candidates", {})
    sha = family.get("baseline_jar_sha256")
    winner_doc = (DOCS / "ENGINE-WINNER-JAR.md").read_text(encoding="utf-8") if (DOCS / "ENGINE-WINNER-JAR.md").exists() else ""
    verified = bool(sha and sha == player.get("live_jar_sha256") and
                    sha in winner_doc and JAR_URL in winner_doc and
                    candidates.get("live-CatServer", {}).get("qualified_for_performance_A_B"))
    if verified:
        winner_button = f'<a class="btn" href="{JAR_URL}">⬇️ Descarcă JAR-ul validat</a>'
        winner_note = (f'<p class="sub" style="margin-top:12px">SHA-256: <code style="overflow-wrap:anywhere">{escape(sha)}</code>. '
                       'Fișierul este <b>identic byte-cu-byte cu motorul live</b>, nu un nou upgrade. '
                       f'Pentru moduri și pluginuri descarcă <a href="{PACK_URL}">pack-ul server complet</a>; '
                       'un JAR singur nu înlocuiește pack-ul.</p>')
    else:
        winner_button = f'<a class="btn ghost" href="{PACK_URL}">Pack-ul CatServer existent</a>'
        winner_note = ('<p class="sub">Verificarea checksum-ului pentru descărcarea separată lipsește; '
                       'nu afișăm un câștigător nou neverificat.</p>')

    live, patched = steady.get("summary", {}).get("live", {}), steady.get("summary", {}).get("patched", {})
    if all(steady.get(x, {}).get("valid") for x in ("live-A1", "live-A2", "patched-B1", "patched-B2")):
        ticket_row = (f'<tr><td>Patch-ul nostru: 64 chunk-uri, 75 s stabile după încălzire (2×/motor)</td>'
                      f'<td>CPU {_metric(live, "cpu_seconds_steady_median_of_2", " s")} → '
                      f'{_metric(patched, "cpu_seconds_steady_median_of_2", " s")}; '
                      f'p95 {_metric(live, "p95_ms_median_of_2", " ms")} → '
                      f'{_metric(patched, "p95_ms_median_of_2", " ms")}</td>'
                      '<td>CPU mai mic, p95 nu; <b>nu este upgrade demonstrat</b>.</td></tr>')
    else:
        ticket_row = '<tr><td>Patch ticket</td><td>Raport incomplet</td><td>Nu se promovează.</td></tr>'

    def old_fork(title, data):
        try:
            a, b = data["live"], data["patched"]
            return (f'<tr><td>{title} (2×/motor)</td>'
                    f'<td>p95 {_metric(a, "p95_ms_median_of_2", " ms")} → '
                    f'{_metric(b, "p95_ms_median_of_2", " ms")}; '
                    f'CPU {_metric(a, "cpu_seconds_workload_median_of_2", " s")} → '
                    f'{_metric(b, "cpu_seconds_workload_median_of_2", " s")}</td>'
                    '<td>Nu a câștigat; fără instalare.</td></tr>')
        except (KeyError, TypeError):
            return ''
    fork_rows = old_fork("Patch pe hoppers plini", filled) + old_fork("Patch pe hoppers goale", empty)

    samples = player.get("samples", [])
    if len(samples) == 3 and all(s.get("players", 0) >= 1 for s in samples):
        try:
            times = ' / '.join(f'{s["spark_mspt_min_med_p95_max_10s"][2]:g}' for s in samples)
            real_note = (f'Pe JAR-ul live, trei citiri cu 1 jucător (11 octombrie 2026): '
                         f'<b>p95 pe 10 s {times} ms</b>. Nu este A/B cu un alt JAR, '
                         'nici probă cu trafic, mafii sau vehicule.')
        except (KeyError, IndexError, TypeError):
            real_note = 'Proba cu jucătorul nu are valori complete; consultați raportul.'
    else:
        real_note = 'Proba cu jucătorul nu este disponibilă; nu presupunem încărcare reală.'

    arclight = candidates.get("Arclight", {})
    mist = mist_j11.get("candidates", {}).get("Mist", {})
    competitors = (
        '<li>Arclight cu pack-ul complet: injecție Mixin eșuată la pornire; fără scor TPS comparabil.</li>'
        if arclight.get("smoke") and not arclight.get("qualified_for_performance_A_B") else
        '<li>Arclight: verdictul de compatibilitate nu este disponibil.</li>'
    ) + (
        '<li>Mist pe Java 11: eroare înainte de <code>Done</code>; fără scor TPS comparabil.</li>'
        if mist.get("smoke") and not mist.get("qualified_for_performance_A_B") else
        '<li>Mist: verdictul de compatibilitate nu este disponibil.</li>'
    )

    return f'''<section id="engine-test" aria-label="Benchmark al motorului CUANTIC">
<h2>🔬 JAR-ul validat și benchmarkul — fără „zero lag” inventat</h2>
<div class="sub">Pentru <b>acest</b> modpack Forge 1.16.5 (36 moduri + 14 pluginuri),
păstrăm motorul CatServer CUANTIC deja folosit pe server. Am construit un JAR cu patch propriu și am
comparat fork-uri în copii izolate pe GitHub; <b>niciunul nu a demonstrat un câștig simultan
CPU + p95 și compatibilitate în joc cu vehicule</b>. Nu schimbăm live-ul pentru un scor fără probe.</div>
<div class="card" style="margin-top:18px;border-color:rgba(95,240,192,.38)">
<h3>🏆 Cel mai bun rezultat validat acum: JAR-ul live</h3>
<p>Compatibilitatea pack-ului a fost verificată în smoke cu 36/14. Alte motoare care nu pornesc cu
același pack nu sunt clasate fictiv ca „mai rapide”.</p>
<div class="cta">{winner_button}<a class="btn ghost" href="{REPO_DOCS}BENCHMARK-MOTOARE-CUANTIC-2026-10-12.md">📊 Vezi benchmarkul integral</a></div>
{winner_note}
</div>
<div class="table-scroll"><table class="tbl"><tr><th>Test GitHub, același runner</th><th>Motor actual → candidat</th><th>Verdict</th></tr>
{ticket_row}{fork_rows}</table></div>
<div class="note">{real_note} Toate cifrele sunt datate; badge-ul de sus este doar ultimul
<b>ping public</b>, nu promisiunea că serverul este online acum.</div>
<div class="card" style="margin-top:14px"><h3>Alternative testate cu modpack-ul intact</h3>
<ul style="margin:6px 0 0 20px;color:var(--mut);font-size:14px">{competitors}</ul>
<p style="margin-top:10px">Paper/vanilla fără modurile Forge nu reprezintă același joc. Mohist, Magma și
alte JAR-uri neprobate nu sunt declarate învinse.</p></div>
<p class="sub" style="margin-top:12px">Rapoarte: <a href="{REPO_DOCS}ENGINE-TICKET-STEADY-RESULT.md">A/B/B/A patch propriu</a> ·
<a href="{REPO_DOCS}ENGINE-FAMILY-RESULT.md">compatibilitatea motoarelor</a> ·
<a href="{REPO_DOCS}ENGINE-PLAYER-RESULT.md">proba cu jucător</a>. Un laptop slab și configurațiile
OptiFine + modurile normale respectiv Rubidium/Oculus se testează <b>separat</b> în oraș, cu vehicule.</p>
</section>'''


def strategy_panel():
    """A roadmap, explicitly not an assertion that mafia mechanics exist today."""
    return f'''<section id="viziune" aria-label="Strategia pentru roleplay, survival și oraș">
<h2>🏙️ Direcția CUANTIC: oraș RP modat + survival + mafii</h2>
<p class="sub">Păstrăm gameplay-ul modat. Construim lumea socială în jurul unui server stabil,
nu sacrificăm clientul Forge ca să obținem un TPS frumos pe hârtie.
<b>Etapele de mai jos sunt direcție de dezvoltare, nu funcții declarate deja lansate.</b></p>
<div class="grid">
 <div class="card"><h3>01 · Fundația: intri și rămâi în joc</h3><p><b>Acum:</b> pack Forge 1.16.5 și motorul live cu 36 moduri / 14 pluginuri.
 <b>Înainte de extindere:</b> backup și rollback testate, verificare autentificare cu clientul normal,
 probe cu mai mulți jucători și fără restart în timpul sesiunilor active.</p></div>
 <div class="card"><h3>02 · Survival în oraș</h3><p><b>De proiectat și testat:</b> resurse,
 locuințe/terenuri, economie inteligibilă și progres fără grind inutil. Protecțiile trebuie să
 permită construire și roleplay, dar să limiteze grief-ul; regulile economiei se verifică în joc.</p></div>
 <div class="card"><h3>03 · Mafii și RP cu reguli clare</h3><p><b>De proiectat și testat:</b> facțiuni,
 teritorii, joburi și conflicte cu limite, loguri și moderare. Fără avantaje ascunse pentru OP,
 fără mecanici care distrug survivalul sau obligă jucătorii să instaleze încă zece moduri.</p></div>
 <div class="card"><h3>04 · Oraș viu, inclusiv pe PC modest</h3><p><b>De măsurat:</b> plimbare și
 condus prin oraș, entități și vehicule cu 1, apoi 2–5 jucători. Laptop slab în două instanțe
 distincte: OptiFine + modurile normale versus Rubidium/Oculus. Urmărim FPS client,
 login, p95 MSPT, TPS, RAM și erori; nu promitem „fără nicio problemă” înaintea probelor.</p></div>
</div>
<div class="note"><b>Regula strategiei:</b> mai întâi compatibilitate și sesiuni jucabile,
 apoi conținut RP. Un JAR nou intră pe live doar după test reprezentativ, backup,
 fereastră fără jucători și rollback verificat. Problemele confirmate se documentează și se repară,
 nu se ascund în marketing. <a href="{REPO_DOCS}STRATEGIE-ROLEPLAY-SURVIVAL.md">Vezi planul cu criterii de acceptare →</a></div>
</section>'''
