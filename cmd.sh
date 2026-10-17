export PATH=$PATH:/usr/bin:/bin:/usr/local/bin
echo "== PLAYIT LOG =="
head -25 /tmp/playit.log 2>/dev/null
echo "== help =="
~/playit --help 2>&1 | head -8
echo "== cfg location =="
ls -la ~/.playit/ ~/.config/playit/ 2>/dev/null | head -8
