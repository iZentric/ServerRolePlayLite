#!/usr/bin/env bash
# ENSURE-UP — lasa serverul PORNIT cand iese scriptul, chiar daca a crapat pe jumatate.
# CRITIC: stergem RUNNER_TRACKING_ID din mediu! Altfel GitHub Actions Runner omoara cu SIGKILL
# toate procesele copil (c.sh, java, frpc) in secunda in care jobul se termina ("Complete job")!
unset RUNNER_TRACKING_ID
export -n RUNNER_TRACKING_ID 2>/dev/null || true
D=$HOME/cuantic-live
REPO=iZentric/ServerRolePlayLite
BR=${ARENA_BRANCH:-arena/a29b4ef4-serverroleplaylite}
cd "$D" 2>/dev/null || { echo "ensure-up: lipsa $D (ruleaza intai wake.sh)"; exit 0; }
echo "92.5.171.150:25565" > "$D/ADRESA" 2>/dev/null || true

# Proprietarul a cerut explicit "dai on la server" -> stergem orice OPRIT vechi
rm -f "$D/OPRIT" 2>/dev/null || true

# 0) Repara dublura veche plugins/plugins/ si asigura OP in ops.json (UUID real OfflinePlayer MD5 v3)
if [ -d "$D/plugins/plugins" ]; then
  mv -f "$D"/plugins/plugins/*.jar "$D/plugins/" 2>/dev/null || true
  rmdir "$D/plugins/plugins" 2>/dev/null || true
fi
python3 - "$D/ops.json" "iZentric" <<'PYP' 2>/dev/null || true
import hashlib, json, os, sys, uuid
f, nume = sys.argv[1], sys.argv[2]
b = bytearray(hashlib.md5(("OfflinePlayer:" + nume).encode("utf-8")).digest())
b[6] = (b[6] & 0x0f) | 0x30; b[8] = (b[8] & 0x3f) | 0x80
u = str(uuid.UUID(bytes=bytes(b)))
d = []
if os.path.isfile(f):
    try: d = json.load(open(f, encoding="utf-8"))
    except Exception: d = []
if not isinstance(d, list): d = []
d = [x for x in d if isinstance(x, dict) and str(x.get("name", x.get("Name", ""))).lower() != nume.lower()]
d.append({"uuid": u, "name": nume, "level": 4, "bypassesPlayerLimit": True})
json.dump(d, open(f, "w", encoding="utf-8"), indent=2)
PYP

# 1) supervisorul = cel care tine java, runner-ul GitHub si frpc-ul in viata
cp -f "$GITHUB_WORKSPACE/scripts/cuantic-args.sh" "$HOME/cuantic-args.sh" 2>/dev/null || curl -fsSLo "$HOME/cuantic-args.sh" --max-time 15 "https://raw.githubusercontent.com/$REPO/$BR/scripts/cuantic-args.sh" 2>/dev/null || true
[ -f "$HOME/cuantic-args.sh" ] && bash "$HOME/cuantic-args.sh" "$D" >/dev/null 2>&1 || true
if ! pgrep -f 'bash .*c\.sh' >/dev/null 2>&1; then
  cp -f "$GITHUB_WORKSPACE/scripts/cuantic-live.sh" "$HOME/c.sh" 2>/dev/null || curl -fsSLo "$HOME/c.sh" --max-time 25 \
    "https://raw.githubusercontent.com/$REPO/$BR/scripts/cuantic-live.sh" || true
  if [ -f "$HOME/c.sh" ]; then
    ( env -u RUNNER_TRACKING_ID setsid bash "$HOME/c.sh" >> "$D/sup.log" 2>&1 < /dev/null & )
    echo "ensure-up: supervisor PORNIT (fara RUNNER_TRACKING_ID)"
  else
    echo "ensure-up: FARA c.sh - nu pot porni supervisorul"
  fi
else
  echo "ensure-up: supervisor alive"
fi

# 2) daca nici dupa 100 s nu e java, dam un start direct (sigurenta la un supervisor stricat)
if ! pgrep -f 'java @unix_args' >/dev/null 2>&1; then
  for i in 1 2 3 4 5 6 7 8 9 10; do sleep 10; pgrep -f 'java @unix_args' >/dev/null 2>&1 && break; done
fi
if ! pgrep -f 'java @unix_args' >/dev/null 2>&1 && [ -f unix_args.txt ]; then
  J=$HOME/.local/jdk17/bin/java; [ -x "$J" ] || J=$(ls /usr/lib/jvm/java-17*/bin/java 2>/dev/null | head -1)
  [ -p in.fifo ] || mkfifo -m 600 in.fifo
  ( env -u RUNNER_TRACKING_ID setsid "$J" @unix_args.txt 3<>"$D/in.fifo" <&3 >> "$D/live.log" 2>&1 < /dev/null & )
  echo "ensure-up: java pornita direct (fallback)"
fi
sleep 3
P=$(ss -ltn 2>/dev/null | grep -c ':25565')
echo "ensure-up: java=$(pgrep -f 'java @unix_args' >/dev/null && echo DA || echo NU) port25565=$P"

# 2b) Tunelul public frpc -> 92.5.171.150:25565 (fara el, portul 25565 e doar pe localhost!)
if [ ! -f "$HOME/frpc.toml" ]; then
  printf 'serverAddr = "92.5.171.150"\nserverPort = 443\nauth.method = "token"\nauth.token = "pateu-de-codru-7"\n\n[[proxies]]\nname = "mc"\ntype = "tcp"\nlocalIP = "127.0.0.1"\nlocalPort = 25565\nremotePort = 25565\n' > "$HOME/frpc.toml"
fi
if [ -x "$HOME/frpc" ] && ! pgrep -f 'frpc -c' >/dev/null 2>&1; then
  ( env -u RUNNER_TRACKING_ID setsid "$HOME/frpc" -c "$HOME/frpc.toml" >> "$HOME/frpc.log" 2>&1 < /dev/null & )
  sleep 2
  echo "ensure-up: frpc PORNIT ($(pgrep -f 'frpc -c' | head -1))"
fi

# 3) MOVER pentru puntea de comenzi: cmd.in -> stdin java (in.fifo). Fara el, `op NUME`
#    ramanea neconsumat in fisier (verificat: cmd.in_neconsumat=[op iZentric list]).
if [ -f "$D/cmd.in" ]; then
  if ! pgrep -f "cuantic-mov" >/dev/null 2>&1; then
    printf '#!/usr/bin/env bash\n# cuantic-mov - duce comenzile din cmd.in in stdoin java\nunset RUNNER_TRACKING_ID\nD=%s\nwhile :; do\n  [ -p "$D/in.fifo" ] || mkfifo -m 600 "$D/in.fifo"\n  tail -n +$(( $(wc -l < "$D/cmd.in" 2>/dev/null || echo 0) + 1 )) -F "$D/cmd.in" >> "$D/in.fifo" 2>/dev/null\n  sleep 3\ndone\n' "$D" > "$D/cuantic-mov.sh"
    chmod +x "$D/cuantic-mov.sh"
    ( env -u RUNNER_TRACKING_ID setsid bash "$D/cuantic-mov.sh" >> "$D/mov.log" 2>&1 < /dev/null & )
    echo "ensure-up: mover cmd.in->in.fifo PORNIT"
  else
    echo "ensure-up: mover alive"
  fi
fi
