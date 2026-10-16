#!/usr/bin/env bash
# ops/ops.sh — singura unealta de pe server. Moduri: status | log | backup
# Citeste comanda din fisierul ops/cmd.txt (prima linie). Zero dependente.
set -u
D="$HOME/cuantic-live"                      # directorul live
OUT="$HOME/functity-out"; mkdir -p "$OUT"
R="$OUT/ops-out.txt"; : > "$R"
say(){ echo "$*" | tee -a "$R"; }
CMD=$(head -1 "$1" 2>/dev/null | awk '{print $1}')
JAR=$(ls -t "$D"/*.jar 2>/dev/null | head -1)
case "${CMD:-status}" in
  status)
    say "== STATUS $(date -u '+%F %T') =="
    say "jvm: $(pgrep -fa '[j]ava' | head -1 | cut -c1-120 || SUS)"
    say "supervisor c.sh: $(pgrep -f "bash .*[/]c[.]sh" >/dev/null && say VIE || say absent)"
    say "jar: $(basename "${JAR:-nu}")"
    say "world: $(du -sm "$D/world" 2>/dev/null | cut -f1) MiB"
    say "disk liber: $(df -m "$HOME" | tail -1 | awk '{print $4}') MiB"
    say "port 25565: $( (exec 3<>/dev/tcp/127.0.0.1/25565) 2>/dev/null && say OPEN || say INCHIS )"
    ;;
  log)
    say "== LOG (ultimele 40 din server.log) =="
    tail -40 "$D/logs/latest.log" 2>/dev/null | tail -40 >> "$R"; cat "$R" 2>/dev/null | tail -44
    ;;
  backup)
    say "== BACKUP world (tar.gz in functity-out, gata de urcat pe release) =="
    tar -C "$D" -czf "$OUT/worldsync.tar.gz" world 2>>"$R"
    say "  $(du -m "$OUT/worldsync.tar.gz" 2>/dev/null | cut -f1) MiB sha $(sha256sum "$OUT/worldsync.tar.gz" 2>/dev/null | cut -c1-12) $(date -u '+%F %T')"
    ;;
  *) say "mod necunoscut: $CMD (disponibil: status | log | backup)";;
esac
