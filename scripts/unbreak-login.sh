#!/usr/bin/env bash
# UNBREAK-LOGIN — mod normal: scoage flag-ul /premium. Cu FLAG=DA in mediul jobului, face inversul
# (il pune premium = zero parola, skin real) pentru un cont platit chiar in launcher.
# Mod normal: jucatorul si-a dat /premium (FastLogin) si nu mai poate intra:
# serverul cere sesiune valida de la Mojang unui cont cracked => "Invalid session" / "Failed to verify username".
# Remediu: scoate flag-ul premium din bazele SQLite ale pluginurilor, dezactivea comanda /premium
# pentru ca sa nu se mai intample, apoi reporneste serverul ca sa citeasca noile valori.
# keepalive: orice iesire (si eroare, si Ctrl-C) reporneste ce am oprit noi
trap 'bash "$(dirname "$0")/ensure-up.sh" >/dev/null 2>&1 || true' EXIT INT TERM
D=$HOME/cuantic-live
J=$HOME/.local/jdk17/bin/java
[ -x "$J" ] || J=$(ls /usr/lib/jvm/java-17*/bin/java 2>/dev/null | head -1)
P=${NUME_TAU:-iZentric}
V="FIX: nume=$P"

cd "$D" 2>/dev/null || { echo "FIX: lipsa $D"; echo "FIX: lipsa directorul serverului" > /tmp/fixverdict; exit 0; }

# ---- 1. scoage flag-ul premium din orice SQLite care are coloana *_premium ----
python3 - "$P" <<'PY' 2>&1 | tee /tmp/fixdb.txt
import sqlite3, glob, os, re, sys
name = sys.argv[1] if len(sys.argv) > 1 else "iZentric"
D = os.path.expanduser("~/cuantic-live/plugins")
schimbat = 0
dbs = glob.glob(D + "/**/*.db", recursive=True) + glob.glob(D + "/**/*.sqlite", recursive=True)
print("baze gasite:", len(dbs))
for db in dbs:
    try:
        con = sqlite3.connect(db); cur = con.cursor()
        tabs = [r[0] for r in cur.execute("select name from sqlite_master where type='table'")]
    except Exception as e:
        print(" ", os.path.basename(db), "deschidere esuata:", str(e)[:80]); continue
    for t in tabs:
        try:
            cols = [r[1] for r in cur.execute("pragma table_info(%s)" % t)]
        except Exception:
            continue
        pc = [c for c in cols if re.search("premium", c, re.I)]
        nc = [c for c in cols if c.lower() in ("user", "username", "name", "player", "playername")]
        if not pc or not nc:
            continue
        try:
            before = cur.execute("select %s,%s from %s where lower(%s)=?" % (nc[0], pc[0], t, nc[0]), (name.lower(),)).fetchall()
            val = 1 if os.environ.get("FLAG") == "DA" else 0
            n = cur.execute("update %s set %s=? where lower(%s)=?" % (t, pc[0], nc[0]), (val, name.lower())).rowcount
            con.commit()
            after = cur.execute("select %s,%s from %s where lower(%s)=?" % (nc[0], pc[0], t, nc[0]), (name.lower(),)).fetchall()
            print("  %s:%s.%s inainte=%s dupa=%s randuri_update=%s" % (os.path.basename(db), t, pc[0], before, after, n))
            schimbat += n
        except Exception as e:
            print("  ", os.path.basename(db), t, "update esuat:", str(e)[:110])
    con.close()
print("TOTAL randuri desmarcate:", schimbat)
PY
grep -q "TOTAL randuri desmarcate: 0" /tmp/fixdb.txt && V="$V db=0-randuri" || V="$V db=$(grep -o 'TOTAL.*' /tmp/fixdb.txt | tail -1 | cut -c1-40)"

# ---- 2. opresc comanda /premium ca sa nu-si mai faca rau singur ----
CFG="$D/plugins/FastLogin/config.yml"
if [ -f "$CFG" ]; then
  cp "$CFG" "$CFG.bak.$(date +%s)"
  if [ "${FLAG:-NU}" = DA ]; then V="$V (mod:FLAG=DA)"; fi
  python3 - "$CFG" <<'PY'
import re, sys
p = sys.argv[1]; s = open(p).read()
if re.search(r"^\s*premium\s*:", s, re.M):
    s = re.sub(r"^(\s*premium\s*:).*$", r"\1 false", s, flags=re.M)
    open(p, "w").write(s); print("config: /premium -> false")
else:
    s = s.replace("Commands:", "Commands:\n  premium: false", 1)
    open(p, "w").write(s); print("config: adaugat premium: false sub Commands:")
PY
  V="$V config=SCOS"
else
  V="$V config=LIPSA"
fi

# ---- 3. repornire ca sa citeasca DB + config ----
pkill -TERM -f 'java @unix_args' 2>/dev/null; sleep 20
pgrep -f 'java @unix_args' >/dev/null 2>&1 && { pkill -KILL -f 'java @unix_args'; sleep 6; }
[ -p in.fifo ] || mkfifo -m 600 in.fifo
setsid tail -f /dev/null > "$D/in.fifo" &
setsid "$J" @unix_args.txt < "$D/in.fifo" > "$D/live.log" 2>&1 &
PORNIT=NU
for i in $(seq 1 45); do
  sleep 5
  sed -e 's/\x1b\[[0-9;]*[a-zA-Z]//g' "$D/live.log" 2>/dev/null | grep -qaE 'Done \([0-9.]+s\)' && { PORNIT=DA; break; }
done
V="$V restart=$PORNIT"
sleep 6
A=$(cat "$D/ADRESA" 2>/dev/null)
S=$(curl -fsS --max-time 20 "https://api.mcsrvstat.us/2/92.5.171.150:25565" 2>/dev/null)
echo "$S" | grep -q '"online":true' && V="$V online=DA" || V="$V online=NU"

echo "$V" > /tmp/fixverdict
mkdir -p "$GITHUB_WORKSPACE/analysis" 2>/dev/null && cd "$GITHUB_WORKSPACE"
{ echo "unbreak-login -- $(date -u '+%F %T UTC')"; echo "$V"; echo; cat /tmp/fixdb.txt;
  echo "log final:"; sed -e 's/\x1b\[[0-9;]*[a-zA-Z]//g' "$D/live.log" 2>/dev/null | tail -3; } > analysis/fix-login.md
git config user.name "cuantic-bot"; git config user.email "bot@cuantic.local"
git add -f analysis/fix-login.md >/dev/null 2>&1
git commit -q -m "$(echo "$V" | tr -d '"' | head -c 180)" || true
git pull --rebase -q origin "${GITHUB_REF_NAME:-arena/a29b4ef4-serverroleplaylite}" || true
git push -q origin "HEAD:${GITHUB_REF_NAME:-arena/a29b4ef4-serverroleplaylite}" || echo "push: nimic"
exit 0
