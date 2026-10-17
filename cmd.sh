export PATH=$PATH:/usr/bin:/bin:/usr/local/bin
echo "== test VPS vechi cu keep.key =="
chmod 600 ~/.oci/keep.key 2>/dev/null
for U in oracle ubuntu opc root centos; do
  R=$(timeout 8 ssh -i ~/.oci/keep.key -o StrictHostKeyChecking=no -o ConnectTimeout=5 -o BatchMode=yes $U@92.5.171.150 "echo TRAIT; hostname; id -u" 2>&1)
  echo "$U: $(echo "$R" | head -2 | tr '\n' ' ')"
  echo "$R" | grep -q TRAIT && { echo ">>> VPS VIU cu user $U"; echo "$U" > ~/vps-user.txt; break; }
done
ping -c1 -W2 92.5.171.150 >/dev/null 2>&1 && echo "ping: raspunde" || echo "ping: niciun raspuns (gazda moarta/filtrata)"
