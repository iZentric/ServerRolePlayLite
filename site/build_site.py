#!/usr/bin/env python3
"""Generatorul site-ului CUANTIC - citeste verdictele reale din analysis/ si naste index.html"""
import os, re, glob, datetime
from engine_results import latest_status, panel, strategy_panel

AN = os.path.join(os.path.dirname(__file__), "..", "analysis")

# Historical boot minima (site/records.json) had no retained source logs and
# even combined the lowest RAM and fastest boot from different runs. They are
# archival notes, NOT a ranking; only controlled same-run A/B appears on site.

# ===== SECTIUNEA LIVE: masuratori pe serverul care ruleaza ACUM, cu un jucator in lume =====
LIVE_PATH = os.path.join(AN, "BENCH-LIVE.md")

def live_metrics():
    try:
        txt = open(LIVE_PATH, encoding="utf-8", errors="replace").read()
    except Exception:
        return {}
    def g(pat):
        m = re.search(pat, txt)
        return m.group(1).strip() if m else None
    d = {}
    d["data"] = g(r"BENCH live CUANTIC — (\d{4}-\d\d-\d\d \d\d:\d\d:\d\d UTC)")
    d["mspt"] = g(r"Tick durations \(min/med/95%ile/max ms\) from last 10s, 1m:\s*([0-9.]+/[0-9.]+/[0-9.]+/[0-9.]+)")
    d["mspt1m"] = g(r"from last 10s, 1m:\s*[0-9./]+;\s*([0-9.]+/[0-9.]+/[0-9.]+/[0-9.]+)")
    d["cpu"] = g(r"\(system\)\s*([0-9%, ]+?)\s*\(process\)")
    d["heap"] = g(r"Memory usage:\s*([0-9.]+ MB / [0-9.]+ GB\s*\([0-9]+%\))")
    d["gcy"] = g(r"([0-9.]+ ms avg, [0-9]+ total collections)")
    d["gco"] = g(r"G1 Old Generation collector:\s*([0-9]+)(?: total)? collections")
    d["keep"] = g(r"Cant't keep up: total=([0-9]+)") or g(r"Can't keep up: total=([0-9]+)")
    d["players"] = g(r"There are ([0-9]+) out of maximum ([0-9]+) players online") or ""
    d["maxp"] = g(r"There are [0-9]+ out of maximum ([0-9]+) players online") or ""
    d["done"] = g(r"Done: Done \(([0-9.]+)s\)")
    d["full"] = g(r"Dedicated server took ([0-9.]+) seconds to load")
    d["lat"] = g(r"port public: ([0-9]+)ms")
    d["rss"] = g(r"rss=([0-9]+)MB")
    d["cpu_proc"] = g(r"java cpu=([0-9.]+)%")
    d["crit"] = g(r"erori CRITICE in sesiune: ([0-9]+)")
    d["disc"] = g(r"disc=([0-9]+% din [0-9.]+G)")
    return d

L = live_metrics()

def lv(k, alt="nesuparat"):
    v = L.get(k)
    return v if v else ("**" + alt + "**") if False else (v if v else "—")

live_rows = [
    ("Jucători în lume la momentul probei", (L.get("players") or "—") + " (max " + (L.get("maxp") or "25") + ")", "comanda `list` în consola, răspunsul citit din live.log"),
    ("MSPT min/mediu/p95/max (10 s)", lv("mspt"), "2.4 ms pe tick = 5% din bugetul de 50 ms → 20 TPS fără efort"),
    ("MSPT (1 min)", lv("mspt1m"), "varful de 279 ms cade in fereastra in care EU rulasem comenzile de diagnostic — neatribuit"),
    ("`Can't keep up` în toată sesiunea", lv("keep"), "0 = niciun tick intarziat anuntat de server"),
    ("Pauze GC (G1 Young)", lv("gcy"), "colectorile sunt scurte si rare; frecventa ~24 s"),
    ("Full-GC (G1 Old)", (L.get("gco") + " colectari") if L.get("gco") else "—", "0 = fara blocaje lungi de secunde"),
    ("Heap folosit", lv("heap"), "cu -Xmx2G; mai avem marja pentru playeri"),
    ("RAM proces", (L.get("rss") + " MB RSS") if L.get("rss") else "—", "varful masurat din /proc (VmHWM) in sesiune: 2.59 GB"),
    ("CPU", ("proces " + L["cpu_proc"] + "% din 2 vCPU") if L.get("cpu_proc") else "—", "restul il mananca joburile de test ale agentului"),
    ("Pornire", (lv("done") + "s până la `Done`") if L.get("done") else "—", "incarcare completa (pluginuri): " + (lv("full") + "s")),
    ("Latență rețea prin tunel", (lv("lat") + " ms") if L.get("lat") else "—", "RTT TCP pana la portul public, numaratoarea din aceeasi masina"),
    ("Eroare critică", (L.get("crit") + " în sesiune") if L.get("crit") is not None else "—", "crash / OOM / exceptie in tick loop"),
    ("Disc gazdă", lv("disc"), "limita fizica a cutiei, nu a serverului"),
]
live_tabel = "\n".join(
    f'<tr><td><b>{a}</b></td><td>{b}</td><td style="color:var(--mut)">{c}</td></tr>'
    for a, b, c in live_rows)
live_date = L.get("data") or "fara masuratori"
live_sec = f"""
<h2>🔬 Arhiva măsurătorilor de pe gazda reală (nu în timp real)</h2>
<div class="sub">Proba istorică din <b>{live_date}</b>. Este separată de
<a href="https://github.com/iZentric/ServerRolePlayLite/blob/arena/a29b4ef4-serverroleplaylite/docs/ENGINE-PLAYER-RESULT.md">cele trei citiri cu un jucător din 11 octombrie 2026</a>.
Nu presupunem că jucătorii, traficul sau starea serverului de atunci sunt valabile acum.
Valorile de aici nu se compară numeric cu probele CI de boot: sarcina și timpul diferă.</div>
<table class="tbl">
<tr><th>Ce măsurăm</th><th>Valoare</th><th>Cum se citește</th></tr>
{live_tabel}
</table>
<div class="sub" style="margin-top:10px">Ce <b>nu</b> acoperă: 3-10 jucători deodată, baseline-ul packului original
pe aceeași mașină (deci nu vindem „de X ori mai repede"), și costul exact al layerului hibrid (Forge curat vs
Forge+Bukkit, același set de moduri). Următorul experiment. Date brute: <code>analysis/BENCH-LIVE.md</code>,
generator: <code>scripts/bench-live.sh</code>.</div>
"""

