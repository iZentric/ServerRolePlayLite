"""Derive an evidence tier list for hybrid Forge+Bukkit JARs from committed proof.

The committed atlas (`docs/CUANTIC-JAR-ATLAS-2026-10-12.md`) and the raw A/B
report (`docs/ENGINE-NATIVE-RESULT.md`) are the only sources. Nothing here may
invent a TPS/RAM figure, promote an unmeasured JAR into a measured tier, or
declare a performance winner.

Tiers rank EVIDENCE, not speed: a JAR reaches tier S only because it was
actually booted with 36 mods and 14 plugins, not because it is fast. The same
minimum-trial rule used by `scripts/cuantic_tenx_gate.py` decides whether a
measured difference may be called a verdict at all.
"""
from pathlib import Path
import re

from jar_atlas import ATLAS, inline, rows

NATIVE = ATLAS.parent / "ENGINE-NATIVE-RESULT.md"

# Same threshold the claim gate uses: fewer than three repeated real trials per
# arm cannot produce a verdict, only a measurement.
MIN_TRIALS = 3

# category (from jar_atlas._status) -> tier letter
TIER_OF = {
    "confirmed": "S",
    "rejected": "A",
    "failed": "B",
    "pending": "C",
    "other": "D",
}

TIERS = (
    ("S", "Măsurat · pornește cu 36 moduri + 14 pluginuri",
     "Singurii candidați care pot fi comparați între ei. Asta înseamnă că au pornit "
     "cu pack-ul intact, nu că sunt rapizi."),
    ("A", "Măsurat · respins la pragul strict",
     "A intrat în bancul de probe și a pierdut: nu a trecut simultan CPU, p95, RSS și boot."),
    ("B", "Măsurat · nu pornește cu pack-ul nostru",
     "„Nu pornește” nu înseamnă „mai lent”. Înseamnă incompatibil, deci fără scor comparabil."),
    ("C", "Sursă verificabilă · nemăsurat cu 36/14",
     "Există release sau sursă pentru versiunea corectă, dar nu avem smoke pe pack-ul exact. "
     "Fără punctaj până la o probă reală."),
    ("D", "Alt ecosistem · nu adversar echivalent",
     "Alt loader, alt API de pluginuri sau altă versiune. Nu le numărăm ca motoare învinse; "
     "ar cere portarea modurilor, a pluginurilor sau a clientului."),
)

MEASURES = (
    ("RSS stabil", "RAM RSS în fereastra stabilă", "MiB",
     "Consumul de memorie cerut. Cea mai mică valoare nu este automat câștigătoare."),
    ("CPU pe fereastra stabilă", "CPU proces în fereastra stabilă", "s",
     "Timp CPU consumat pe aceeași sarcină sintetică."),
    ("p95 MSPT", "p95 MSPT, spark 1 minut", "ms",
     "Bugetul de tick. Sub 50 ms jocul este fluent; aici ambele sunt departe de limită."),
    ("Done` intern", "Boot intern până la `Done`", "s",
     "Nu include toată inițializarea observată din afara procesului."),
    ("Timp extern pornire", "Boot extern java → `Done`", "s",
     "Măsurat cu verificări la ~0,25 s, nu cu un cronometru perfect."),
)


def _pairs(cell):
    """'2205,1 / 2452,0' -> (2205.1, 2452.0). Romanian decimal comma included."""
    values = []
    for part in cell.split("/"):
        token = part.strip().replace(",", ".")
        if re.fullmatch(r"\d+(\.\d+)?", token):
            values.append(float(token))
    return tuple(values)


def measured():
    """Read the raw A/B table. Returns [] rather than guessing if it is missing."""
    try:
        text = NATIVE.read_text(encoding="utf-8")
    except OSError:
        return []
    table = {}
    for line in text.splitlines():
        if not line.startswith("| "):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) != 3:
            continue
        cuantic, official = _pairs(cells[1]), _pairs(cells[2])
        if cuantic and official:
            table[cells[0]] = (cells[1], cells[2], cuantic, official)
    found = []
    for needle, label, unit, note in MEASURES:
        for key, (raw_a, raw_b, cuantic, official) in table.items():
            if needle in key:
                # Raw cells are displayed verbatim so the page can never drift
                # from the committed report through float re-formatting.
                found.append({"label": label, "unit": unit, "note": note,
                              "cuantic_raw": raw_a, "official_raw": raw_b,
                              "cuantic": cuantic, "official": official})
                break
    return found


