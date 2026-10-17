export PATH=$PATH:/usr/bin:/bin:/usr/local/bin
echo "== procese =="; pgrep -af "ssh|serveo" | cut -c1-100 | head -5
echo "== log serveo =="; tail -8 /tmp/serveo.log
echo "== addr fisiere =="; cat ~/addr-last.txt 2>/dev/null; echo; ls -la ~/addr*.txt 2>/dev/null
echo "== test local al tunelului prin serveo (edge self-connect) =="
timeout 8 bash -c 'echo > /dev/tcp/serveousercontent.com/43016' 2>&1 && echo "EDGE: port deschis si el raspunde" || echo "EDGE: refuzat si de pe masina"
ss -lnt 2>/dev/null | grep -q ":25565 " && echo "MC local: VIU" || echo "MC local: MORT"