now = datetime.datetime.utcnow().strftime("%d %b %Y, %H:%M UTC")


# ===== PROGRES CUANTIFICAT — cat a devenit mai bun, pe aceeasi masina, cu aceleasi unelte =====
import re as _re
_acc = ""
try:
    _acc = open(os.path.join(os.path.dirname(__file__), "..", "analysis", "ACCEPTANCE.md"), encoding="utf-8", errors="replace").read()
except Exception:
    pass
_scor_full = _re.search(r"SCOR: TRECE=(\d+) VERIFICA=(\d+) CADE=(\d+) INFO=(\d+) N-A=(\d+)", _acc)
_scor = _re.search(r"SCOR: TRECE=(\d+) VERIFICA=(\d+) CADE=(\d+)", _acc)
_data = _re.search(r"# ACCEPTANCE CUANTIC — ([0-9: -]+) UTC", _acc)
_al = ""
try:
    _al = open(os.path.join(os.path.dirname(__file__), "..", "analysis", "ALIVE.md"), encoding="utf-8", errors="replace").read()
except Exception:
    pass
_am = _re.search(r"# ALIVE CUANTIC — ([0-9: -]+) UTC.*?```\n(.+?)\n```", _al, _re.S)
alive_txt, alive_cul = latest_status()
if _scor_full:
    scor = f"{_scor_full.group(1)} TRECE / {_scor_full.group(2)} DE VERIFICAT / {_scor_full.group(3)} CADE / {_scor_full.group(4)} INFO / {_scor_full.group(5)} N-A (10/10 teste, T1-T10)"
elif _scor:
    scor = f"{_scor.group(1)} TRECE / {_scor.group(2)} DE VERIFICAT / {_scor.group(3)} CADE"
else:
    scor = "—"

progres_rows = [
    ("1.5.9", "2G heap, 3 flaguri GC, 32 moduri", "2613 MB", "47.2 ms × 25", "4.9 ms", "14.448 s / 92.639 s", "analysis/BENCH-LIVE.md (istoric)"),
    ("experiment 8G", "heap 8G, tot 3 flaguri — dovedit mai prost", "3367 MB", "111.38 ms × 8", "9.1 ms", "—", "analysis/BENCH-RAM.md"),
    ("RAM total + set validat", "-Xmx = MemTotal (11884 MB) + 32 flaguri validate pe Java 17 în CI", "3192 MB", "115.88 ms × 8", "2.0 ms", "13.664 s / 96.788 s", "analysis/RAM-ALL.md + BENCH-LIVE.md"),
    ("1.6.2", "30 moduri (tuns), chunk-gc load-threshold=300, FerriteCore în mrpack", "ne-măsurat încă", "ne-măsurat încă", "ne-măsurat încă", "11.096 s / 59.972 s", "analysis/ACCEPTANCE.md + APPLY-LIVE.md"),
    ("1.6.3", "FerriteCore ȘI pe server (slug 404 reparat) + manifest-cuantic.json în zip", "BENCH după APPLY", "BENCH după APPLY", "BENCH după APPLY", "BENCH dupa APPLY", "analysis/BENCH-LIVE.md"),
    ("1.7.0", "Motor CUANTIC cioplit în bytecode + Cuantic-Brand (14/14 plugini) + Client redus 133.1 → 72.5 MB + 6 GB max heap", "3119 MB RSS (4700 MB liberi)", "G1GC 37ms target", "2.0 ms (la gol)", "17.253 s / 74.453 s", "analysis/ACCEPTANCE.md + APPLY-LIVE.md"),
    ("1.7.7 (ACUM — Sincronizat 1:1)", "36 moduri server + 14 pluginuri · Sincronizare 1:1 Server↔Client (Out of Sight 24/32m, EntityCulling 32m, scaling 60%) · Texturi 256x256 HD RGBA + Oculus (0 negru-mov) · Connectivity 2.4 · servers.dat pre-salvat", "3335 MB RSS (4533 MB liberi)", "0 Full-GC · 0 erori în log", "2.0 ms (20.0 TPS)", "12.634 s / 70.448 s", "analysis/ACCEPTANCE.md (8/8 TRECE) + analysis/chk.md"),
]
# ===== BENCH auto: ultimul rand din tabelul de progres se completeaza din verdict =====
_b = ""
try:
    _b = open(os.path.join(os.path.dirname(__file__), "..", "analysis", "BENCH-LIVE.md"), encoding="utf-8", errors="replace").read()
except Exception:
    pass
_bd = _re.search(r"Done \(([0-9.]+)s\)", _b)
_bf = _re.search(r"took ([0-9.]+) seconds", _b)
_bk = _re.search(r"Can't keep up: total=(\d+)", _b)
_bw = _re.search(r"VmHWM:\s+(\d+) kB", _b)
_bt = _re.search(r"MSPT[^0-9]*([0-9.]+)/([0-9.]+)/([0-9.]+)/([0-9.]+)", _b)
_bh = _re.search(r"TPS from last[^:]*:\s*([0-9.]+)", _b)
_bwts = _re.search(r"# BENCH live CUANTIC — ([0-9: -]+) UTC", _b)
if _bt or _bd or _bw:
    _p95 = f"{_bt.group(3)} ms" if _bt else "ne-măsurat"
    _rss = f"{round(int(_bw.group(1))/1024)} MB (vârf /proc)" if _bw else "ne-măsurat"
    _boot = (f"{_bd.group(1)} s / {_bf.group(1)} s" if _bd and _bf else (f"{_bd.group(1)} s" if _bd else "ne-măsurat"))
    _keep = f"`Can't keep up` = {_bk.group(1)}" if _bk else "keep-up ne-măsurat"
    _tps = f"TPS {_bh.group(1)}" if _bh else ""
    progres_rows.append(("BENCH de pe box (se actualizează singur)",
        "straturi de tuning ajunse și pe box (spigot/bukkit/catserver/commands) + max-tnt-per-tick + use-native-transport + MOTD corectat",
        _rss, _keep + (f" · {_tps}" if _tps else ""), _p95, _boot,
        "analysis/BENCH-LIVE.md" + (f" · proba {_bwts.group(1)}" if _bwts else "")))

