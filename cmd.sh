export PATH=$PATH:/usr/bin:/bin:/usr/local/bin
cd ~
pkill -f serveo-loop; pkill -f "ssh.*serveo"; sleep 2
systemctl --user status playit --no-pager 2>/dev/null | head -3
~/.local/bin/playit --version 2>/dev/null || ~/playit --version 2>/dev/null || ls ~/playit* ~/.local/bin/ 2>/dev/null | head
~/.local/bin/playit service install 2>&1 | head -3
