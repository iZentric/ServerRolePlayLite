#!/usr/bin/env python3
"""Generate a conservative public landing page; no live status or invented FPS/TPS."""
from pathlib import Path

HERE = Path(__file__).resolve().parent
HTML = '''<!doctype html>
<html lang="ro">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>FunCity — Roleplay Lite</title>
<style>
body{margin:0;background:#0d1117;color:#e6edf3;font:17px/1.6 system-ui,sans-serif}
main{max-width:760px;margin:auto;padding:44px 20px 80px}
h1{color:#7ee787;margin-bottom:0}h2{margin-top:32px;font-size:1.2em}
p,li{max-width:70ch}a{color:#79c0ff}
small,.muted{color:#a3acb7}.card{background:#161b22;border:1px solid #30363d;border-radius:12px;padding:14px 20px;margin:22px 0}
</style>
</head>
<body><main>
<h1>FunCity — Roleplay Lite</h1>
<p class="muted">Minecraft 1.16.5 · oraș deschis · roleplay cu moduri</p>
<div class="card"><strong>Client Lite în validare</strong>
<p>„Lite” înseamnă instalare simplă și setări prietenoase cu laptopurile vechi, nu un joc fără vehicule, mobilier sau celelalte funcții RP. Nu anunțăm un număr minim de FPS ori compatibilitate cu orice PC până la testul pe hardware real.</p></div>
<h2>Ce păstrăm</h2>
<ul><li>Vehicule, mobilier, hrană, arme și emote pentru comunitate.</li>
<li>Un singur pachet verificabil, cu dependențele potrivite client–server.</li>
<li>Profil grafic ușor: shaders dezactivate, distanță de randare redusă.</li></ul>
<h2>Stadiu</h2>
<p>Selecția și configurarea sunt în pregătire. Importul curat, intrarea în joc cu Forge și performanța pe un laptop modest nu au fost încă validate pentru următorul pachet. Nu instalăm automat moduri pe PC-ul tău și nu publicăm un pachet nou înaintea verificărilor.</p>
<p><a href="https://github.com/iZentric/ServerRolePlayLite">Cod, licențe și jurnal tehnic</a></p>
<small>Fără cookies și fără cifre live nemăsurate.</small>
</main></body></html>
'''


def main():
    dest = HERE / 'index.html'
    dest.write_text(HTML, encoding='utf-8')
    print(f'landing page generated: {dest} ({len(HTML.encode())} bytes)')


if __name__ == '__main__':
    main()
