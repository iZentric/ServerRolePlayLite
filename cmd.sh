export PATH=$PATH:/usr/bin:/bin:/usr/local/bin
echo "=== CUANTIC-LIVE: ce e inauntru? ==="
ls ~/cuantic-live 2>/dev/null | head -14
[ -d ~/cuantic-live/world ] && echo "WORLD AICI: $(du -sh ~/cuantic-live/world | cut -f1)" || echo "fara world aici"
echo "=== STERG DEJEAUNA ==="
rm -rf ~/.cache ~/.local/share/Trash ~/.local/lib/python3.*/site-packages 2>/dev/null
rm -rf ~/externals ~/_work ~/_diag ~/functity-out ~/funcity-backup ~/funcity-live 2>/dev/null
rm -f ~/actions-runner-linux-arm64-*.tar.gz 2>/dev/null
sync
echo "=== DUPA ==="
df -h ~ | tail -1
echo "=== TOP RAMAS ==="
du -sh ~/* ~/.[a-z]* 2>/dev/null | sort -rh | head -8
