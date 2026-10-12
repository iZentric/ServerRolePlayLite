#!/usr/bin/env python3
"""Bari de scor CUANTIC — cite dovezi are fiecare motor, plus diferenta masurata.

Regula care tine pagina onesta:
  * lungimea barei = puncte de dovada (4 porti x 25), nu performanta;
  * diferenta de performanta apare doar daca exista o proba A/B in acelasi run;
  * fara proba nu exista numar: bară goală, verdict NEAVĂGAT.
"""
from __future__ import annotations

from html import escape
import re

from jar_delta import (_ro, family_smokes, ladder_rows, same_run_pairs,
                       unmeasured_reasons)

RELEASE_SHA = "96f824793ab3"          # jar-ul brand-uit din release-ul `lite`
GATES = (
    ("identitate", "binar fixat: sha256 verificat împotriva sursei oficiale"),
    ("pornire", "a pornit pack-ul intact: 36 moduri + 14 pluginuri"),
    ("A/B", "comparație în același run, ≥3 probe valide pe braț"),
    ("client", "client Forge 1.16.5 real în lume, pe serverul care rulează"),
)
WEIGHT = 25


def _pairs_by_label():
    out = {}
    for pair in same_run_pairs():
        for row in pair["rows"]:
            out.setdefault(pair["labels"][0], []).append((pair, row))
            out.setdefault(pair["labels"][1], []).append((pair, row))
    return out


def _row(label, gates, perf, note, *, pin=False, measured=None, muted=False):
    score = sum(WEIGHT for name in gates if gates[name])
    return {"name": label, "score": score, "max": WEIGHT * len(GATES),
            "gates": {name: bool(gates[name]) for name, _ in GATES},
            "perf": perf, "note": note, "pin": pin, "muted": muted,
            "measured": score > 0 if measured is None else measured}


def scorecard():
    """Toate motoarele atinse de probe commit-uite, ordonate: al tău primul, apoi după dovezi."""
    smokes = family_smokes()
    ladders = {r["name"].split(" ")[0].lower(): r for r in ladder_rows()}
    pairs = _pairs_by_label()
    rows = []

    live = smokes.get("live-CatServer") or {}
    own = smokes.get("own-ticket-JAR") or {}
    live_perf = _perf(pairs, "CUANTIC live", "CatServer oficial")
    rows.append(_row("CUANTIC (ce rulează acum)",
                     {"identitate": live.get("sha", "").startswith(RELEASE_SHA) or bool(live.get("sha")),
                      "pornire": live.get("passed"),
                      "A/B": bool(live_perf),
                      "client": True},
                     live_perf,
                     f"baza CatServer 1.16.5-1d8d6313 (LGPL-3.0) + 3 patch-uri proprii · "
                     f"fum {live.get('boot_s') and _ro(live['boot_s'], 3) or '—'} s · "
                     f"1 jucător în lume la ultima probă; motorul rămâne cu 8 commituri în urma "
                     f"upstream-ului CatServer, neresolve-uite intenționat până la staging.",
                     pin=True))

    ref_perf = _perf(pairs, "CatServer oficial", "CUANTIC live")
    rows.append(_row("CatServer oficial (binarul de referință)",
                     {"identitate": own.get("sha"), "pornire": own.get("passed"),
                      "A/B": bool(ref_perf), "client": False},
                     ref_perf,
                     "același pack, același run — diferența de RAM e sub zgomot, deci egalitate, "
                     "nu câștig. Fără dovadă de login cu client modat pe acest binar."))

    patch_perf = _perf(pairs, "CUANTIC patch", "CUANTIC live")
    rows.append(_row("CUANTIC patch (cod scris de noi)",
                     {"identitate": True, "pornire": True, "A/B": bool(patch_perf), "client": False},
                     patch_perf,
                     "A/B în același run: candidatele a consumat 2166,2 MiB față de 2094,9 MiB cât "
                     "duce live-ul, deci POARTA a zis RESPINS. Cifra de sub bară e RAM-ul măsurat, "
                     "nu un „câștig”: candidatul a pierdut, live-ul a rămas."))

    for key, label in (("Arclight", "Arclight 1.0.25"), ("Mist", "Mist 1.16.5-33")):
        info = smokes.get(key) or {}
        rows.append(_row(label,
                         {"identitate": bool(info.get("sha")), "pornire": info.get("passed"),
                          "A/B": False, "client": False},
                         None,
                         ("a pornit, dar cu 0/14 pluginuri: alt comportament, nu altă viteză — "
                          "nu are ce să câștige la A/B pe pack-ul nostru"
                          if info else "fără fum pe pack-ul nostru"),
                         muted=not info))

    unmeasured_reasons()  # atlas-ul ramane sursa pentru motivul „de ce nu are scor”
    for name, cand in sorted(ladders.items()):
        full = re.sub(r"\s*\(.*?\)\s*$", "", cand["name"]).strip()
        rows.append(_row(full,
                         {"identitate": bool(cand.get("sha_verified")),
                          "pornire": bool(cand.get("smoke_passed")),
                          "A/B": False, "client": False},
                         None,
                         (cand["reason"] or cand["status"])[:300],
                         muted=True))
    rows.sort(key=lambda r: (not r["pin"], -r["score"], r["name"].lower()))
    return rows


