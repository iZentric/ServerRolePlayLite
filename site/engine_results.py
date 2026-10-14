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


def chooser_panel(verified, native_ok, strict_ok, arclight_ok, mist_ok):
    """Plain-language product choice; no speed ranking across incompatible packs."""
    source = lambda name: f'{REPO_DOCS}{name}'
    live = ('<b>DA</b> · 36 moduri și 14 pluginuri au pornit; există și citiri cu 1 jucător.'
            if verified else 'Dovada pentru JAR-ul public nu este completă; nu recomandăm un binar neverificat.')
    official = ('<b>DA</b> · 36/14 au pornit în copie; RAM/p95 nu arată un avantaj stabil pentru branding.'
                if native_ok else 'Comparația cu pack identic nu este verificată complet.')
    patched = ('<b>DA</b> la pornire; <b>NU</b> la pragul complet CPU + RAM + p95 + boot.'
               if strict_ok else 'Testul complet al patch-ului este incomplet.')
    arclight = ('<b>NU</b> cu pack-ul nostru intact: eroare Mixin la pornire.'
                if arclight_ok else 'Nu există verdict de compatibilitate verificat aici.')
    mist = ('<b>NU</b> cu acest binar și Java 11: eroare înainte de pornire.'
            if mist_ok else 'Nu există verdict de compatibilitate verificat aici.')
    return f'''<div id="alegere">
<h2>🧭 Ce motor alegi? Pe scurt, fără reclamă</h2>
<p class="sub">Comparăm <b>același joc</b>: Minecraft Forge 1.16.5 cu cele 36 de moduri și
14 pluginuri ale serverului CUANTIC. „Pornește” înseamnă un test izolat, nu dovadă
că 25 de oameni pot conduce simultan fără lag. Rândurile fără același pack <b>nu au scor comparabil</b>.</p>
<div class="table-scroll"><table class="tbl">
<tr><th>Motor</th><th>Ce am verificat pe pack-ul nostru</th><th>Alegerea corectă acum</th></tr>
<tr><td><b>CUANTIC live</b><br><small>CatServer 1.16.5 configurat pentru acest pack</small></td>
<td>{live} <a href="{source('ENGINE-FAMILY-RESULT.md')}">Proba →</a></td>
<td><b>Da, pentru pack-ul RP actual</b>: configurația și JAR-ul folosit sunt cunoscute. Nu îl declarăm mai rapid decât oficialul.</td></tr>
<tr><td><b>CatServer oficial</b><br><small>aceeași versiune de bază</small></td>
<td>{official} <a href="{source('ENGINE-NATIVE-RESULT.md')}">A/B-ul →</a></td>
<td>Alternativă care pornește în copie; <b>nu e demonstrat că pierde</b> la performanță. Nu schimbăm live-ul doar pentru etichetă.</td></tr>
<tr><td><b>CUANTIC experimental</b><br><small>patch de cod pentru ticket/chunk</small></td>
<td>{patched} <a href="{source('ENGINE-STRICT-RESULT.md')}">Toate cele 6 probe →</a></td>
<td><b>Nu îl instala</b>: o pornire rapidă nu repară regresiile sau egalitățile la celelalte măsuri.</td></tr>
<tr><td><b>Arclight</b></td><td>{arclight} <a href="{source('ENGINE-FAMILY-RESULT.md')}">Proba →</a></td>
<td>Nu este înlocuitor pentru <b>acest</b> pack intact; cu alt pack ar putea funcționa.</td></tr>
<tr><td><b>Mist</b></td><td>{mist} <a href="{source('ENGINE-MIST-J11-RESULT.md')}">Proba →</a></td>
<td>Nu pentru combinația testată; nu îi inventăm TPS.</td></tr>
<tr><td><b>Paper / Forge simplu</b></td><td>Nu au aceeași combinație de moduri Forge și pluginuri Bukkit în acest test.</td>
<td>Alt tip de server: poate fi potrivit dacă <b>renunți</b> la o parte din joc; nu este o victorie A/B asupra pack-ului nostru.</td></tr>
<tr><td><b>Mohist / Magma / altele</b></td><td>Nu au fost testate identic în această rundă.</td>
<td><b>Necunoscut</b>, nu „mai lente”. Este nevoie de aceeași versiune, pack și scenariu.</td></tr>
</table></div>
<div class="note"><b>Cum citești cifrele de mai jos:</b> RAM RSS = memoria întregului proces server (MiB);
CPU = cât procesor a consumat în aceeași fereastră de test; p95 MSPT = durata sub care s-au încadrat
95% dintre tick-urile măsurate (mai mic e bine). Boot extern = din momentul lansării Java până la
mesajul <code>Done</code>, <b>nu</b> până la loginul jucătorului. Niciuna nu este FPS-ul clientului.</div>
<h3 style="margin-top:25px">De ce să alegi CUANTIC, atunci?</h3>
<div class="table-scroll"><table class="tbl">
<tr><th>Îți trebuie...</th><th>Ce primești azi</th><th>Ce NU promitem</th></tr>
<tr><td>RP modat fără a reconstrui singur pack-ul</td><td>Client Forge 1.16.5 și serverul cu 36 moduri + 14 pluginuri, testate la pornire; <a href="{PACK_URL}">arhiva completă →</a></td><td>Compatibilitate universală cu orice alt mod sau laptop.</td></tr>
<tr><td>Configurare simplă</td><td>Clientul are adresa salvată și reglaje grafice incluse; memoria JVM se setează manual în launcher după ghid. Serverul are configurația pack-ului. <a href="#cum-intri">Pașii de instalare →</a></td><td>Loginul cu toate modurile, vehiculele și FPS-ul pe un PC slab nu sunt încă validate într-un test comparativ.</td></tr>
<tr><td>JAR verificabil</td><td>{'JAR-ul descărcabil are același SHA ca binarul live.' if verified else 'JAR-ul descărcabil necesită reverificarea SHA.'} <a href="{source('ENGINE-WINNER-JAR.md')}">Proveniență →</a></td><td>Brandul „CUANTIC” nu reduce de la sine RAM, CPU sau timpul de boot față de CatServer oficial.</td></tr>
<tr><td>O alegere fără cifre umflate</td><td>Publicăm și testele eșuate, inclusiv încercarea cu boți: <a href="{source('ENGINE-FAKEPLAYERS-RESULT.md')}">0/25, nevalidată →</a></td><td>„Zero lag”, 25 jucători testați sau „mai rapid decât orice motor”.</td></tr>
</table></div>
<p class="sub" style="margin-top:12px">În launcher încearcă <b>2560 MB pentru client</b> pe un laptop cu 4 GB RAM
(doar dacă rămâne suficient pentru sistemul de operare) sau <b>4096 MB</b> la 8+ GB.
Nu sunt setate automat și nici FPS garantat; dacă sistemul rămâne fără memorie, ajustăm după probe reale.
Ține shader-ele oprite la început și testează separat OptiFine + modurile normale față de Rubidium/Oculus.
În oraș și cu vehicule, un test pe laptopul tău contează mai mult decât un scor de server fără jucători.</p>
</div>'''


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

    # Never render numbers from a partial run or a different release/pack. Each
    # displayed value is a pair of individual runs, not a hand-picked minimum.
    native = result("ENGINE-NATIVE-RESULT.md")
    native_labels = ("branded-A1", "official-B1", "official-B2", "branded-A2")
    native_ok = (native.get("branded_sha256") == sha and
                 native.get("official_sha256") == "8edea98c597e7af44a45ef9093678c38ca3749d55a71cdff10218c1c6b946fd0" and
                 native.get("pack_sha256") == "fe1e261097d92f26c6653239a7161613e6be54b8e9f82c79739c101ce8aa8a15" and
                 all(native.get(label, {}).get("valid") for label in native_labels))
    if native_ok:
        a = [native[x] for x in ("branded-A1", "branded-A2")]
        b = [native[x] for x in ("official-B1", "official-B2")]
        def pair(items, key, unit, places=1):
            return " / ".join(f'{float(x[key]):.{places}f}'.replace(".", ",") for x in items) + unit
        native_rows = (
            ("RAM RSS în fereastra stabilă (MiB)", "rss_steady_median_mb", " MiB", 1),
            ("CPU proces în 75 s stabile", "cpu_seconds_steady_after_55s", " s", 2),
            ("p95 MSPT, spark 1 min", "spark_tick_min_median_p95_max_ms_1m", " ms", 1),
            ("Boot intern până la Done", "boot_done_s", " s", 3),
            ("Boot extern java → Done", "boot_wall_seconds", " s", 2),
        )
        table = ""
        for title, key, unit, places in native_rows:
            if key == "spark_tick_min_median_p95_max_ms_1m":
                aval = pair([{"p95": x[key][2]} for x in a], "p95", unit, places)
                bval = pair([{"p95": x[key][2]} for x in b], "p95", unit, places)
            else:
                aval, bval = pair(a, key, unit, places), pair(b, key, unit, places)
            table += f'<tr><td>{title}</td><td>{aval}</td><td>{bval}</td></tr>'
        native_panel = (f'<h3 style="margin-top:24px">Diferența reală: CUANTIC vs CatServer oficial</h3>'
                        '<p class="sub">A/B/B/A pe același runner, Java 17 și același pack 36/14; '
                        'fiecare celulă arată <b>ambele porniri</b> ale motorului, nu cel mai mic număr. '
                        '64 chunkuri forțate + 40 zombie, 55 s încălzire și 75 s măsurare, fără jucători.</p>'
                        '<div class="table-scroll"><table class="tbl"><tr><th>Măsură</th><th>CUANTIC A1 / A2</th>'
                        f'<th>Oficial B1 / B2</th></tr>{table}</table></div>'
                        '<p class="sub">Diferența medianelor RSS este ~2 MiB, în timp ce <b>variația '
                        'în interiorul fiecărei variante este 247–290 MiB</b>; p95 median este 1,2 ms '
                        'pentru ambele. Nu se confirmă o economie de 171 MB sau un câștig nativ stabil. '
                        'Timpul intern „Done” nu include tot boot-ul extern. Două probe/motor, fără '
                        'jucători sau vehicule: <b>nu demonstrează FPS ori consum în oraș</b>. '
                        f'<a href="{REPO_DOCS}ENGINE-NATIVE-RESULT.md">Metodă, SHA și valori brute →</a> · '
                        f'<a href="{REPO_DOCS}ENGINE-NATIVE-TECH.md">Tehnologiile analizate →</a></p>')
    else:
        native_panel = (f'<p class="sub" style="margin-top:16px">Comparația cu CatServer oficial '
                        f'nu are încă un rezultat complet verificat. <a href="{REPO_DOCS}ENGINE-OLD-RECORDS.md">'
                        'De ce am retras recordurile istorice →</a></p>')

    strict = result("ENGINE-STRICT-RESULT.md")
    checks = strict.get("screen", {}).get("checks", {})
    strict_labels = ("branded-A1", "official-B1", "patched-C1", "patched-C2", "official-B2", "branded-A2")
    required = ("rss_steady_median_mb", "cpu_steady_s", "p95_ms", "boot_internal_done_s", "boot_wall_s")
    strict_ok = (strict.get("pack_sha256") == "fe1e261097d92f26c6653239a7161613e6be54b8e9f82c79739c101ce8aa8a15" and
                 strict.get("official_sha256") == "8edea98c597e7af44a45ef9093678c38ca3749d55a71cdff10218c1c6b946fd0" and
                 strict.get("candidate_sha256") == "b081735815f53e1118608464c39659b537b10fc74fa96458a4a922b7d1215ee3" and
                 all(strict.get(name, {}).get("valid") for name in strict_labels) and
                 all(key in checks for key in required))
    if strict_ok:
        def tested_pair(metric, arm, decimals):
            return " / ".join(f"{v:.{decimals}f}".replace(".", ",") for v in checks[metric]["samples"][arm])
        rows = ""
        for name, key, decimals, unit in (("CPU stabil", "cpu_steady_s", 2, "s"),
                                           ("p95 MSPT", "p95_ms", 1, "ms"),
                                           ("RAM RSS stabil", "rss_steady_median_mb", 1, "MiB"),
                                           ("Boot intern Done", "boot_internal_done_s", 3, "s"),
                                           ("Boot extern java → Done", "boot_wall_s", 2, "s")):
            c = checks[key]
            rows += (f'<tr><td>{name}</td><td>{tested_pair(key, "branded", decimals)} {unit}</td>'
                     f'<td>{tested_pair(key, "official", decimals)} {unit}</td>'
                     f'<td>{tested_pair(key, "patched", decimals)} {unit}</td>'
                     f'<td>{"Da" if c["pass"] else "<b>NU</b>"}</td></tr>')
        labels = {"rss_steady_median_mb": "RAM RSS", "cpu_steady_s": "CPU stabil",
                  "p95_ms": "p95 MSPT", "boot_internal_done_s": "Done intern",
                  "boot_wall_s": "boot extern"}
        good = ", ".join(labels[k] for k in required if checks[k]["pass"]) or "niciuna"
        bad = ", ".join(labels[k] for k in required if not checks[k]["pass"]) or "niciuna"
        strict_panel = (f'<h3 style="margin-top:24px">Patch REAL în JAR — verdict: '
                        f'{"doar pre-calificare sintetică" if strict["screen"]["synthetic_screen_pass"] else "RESPINS la pragul strict"}</h3>'
                        '<p class="sub">JAR recompilat cu optimizare în <code>SortedArraySet.removeIf</code> '
                        '(nu branding); 6 porniri pe aceeași mașină: live/oficial/patch/patch/oficial/live. '
                        'Pragul tău: cea mai slabă probă patch trebuie să fie strict mai bună decât cea mai '
                        'bună probă din ambele baseline-uri, pe FIECARE măsură.</p>'
                        '<div class="table-scroll"><table class="tbl"><tr><th>Indicator</th><th>Live 1/2</th>'
                        f'<th>Oficial 1/2</th><th>Patch 1/2</th><th>Trece?</th></tr>{rows}</table></div>'
                        f'<p class="sub">În această rundă, trec: {good}; <b>nu trec: {bad}</b>. '
                        'Un rezultat favorabil din runda anterioară la CPU/p95 s-a inversat la repetare; '
                        'diferențele mici nu sunt un avantaj stabil demonstrat. '
                        'Boot-ul extern este măsurat cu verificări la ~'
                        f'{strict["patched-C1"].get("boot_wall_poll_interval_seconds", 2)} secunde, nu un cronometru perfect. '
                        'Doar 2 probe/motor, fără jucători și vehicule. <b>Nu am lansat JAR-ul.</b> '
                        f'<a href="{REPO_DOCS}ENGINE-STRICT-RESULT.md">Toate probele, SHA și limitele →</a></p>')
    else:
        strict_panel = ''

    fake = result("ENGINE-FAKEPLAYERS-RESULT.md")
    fake_provenance = (fake.get("pack_sha256") == "fe1e261097d92f26c6653239a7161613e6be54b8e9f82c79739c101ce8aa8a15" and
                       fake.get("curtain_sha256") == "c9234d2c5ca43c337abac25a05022fe2f226c884855aa6941b6130c60777819d" and
                       fake.get("production_changes") is False)
    if fake_provenance:
        reported_count = fake.get("local_status", {}).get("players", {}).get("online")
        three_valid = (fake.get("valid") and fake.get("list_count", 0) >= 3 and
                       reported_count is not None and reported_count >= 3)
        fake_panel = (f'<div class="card" style="margin-top:16px"><h3>Test cu jucători simulați '
                      f'— {"trece doar proba izolată" if three_valid else "NU validat încă"}</h3>'
                      '<p>Într-o copie temporară a pack-ului am încercat trei jucători falși cu '
                      'Curtain 1.16.5. Modul de test necesită dezactivarea unui mixin incompatibil '
                      'cu CatServer; JAR-ul live și modpack-ul public rămân intacte. '
                      + ('Au rămas trei jucători în <code>list</code> și status local.' if three_valid else
                         f'Au apărut încercări de login în log, dar <code>list</code> și status local au rămas '
                         f'la <b>{escape(str(reported_count) if reported_count is not None else "necunoscut")}/25</b>: nu numărăm boți inexistenți drept test reușit.') +
                      ' Chiar și o probă reușită cu jucători falși nu testează handshake-ul clientului '
                      'modat, vehiculele sau FPS-ul. '
                      f'<a href="{REPO_DOCS}ENGINE-FAKEPLAYERS-RESULT.md">Loguri și limite →</a></p></div>')
    else:
        fake_panel = ''

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

    quick_choice = chooser_panel(
        verified, native_ok, strict_ok,
        bool(arclight.get("smoke") and not arclight.get("qualified_for_performance_A_B")),
        bool(mist.get("smoke") and not mist.get("qualified_for_performance_A_B")),
    )
    return f'''<section id="engine-test" aria-label="Benchmark al motorului CUANTIC">
{quick_choice}
<div class="note"><b>12 octombrie · audit de performanță:</b> release-ul public verificat prin SHA conține deja 36 moduri, 14 pluginuri și optimizări precum ModernFix, FerriteCore și RoadRunner. Nu adăugăm duplicat și nu instalăm un JAR nou fără câștig strict, test de login modat și vehicule. Recuperarea gazdei live se verifică separat; un job în coadă nu înseamnă server pornit. <a href="{REPO_DOCS}ENGINE-PERFORMANCE-2026-10-12.md">Lista probelor, eșecurilor și pașilor următori →</a> · <a href="{REPO_DOCS}ENGINE-PACK-AUDIT.md">Inventarul release-ului →</a></div>
<h2>🔬 JAR-ul validat și benchmarkul — fără „zero lag” inventat</h2>
<div class="sub">Pentru <b>acest</b> modpack Forge 1.16.5 (36 moduri + 14 pluginuri),
păstrăm motorul CatServer CUANTIC deja folosit pe server. Am construit un JAR cu patch propriu și am
comparat fork-uri în copii izolate pe GitHub; <b>niciunul nu a demonstrat un câștig simultan
CPU + p95 și compatibilitate în joc cu vehicule</b>. Nu schimbăm live-ul pentru un scor fără probe.</div>
<div class="card" style="margin-top:18px;border-color:rgba(95,240,192,.38)">
<h3>JAR-ul de producție: pornește pack-ul, nu e declarat mai rapid</h3>
<p>Compatibilitatea pack-ului a fost verificată în smoke cu 36/14. Alte motoare care nu pornesc cu
același pack nu sunt clasate fictiv ca „mai rapide”.</p>
<div class="cta">{winner_button}<a class="btn ghost" href="{REPO_DOCS}BENCHMARK-MOTOARE-CUANTIC-2026-10-12.md">📊 Vezi benchmarkul integral</a></div>
{winner_note}
</div>
{native_panel}
{strict_panel}
{fake_panel}
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
<p class="sub" style="margin-top:12px">Transparență: <a href="{REPO_DOCS}INCIDENT-2026-10-11-STATUS.md">serverul a fost indisponibil la 22:13 UTC, recuperat și verificat local/public la 22:16 UTC</a>.
Cauza opririi este încă necunoscută; verifică badge-ul datat de sus pentru ultima probă, nu presupune uptime permanent.</p>
</section>'''