def verdict(entry):
    """Never a winner: mirror the claim gate's own minimum-trial rule."""
    trials = min(len(entry["cuantic"]), len(entry["official"]))
    if trials < MIN_TRIALS:
        return (f"NECONCLUDENT · {trials} probe/braț",
                f"Poarta cere minimum {MIN_TRIALS} repetări reale pe braț, iar diferența este "
                "mai mică decât variația din interiorul aceleiași variante.")
    # Same ceiling as cuantic_tenx_gate.py: valid data yields at most a
    # preliminary verdict, never automatic proof.
    return ("PRELIMINAR · nu dovadă",
            "Logurile trebuie inspectate independent înainte de orice afirmație publică.")


def classify(text):
    """Split the atlas into tiers using the atlas' own evidence categories."""
    try:
        hybrids = rows(text, "## A. Duel echivalent posibil", "## B. Celelalte JAR-uri", 4)
        alternatives = rows(text, "## B. Celelalte JAR-uri", "## Ce înseamnă 10×", 3)
    except IndexError:
        raise ValueError("Atlas sections missing: refusing to publish a partial tier list") from None
    if len(hybrids) < 7 or len(alternatives) < 20:
        raise ValueError("Atlas incomplete: refusing to publish a partial tier list")
    from jar_atlas import _status  # local import: private helper, same package
    buckets = {letter: [] for letter, _, _ in TIERS}
    for name, history, evidence, decision in hybrids:
        _, category = _status(name)
        buckets[TIER_OF[category]].append(
            {"name": name, "detail": history, "evidence": evidence, "decision": decision})
    for name, context, reason in alternatives:
        buckets["D"].append({"name": name, "detail": "", "evidence": context,
                             "decision": reason})
    return buckets, len(hybrids), len(alternatives)


def _tier_block(letter, title, blurb, entries):
    cards = []
    for entry in entries:
        detail = f"<small>{inline(entry['detail'])}</small>" if entry["detail"] else ""
        cards.append(
            f'<li class="tier-card" data-tier-row data-tier="{letter}">'
            f'<div class="tier-card-head"><strong>{inline(entry["name"])}</strong>'
            f'<span class="tier-chip" aria-hidden="true">{letter}</span></div>'
            f"{detail}"
            f'<p class="tier-know">{inline(entry["evidence"])}</p>'
            f'<p class="tier-decide">{inline(entry["decision"])}</p></li>')
    return (f'<div class="tier-band" data-tier-band="{letter}">'
            f'<div class="tier-band-label" aria-hidden="true">{letter}</div>'
            f'<div class="tier-band-body"><h3>{title} <span>{len(entries)}</span></h3>'
            f'<p class="tier-blurb">{blurb}</p>'
            f'<ul class="tier-cards">{"".join(cards)}</ul></div></div>')


def _ro(value, decimals=2):
    """Romanian decimal comma, fixed precision so medians stay comparable."""
    return f"{value:.{decimals}f}".replace(".", ",")


