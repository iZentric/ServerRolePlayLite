export PATH=$PATH:/usr/bin:/bin:/usr/local/bin
echo "ora: $(date +%H:%M:%S)"
ls -la ~/cuantic-live/plugins/CoreProtect.jar 2>/dev/null | awk '{print "CP.jar:",$5,"B",$6,$7,$8}'
pgrep -f "java.*-jar" >/dev/null && echo "java: RULEAZA (pid $(pgrep -f 'java.*-jar'|head -1))" || echo "java: mort"
grep -aE "Done \(|CoreProtect" ~/cuantic-live/boot.log 2>/dev/null | tail -5
ss -lnt 2>/dev/null | grep -q ":25565 " && echo "PORT 25565: DESCHIS" || echo "PORT: inchis"
ls -la ~/cuantic-live/plugins/CoreProtect/ 2>/dev/null | head -5