FUNCTITY_DOC = ROOT / "analysis" / "FUNCTITY-BENCH.md"
FC_OUT_BENCH = "https://github.com/iZentric/ServerRolePlayLite/tree/functity-out/bench-v4"


def functity_data():
    """Snapshotul masurat FC-BENCH v4 (din analysis/FUNCTITY-BENCH.md), sau {}."""
    try:
        text = FUNCTITY_DOC.read_text(encoding="utf-8")
    except OSError:
        return {}
    m = re.search(r"```json\s*(\{.*?\})\s*```", text, re.S)
    if not m:
        return {}
    try:
        return json.loads(m.group(1))
    except ValueError:
        return {}


def functity_panel():
    d = functity_data()
    if not d or "runde" not in d:
        return ('<section id="functity"><h2>🏗️ FunCity — banca de măsurare a motorului propriu</h2>'
                '<div class="sub">Nicio măsurătoare FC-BENCH încă încărcată; secțiunea se populează '
                'din <code>analysis/FUNCTITY-BENCH.md</code> după prima rulare verde.</div></section>')
    nume = d["brate"]
    rows = []
    for key, label in nume.items():
        a = d["runde"].get("A", {}).get("arms", {}).get(key, {})
        b = d["runde"].get("B", {}).get("arms", {}).get(key, {})
        def med(x):
            v = x.get("done_s") or []
            return round(sum(v) / len(v), 2) if v else None
        ma, mb = med(a), med(b)
        cvs = [x.get("cv") for x in (a, b) if x.get("cv") is not None]
        cv = max(cvs) if cvs else None
        crit = (a.get("critice", 0) or 0) + (b.get("critice", 0) or 0)
        over = (a.get("overrun", 0) or 0) + (b.get("overrun", 0) or 0)
        tps = b.get("tps") if b.get("tps") is not None else a.get("tps")
        rss = b.get("rss_mb")
        rows.append((label, ma, mb, cv, tps, over, crit, rss))
    cat_a = next((r for r in rows if "CatServer" in r[0]), None)
    body = []
    for label, ma, mb, cv, tps, over, crit, rss in rows:
        delta = "referința"
        if mb and cat_a and cat_a[2] and "CatServer" not in label:
            delta = f"{(mb - cat_a[2]) / cat_a[2] * 100:+.0f}% vs CatServer"
        body.append(
            "<tr><td><b>" + label + "</b></td>"
            + "<td>" + (f"{ma:.2f} s" if ma else "NEMĂSURAT") + "</td>"
            + "<td>" + (f"{mb:.2f} s" if mb else "NEMĂSURAT") + "</td>"
            + "<td>" + delta + "</td>"
            + "<td>" + (f"{cv:.1f}%" if cv is not None else "—") + "</td>"
            + "<td>" + (f"{tps:.1f}" if tps is not None else "NEMĂSURAT") + "</td>"
            + "<td>" + str(over) + " / " + str(crit) + "</td>"
            + "<td>" + (f"{rss:.0f} MB" if rss else "—") + "</td></tr>")
    pr = d.get("praguri", {})
    prag_rows = "".join("<li><b>" + k + "</b>: " + v + "</li>" for k, v in pr.items())
    lim_rows = "".join("<li>" + x + "</li>" for x in d.get("limite", []))
    return f'''<section id="functity" aria-label="Banca de măsurare FunCity (motor propriu pe bază Mohist)">
<h2>🏗️ FunCity — motorul propriu, măsurat, nu promis</h2>
<div class="sub">{d.get("metoda", "")} · probe {d.get("data", "")}. Timpul comparat e <b>„Done (x.xs)” auto-măsurat de motor</b>
(fără zgomotul de runner partajat din timpii wall); CV = variația între probe.</div>
<div class="table-scroll"><table class="tbl">
<tr><th>Motor (așa cum rulează pack-ul 36/14)</th><th>Boot runda A</th><th>Boot runda B</th><th>Δ față de motorul istoric</th><th>CV max</th><th>TPS idle</th><th>Overrun / critice (6 probe)</th><th>RSS mediu</th></tr>
{chr(10).join(body)}
</table></div>
<div class="card" style="margin-top:14px"><h3>Praguri bătute în cuie ÎNAINTE de rulare</h3><ul style="margin:6px 0 0 20px">{prag_rows}</ul>
<p style="margin-top:10px"><b>Latenta de join cu client modat: NEMĂSURAT încă</b> — proba vanilla a fost respinsă
corect de FML pe toate cele 4 motoare (mesaj „Forge client required”); bot-ul cu pack complet vine în runda următoare.
<b>Pauze GC: NEMĂSURAT</b> în această rundă — parserul nu a recunoscut formatul, nu inventăm 0.</p></div>
<div class="note"><b>Ce înseamnă:</b> FunCity pornește identical cu Mohist oficial (la nivel de zgomot, fără regresie
și fără câștig declarabil) și nu are erori critice pe niciun boot; în plus, ambele motoare Mohist-family termină
boot-ul mai repede decât motorul istoric CatServer pe aceeași sarcină. <b>Ce NU înseamnă:</b> un titlu de „cel mai rapid”
— nu măsurăm gameplay, nu atingem serverul live, și runner-ul CI nu e gazda de 2 vCPU a jucătorilor.</div>
<details><summary>Ce nu acoperă banca (ca să nu iasă surprize)</summary><ul style="margin:6px 0 0 20px">{lim_rows}</ul></details>
<p class="sub" style="margin-top:10px">Rapoarte brute: <a href="{FC_OUT_BENCH}">functity-out/bench-v4</a> ·
sursa cifrelor: <code>analysis/FUNCTITY-BENCH.md</code> · alergări CI A/B cuantificate în document.</p>
</section>'''
