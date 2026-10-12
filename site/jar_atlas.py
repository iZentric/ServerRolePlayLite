"""Render the researched JAR atlas as an accessible, searchable site table.

The committed Markdown atlas is the source of truth. Do not infer a winner from
unmeasured rows or link to a branch-only document that is not public yet.
"""
from html import escape
from pathlib import Path
import re

ATLAS = Path(__file__).resolve().parent.parent / "docs/CUANTIC-JAR-ATLAS-2026-10-12.md"
DOC_URL = "https://github.com/iZentric/ServerRolePlayLite/blob/arena/a29b4ef4-serverroleplaylite/docs/"


def rows(text, start, end, columns):
    chunk = text.split(start, 1)[1].split(end, 1)[0]
    found = []
    for line in chunk.splitlines():
        if not line.startswith("| "):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) == columns and not cells[0].startswith(("---", "JAR/familie")):
            found.append(cells)
    return found


def inline(text):
    """Render only the tiny documented Markdown subset; escape everything else."""
    clean = escape(text)

    def link(match):
        label, url = match.groups()
        if re.fullmatch(r"https://[^\s<>]+", url):
            href = url
        elif re.fullmatch(r"[A-Za-z0-9_-]+\.md", url):
            href = DOC_URL + url
        else:
            return match.group(0)
        return f'<a href="{href}" target="_blank" rel="noopener noreferrer">{label}<span class="atlas-external" aria-hidden="true"> ↗</span></a>'

    clean = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", link, clean)
    clean = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", clean)
    clean = re.sub(r"`([^`]+)`", r"<code>\1</code>", clean)
    return clean


def _status(name):
    if name.startswith(("**CUANTIC live**", "**CatServer oficial**")):
        return "Confirmat la pornire", "confirmed"
    if name.startswith("**CUANTIC patch"):
        return "Testat · respins", "rejected"
    if name.startswith(("**Arclight Forge**", "**Mist**")):
        return "Nu pornește cu 36/14", "failed"
    return "De testat cu 36/14", "pending"


def panel():
    try:
        text = ATLAS.read_text(encoding="utf-8")
        hybrids = rows(text, "## A. Duel echivalent posibil", "## B. Celelalte JAR-uri", 4)
        alternatives = rows(text, "## B. Celelalte JAR-uri", "## Ce înseamnă 10×", 3)
    except (OSError, IndexError):
        return '<section id="atlas"><h2>Atlasul JAR-urilor nu este disponibil</h2></section>'
    if len(hybrids) < 7 or len(alternatives) < 20:
        raise ValueError("Atlas incomplete: do not silently present a partial comparison")
    tr = []
    for name, history, evidence, decision in hybrids:
        status, category = _status(name)
        tr.append(f'''<tr data-atlas-row data-kind="same" data-status="{category}">
<td class="atlas-name">{inline(name)}<small>{inline(history)}</small></td>
<td><span class="atlas-badge {category}">{status}</span></td>
<td>{inline(evidence)}</td><td>{inline(decision)}</td></tr>''')
    for name, context, reason in alternatives:
        tr.append(f'''<tr data-atlas-row data-kind="other" data-status="other">
<td class="atlas-name">{inline(name)}</td>
<td><span class="atlas-badge other">Alt ecosistem / control</span></td>
<td>{inline(context)}</td><td>{inline(reason)}</td></tr>''')
    total = len(tr)
    return f'''<section id="atlas" class="atlas-section" aria-labelledby="atlas-title">
<div class="atlas-overline"><span class="atlas-orbit" aria-hidden="true">◉</span> LABORATORUL CUANTIC <span class="atlas-overline-rule"></span> 12 OCT 2026</div>
<h2 id="atlas-title">Toate motoarele pe masă.<br><span>Doar probele decid.</span></h2>
<p class="atlas-lead">{total} de familii și JAR-uri cercetate. Primele {len(hybrids)} pot fi evaluate pentru pack-ul Forge 1.16.5; restul cer alt loader, alte pluginuri sau alt joc. Caută un motor, apoi citește verdictul și sursa din fiecare rând.</p>
<div class="atlas-stats" aria-label="Rezumatul probelor">
<div class="atlas-stat"><span class="atlas-stat-icon">◈</span><b>{total}</b><span>JAR-uri &amp; familii<br>în atlasul cercetat</span></div>
<div class="atlas-stat"><span class="atlas-stat-icon">▣</span><b>36 + 14</b><span>moduri Forge + pluginuri<br>de păstrat împreună</span></div>
<div class="atlas-stat"><span class="atlas-stat-icon">↗</span><b>0</b><span>probe care confirmă 10×<br>până acum</span></div>
</div>
<div class="atlas-toolbar" aria-label="Filtre pentru tabel">
<div class="atlas-tabs" role="group" aria-label="Tip de motor">
<button type="button" data-atlas-filter="all" aria-pressed="true">Toate <span>{total}</span></button>
<button type="button" data-atlas-filter="same" aria-pressed="false">Forge + Bukkit <span>{len(hybrids)}</span></button>
<button type="button" data-atlas-filter="other" aria-pressed="false">Alte motoare <span>{len(alternatives)}</span></button>
</div>
<label class="atlas-search"><span aria-hidden="true">⌕</span><span class="sr-only">Caută în tabel</span><input id="atlas-query" type="search" autocomplete="off" placeholder="Caută JAR / verdict / sursă…"></label>
</div>
<p class="atlas-result" id="atlas-count" role="status" aria-live="polite">Se afișează {total} din {total} rânduri</p>
<div class="atlas-scroll" tabindex="0" role="region" aria-label="Tabel comparativ al JAR-urilor; derulează orizontal pe ecran mic">
<table class="atlas-table"><caption>Atlasul JAR-urilor CUANTIC, pe baza probelor disponibile la 12 octombrie 2026</caption>
<thead><tr><th scope="col">Motor / proveniență</th><th scope="col">Stare</th><th scope="col">Ce știm</th><th scope="col">Decizia pentru Cuantic</th></tr></thead>
<tbody>{''.join(tr)}</tbody></table></div>
<div class="atlas-bottom"><div><span class="atlas-bottom-mark">10×</span><div><strong>Ținta. Nu rezultatul.</strong><p>10× mai mulți jucători activi per resursă ar necesita clienți Forge confirmați, același pack și aceeași sarcină în repetări. Azi nu există această dovadă. Un JAR care nu pornește nu este un adversar „învins”.</p></div></div><a href="#engine-test">Vezi benchmarkul măsurat ↑</a></div>
</section>'''


