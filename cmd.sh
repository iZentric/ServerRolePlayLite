export PATH=$PATH:/usr/bin:/bin:/usr/local/bin
chmod 600 ~/.ssh/cuantic_oci 2>/dev/null
ssh-keygen -lf ~/.ssh/cuantic_oci.pub 2>/dev/null
for U in oracle ubuntu cloud-user opc root debian admin; do
  R=$(timeout 6 ssh -i ~/.ssh/cuantic_oci -o StrictHostKeyChecking=no -o ConnectTimeout=4 -o BatchMode=yes $U@92.5.171.150 "echo TRAIT; whoami; free -m | awk '/Mem/{print \$2}'" 2>&1)
  if echo "$R" | grep -q TRAIT; then
    echo ">>> VPS VIU cu $U:"; echo "$R" | head -3
    echo "$U" > ~/vps-user.txt; break
  fi
done
cat ~/vps-user.txt 2>/dev/null || echo "v62: niciun user cu cuantic_oci"