progres_tabel = "\n".join(
    f'<tr><td><b>{a}</b></td><td>{b}</td><td>{c}</td><td>{d}</td><td><b>{e}</b></td><td>{f}</td>'
    f'<td style="color:var(--mut)"><small>{g}</small></td></tr>' for a, b, c, d, e, f, g in progres_rows)
progres_sec = f"""
<h2 id="cifre">📈 Arhiva probelor anterioare (scenarii diferite)</h2>
<div class="sub">Arhiva combină valori din alte date și scenarii (unele cu un jucător, altele la idle); nu presupunem aceeași sarcină sau 120 s de încălzire în toate rândurile. Nu compara cifrele acestei arhive ca pe un benchmark A/B. Lipsa unei măsurători este marcată ca atare.</div>
<table class="tbl">
<tr><th>Pas</th><th>Ce s-a schimbat</th><th>Memorie ocupată (vârf)</th><th>Curățenie memorie (cât durează × de câte ori)</th><th>Întârzierea pe care o simți (a 95-a sutime din secunde)</th><th>Cât aștepti până poți intra</th><th>Unde-i dovada</th></tr>
{progres_tabel}
</table>
<div class="sub" style="margin-top:10px">Valorile provin din runde separate, cu sarcini și configurări diferite.
Nu reprezintă un A/B controlat, deci procentele de câștig nu sunt o promisiune de performanță.
Verdictele de compatibilitate istorică: {scor}{' — ' + _data.group(1) if _data else ''}.</div>
"""


STYLE = r"""
:root{--bg:#070a12;--ink:#eef2ff;--mut:#98a6c0;--card:rgba(20,26,42,.72);--line:rgba(148,163,184,.16);
--mint:#5ff0c0;--blue:#7fb0ff;--violet:#b79cff;--amber:#f6c76a;--red:#ff7d8d;--r:18px}
*{box-sizing:border-box;margin:0;padding:0}
html{scroll-behavior:smooth}
body{background:var(--bg);color:var(--ink);font:16px/1.6 system-ui,"Segoe UI",Roboto,Inter,sans-serif;
 -webkit-font-smoothing:antialiased;overflow-x:hidden}
body:before{content:"";position:fixed;inset:-30% -10% auto;height:70vh;z-index:-1;
 background:radial-gradient(60% 60% at 20% 0%,rgba(95,240,192,.14),transparent 70%),
 radial-gradient(50% 50% at 80% 10%,rgba(127,176,255,.16),transparent 70%),
 radial-gradient(40% 40% at 55% 40%,rgba(183,156,255,.12),transparent 70%)}
.wrap{max-width:1080px;margin:0 auto;padding:0 22px 70px}
nav{position:sticky;top:0;z-index:9;backdrop-filter:blur(12px);background:rgba(7,10,18,.72);
 border-bottom:1px solid var(--line)}
nav .in{max-width:1080px;margin:auto;display:flex;align-items:center;gap:14px;padding:12px 22px}
.logo{display:flex;align-items:center;gap:10px;font-weight:800;letter-spacing:.02em}
.logo svg{width:26px;height:26px}
.pill{border:1px solid var(--line);border-radius:999px;padding:6px 12px;font-size:12px;color:#cbd5e1;
 background:rgba(20,26,42,.6);white-space:nowrap}
.pill i{display:inline-block;width:7px;height:7px;border-radius:50%;background:var(--mint);margin-right:7px;
 box-shadow:0 0 12px var(--mint);vertical-align:1px}
nav a.l{margin-left:auto;color:var(--mut);text-decoration:none;font-size:13px}
nav a.l:hover{color:var(--ink)}
header{padding:72px 0 30px;text-align:left}
.eyebrow{display:inline-flex;align-items:center;gap:8px;font-size:11px;letter-spacing:.16em;text-transform:uppercase;
 color:var(--mint);font-weight:700}
.eyebrow:before{content:"";width:26px;height:1px;background:var(--mint)}
h1{font-size:clamp(38px,7.4vw,74px);line-height:1.02;letter-spacing:-.03em;margin:16px 0 14px;font-weight:850}
h1 span{background:linear-gradient(100deg,#f4fffb,#6ff0c4 45%,#8fbaff);-webkit-background-clip:text;background-clip:text;color:transparent}
.lede{font-size:clamp(17px,2.3vw,21px);color:#aebbd0;max-width:640px}
.cta{display:flex;flex-wrap:wrap;gap:12px;margin:26px 0 4px}
.btn{display:inline-flex;align-items:center;gap:9px;border-radius:12px;padding:13px 18px;font-weight:800;
 text-decoration:none;background:linear-gradient(100deg,#63f0bf,#8cc0ff);color:#06131f;
 box-shadow:0 12px 34px rgba(76,214,175,.18);transition:.18s}
.btn:hover{transform:translateY(-1px);filter:brightness(1.06)}
.btn.ghost{background:rgba(20,26,42,.7);color:var(--ink);border:1px solid var(--line);box-shadow:none}
.stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:12px;margin:34px 0 6px}
.stat{border:1px solid var(--line);background:var(--card);border-radius:var(--r);padding:16px 16px 14px}
.stat b{display:block;font-size:30px;font-weight:850;letter-spacing:-.02em;color:var(--mint)}
.stat b.b2{color:var(--blue)}.stat b.b3{color:var(--violet)}.stat b.b4{color:var(--amber)}
.stat span{color:var(--mut);font-size:12.5px;display:block;margin-top:3px}
h2{margin:62px 0 4px;font-size:clamp(23px,3.4vw,33px);letter-spacing:-.02em}
h2 + .sub,.sub{color:var(--mut);font-size:14.5px;max-width:760px}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(258px,1fr));gap:14px;margin-top:20px}
.card{border:1px solid var(--line);background:var(--card);border-radius:var(--r);padding:18px}
.card h3{font-size:16.5px;margin-bottom:7px;letter-spacing:-.01em}
.card p{color:#a9b7cc;font-size:14px}
.card p b{color:var(--ink)}
.src{margin-top:12px;display:inline-block;font:11px/1 ui-monospace,Menlo,monospace;color:#7f8ea8;
 border:1px dashed var(--line);border-radius:7px;padding:6px 8px}
.ba{border:1px solid var(--line);border-radius:var(--r);background:var(--card);padding:6px 16px;margin-top:16px}
.bar-row{display:grid;grid-template-columns:230px 1fr;gap:14px;align-items:center;padding:14px 0;
 border-bottom:1px solid rgba(148,163,184,.10)}
.bar-row:last-child{border-bottom:0}
.bar-row .q{font-size:14px;color:#c3cfe2}
.bar-row .q small{display:block;color:var(--mut);font-size:12px}
.meter{display:flex;align-items:center;gap:12px;font-weight:800;font-size:14px}
.meter .seg{border-radius:9px;padding:9px 12px;white-space:nowrap;font-size:13px}
.was{background:rgba(255,125,141,.12);color:#ffc3cb;border:1px solid rgba(255,125,141,.24)}
.now2{background:linear-gradient(100deg,rgba(99,240,191,.2),rgba(140,192,255,.2));color:#d8fff1;
 border:1px solid rgba(95,240,192,.3)}
.arrow{color:var(--mut);font-weight:600}
.tbl{width:100%;border-collapse:collapse;margin-top:14px;background:var(--card);border:1px solid var(--line);
 border-radius:var(--r);overflow:hidden}
.tbl th,.tbl td{padding:11px 13px;text-align:left;border-bottom:1px solid rgba(148,163,184,.10);font-size:13.5px;vertical-align:top}
.tbl th{color:var(--mut);font-weight:650;background:rgba(13,18,30,.5)}
.tbl tr:last-child td{border-bottom:0}
.tbl tr.hl td{color:#a7ffd9;background:rgba(99,240,191,.06)}
.table-scroll{max-width:100%;overflow-x:auto}.table-scroll .tbl{min-width:650px}
.card a:not(.btn),.sub a,.note a{color:var(--mint)}
.bar{background:#374151;border-radius:8px;padding:8px 12px;font-weight:700;white-space:nowrap}
.bar.win{background:linear-gradient(90deg,#059669,#34d399);color:#04281c}
.bar.dead{background:#7f1d1d;color:#fecaca;display:inline-block;width:auto!important}
.row{display:grid;grid-template-columns:minmax(200px,340px) 1fr;gap:12px;align-items:center;margin:10px 0}
.eng{display:flex;flex-direction:column}.eng small{color:var(--mut)}.ico{margin-right:6px}
.evo{display:flex;gap:6px;align-items:flex-end;margin-top:16px;height:130px}
.evo div{flex:1;background:linear-gradient(180deg,#60a5fa,#1d4ed8);border-radius:7px 7px 0 0;
 display:flex;align-items:flex-start;justify-content:center;font-size:.72rem;padding-top:5px;color:#dbeafe}
.evo div.last{background:linear-gradient(180deg,#34d399,#059669);color:#04281c;font-weight:700}
.note{border-left:3px solid var(--amber);background:rgba(246,199,106,.07);border-radius:0 12px 12px 0;
 padding:14px 16px;margin-top:18px;font-size:14px;color:#e8d7b4}
.note b{color:var(--amber)}
.honest{border:1px solid rgba(255,125,141,.28);background:rgba(255,125,141,.05);border-radius:var(--r);padding:18px;margin-top:18px}
.honest h3{color:#ffc3cb;font-size:16px;margin-bottom:8px}
.honest ul{list-style:none;color:#c6b3b8;font-size:14px}
.honest li{padding:6px 0 6px 22px;position:relative;border-bottom:1px dashed rgba(255,125,141,.14)}
.honest li:last-child{border:0}
.honest li:before{content:"✕";position:absolute;left:0;color:var(--red);font-size:12px;top:8px}
details{border:1px solid var(--line);border-radius:14px;background:var(--card);padding:14px 16px;margin-top:12px}
summary{cursor:pointer;font-weight:750;color:#d5e0f0}
details p{color:var(--mut);font-size:14px;margin-top:9px}
pre{color:var(--mut);overflow-x:auto;font-size:12.5px;line-height:1.5}
footer{margin-top:70px;padding-top:22px;border-top:1px solid var(--line);color:#6d7d96;font-size:12.5px;text-align:left}
footer code{color:#9fb0c9}
.live{color:var(--mint)}
@media(max-width:700px){header{padding:44px 0 22px}.bar-row{grid-template-columns:1fr}.row{grid-template-columns:1fr}
 nav a.l{display:none}}
"""

