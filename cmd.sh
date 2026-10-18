export PATH=$PATH:/usr/bin:/bin:/usr/local/bin
cd /tmp
curl -sfLo a.zip "https://github.com/iZentric/ServerRolePlayLite/releases/download/funcity/FunCity-1.2.0.mrpack" && echo "1.2.0 bat-target: $(stat -c%s a.zip)B (1.2.1 are 135770515)"