def _consumption_block(entries):
    if not entries:
        return ('<p class="tier-note">Raportul brut de consum nu este disponibil; '
                "niciun număr nu este afișat în lipsa lui.</p>")
    tr = []
    for entry in entries:
        median_a = sum(entry["cuantic"]) / len(entry["cuantic"])
        median_b = sum(entry["official"]) / len(entry["official"])
        label, rationale = verdict(entry)
        tr.append(f'<tr><th scope="row">{entry["label"]} <span class="tier-unit">'
                  f'{entry["unit"]}</span><small>{entry["note"]}</small></th>'
                  f'<td>{entry["cuantic_raw"]}</td><td>{entry["official_raw"]}</td>'
                  f'<td>{_ro(median_a)} vs {_ro(median_b)}</td>'
                  f'<td><span class="tier-verdict">{label}</span>'
                  f"<small>{rationale}</small></td></tr>")
    return ('<div class="tier-consum"><h3>Consum și performanță — singurele numere reale</h3>'
            '<p class="tier-lead">Două repetări pe braț, pack identic 36/14, Java 17, '
            "64 chunkuri forțate + 40 zombies, 55 s încălzire + 75 s stabil, "
            "<b>fără jucători și fără vehicule</b>. Fiecare celulă arată ambele porniri, "
            "nu cel mai mic număr.</p>"
            '<div class="tier-scroll" tabindex="0" role="region" '
            'aria-label="Tabel cu consumul măsurat; derulează orizontal pe ecran mic">'
            '<table class="tier-table"><thead><tr><th scope="col">Măsură</th>'
            '<th scope="col">CUANTIC live A1 / A2</th><th scope="col">CatServer oficial B1 / B2</th>'
            '<th scope="col">Mediane</th><th scope="col">Verdict</th></tr></thead>'
            f'<tbody>{"".join(tr)}</tbody></table></div>'
            '<p class="tier-note">Cea mai mică valoare dintr-o coloană <b>nu</b> este un '
            "câștigător. Variația între cele două porniri ale aceluiași JAR este de ordinul "
            "sutelor de MiB, iar diferența dintre mediane este de ordinul unităților. "
            "Aceste probe sintetice nu măsoară orașul, vehiculele, login-ul modat sau "
            "FPS-ul clientului.</p></div>")


def panel():
    try:
        text = ATLAS.read_text(encoding="utf-8")
    except OSError:
        return '<section id="tier"><h2>Tier list indisponibil</h2></section>'
    buckets, hybrid_count, other_count = classify(text)
    total = sum(len(entries) for entries in buckets.values())
    bands = [_tier_block(letter, title, blurb, buckets[letter])
             for letter, title, blurb in TIERS if buckets[letter]]
    counts = " · ".join(f"{letter} {len(buckets[letter])}"
                        for letter, _, _ in TIERS if buckets[letter])
    return f'''<section id="tier" class="tier-section" aria-labelledby="tier-title">
<div class="tier-overline"><span aria-hidden="true">◈</span> CLASAMENT PE DOVEZI <span class="tier-rule"></span> 12 OCT 2026</div>
<h2 id="tier-title">Tier list motoare hibride.<br><span>Litera urcă după probe, nu după promisiuni.</span></h2>
<p class="tier-lead">{total} familii și JAR-uri cercetate, repartizate după <b>ce am reușit să măsurăm cu pack-ul nostru intact</b> — 36 moduri Forge + 14 pluginuri Bukkit, aceeași lume, același Java. Aceasta nu este o listă de viteză: un motor ajunge în <b>S</b> pentru că a pornit și a fost măsurat, nu pentru că este cel mai rapid.</p>
<div class="tier-answer" role="note">
<div><span class="tier-answer-mark">?</span><div><strong>„Care e cel mai performant JAR, cu cel mai mic consum?”</strong>
<p><b>Răspunsul onest azi: NEDECIS.</b> Doar doi candidați au fost măsurați în condiții echivalente — <b>CUANTIC live</b> (CatServer adaptat) și <b>CatServer oficial</b> — iar diferențele dintre ei sunt de <b>~2 MiB la RSS</b> și <b>0,0–0,1 ms la p95</b>, adică mult sub variația din interiorul aceluiași JAR (247–290 MiB). Nu există un câștigător demonstrat, deci nu îl numim. Tot ce urcă în <b>A</b>, <b>B</b> sau <b>C</b> a fost deja respins, nu a pornit, sau nu a fost măsurat deloc.</p></div></div>
</div>
{_consumption_block(measured())}
<div class="tier-counts" role="status" aria-live="polite">{counts} · {total} rânduri</div>
{''.join(bands)}
<div class="tier-footer"><div><strong>Ce ar schimba acest clasament</strong>
<p>Un motor urcă doar cu: build autentic 1.16.5 cu SHA și licență verificate, pornire cu 36/14, apoi minimum <b>{MIN_TRIALS} repetări reale pe braț</b> cu clienți Forge confirmați în <code>/list</code>, aceeași lume și aceeași sarcină, cu vehicule și survival funcționale. <code>scripts/cuantic_tenx_gate.py</code> aplică exact această regulă și, fără date, întoarce <code>NEMASURAT</code> — niciodată un număr favorabil.</p></div>
<a href="#atlas">Vezi atlasul complet cu surse ↓</a></div>
</section>'''