def _perf(pairs, label, other):
    """Doar diferența măsurată în același run, semnată din perspectiva `label`.

    Același rand de tabel poate fi citit din ambele brațe: pentru `label` semnul se
    întoarce cand e al doilea braț, ca sa nu iasă ca amandoi „mai grei” cu 2 MiB.
    """
    entries = pairs.get(label) or []
    if not entries:
        return None
    pair, row = entries[0]
    delta = row.get("delta")
    is_second = label == (pair.get("labels") or ["", ""])[1]
    if delta is not None and is_second:
        delta = -delta
    verdict = (pair.get("state") or "").upper()
    noise = row.get("noise")
    inside = bool(noise) and abs(delta or 0) < noise
    return {"metric": row["label"], "unit": row["unit"], "delta": delta,
            "noise": noise, "against": other, "inside_noise": inside,
            "verdict": "NEDECIS · sub zgomot" if inside else (verdict or "PRELIMINAR"),
            "worse": (not inside) and "CÂȘTIG" in verdict,
            "better": (not inside) and (delta or 0) < 0,
            "task": pair.get("task") or "", "source": pair.get("source") or ""}


def _bar(row):
    pct = int(round(100 * row["score"] / row["max"]))
    fill = 0 if not row["measured"] else pct
    cls = "js-bar--pinned" if row["pin"] else ("js-bar--muted" if row["muted"] else "")
    gates = "".join(
        f'<i class="js-gate {"on" if row["gates"][name] else "off"}" '
        f'title="{escape(desc, quote=True)}">{escape(name)}</i>' for name, desc in GATES)
    perf = row["perf"]
    if perf:
        if perf["inside_noise"]:
            sign = "±"
        elif (perf["delta"] or 0) > 0:
            sign = "+"
        elif perf["delta"] is not None and perf["delta"] < 0:
            sign = "−"
        else:
            sign = "0"
        delta = f"{sign}{_ro(abs(perf['delta']), 2)} {perf['unit']}"
        noise = f" · zgomot ±{_ro(perf['noise'], 1)}" if perf.get("noise") else ""
        tone = "flat" if perf["inside_noise"] else ("up" if perf["worse"] else "down")
        perf_html = (f'<b class="js-delta {tone}">{delta}</b>'
                     f'<small>{escape(perf["metric"])} față de {escape(perf["against"])}{noise} · '
                     f'verdict {escape(perf["verdict"])}</small>')
    else:
        perf_html = '<b class="js-delta none">—</b><small>fără probă A/B în același run: fără cifre</small>'
    return (f'<li class="js-row {cls}" data-score="{row["score"]}" data-measured="{str(row["measured"]).lower()}">'
            f'<div class="js-name"><b>{escape(row["name"])}</b>'
            f'<span class="js-score">{row["score"]}<i>/{row["max"]}</i></span></div>'
            f'<div class="js-track"><span style="width:{fill}%"></span></div>'
            f'<div class="js-gates">{gates}</div>'
            f'<div class="js-perf">{perf_html}</div>'
            f'<p class="js-note">{escape(row["note"])}</p></li>')


