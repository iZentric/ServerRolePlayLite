echo SALUT de la cloudshell: $(whoami)@$(hostname)
java -version 2>&1 | head -1
curl -sI https://api.papermc.io 2>/dev/null | head -1 || echo "papermc: net OK"
free -m | head -2
nproc
