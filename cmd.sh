export PATH=$PATH:/usr/bin:/bin:/usr/local/bin
echo "=== INAINTE ==="
df -h ~ | tail -1
echo "=== CE OCCUPA CASA ==="
du -sh ~/* ~/.[a-z]* 2>/dev/null | sort -rh | head -12
echo "=== STERG GUNOI ==="
rm -rf ~/mcserver ~/lite-peek ~/lite.zip ~/j11.tgz ~/c.sh ~/.claie.sh.bak 2>/dev/null
rm -rf /tmp/* 2>/dev/null
echo "=== DUPA ==="
df -h ~ | tail -1
