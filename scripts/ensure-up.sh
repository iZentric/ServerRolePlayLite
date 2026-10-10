#!/usr/bin/env bash
# ENSURE-UP — lasa serverul PORNEST cand iese scriptul, chiar daca a crapat pe jumatate.
# Il cheama tot ce opreste java (apply/tune/jvm-tune/ram-test/brand/no-login/op) prin `trap ... EXIT`
# si il cheama si jobul de heartbit. Nu atinge lumea, nu rescrie configuri: doar aprinde ce lipseste.
D=$HOME/cuantic-live
REPO=iZentric/ServerRolePlayLite
BR=${ARENA_BRANCH:-arena/a29b4ef4-serverroleplaylite}
cd "$D" 2>/dev/null || { echo "ensure-up: lipsa $D (ruleaza intai wake.sh)"; exit 0; }

# 1) supervisorul = cel care tine java, runner-ul GitHub si frpc-ul in viata
if ! pgrep -f 'bash .*c\.sh' >/dev/null 2>&1; then
  [ -f "$HOME/c.sh" ] || curl -fsSLo "$HOME/c.sh" --max-time 25 \
    "https://raw.githubusercontent.com/$REPO/$BR/scripts/cuantic-live.sh" || true
  if [ -f "$HOME/c.sh" ]; then
    ( setsid bash "$HOME/c.sh" >> "$D/sup.log" 2>&1 < /dev/null & )
    echo "ensure-up: supervisor PORNIT (el aprinde java in ~15 s)"
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
  ( setsid "$J" @unix_args.txt 3<>"$D/in.fifo" <&3 >> "$D/live.log" 2>&1 < /dev/null & )
  echo "ensure-up: java pornita direct (fallback)"
fi
sleep 3
P=$(ss -ltn 2>/dev/null | grep -c ':25565')
echo "ensure-up: java=$(pgrep -f 'java @unix_args' >/dev/null && echo DA || echo NU) port25565=$P"
