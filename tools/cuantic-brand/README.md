# Cuantic-Brand — pluginul pentru /version

Un singur fisier de Cod (`src/.../CuanticBrandPlugin.java`) + `plugin.yml` cu versiunea
`__VER__`, inlocuita de `scripts/build_lite.py` la build cu `pack_version` din `pack-rules.json`.

* `stubs/` = DOAR antetele API-ului (org.bukkit.* semnaturi din 1.16.5). Ele nu ajung in jar;
  in runtime pluginul leaga de API-ul real din server. Le tinem in repo ca build-ul sa fie
  determinist: maven (Spigot/Paper) da 404-uri intermitente pe CI, iar un esec de descarcare
  nu ar trebui sa lase pack-ul fara brand.
* Compilarea ruleaza in CI (sandbox-ul nostru nu are `javac`), in `scripts/build_lite.py`.
* Comanda `/version` originala ramane functionala pentru API; noi schimbam doar textul
  vazut de jucator si pastram sirul upstream-ului pe linia "based on / adapted from".