STYLE = r'''
/* Tier list: evidence ranking, visually distinct from the atlas table. */
.tier-section{margin:72px 0 8px;padding:36px 28px 30px;background:radial-gradient(circle at 6% 2%,rgba(185,156,255,.13),transparent 38%),radial-gradient(circle at 96% 46%,rgba(95,240,192,.08),transparent 40%),#0c1220;border:1px solid rgba(150,130,211,.26);border-radius:24px;box-shadow:0 28px 90px rgba(0,0,0,.27);position:relative;overflow:hidden}
.tier-section:before{content:"";height:2px;position:absolute;left:0;right:0;top:0;background:linear-gradient(90deg,#b79cff,#5ff0c0,#f6c76a)}
.tier-overline{display:flex;align-items:center;gap:10px;color:#c3b3e8;letter-spacing:.16em;font-weight:800;font-size:11px}.tier-rule{height:1px;background:rgba(195,179,232,.27);width:34px}
.tier-section h2{font-size:clamp(30px,4.6vw,50px);line-height:1.1;letter-spacing:-.04em;margin:16px 0}.tier-section h2 span{color:#b79cff}
.tier-lead{max-width:880px;line-height:1.72;color:#adbed5;font-size:15px}
.tier-answer{margin:24px 0;padding:20px;border:1px solid rgba(246,199,106,.3);border-radius:15px;background:linear-gradient(100deg,rgba(246,199,106,.1),rgba(183,156,255,.06))}
.tier-answer>div{display:flex;gap:16px;align-items:flex-start}.tier-answer-mark{font-size:26px;font-weight:900;color:#f6c76a;line-height:1}
.tier-answer strong{color:#fff5e2;font-size:15px}.tier-answer p{color:#c8bcab;font-size:13px;line-height:1.62;margin:7px 0 0}
.tier-consum{margin:26px 0}.tier-consum h3{font-size:19px;color:#eef4ff;margin:0 0 8px;letter-spacing:-.02em}
.tier-scroll{overflow-x:auto;border:1px solid rgba(150,130,211,.24);border-radius:13px}
.tier-table{width:100%;min-width:820px;border-collapse:separate;border-spacing:0;font-size:13px;line-height:1.55}
.tier-table th[scope="col"]{text-align:left;position:sticky;top:0;background:#1d1a33;color:#c9bce8;font-size:11px;letter-spacing:.075em;text-transform:uppercase;padding:13px 14px;z-index:2}
.tier-table td,.tier-table th[scope="row"]{padding:14px;border-top:1px solid rgba(160,145,215,.14);color:#b6c2d8;background:rgba(17,15,32,.82);vertical-align:top;text-align:left;font-weight:400}
.tier-table tbody tr:nth-child(2n) td,.tier-table tbody tr:nth-child(2n) th[scope="row"]{background:rgba(24,21,44,.86)}
.tier-table th[scope="row"] strong,.tier-table td strong{color:#f2f6ff}
.tier-unit{display:inline-block;margin-left:6px;color:#8f83c4;font-size:11px}
.tier-table small{display:block;margin-top:5px;color:#8b93b5;font-size:11px;line-height:1.45}
.tier-verdict{display:inline-block;border-radius:30px;padding:5px 10px;font-size:11px;font-weight:750;white-space:nowrap;background:rgba(255,144,147,.13);color:#ffb8b8}
.tier-note{font-size:12.5px;color:#9aa4c0;line-height:1.62;margin:12px 0 0;max-width:900px}
.tier-counts{margin:24px 0 14px;font-size:12px;color:#9d94c4;letter-spacing:.04em}
.tier-band{display:flex;gap:16px;padding:18px 0;border-top:1px solid rgba(150,130,211,.16)}
.tier-band-label{flex:0 0 54px;height:54px;display:flex;align-items:center;justify-content:center;font-size:26px;font-weight:900;letter-spacing:-.05em;border-radius:14px;background:rgba(255,255,255,.05);color:#d9ccff;border:1px solid rgba(183,156,255,.3)}
.tier-band[data-tier-band="S"] .tier-band-label{color:#8af5ce;border-color:rgba(95,240,192,.4);background:rgba(95,240,192,.1)}
.tier-band[data-tier-band="A"] .tier-band-label{color:#9fd0ff;border-color:rgba(127,176,255,.4);background:rgba(127,176,255,.1)}
.tier-band[data-tier-band="B"] .tier-band-label{color:#ffb8b8;border-color:rgba(255,144,147,.36);background:rgba(255,144,147,.09)}
.tier-band[data-tier-band="C"] .tier-band-label{color:#f6d69e;border-color:rgba(246,199,106,.36);background:rgba(246,199,106,.09)}
.tier-band[data-tier-band="D"] .tier-band-label{color:#bdcce7;border-color:rgba(140,166,207,.3);background:rgba(140,166,207,.08)}
.tier-band-body{flex:1;min-width:0}.tier-band-body h3{margin:2px 0 4px;font-size:16px;color:#eef3ff;letter-spacing:-.02em}
.tier-band-body h3 span{margin-left:7px;font-size:11px;font-weight:750;color:#9d94c4;background:rgba(255,255,255,.06);border-radius:20px;padding:3px 8px;vertical-align:middle}
.tier-blurb{color:#98a2c0;font-size:12.5px;line-height:1.6;margin:0 0 12px;max-width:900px}
.tier-cards{list-style:none;margin:0;padding:0;display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:10px}
.tier-card{border:1px solid rgba(150,130,211,.2);border-radius:12px;padding:13px 14px;background:rgba(255,255,255,.028)}
.tier-card-head{display:flex;justify-content:space-between;gap:10px;align-items:flex-start}
.tier-card strong{color:#f0f5ff;font-size:13.5px;line-height:1.35}
.tier-chip{flex:0 0 auto;font-size:10px;font-weight:800;color:#b3a6dd;border:1px solid rgba(183,156,255,.3);border-radius:6px;padding:2px 6px}
.tier-card small{display:block;margin-top:6px;color:#8b93b5;font-size:11px;line-height:1.5}
.tier-know{margin:9px 0 0;color:#a9b5cd;font-size:12px;line-height:1.58}
.tier-decide{margin:6px 0 0;color:#8f9ab5;font-size:11.5px;line-height:1.55;padding-top:6px;border-top:1px dashed rgba(150,130,211,.18)}
.tier-card a{color:#8fd8c9;text-underline-offset:3px}
.tier-card code{color:#d1c5ff;background:rgba(165,145,240,.1);padding:1px 3px;border-radius:3px;font-size:11px;overflow-wrap:anywhere}
.tier-footer{display:flex;justify-content:space-between;gap:20px;align-items:center;margin-top:22px;padding:20px;border:1px solid rgba(183,156,255,.26);border-radius:14px;background:linear-gradient(100deg,rgba(183,156,255,.09),rgba(95,240,192,.05))}
.tier-footer strong{color:#f1ecff;font-size:14px}.tier-footer p{color:#a7a9c8;font-size:12px;line-height:1.6;margin:6px 0 0;max-width:760px}
.tier-footer>a{font-size:12px;color:#a89cf0;white-space:nowrap}
.tier-footer code{color:#d1c5ff;background:rgba(165,145,240,.12);padding:1px 4px;border-radius:3px;font-size:11px}
@media(max-width:740px){.tier-section{padding:26px 14px;margin:52px 0 6px}.tier-band{flex-direction:column;gap:10px}.tier-band-label{flex:0 0 auto;width:46px;height:46px;font-size:22px}.tier-cards{grid-template-columns:1fr}.tier-footer{flex-direction:column;align-items:flex-start}.tier-answer>div{flex-direction:column;gap:8px}}
'''

SCRIPT = r'''<script>
(() => {
  const tier = document.getElementById('tier');
  if (!tier) return;
  const rows = [...tier.querySelectorAll('[data-tier-row]')];
  const bands = [...tier.querySelectorAll('[data-tier-band]')];
  // Keyboard users get tier jump links without any hidden content.
  bands.forEach(band => {
    const letter = band.dataset.tierBand;
    const cards = band.querySelectorAll('[data-tier-row]').length;
    band.setAttribute('aria-label', `Tier ${letter}, ${cards} intrări`);
  });
  tier.dataset.tierRows = String(rows.length);
})();
</script>'''