# ===== STRATURILE CUANTIC — de ce nu e "CatServer + Java 17" gol =====
straturi_rows = [
    ("1. Sincronizare 1:1 Server ↔ Client", "<b>Aliniere matematică între ce trimite serverul și ce desenează clientul</b>: serverul are <code>view-distance=4</code> (64m) și trimite entitățile la <code>32m</code> (<code>players: 48m</code>, <code>animals/monsters: 24m</code>, <code>misc: 12m</code>). Pe client am setat <code>EntityCulling tracingDistance=32</code>, <code>Out of Sight entity=32m / tileEntity=24m</code> și <code>entityDistanceScaling=0.6</code>",
     "Pe scurt: degeaba pui laptopul să caute mașini sau mobi la 64–128 de blocuri dacă serverul oricum îi trimite doar până la 32 de blocuri! Iar la mobilierul 3D (care vine cu tot chunk-ul de 64m), desenăm doar clădirea și strada din fața ta (24m), tăind <b>86% din aria de mobilier invizibil</b> după pereți!",
     "Estimare geometrică, nu FPS măsurat", "config/out_of_sight-client.toml + entityculling.json + spigot.yml"),
    ("2. Texturi 256×256 HD RGBA + Oculus", "<b>Texturi compactate; VRAM real ne-măsurat</b>: păstrăm <b>Oculus 1.4.7</b> pe client (cu <code>shaderPack=(off)</code> implicit) și <code>dynamic_resources=false</code> pe client, iar pozele gigantice <code>1024×1024</code> / <code>2048×2048</code> din <code>Pizzaland</code> și <code>ModernXL</code> sunt aduse la <b>256×256 HD</b> în format 32-bit <code>RGBA</code> curat",
     "Pe scurt: un bloc normal în Minecraft are 16×16 pixeli. Reducerea imaginilor de 1024/2048 la 256 pixeli micșorează numărul de pixeli al acelor imagini; VRAM și FPS pe laptop slab nu au fost încă măsurate.",
     "90.7 MB pack (−41.7 MB) · 0 texturi lipsă", "scripts/build_lite.py (slim_client_jar)"),
    ("3. Configuri Client gata reglate", "<b>Rubidium + Rubidium Extra + EntityCulling + FerriteCore</b> pre-configurate în <code>overrides/config/</code>: <code>smooth_lighting: OFF</code>, <code>enable_clouds: false</code>, <code>always_defer_chunk_updates: true</code>, <code>fog_distance: 33</code>, animații lavă/foc oprite",
     "Pe scurt: am descoperit în codul Rubidium că ignora <code>options.txt</code> și lăsa iluminarea grea și norii porniți! Acum vin oprite din fabrică, dar impactul real când conduci prin oraș cere o probă pe un laptop slab.",
     "FPS pe Intel HD încă netestat în A/B", "overrides/config/rubidium-options.json + sodium-extra-options.json"),
    ("4. Connectivity 2.4 (Anti-Timeout)", "<b>Connectivity 2.4</b> instalat atât pe Server cât și pe Client + <code>connectivity-common.toml</code> (<code>logintimeout = 2400</code> ticks = 120s, fără limită de 1 MB pe pachete)",
     "Pe scurt: când un laptop vechi sau un Wi-Fi slab încarcă 36 de moduri la intrarea în oraș, Minecraft-ul normal îl dădea afară după 30 de secunde cu <code>Timed out</code>. Timeout-ul configurat este mai lung; reușita pe Wi-Fi slab și laptop ieftin rămâne de testat.",
     "Login pe PC slab încă netestat în A/B", "mods/connectivity-2.4-1.16.5.jar"),
    ("5. Motor Hibrid CUANTIC + Java 17", "<b>CatServer 1.16.5</b> cioplit în bytecode la <code>CUANTIC</code> + <b>Cuantic-Brand-1.7.7.jar</b> (cu optimizări runtime stil Gale/Pufferfish: îngheață AI-ul mobilor la >18m, curăță proiectilele, reglează anti-cheatul pentru mașini) + <b>29 flaguri JVM OpenJDK 17 + Netty</b>",
     "Pe scurt: rulează simultan <b>36 de moduri Forge</b> (mașini, arme, mobilier, mâncare, voicechat) și <b>14 pluginuri Bukkit</b> (grade, bani, terenuri, protecții) în același server, cu pornire în <b>12.6 secunde</b>.",
     "8/8 TRECE în ACCEPTANCE · 0 erori în log", "tools/cuantic-brand + deploy/jvm-flags-17.txt"),
    ("6. Cele 18 Moduri de Performanță pe Server", "<b>RoadRunner</b> (Lithium) · <b>ModernFix</b> · <b>FerriteCore</b> · <b>SmoothChunkSave</b> · <b>FastSuite</b> (rețete multithread) · <b>FastWorkbench</b> · <b>FastFurnace</b> · <b>Placebo</b> · <b>LetMeDespawn</b> · <b>SpawnerFix</b> · <b>GetItTogetherDrops</b> · <b>Clumps</b> · <b>AI-Improvements</b> · <b>InControl!</b> · <b>MemoryLeakFix</b> · <b>Ksyxis</b> · <b>Bad Wither No Cookie</b> · <b>spark</b>",
     "Pe scurt: fiecare mod rezolvă o frână precisă a serverului — salvarea lumii nu mai blochează jocul, mesele de lucru și cuptoarele nu mai scanează 5.000 de rețete pe fiecare tick, mobii cu iteme în mână se despawnează corect, iar liliecii din peșteri sunt opriți complet (<code>ambient: 0</code>).",
     "36 moduri totale pe server (18 gameplay + 18 perf)", "analysis/chk.md + pack-rules.json"),
]
straturi_tabel = "\n".join(
    f'<tr><td><b>{a}</b></td><td>{b}</td><td style="color:var(--mut)">{c}</td><td>{d}</td>'
    f'<td style="color:var(--mut)"><small>{e}</small></td></tr>' for a, b, c, d, e in straturi_rows)
