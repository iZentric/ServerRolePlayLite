#!/usr/bin/env bash
# CHK — doar citeste: traieste serverul dupa job? e ascultat portul? raspunde dinafara?
LOG=/tmp/chk.txt; : > $LOG
say(){ echo "$*" | tee -a $LOG; }
DIR=$HOME/cuantic-live
say "== CHK — $(date -u '+%F %T UTC') =="
say "tmux: $(tmux ls 2>&1 | tr '\n' ';')"
say "java: $(pgrep -fc 'unix_args.txt') procese | bore: $(pgrep -fc 'bore local')"
say "uptime: $(uptime | sed 's/^ *//')"
say "ss 25565:"; ss -lnt 2>/dev/null | grep -E '25565|24454' | sed 's/^/  /' >> $LOG
say "live.log: $(wc -l < $DIR/live.log 2>/dev/null) linii | $(grep -m1 -oE 'Done \([0-9.]+s\)' $DIR/live.log 2>/dev/null)"
say "log final: $(tail -3 $DIR/live.log 2>/dev/null | tr '\n' ' ' | cut -c1-260)"
say "disc: $(df -h "$HOME" 2>/dev/null | tail -1)"
say "fisiere: $(ls "$DIR" 2>/dev/null | tr '\n' ' ' | cut -c1-200)"
say "pack marcat: $(cat "$DIR/.pack" 2>/dev/null || echo FARA-MARCARE)"
say "unix_args: $(head -4 "$DIR/unix_args.txt" 2>/dev/null | tr '\n' ' ')"
say "erori-cheie: $(grep -aiE 'error|exception|Unrecognized|Address already|Done \(' "$DIR/live.log" 2>/dev/null | tail -5 | cut -c1-140 | tr '\n' '|')"
say "=== ISTORIC PORNIRI / OPRIRI / JUCATORI (live.log) ==="
grep -anE '==== pornire|Done \(|Stopping|Server closed|iZentric|lost connection|disconnect|CrashReport|OutOfMemory|Killed|watchdog|Watchdog' "$DIR/live.log" 2>/dev/null | tail -45 >> $LOG
say "=== ULTIMELE 60 LINII DIN live.log ==="
tail -60 "$DIR/live.log" 2>/dev/null | sed "s/$(printf '\033')\[[0-9;]*[a-zA-Z]//g" >> $LOG
say "=== ULTIMELE 35 LINII DIN sup.log ==="
tail -35 "$DIR/sup.log" 2>/dev/null >> $LOG
say "=== CRASH REPORTS ==="
ls -lt "$DIR/crash-reports" 2>/dev/null | head -5 >> $LOG
LATEST_CRASH=$(ls -t "$DIR/crash-reports"/*.txt 2>/dev/null | head -1)
[ -n "$LATEST_CRASH" ] && head -45 "$LATEST_CRASH" >> $LOG
say "=== DMESG OOM ==="
dmesg -T 2>/dev/null | grep -iE 'oom|killed process|java' | tail -10 >> $LOG || true
say "sup.log: $(tail -5 "$DIR/sup.log" 2>/dev/null | tr '\n' '|' | cut -c1-260)"
say "frpc.toml: $(grep -c . "$HOME/frpc.toml" 2>/dev/null || echo NICIFISIER)"
A=$(cat $DIR/ADRESA 2>/dev/null)
say "adresa din fisier: ${A:-NU}"
for i in 1 2 3; do
  R=$(curl -fsS --max-time 25 "https://api.mcsrvstat.us/3/${A:-bore.pub:1}" 2>/dev/null)
  say "  dinafara $i: $(echo "$R" | grep -oE '\"online\":(true|false)') | $(echo "$R" | grep -oE '\"version\":\"[^\"]*\"') | $(echo "$R" | grep -oE '\"motd\":\[[^]]*\]') $(echo "$R" | grep -oE '\"message\":\"[^\"]+\"' | head -1)"
  case "$R" in *'"online":true'*) break;; esac
  sleep 8
done
mkdir -p "$GITHUB_WORKSPACE/analysis"; cd "$GITHUB_WORKSPACE"
{ printf '# CHK — %s\n\n' "$(date -u '+%F %T UTC')"; echo '```'; cat $LOG; echo '```'; } > analysis/chk.md
git add -f analysis/chk.md; git commit -q -m "chk" || true
git pull --rebase -q origin "$GITHUB_REF_NAME" || true; git push -q origin "$GITHUB_REF_NAME" || true
say "GATA"; exit 0

# PROBĂ PLUGINS/BRAND (cerută de verdictul T5=0 linii de incarcare si T10CADE): catologul zice
# altfel decat numaratoarea noastra - masuram direct in live.log.
L="$D/live.log"; [ -f "$L" ] || L=$(ls -t "$D"/*.log 2>/dev/null | head -1)
{ echo "--- plugins/brand in log:";
  echo "fisiere in plugins: $(ls "$D"/plugins/*.jar 2>/dev/null | wc -l) (Cuantic-Brand: $(ls "$D"/plugins/ 2>/dev/null | grep -ci cuantic))"
  echo "linii Enabling: $(tail -4000 "$L" 2>/dev/null | grep -aci 'Enabling') | 'Server booting'|'Done': $(tail -4000 "$L" 2>/dev/null | grep -aci 'Done (')"
  echo "Cuantic in log (ultimele 4000 linii): $(tail -4000 "$L" 2>/dev/null | grep -aci cuantic)"
  tail -4000 "$L" 2>/dev/null | grep -ai "Cuantic/version" | tail -2
  echo "esecuri plugin: $(tail -4000 "$L" 2>/dev/null | grep -aiE 'Could not (load|enable)|error occurred while enabling' | wc -l)"
  tail -4000 "$L" 2>/dev/null | grep -aiE 'Could not (load|enable)|error occurred while enabling' | tail -3 | cut -c1-160
} >> "$ANALYSIS/chk.md" 2>/dev/null || true
