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