straturi_sec = f"""
<h2 id="explicat">🧠 Explicat „ca la proști": TOT ce am făcut în CUANTIC și DE CE</h2>
<div class="sub">Fără cuvinte pompoase aruncate degeaba: mai jos vezi exact <b>ce am băgat în modpack și în server</b>, <b>ce am scos</b> și <b>de ce fiecare piesă face diferența</b> pe un laptop vechi fără placă video.</div>
<table class="tbl">
<tr><th>Pilon strategic</th><th>Ce am implementat tehnic</th><th>Explicat simplu („ca la proști” — de ce contează)</th><th>Rezultat / limită</th><th>Unde e în proiect</th></tr>
{straturi_tabel}
</table>

<h2>🔍 Ce poți verifica singur în joc (Dovezi pe care le poți verifica TU în joc)</h2>
<div class="sub">Nu trebuie să ne crezi pe cuvânt. Intră pe server și verifică singur acești <b>4 indicatori concreți</b>:</div>
<div class="grid">
  <div class="card"><h3>1️⃣ Apasă <code>F3</code> în joc (stânga-sus)</h3><p>Uită-te la două lucruri: (1) pe rândul serverului scrie direct <b><code>CUANTIC</code></b>, iar în stânga-sus ai contorul de FPS din <code>Rubidium Extra</code>; (2) în dreapta-sus la <b><code>Mem:</code></b> poți verifica RAM-ul real al clientului; nu există încă o garanție pentru orice laptop în mijlocul orașului, datorită <code>FerriteCore</code> + texturilor HD 256×256.</p></div>
  <div class="card"><h3>2️⃣ Scrie <code>/tps</code> sau <code>/spark tps</code> în chat</h3><p>Verifică TPS-ul și MSPT-ul curent (nu garantăm 20 TPS când intră mulți jucători). Probele istorice cu 1 jucător au raportat ~2–3.5 ms (din bugetul maxim de 50 ms pe tick). Bugetul unui tick este 50 ms, dar sarcina mare și vehiculele nu au fost măsurate în același scenariu.</p></div>
  <div class="card"><h3>3️⃣ Verifică toate itemele în Creative / Inventar</h3><p>Ia orice armă din <code>CGM</code>, orice mașină din <code>Vehicle Mod</code>, orice felie de pizza din <code>Pizzaland</code> sau mobilier din <code>ModernXL</code>: <b>0 pătrate negru-mov</b>, toate modelele 3D sunt clare, iar când conduci mașina cu viteză nu mai îngheață imaginea la trecerea dintre chunk-uri (<code>always_defer_chunk_updates: true</code>).</p></div>
  <div class="card"><h3>4️⃣ Scrie <code>/cuantic</code>, <code>/version</code> și <code>/pl</code></h3><p>În ultimul smoke-test izolat, cele <b>14 pluginuri Bukkit</b> (<code>LuckPerms</code>, <code>EssentialsX</code>, <code>WorldGuard</code>, <code>ClaimChunk</code>, <code>SkinsRestorer</code> etc.) au fost activate cu cele <b>36 de moduri Forge</b>; nu e test de autentificare sau de sarcină mare.</p></div>
</div>
"""

