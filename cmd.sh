export PATH=$PATH:/usr/bin:/bin
grep -A 2 "issued server command: /tps" ~/cuantic-live/boot.log | tail -3 | sed "s/\x1b\[[0-9;]*m//g"
grep -E "Done \(|previously" ~/cuantic-live/boot.log | tail -2
uptime
