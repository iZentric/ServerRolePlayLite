export PATH=$PATH:/usr/bin:/bin:/usr/local/bin
echo "== cheia noastra =="; ssh-keygen -lf ~/.oci/keep.key.pub 2>/dev/null; ssh-keygen -lf ~/.oci/keep.key 2>/dev/null
echo "== alte chei pe masina =="; ls -la ~/.ssh/ 2>/dev/null | head -8
echo "== sshd deschis = gazda viva, mai incerc useri =="
for U in cloud-user debian ubuntu22 admin mc playit ec2-user fedora rocky oracleuser app; do
  R=$(timeout 6 ssh -i ~/.oci/keep.key -o StrictHostKeyChecking=no -o ConnectTimeout=4 -o BatchMode=yes $U@92.5.171.150 "echo TRAIT" 2>&1)
  echo "$R" | grep -q TRAIT && { echo ">>> VPS VIU cu $U"; echo "$U" > ~/vps-user.txt; break; }
done
cat ~/vps-user.txt 2>/dev/null || echo "(niciun user)"
echo "== port 22 verificat =="; timeout 4 bash -c 'echo > /dev/tcp/92.5.171.150/22' 2>&1 && echo "22: DESCHIS (ssd viu)" || echo "22: inchis"
