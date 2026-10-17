export PATH=$PATH:/usr/bin:/bin:/usr/local/bin
pgrep -af "lr-loop|ssh.*localhost.run" | grep -v grep | cut -c1-90
echo "== LOG COMPLET =="; tail -25 /tmp/lr.log