STYLE = r'''
/* The atlas is deliberately separate from the historic benchmark table. */
.atlas-section{margin:72px 0 65px;padding:36px 28px 28px;background:radial-gradient(circle at 92% 3%,rgba(91,160,255,.13),transparent 36%),radial-gradient(circle at 5% 40%,rgba(95,240,192,.07),transparent 40%),#0b1321;border:1px solid rgba(130,168,211,.25);border-radius:24px;box-shadow:0 28px 90px rgba(0,0,0,.27);position:relative;overflow:hidden}
.atlas-section:before{content:"";height:2px;position:absolute;left:0;right:0;top:0;background:linear-gradient(90deg,#5ff0c0,#7fb0ff,#b79cff)}
.atlas-overline{display:flex;align-items:center;gap:10px;color:#a3c9e5;letter-spacing:.16em;font-weight:800;font-size:11px}.atlas-orbit{font-size:20px;color:#5ff0c0}.atlas-overline-rule{height:1px;background:rgba(163,201,229,.27);width:34px}
.atlas-section h2{font-size:clamp(32px,5vw,54px);line-height:1.08;letter-spacing:-.04em;margin:17px 0}.atlas-section h2 span{color:#5ff0c0}.atlas-lead{max-width:840px;line-height:1.7;color:#adbed5;font-size:15px}
.atlas-stats{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px;margin:28px 0 26px}.atlas-stat{border:1px solid rgba(134,170,211,.19);background:rgba(255,255,255,.035);border-radius:15px;padding:18px 18px 18px 54px;position:relative;min-height:98px}.atlas-stat b{font-size:28px;display:block;line-height:1.18;color:#f5fbff;letter-spacing:-.03em}.atlas-stat>span:last-child{display:block;color:#a5b7d0;font-size:12px;line-height:1.45;margin-top:4px}.atlas-stat-icon{position:absolute;left:20px;top:21px;color:#67debe;font-size:20px}
.atlas-toolbar{display:flex;align-items:center;justify-content:space-between;gap:14px;flex-wrap:wrap}.atlas-tabs{display:flex;gap:5px;padding:4px;border:1px solid rgba(139,169,206,.18);border-radius:12px;background:#111c2d}.atlas-tabs button{background:transparent;color:#9db0c9;border:0;border-radius:8px;padding:9px 12px;cursor:pointer;font:inherit;font-size:13px;font-weight:700;white-space:nowrap}.atlas-tabs button span{opacity:.65;font-size:11px;margin-left:4px}.atlas-tabs button[aria-pressed="true"]{background:#233b50;color:#c8ffee;box-shadow:0 1px 5px rgba(0,0,0,.24)}.atlas-tabs button:focus-visible,.atlas-search input:focus-visible,.atlas-scroll:focus-visible{outline:2px solid #5ff0c0;outline-offset:2px}
.atlas-search{display:flex;align-items:center;gap:7px;background:#101c2d;border:1px solid rgba(139,169,206,.3);border-radius:10px;padding:0 12px;color:#8fa6c3;flex:1;max-width:330px;min-width:200px}.atlas-search>span:first-child{font-size:24px}.atlas-search input{width:100%;padding:11px 0;background:transparent;border:0;outline:0;color:#f2f8ff;font:inherit;font-size:13px}.atlas-search input::placeholder{color:#8294ad}.atlas-result{font-size:12px;color:#9bb0c8;margin:15px 0 9px}.atlas-scroll{overflow-x:auto;border:1px solid rgba(140,171,210,.2);border-radius:13px;max-height:740px;overflow-y:auto}.atlas-table{width:100%;min-width:790px;border-collapse:separate;border-spacing:0;font-size:13px;line-height:1.55}.atlas-table caption{position:absolute;width:1px;height:1px;padding:0;margin:-1px;overflow:hidden;clip:rect(0,0,0,0);white-space:nowrap;border:0}.atlas-table th{text-align:left;position:sticky;top:0;background:#1b2d40;color:#b7cce1;z-index:2;font-size:11px;letter-spacing:.075em;text-transform:uppercase;padding:14px 15px}.atlas-table th:nth-child(1){width:22%}.atlas-table th:nth-child(2){width:16%}.atlas-table th:nth-child(3){width:29%}.atlas-table td{padding:15px;vertical-align:top;border-top:1px solid rgba(155,180,211,.12);color:#afc0d4;background:rgba(15,26,42,.8)}.atlas-table tr:nth-child(2n) td{background:rgba(21,35,53,.85)}.atlas-table tr:hover td{background:#20344c}.atlas-table td strong{color:#f0f7ff}.atlas-table td:first-child strong{font-size:14px}.atlas-table td small{display:block;margin-top:6px;color:#8ba7c2;font-size:11px}.atlas-table a{color:#81dbd0;text-underline-offset:3px}.atlas-external{font-size:10px;opacity:.8}.atlas-table code{color:#d1c5ff;background:rgba(165,145,240,.1);padding:1px 3px;border-radius:3px;font-size:11px;white-space:normal;overflow-wrap:anywhere}.atlas-badge{display:inline-block;border-radius:30px;padding:5px 9px;font-size:11px;font-weight:750;white-space:nowrap}.atlas-badge.confirmed{background:rgba(95,240,192,.13);color:#8af5ce}.atlas-badge.failed,.atlas-badge.rejected{background:rgba(255,144,147,.12);color:#ffb8b8}.atlas-badge.pending{background:rgba(246,199,106,.12);color:#f6d69e}.atlas-badge.other{background:rgba(140,166,207,.13);color:#bdcce7}
.atlas-bottom{display:flex;justify-content:space-between;gap:20px;align-items:center;margin-top:19px;padding:20px;border:1px solid rgba(95,240,192,.22);border-radius:14px;background:linear-gradient(100deg,rgba(95,240,192,.08),rgba(127,176,255,.06))}.atlas-bottom>div{display:flex;align-items:center;gap:16px}.atlas-bottom-mark{font-size:25px;font-weight:900;letter-spacing:-.07em;color:#5ff0c0}.atlas-bottom strong{color:#edfff8}.atlas-bottom p{color:#a7bbd0;font-size:12px;line-height:1.5;margin:4px 0 0;max-width:650px}.atlas-bottom>a{font-size:12px;color:#76dfcc;white-space:nowrap}
.sr-only{position:absolute;width:1px;height:1px;padding:0;margin:-1px;overflow:hidden;clip:rect(0,0,0,0);white-space:nowrap;border:0}
@media(max-width:740px){.atlas-section{padding:26px 14px;margin:52px 0}.atlas-stats{grid-template-columns:1fr 1fr}.atlas-stat:last-child{grid-column:1/-1}.atlas-tabs{max-width:100%;overflow-x:auto}.atlas-tabs button{padding:8px 9px}.atlas-search{max-width:none}.atlas-bottom{align-items:flex-start;flex-direction:column}.atlas-table{min-width:700px}}
'''

SCRIPT = r'''<script>
(() => {
  const root = document.getElementById('atlas');
  if (!root) return;
  const tabs = [...root.querySelectorAll('[data-atlas-filter]')];
  const rows = [...root.querySelectorAll('[data-atlas-row]')];
  const input = root.querySelector('#atlas-query');
  const count = root.querySelector('#atlas-count');
  let selected = 'all';
  function update() {
    const query = input.value.trim().toLocaleLowerCase('ro');
    let shown = 0;
    for (const row of rows) {
      row.hidden = (selected !== 'all' && row.dataset.kind !== selected) ||
                   (query && !row.textContent.toLocaleLowerCase('ro').includes(query));
      if (!row.hidden) shown++;
    }
    count.textContent = `Se afișează ${shown} din ${rows.length} rânduri`;
  }
  tabs.forEach(button => button.addEventListener('click', () => {
    selected = button.dataset.atlasFilter;
    tabs.forEach(tab => tab.setAttribute('aria-pressed', String(tab === button)));
    update();
  }));
  input.addEventListener('input', update);
})();
</script>'''