# ===== DETALIIILE PACK-ULUI SE CITESC DIN RELEASE, NU DIN MEMORIE =====
import json as _json, re as _re, urllib.request as _rq
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PACKV = "?"
try:
    PACKV = _json.load(open(os.path.join(ROOT, "pack-rules.json"), encoding="utf-8"))["pack_version"]
except Exception:
    pass
REL, RTAG = {}, ""
RELEASE_SOURCE = "GitHub release (verificare curentă)"
try:
    with _rq.urlopen("https://api.github.com/repos/iZentric/ServerRolePlayLite/releases/tags/lite", timeout=25) as _r:
        _d = _json.load(_r)
        REL = {a["name"]: a for a in _d.get("assets", [])}
        RTAG = _d.get("name", "")
except Exception:
    pass
# Actions occasionally cannot reach the public API; publishing 0 MB was false.
# Use a dated, committed snapshot of the exact same release instead, and make
# its provenance explicit. Never silently invent a file size.
if not REL:
    try:
        _cache = _json.load(open(os.path.join(os.path.dirname(__file__), "release-assets.json"), encoding="utf-8"))
        REL = {a["name"]: a for a in _cache["assets"]}
        RELEASE_SOURCE = "GitHub release (snapshot verificat " + _cache["checked_utc_date"] + ")"
    except (OSError, KeyError, ValueError):
        pass
def asset(tip, sufix):
    """Numele + marimea reala a asset-ului de pe release; fallback = nume derivat din pack_version."""
    n = next((k for k in REL if tip in k and k.endswith(sufix)), None)
    if not n:
        n = ("CUANTIC-%s-%s%s" % (tip, PACKV, sufix))
    mb = round(REL[n]["size"] / 1e6, 1) if n in REL else None
    return n, mb
def _existent(tip, sufix):
    """Daca pack_version a fost deja data inainte sa apuce CI-ul sa urce arhiva,
    legam linkul de ultimul asset CARE EXISTA pe release, ca pagina sa nu dea 404."""
    return next((k for k in sorted(REL, reverse=True) if tip in k and k.endswith(sufix)), None)
CLIENT, CLIENT_MB = asset("Client", ".mrpack")
SERVER, SERVER_MB = asset("Server-CatServer", ".zip")
if CLIENT not in REL and _existent("Client", ".mrpack"):
    CLIENT = _existent("Client", ".mrpack"); CLIENT_MB = round(REL[CLIENT]["size"]/1e6, 1)
if SERVER not in REL and _existent("Server-CatServer", ".zip"):
    SERVER = _existent("Server-CatServer", ".zip"); SERVER_MB = round(REL[SERVER]["size"]/1e6, 1)
CLIENT_MB = CLIENT_MB if CLIENT_MB is not None else "—"
SERVER_MB = SERVER_MB if SERVER_MB is not None else "—"
DL = "https://github.com/iZentric/ServerRolePlayLite/releases/download/lite/"
print("pack %s | client %s (%s MB) | server %s (%s MB)" % (PACKV, CLIENT, CLIENT_MB, SERVER, SERVER_MB))

ADRESA = "92.5.171.150:25565"
try:
    _pa = open(os.path.join(os.path.dirname(__file__), "..", "deploy", "play-address.txt"), encoding="utf-8").read().strip()
    if _pa and ":" in _pa:
        ADRESA = _pa
except Exception:
    pass

# Sectiunea „ce s-a schimbat" se citeste din site/changelog.json, iar titlul din
# pack-rules.json (PACKV) — text batut de mana in HTML ramanea in urma pack-ului.
CARDS = {}
_cl = os.path.join(os.path.dirname(__file__), "changelog.json")
if os.path.isfile(_cl):
    try:
        CARDS = _json.load(open(_cl, encoding="utf-8"))
    except Exception as e:  # noqa: BLE001
        print("!! changelog.json citit gresit: %s" % str(e)[:120])
def _card(c):
    txt = _re.sub(r"`([^`]+)`", r"<code>\\1</code>", c["p"])
    return '  <div class="card"><h3>%s</h3><p>%s</p></div>' % (c["t"], txt)

_noua = CARDS.get(PACKV) or []
_istoric = [(v, CARDS[v]) for v in sorted((v for v in CARDS if v != PACKV), reverse=True)]
noutati_sec = ""
if _noua:
    noutati_sec = '\n<h2>🆕 Ce s-a schimbat în %s (și de ce contează pentru tine)</h2>\n<div class="grid">\n%s\n</div>\n' % (
        PACKV, "\n".join(_card(c) for c in _noua))
if _noua and _istoric:
        noutati_sec += '<details><summary><b>Istoric: ce am reparat pe rând</b> (%d versiuni)</summary>\n' % len(_istoric)
        for v, cs in _istoric:
            noutati_sec += '<h3 style="margin:14px 0 6px">%s</h3>\n<div class="grid">\n%s\n</div>\n' % (v, "\n".join(_card(c) for c in cs))
        noutati_sec += '</details>\n'

