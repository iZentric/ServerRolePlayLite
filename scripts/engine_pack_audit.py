#!/usr/bin/env python3
"""Read ONLY the public release ZIP; inventory real components and safe tuning keys.

No downloads outside the calling workflow, no live access, no config secrets,
no inference that installing a mod saved RAM without an A/B measurement.
"""
import hashlib
from pathlib import Path
import sys
import zipfile

EXPECTED_PACK_SHA = "fe1e261097d92f26c6653239a7161613e6be54b8e9f82c79739c101ce8aa8a15"
WATCH = ("ferritecore", "modernfix", "roadrunner", "lazydfu", "spark", "voicechat", "vehicle", "smoothchunk", "ksyxis")
CONFIG = ("server.properties", "spigot.yml", "bukkit.yml", "catserver.yml", "config/modernfix-mixins.properties", "config/ferritecore-mixin.toml")
PROPS = ("use-native-transport", "view-distance", "online-mode", "network-compression-threshold", "max-players")


def audit(pack):
    digest = hashlib.sha256(pack.read_bytes()).hexdigest()
    if digest != EXPECTED_PACK_SHA:
        raise ValueError("release SHA changed: refuse to label as the tested 1.7.7 pack")
    with zipfile.ZipFile(pack) as archive:
        names = archive.namelist()
        if len(names) != len(set(names)):
            raise ValueError("duplicate ZIP paths can hide different components")
        mods = sorted(p[5:] for p in names if p.startswith("mods/") and p.count("/") == 1 and p.endswith(".jar"))
        plugins = sorted(p[8:] for p in names if p.startswith("plugins/") and p.count("/") == 1 and p.endswith(".jar"))
        if len(mods) != 36 or len(plugins) != 14:
            raise ValueError(f"expected 36 mods/14 plugins, got {len(mods)}/{len(plugins)}")
        found = {name: [mod for mod in mods if name in mod.lower().replace("-", "").replace("_", "")]
                 for name in WATCH}
        # Whitelist only public, non-secret server.properties keys, no arbitrary
        # config dumps or paths containing personal data.
        props = {}
        if "server.properties" in names:
            text = archive.read("server.properties").decode("latin-1", "replace")
            for line in text.splitlines():
                if "=" in line and not line.lstrip().startswith("#"):
                    key, value = line.split("=", 1)
                    if key.strip() in PROPS:
                        props[key.strip()] = value.strip()
        return digest, mods, plugins, found, [p for p in CONFIG if p in names], props


def main(pack, report):
    digest, mods, plugins, found, configs, props = audit(pack)
    rows = "\n".join(f'| `{name}` | {", ".join("`" + p + "`" for p in paths) if paths else "Nu este în această arhivă"} |'
                     for name, paths in found.items())
    text = f'''# Inventar real al pack-ului CUANTIC 1.7.7 — numai citire

Arhivă: [release public `lite`](https://github.com/iZentric/ServerRolePlayLite/releases/tag/lite), SHA-256 `{digest}`.
Inventar exact: **{len(mods)} moduri / {len(plugins)} pluginuri**. Citit din ZIP, nu dedus din `pack-rules.json`.
**Prezența unui mod NU dovedește un câștig de FPS/RAM**, iar eliminarea lui fără test poate strica loginul/vehiculele.
Nicio modificare la live, JAR, lume sau pack. Nu am pus în raport chei de acces sau setări sensibile; parserul citește `server.properties` dar afișează exclusiv chei permise.

## Ce optimizări/funcții apar deja în arhivă

| Componentă urmărită | Fișier găsit (sau lipsa lui) |
| --- | --- |
{rows}

## Configuri existente și câteva setări publice

Configuri detectate: {', '.join('`' + p + '`' for p in configs) or 'niciuna din lista sigură'}.

| Setare (server.properties) | Valoare în arhivă |
| --- | --- |
{chr(10).join('| `' + p + '` | `' + props.get(p, 'nespecificată') + '` |' for p in PROPS)}

**Atenție:** arhiva nu garantează că gazda live rulează aceeași configurație chiar acum; verificarea gazdei necesită runnerul self-hosted. Nu adăugăm FerriteCore/ModernFix/RoadRunner încă o dată fără a verifica fișierele de mai sus. RoadRunner/ModernFix au mecanisme care pot intra în conflict cu alte mixin-uri; logurile și testele de compatibilitate contează mai mult decât lista de moduri.

<details><summary>Toate cele 36 de moduri din arhivă</summary>

{chr(10).join('- `' + x + '`' for x in mods)}
</details>

<details><summary>Toate cele 14 pluginuri din arhivă</summary>

{chr(10).join('- `' + x + '`' for x in plugins)}
</details>
'''
    report.write_text(text, encoding="utf-8")
    print(f"audit OK: {digest} {len(mods)} mods {len(plugins)} plugins; {len(configs)} config files")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit("usage: engine_pack_audit.py <release-pack.zip> <report.md>")
    main(Path(sys.argv[1]), Path(sys.argv[2]))
