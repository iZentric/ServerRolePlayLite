#!/usr/bin/env bash
# Reproductible, read-only FunCity session preflight. Never touches the live server.
set -Eeuo pipefail
cd "$(dirname "$0")/.."
ROOT=$PWD
PIN=754b578ef3e4881d854bcd1df5d299ada3fd429f
TMP=$(mktemp -d /tmp/fc-init.XXXXXXXX)
trap 'rm -rf -- "$TMP"' EXIT

echo 'F0: JSON / Python / Bash'
python3 - <<'PY'
import json
from pathlib import Path
p=Path('agent/obiective.json')
data=json.loads(p.read_text())
assert [x['id'] for x in data['obiective']]==[f'F{i}' for i in range(11)]
assert all(x['status'] in ('nepornit','in lucru','trecut','blocat') for x in data['obiective'])
for root in ('scripts','functity/ci','site'):
    for f in Path(root).glob('*.py'): compile(f.read_bytes(),str(f),'exec')
print('JSON+Python PASS')
PY
while IFS= read -r -d '' shfile; do bash -n "$shfile"; done < <(find agent scripts -maxdepth 1 -name '*.sh' -print0)
echo 'Bash PASS'

echo 'F0: YAML (install PyYAML into temporary directory only if unavailable)'
if python3 -c 'import yaml' 2>/dev/null; then
  :
else
  python3 -m pip install --disable-pip-version-check -q --target "$TMP/yaml" 'PyYAML==6.0.3'
  export PYTHONPATH="$TMP/yaml${PYTHONPATH:+:$PYTHONPATH}"
fi
python3 - <<'PY'
from pathlib import Path
import yaml
files=list(Path('.github/workflows').glob('*.yml'))+list(Path('functity-config').glob('*.yml'))
legacy = {'aichat.yml','bat-v2.yml','funcity-brand.yml','functity-server.yml',
          'functity-stage.yml','move-to-pc.yml','pack-build.yml','pack-srv.yml',
          'pc-client.yml','release-jars.yml','rp-lite.yml','tunnel-test.yml',
          'check-live.yml','oci-cloudshell.yml','oci-probe.yml','oci-vm.yml',
          'pc-cp.yml','pc-functity.yml','pc-install.yml','pc-oldcfg.yml',
          'pc-probe.yml','pc-serverd.yml','runner-probe.yml','site-auto.yml',
          'pack-test.yml'}
for f in files:
    try:
        data=yaml.load(f.read_text(), Loader=yaml.BaseLoader)
        assert isinstance(data, dict)
        if f.name in legacy:
            assert list(data['on']) == ['workflow_dispatch']
            assert data['permissions']['contents'] == 'read'
            assert 'self-hosted' not in f.read_text()
    except (yaml.YAMLError, AssertionError, KeyError) as exc:
        raise SystemExit(f'YAML/SAFETY FAIL {f}: {exc}')
build=yaml.load(Path('.github/workflows/functity-build.yml').read_text(), Loader=yaml.BaseLoader)
assert list(build['on']) == ['workflow_dispatch'] and build['permissions']['contents'] == 'read'
print(f'YAML PASS: {len(files)} files; retired workflows manual-only/read-only; build manual/read-only')
bat=Path('tools/FunCity-Update.bat').read_text()
front=bat.split(':full\n', 1)[0]
assert 'if /I "%~1"=="--lean-test" goto blocked' in front
assert 'if /I "%~1"=="--full" goto blocked' in front
assert front.index(':blocked\n') < front.index('exit /b 2')
assert 'goto lean' not in front and 'goto full' not in front
print('updater all modes fail-closed PASS (static only; no Windows execution)')
page=Path('site/index.html').read_text(encoding='utf-8')
from runpy import run_path
assert page == run_path('site/build_site.py')['HTML']
assert 'Client Lite în validare' in page and 'TPS susținut' not in page
site=yaml.load(Path('.github/workflows/site.yml').read_text(), Loader=yaml.BaseLoader)
assert list(site['on']) == ['workflow_dispatch']
print('public site static claims PASS; publication requires manual dispatch')
PY

export PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="scripts${PYTHONPATH:+:$PYTHONPATH}"
python3 - <<'PY'
from fc_fakeplayer_smoke import LIST
from fc_bench import parse_tps_mspt
assert LIST.search('There are 3 of a max of 20 players online: A, B, C').group(1)=='3'
assert parse_tps_mspt(['TPS: 19.9', 'MSPT 33.0 ms'])[:2]==([19.9],[33.0])
print('smoke parsers PASS (NU este un boot Minecraft)')
PY
python3 scripts/fc_client_audit.py --self-test
python3 scripts/fc_client_audit.py >/dev/null
python3 - <<'PY'
from fc_client_audit import INVENTORY
from pathlib import Path
inventories=INVENTORY.findall(Path('diag/pc-client.txt').read_text())
assert len(inventories)==2 and inventories[0]==inventories[1]
assert len(inventories[0].split(', '))==25
selection=Path('agent/selectie-lite.md').read_text()
assert all(tag in selection for tag in ('Conținut RP (11)', 'Biblioteci ale conținutului (4)',
                                     'Pornire/RAM/randare (6)', 'Vizibilitate (3)', 'Compatibilitate XP (1)'))
print('Lite selection 25 historical names / five role groups PASS (names only)')
PY
python3 - <<'PY'
from pathlib import Path
import re, subprocess
text=subprocess.check_output(['git','show','b1ec20c:docs/ENGINE-PACK-AUDIT.md'], text=True)
source=text.split('<details><summary>Toate cele 36 de moduri',1)[1].split('</details>',1)[0]
names=set(re.findall(r'^- `([^`]+\.jar)`$', source, re.M))
chosen=re.findall(r'^\|\s*\d+\s*\| `([^`]+\.jar)` \|', Path('agent/decizie-server-36.md').read_text(), re.M)
assert len(names)==len(chosen)==len(set(chosen))==36 and set(chosen)==names
print('server 36/36 historical JAR names PASS (static archive, not live)')
PY
echo 'client inventory + historical handshake audit PASS (static, not Forge login/FPS)'
python3 scripts/fc_mrpack_audit_test.py
python3 scripts/fc_lite_repack_test.py
echo 'Lite mrpack audit + 24-mod RP voice repack fixtures PASS (synthetic, not a real import)'
python3 scripts/fc_pack_stage_test.py
echo 'server mod A/B stage fixtures PASS (no Java boot or player FPS)'
python3 scripts/fc_plugin_audit_test.py
echo 'plugin metadata parser fixtures PASS (synthetic; no live audit)'

echo "F0: patches on exact upstream commit $PIN (disposable source)"
if [ "${FC_INIT_OFFLINE:-0}" = 1 ]; then
  echo 'BLOCAT: offline mode skips pinned-source patch check (not PASS)' >&2
  exit 2
fi
SRC="$TMP/source"
if timeout 90 git clone -q -b 1.16.5 https://github.com/TiangongCraft/Tenet "$SRC" &&
   git -C "$SRC" checkout -q --detach "$PIN" &&
   test "$(git -C "$SRC" rev-parse HEAD)" = "$PIN"; then
  echo 'source: git pinned'
else
  # One alternate transport, not another source or a changed commit.
  rm -rf -- "$SRC"
  mkdir -p "$SRC"
  curl -fsSL --max-time 90 "https://codeload.github.com/TiangongCraft/Tenet/tar.gz/$PIN" | tar -xz -C "$SRC" --strip-components=1
  test -s "$SRC/src/main/java/com/mohistmc/MohistMC.java"
  echo 'source: GitHub archive of pinned commit (fallback)'
fi
for patch in "$ROOT"/functity/buildfix/*.patch "$ROOT"/functity/patches/*.patch; do
  git -C "$SRC" apply --check "$patch"
  git -C "$SRC" apply "$patch"
  echo "patch PASS: $(basename "$patch")"
done
grep -q 'NAME = "FunCity"' "$SRC/src/main/java/com/mohistmc/MohistMC.java"
echo 'F0 PASS: syntax, parsers and all pinned source patches. No server/JAR/client was changed.'