html = f"""<!DOCTYPE html>
<html lang="ro"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>CUANTIC — Roleplay modat, survival și oraș | Minecraft Forge 1.16.5</title>
<meta name="description" content="CUANTIC: server Minecraft Forge 1.16.5 cu 36 de moduri și 14 pluginuri. Roleplay, survival și direcție pentru mafii în oraș. JAR validat, benchmark public și limite explicate, fără promisiuni de zero lag.">
<style>{STYLE}
</style></head><body>
<nav><div class="in">
  <div class="logo"><svg viewBox="0 0 24 24" fill="none"><circle cx="12" cy="12" r="2.6" fill="#5ff0c0"/><ellipse cx="12" cy="12" rx="10" ry="4.4" stroke="#7fb0ff" stroke-width="1.3"/><ellipse cx="12" cy="12" rx="10" ry="4.4" stroke="#b79cff" stroke-width="1.3" transform="rotate(60 12 12)"/><ellipse cx="12" cy="12" rx="10" ry="4.4" stroke="#5ff0c0" stroke-width="1.3" transform="rotate(120 12 12)"/></svg>CUANTIC</div>
  <span class="pill"><i style="background:{alive_cul};box-shadow:0 0 12px {alive_cul}"></i>{alive_txt}</span>
  <span class="pill">cost 0 lei</span>
  <a class="l" href="#cifre">sari la cifre ↓</a>
</div></nav>
<div class="wrap">

<header>
  <div class="eyebrow">Forge 1.16.5 · 36 moduri + 14 pluginuri · Palma City</div>
  <h1>Oraș roleplay modat. <span>Supraviețuire cu miză.</span></h1>
  <p class="lede">Intră în CUANTIC cu modpack-ul normal. Construim o experiență de <b>RP urban, survival și mafii</b>, fără să sacrificăm compatibilitatea pentru un motor „rapid” doar în reclame. Pack-ul actual are <b>36 de moduri pe server și 14 pluginuri</b>. Mafii și regulile de joc sunt direcția de dezvoltare, nu funcții pretinse ca finalizate.</p>
  <div class="cta">
    <a class="btn" href="{DL}{CLIENT}">⬇️ Modpack-ul client ({PACKV} · {CLIENT_MB} MB)</a>
    <a class="btn ghost" href="#engine-test">📊 JAR-ul și benchmarkul</a>
    <a class="btn ghost" href="#viziune">🏙️ Strategia orașului</a>
    <a class="btn ghost" href="#cum-intri">🚀 Cum intri</a>
  </div>
  <div class="stats">
    <div class="stat"><b>2,1 ms</b><span>ultima citire p95/10 s cu 1 jucător, 11 octombrie; nu promisiune la 25</span></div>
    <div class="stat"><b class="b2">{CLIENT_MB} MB</b><span>client optimizat HD RGBA · serverul încarcă 50 componente (36 moduri + 14 pluginuri)</span></div>
    <div class="stat"><b class="b3">14 / 14</b><span>pluginuri activate în smoke-ul motorului validat; patch-ul nou rămâne experimental</span></div>
    <div class="stat"><b class="b3" style="font-size:20px">{PACKV}</b><span>ultimul pack: {CLIENT}{" + " + SERVER if SERVER in REL else ""}</span></div>
    <div class="stat"><b class="b4">Adresă</b><span>pack-ul include <b>{ADRESA}</b> în lista de servere; verifică accesul înainte de sesiune</span></div>
  </div>
</header>

{panel()}

{strategy_panel()}

<h2 id="cum-intri">🚀 Cum intri pe server în 3 pași simpli</h2>
<div class="sub">Pentru Forge 1.16.5 ai nevoie de un launcher compatibil. Durata instalării și FPS-ul depind de hardware, rețea și modurile alese:</div>
<div class="grid">
  <div class="card"><h3>Pasul 1️⃣ — Descarcă fișierul</h3><p>Apasă pe butonul verde de mai jos ca să iei fișierul <b><code>{CLIENT}</code></b> ({CLIENT_MB} MB). Nu trebuie să îl dezarhivezi!</p><p style="margin-top:10px"><a class="btn" href="{DL}{CLIENT}">⬇️ Descarcă {CLIENT}</a></p></div>
  <div class="card"><h3>Pasul 2️⃣ — Pune-l în Launcher</h3><p>Deschide <a href="https://prismlauncher.org/download" style="color:var(--mint)">Prism Launcher</a> sau <a href="https://modrinth.com/app" style="color:var(--mint)">Modrinth App</a> → apasă <b>Add Instance</b> → <b>Import</b> → alege fișierul <code>{CLIENT}</code> descărcat la Pasul 1.<br><br><b>💡 Setare de pornire, nu performanță garantată:</b> în setările instanței (Memory), pune <b><code>2560 MB</code></b> dacă ai 4 GB RAM în laptop, sau <b><code>4096 MB</code></b> dacă ai 8+ GB RAM.</p></div>
  <div class="card"><h3>Pasul 3️⃣ — Intră direct în joc!</h3><p>Apasă <b>Launch / Play</b>. Când se deschide meniul Minecraft, apasă pe <b>Multiplayer</b>:<br><br>✅ <b>Nu trebuie să scrii niciun IP!</b> Serverul <b><code>CUANTIC RolePlay • Palma City</code></b> (<code>{ADRESA}</code>) este <b>deja salvat primul în listă</b>! Dai dublu-click pe el și intri direct în oraș, fără parolă.</p></div>
</div>

<h2>🗂️ Măsurători istorice: comparații doar cu aceeași sarcină</h2>
<div class="sub">Valorile mai vechi au fost făcute cu alte configurații și la momente diferite.
Nu le folosim ca dovadă că noul JAR e mai rapid; vezi A/B-ul reproductibil de mai sus.
Sub 50 ms pe tick nu înseamnă FPS garantat pe laptop sau 20 TPS cu 25 jucători.</div>

{progres_sec}

{noutati_sec}

{live_sec}

{straturi_sec}

<h2>🤝 Ce primești și ce NU promitem</h2>
<div class="grid">
  <div class="card"><h3>📦 Pack-ul tău, ușurat cu −45.5%</h3><p>Modurile de conținut din Freeroam rămân în pack; ultimele probe izolate nu substituie un handshake modat real, dar fișierele multimedia au fost compactate; calitatea vizuală și FPS-ul cer test pe laptop, iar <code>Freeroam.1.0.0.mrpack</code> original rămâne intact în tagul <code>pack-original</code>.</p><span class="src">{PACKV} · {CLIENT} · {CLIENT_MB} MB (redus de la 133.1 MB = −60.6 MB pentru copii cu net slab)</span></div>
  <div class="card"><h3>🚪 Intrare în pack</h3><p>Clientul modat se descarcă mai sus. Verifică identitatea operatorului înainte de a deschide un server fără autentificare: numele unui jucător nu este o dovadă de identitate.</p><span class="src">analysis/NO-LOGIN.md · analysis/op.md</span></div>
  <div class="card"><h3>🩺 Recuperare monitorizată</h3><p>Dacă Java moare, supervisorul încearcă repornirea, iar logul nu se mai șterge la repornire (dovada morii rămâne pe disc). Schimbările pe serverul live cer backup verificat și rollback; nu promitem recuperare instantanee.</p><span class="src">scripts/cuantic-live.sh · analysis/ACCEPTANCE.md</span></div>
  <div class="card"><h3>🧾 Probe verificabile</h3><p>A/B-ul din partea de sus citește rezultatele jobului GitHub; arhiva istorică include și valori vechi introduse manual. Le poți citi pe toate în repo, la <code>analysis/</code>.</p><span class="src">BENCH-LIVE.md · RAM-ALL.md · APPLY-LIVE.md</span></div>
</div>
<div class="honest">
  <h3>Ce nu știm încă (si de ce e scris aici, nu ascuns după un slogan)</h3>
  <ul>
    <li>Nu există încă un JAR nou demonstrat mai bun decât cel public. Cel mai recent A/B/B/A a redus CPU în scenariul sintetic, dar p95 a crescut ușor; nu am instalat candidatul.</li>
    <li>Nu avem măsurat cu 10-25 de jucători deodată — baza reală are trei citiri cu <b>un</b> jucător, iar A/B-ul izolat nu are jucători. Nu mai afișăm niciun „câți jucători duce" — valorile acelea erau extrapolări, nu probe, și nu le-am verificat.</li>
    <li>Nu avem un test client complet al șofatului și al orașului pe un laptop ieftin. Metricile serverului nu demonstrează FPS bun sau lipsa erorilor la toți jucătorii.</li>
    <li>Nu avem backup zilnic programat pe cutia asta. Ce avem: snapshot <code>tar</code> înaintea fiecărei schimbări + copii <code>.bak</code>. Backup-ul zilnic vine odată cu mutarea pe VM.</li>
    <li>Restartul programat de la 06:00 (ghilotina anti-scurgeri) e <b>plan</b>, nu stare de fapt. Supervisorul încearcă repornirea la crash; nu efectuăm restarturi experimentale în timpul sesiunilor active.</li>
    <li>Trezirea la prima conectare (wake-on-join) e scrisă și documentată, dar <b>n-a fost încă verificată live</b> — pe Cloud Shell e imposibil fizic.</li>
    <li>Nu vindem „de 1000× mai bun": 1000× pe p95 ar însemna 0.005 ms, adică sub cuantumul unui singur tick. Datele istorice nu demonstrează că un JAR nou a redus p95.</li>
  </ul>
</div>

<details><summary>📖 Dicționar de termeni, ca să nu te păcălim cu jargon</summary>
  <p><b>MSPT</b> = cât durează o „bătăre" a serverului. Bugetul pentru 20 TPS este 50 ms pe tick; un tick rapid nu garantează FPS client bun.</p>
  <p><b>p95</b> = a 95-a valoare din 100, adică 95% dintre măsurători sunt cel mult acea valoare; maximele pot fi mai rele.</p>
  <p><b>GC</b> = momentul în care Java își face curat în memorie și stă puțin loc. Mai rare = mai bine, dar prea lungi = se simte.</p>
  <p><b>RSS / RAM vârf</b> = câtă memorie ocupă cu adevărat serverul, nu cât i-am dat voie să ceară.</p>
  <p><b>Hibrid</b> = server care rulează simultan moduri (Forge) și pluginuri (Bukkit). Integrarea este asigurată de CatServer; compatibilitatea în joc trebuie testată cu pack-ul normal.</p>
</details>

<h2>🥔 Merge și pe un calculator de bibliotecă?</h2>
<div class="grid">
  <div class="card"><h3>Clientul</h3><p>Pack-ul modat are reglaje pentru grafica redusă; OptiFine și Rubidium/Oculus trebuie încercate în instanțe separate. Nu promitem FPS pe PC-uri vechi fără test în oraș cu vehicule. Mărime: <b>{CLIENT_MB} MB</b> client / <b>{SERVER_MB} MB</b> server. Sursă: {RELEASE_SOURCE}; nu estimări.</p></div>
  <div class="card"><h3>Serverul</h3><p>La ultima probă fără jucători a raportat 20 TPS. Nu avem încă sarcină controlată cu mai mulți jucători, deci consumul la vârf nu este garantat.</p></div>
  <div class="card"><h3>Gazda</h3><p>Rulează acum pe un cont gratuit, 2 vCPU · 11.8 GB RAM · disc 5 GB (66% ocupat — limita reală a cutiei, nu a serverului).</p></div>
</div>

<h2>📦 Cum intri, în 3 mișcări</h2>
<div class="grid">
  <div class="card"><h3>1️⃣ Descarcă</h3><p>Apasă butonul de sus: <b>{CLIENT}</b>. E același Freeroam pe care-l cunoști, verificat și ușurat.</p><p style="margin-top:10px"><a class="btn" href="{DL}{CLIENT}">⬇️ Descarcă pack-ul</a></p></div>
  <div class="card"><h3>2️⃣ Importă (o dată)</h3><p><a href="https://prismlauncher.org/download">Prism Launcher</a> → Add Instance → Import → alege fișierul <code>.mrpack</code> → Launch. Folosește un launcher care importă mrpack; nu am testat orice launcher.</p></div>
  <div class="card"><h3>3️⃣ Joacă-te</h3><p>Multiplayer → Add Server → <b>{ADRESA}</b>. Fără parolă, fără /register — intri direct în oraș. 🏙️</p></div>
</div>

<footer>
  <span class="live">●</span> Pagina se regenerează automat din verdictele joburilor · ultima actualizare: {now}<br>
  CUANTIC · Roleplay Lite · 1.16.5 Forge+Bukkit (CatServer) · set de flaguri JVM validat pe Java 17 în CI<br>
  Date brute: <code>docs/ENGINE-DECISION.md</code> · <code>docs/ENGINE-AB-GITHUB.md</code> · <code>docs/ENGINE-PREFLIGHT.md</code>
</footer>
</div></body></html>"""

if '</style' in STYLE[1:-3] or '<style>' not in html or ':root{' not in html.split('<style>',1)[1].split('</style>',1)[0]:
    raise SystemExit('CSS malformat: blocul <style> nu e inchis corect')

out = os.path.join(os.path.dirname(__file__), "index.html")
open(out, "w", encoding="utf-8").write(html)
print(f"site generat: {out} ({len(html)} bytes)")
