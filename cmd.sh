export PATH=$PATH:/usr/bin:/bin:/usr/local/bin
tail -12 /tmp/lr.log | cat -v | cut -c1-160
pgrep -af "ssh -n -i" | head -2 | cut -c1-120
