#!/usr/bin/env python3
"""FunCity — site simplu, o singura pagina. Tot ce apare e MASURAT sau etichetat.
Datele din tabel vin din bench-v4 (branch functity-out); pagina nu adauga claims."""
import os, datetime
HERE = os.path.dirname(os.path.abspath(__file__))

JAR = "FunCity-1.16.5-b1.0827.jar"
SHA = "d6ffa35c1ea9032a4a95f7f1e34b734aa7f53b0358dda6b9e6592326640a15dd"

# FC-BENCH v4, 2026-10-14, aceeasi masina (ubuntu-24.04, 4 vCPU), acelasi pack
# (36 moduri + 14 plugini, sha fe1e2610...), 3 probe/armate, media. brut din functity-out/bench-v4/.
ROWS = [  # (nume, boot_medie_s, boot_logic_s, tps_p50, cpu_pct, rss_mb, critice)
    ("FunCity b1.2256 (motor propriu, patch P1 inclus)", "33.34", "3.03", "20.0 / 20.0", "1.8", "2256.1", 0),
    ("FunCity b0 (baseline, fara patch-uri)", "42.68", "4.24", "20.0 / 20.0", "2.4", "2267.6", 0),
    ("CatServer 1.16.5 (motorul istoric, referinta)", "43.35", "8.07", "20.0 / 20.0", "2.5", "2227.8", 0),
]

def status_live():
    for p in ("/tmp/alive.txt", os.path.join(HERE, "status-probe.txt")):
        try:
            t = open(p, encoding="utf-8").read().strip()
            if t:
                return t
        except OSError:
            pass
    return "netestat la aceasta constructie (sonda ruleaza in CI)"

def main():
    now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    rows = "\n".join(
        "<tr" + (' class="win"' if i == 0 else "") + "><td>" + n + "</td><td>" + b + "</td><td>" + bl +
        "</td><td>" + t + "</td><td>" + c + "</td><td>" + r + "</td><td>" + str(cr) + "</td></tr>"
        for i, (n, b, bl, t, c, r, cr) in enumerate(ROWS))
    html = f"""<!doctype html>
<html lang="ro"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>FunCity RP Lite — motor hibrid 1.16.5</title>
<style>
body{{margin:0;background:#0d1117;color:#e6edf3;font:16px/1.55 system-ui,sans-serif}}
main{{max-width:880px;margin:0 auto;padding:40px 20px 70px}}
h1{{font-size:2.1em;margin:.2em 0 .1em;letter-spacing:.02em}}
h1 b{{color:#7ee787}}
.sub{{color:#8b949e;margin-bottom:28px}}
.card{{background:#161b22;border:1px solid #30363d;border-radius:10px;padding:18px 20px;margin:18px 0}}
table{{width:100%;border-collapse:collapse;font-size:.92em}}
th,td{{padding:8px 10px;text-align:left;border-bottom:1px solid #21262d}}
th{{color:#8b949e;font-weight:600}}
tr.win td{{background:#12261a}}
code{{background:#21262d;padding:2px 6px;border-radius:5px;font-size:.92em;word-break:break-all}}
.mut{{color:#8b949e;font-size:.88em}}
a{{color:#79c0ff}}
ul{{padding-left:20px}}
</style></head><body><main>
<h1><b>FUNCITY</b> · RP Lite</h1>
<p class="sub">Motor propriu pentru roleplay 1.16.5: baza Mohist (commit fixat <code>754b578e</code>, GPL-3.0, rămâne atribuit) + patch-urile noastre, documentate și verificate. Cifrele de pe pagina asta sunt măsurate, nu promise.</p>

<div class="card"><b>Intrare jucători</b>
<ul>
<li>Adresă: <code>92.5.171.150:25565</code> — client <b>Forge 1.16.5</b> (loader 36.2.34) + folderul <code>mods/</code> (36 fișiere) din <a href="https://github.com/iZentric/ServerRolePlayLite/releases/tag/lite">pachetul <code>lite</code></a>. Java 11 la client, 3–4 GB RAM.</li>
<li>Fără Forge nu intri — e server cu moduri, nu vanilla. Pași completi: <code>analysis/FUNCTITY-CLIENT.md</code> din repo.</li>
</ul>
<p class="mut">Stiată la ultima construcție: {status_live()}</p></div>

<div class="card"><b>Motorul — comparație (FC-BENCH v4)</b>
<table>
<tr><th>Armă</th><th>Boot mediu (s)</th><th>Boot logic (s)</th><th>TPS p50/min</th><th>CPU idle (%)</th><th>RSS (MB)</th><th>Erori critice</th></tr>
{rows}
</table>
<p class="mut">Condiții: aceeasi mașină (runner găzduit, 4 vCPU), același pack (sha <code>fe1e2610…</code>), 3 probe/ramură, medie, 2026-10-14. Date brute: branch-ul <code>functity-out</code>, folderul <code>bench-v4/</code>. Singura metrică unde CatServer stă mai bine e RSS-ul idle (2228 vs 2256 MB). Benchmark idle pe 4 vCPU — nu e dovadă de „cel mai bun la 100 de jucători", e dovada a exact ce scrie mai sus.</p></div>

<div class="card"><b>Artefact livrat</b>
<ul>
<li>JAR: <code>{JAR}</code></li>
<li>SHA-256: <code>{SHA}</code></li>
<li>Bază: MohistMC/Mohist @ <code>754b578e</code> (GPL-3.0) · patch propriu: dropper-insert-null-guard (0001), compilație verificată + semnătură hibridă testată pe gazdă</li>
<li>Proveniență completă: branch <code>functity-out</code> → <code>builds/b1.0827/</code> (metadata + SHA256SUMS)</li>
</ul></div>

<p class="mut">Pagina generată {now} de build_site.py · fără cookies, fără analytics, fără promisiuni.</p>
</main></body></html>"""
    out = os.path.join(HERE, "index.html")
    open(out, "w", encoding="utf-8").write(html)
    print(f"index.html scris ({len(html)} B)")

if __name__ == "__main__":
    main()