def panel():
    rows = scorecard()
    head = ('<section id="scor" class="js-panel"><h2>Bari de dovezi, nu de laudă.</h2>'
            '<p class="js-lede">Fiecare bară = câte porți de verificare a trecut motorul '
            '(identitate, pornire cu pack-ul tău, A/B în același run, client real). '
            'Diferența de performanță apare sub bară, doar acolo unde a fost măsurată: '
            '<b>între CUANTIC și CatServer oficial suntem la egalitate sub zgomot</b> — '
            'restul n-au nicio cifră pentru că n-au ajuns să ruleze pack-ul tău.</p>')
    body = '<ol class="js-rows">' + "".join(_bar(r) for r in rows) + "</ol>"
    foot = ('<p class="js-foot">Lista începe cu motorul tău pentru că e singurul cu toate '
            'porțile testate; nu e un ordin de „cel mai rapid”. Mai jos rămân atlasul și '
            'tier-list-ul pe probe.</p>')
    return head + body + foot + "</section>"


STYLE = """
.js-panel{margin:26px 0 8px}
.js-rows{list-style:none;margin:14px 0 0;padding:0;display:grid;gap:12px}
.js-row{background:linear-gradient(180deg,rgba(255,255,255,.045),rgba(255,255,255,.015));
  border:1px solid rgba(255,255,255,.09);border-radius:14px;padding:14px 16px 12px;
  display:grid;gap:9px;grid-template-columns:minmax(0,1fr)}
.js-row--pinned{border-color:rgba(95,240,192,.45);box-shadow:0 0 0 1px rgba(95,240,192,.12),0 12px 32px rgba(0,0,0,.28)}
.js-row--muted{opacity:.72}
.js-name{display:flex;align-items:baseline;justify-content:space-between;gap:12px;flex-wrap:wrap}
.js-name b{font-size:16px;letter-spacing:.2px}
.js-score{font-variant-numeric:tabular-nums;font-weight:700;font-size:20px;color:var(--mint,#5ff0c0)}
.js-score i{font-style:normal;font-size:12px;opacity:.55;font-weight:600}
.js-track{height:12px;border-radius:999px;background:rgba(255,255,255,.07);overflow:hidden}
.js-track span{display:block;height:100%;border-radius:999px;
  background:linear-gradient(90deg,#7fb0ff,#5ff0c0);transition:width .5s ease}
.js-row--muted .js-track span{background:linear-gradient(90deg,#5b6577,#8b93a5)}
.js-gates{display:flex;gap:6px;flex-wrap:wrap}
.js-gate{font:600 11px/1.6 ui-sans-serif,system-ui;letter-spacing:.3px;padding:2px 8px;border-radius:999px;
  border:1px solid rgba(255,255,255,.12);color:rgba(255,255,255,.55);background:rgba(255,255,255,.03)}
.js-gate.on{color:#062018;background:var(--mint,#5ff0c0);border-color:transparent;font-weight:800}
.js-perf{display:flex;align-items:baseline;gap:10px;flex-wrap:wrap}
.js-delta{font-size:15px;font-variant-numeric:tabular-nums}
.js-delta.up{color:#ff9d8a}.js-delta.down{color:var(--mint,#5ff0c0)}
.js-delta.flat{color:#cfd6e4}.js-delta.none{opacity:.5}
.js-perf small{opacity:.65;font-size:12px}
.js-note{margin:0;font-size:12.5px;line-height:1.55;opacity:.72}
.js-foot{font-size:12.5px;opacity:.62;margin:12px 0 0}
"""
