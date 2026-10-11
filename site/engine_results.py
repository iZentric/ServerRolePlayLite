"""Display measured engine comparisons, never a claimed winner from a single sample."""
from datetime import datetime, timezone
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
REPO_DOCS = "https://github.com/iZentric/ServerRolePlayLite/blob/arena/a29b4ef4-serverroleplaylite/docs/"


def result(name):
    try:
        text = (DOCS / name).read_text(encoding="utf-8")
        return json.loads(re.search(r"```json\s*(\{.*?\})\s*```", text, re.S).group(1))
    except (OSError, AttributeError, ValueError):
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


def panel():
    ci = result("ENGINE-AB-GITHUB.md")
    host = result("ENGINE-AB-HOST.md")
    filled = result("ENGINE-CURRENT-RESULT.md").get("summary", {})
    empty = result("ENGINE-EMPTY-RESULT.md").get("summary", {})
    old, new = ci.get("baseline-2023", {}), ci.get("candidate-2024", {})
    if not old.get("valid") or not new.get("valid"):
        row = '<tr><td colspan="3">Comparația CI lipsește sau nu a trecut verificările.</td></tr>'
    else:
        def fmt(d):
            p95 = d.get("spark_tick_min_median_p95_max_ms_1m") or []
            try:
                return (f'{float(p95[2]):.1f} ms p95 · '
                        f'{float(d["rss_median_mb"]):.1f} MiB RSS · '
                        f'{int(d["plugins_enabled"])} pluginuri')
            except (IndexError, TypeError, ValueError, KeyError):
                return "valori lipsă"
        row = (f'<tr><td>JAR public actual (CatServer 2023)</td><td>{fmt(old)}</td><td>Referință</td></tr>'
               f'<tr><td>Candidat upstream (nepublicat)</td><td>{fmt(new)}</td>'
               '<td>Nu a redus p95 în proba unică</td></tr>')
    host_note = ("Gazda reală: comparația A/B s-a oprit înainte de testul candidatului; "
                 "nu există verdict de performanță pe gazdă."
                 if host.get("status", "").startswith("ABORTED")
                 else "Gazda reală: rezultat neconfirmat; citește raportul înainte de concluzii.")
    def fork_row(title, values):
        try:
            a, b = values["live"], values["patched"]
            return (f'<tr><td>{title} (2×/motor)</td>'
                    f'<td>p95 {a["p95_ms_median_of_2"]} → {b["p95_ms_median_of_2"]} ms; '
                    f'CPU {a["cpu_seconds_workload_median_of_2"]} → {b["cpu_seconds_workload_median_of_2"]} s</td>'
                    '<td>Nu a câștigat; doar artifact experimental</td></tr>')
        except (KeyError, TypeError):
            return ''
    fork_rows = fork_row("Fork din codul live: hoppers plini", filled) + fork_row("Fork din codul live: hoppers goale", empty)
    return f'''<section id="engine-test" aria-label="Probe comparative ale motorului">
<h2>🔬 Motorul: ce am măsurat, ce păstrăm</h2>
<div class="sub"><b>Decizie: JAR-ul public rămâne neschimbat.</b> Am compilat și testat fork-uri reale
pe codul CatServer, nu doar un nume nou. Toate au pornit cu 36 moduri și 14 pluginuri, dar niciunul
nu a câștigat împotriva JAR-ului actual în A/B. O probă sintetică, fără jucători, nu stabilește
cel mai rapid JAR din 2026 și nu validează autentificarea unui client modat.</div>
<table class="tbl"><tr><th>Motor/scenariu</th><th>GitHub, același runner, fără jucători</th><th>Decizie</th></tr>{row}{fork_rows}</table>
<div class="note">{host_note} Ultima probă a JAR-ului public a confirmat status Minecraft <b>local</b>
(protocol 754, 0/25 jucători); nu dovedește accesul extern sau FPS pe laptopuri slabe.</div>
<p class="sub" style="margin-top:12px">Date și limite: <a href="{REPO_DOCS}ENGINE-DECISION.md">verdict complet</a> ·
<a href="{REPO_DOCS}ENGINE-AB-GITHUB.md">A/B GitHub</a> ·
<a href="{REPO_DOCS}ENGINE-AB-HOST.md">gazda reală</a> ·
<a href="{REPO_DOCS}ENGINE-FORK-STATUS.md">fork-uri sursă și probe</a> ·
<a href="{REPO_DOCS}ENGINE-PREFLIGHT.md">preflight live</a>.
OptiFine + modurile normale și Rubidium/Oculus se testează separat cu jucători și vehicule.</p>
</section>'''
