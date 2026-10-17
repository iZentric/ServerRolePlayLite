export PATH=$PATH:/usr/bin:/bin:/usr/local/bin
cd ~
echo "=== A: CE E INSTALAT IN LITE ==="
curl -sL -o lite.zip https://github.com/iZentric/ServerRolePlayLite/releases/download/lite/CUANTIC-Server-MaxLite-1.7.7.zip
ls -l lite.zip | awk '{print "zip bytes:",$5}'
mkdir -p lite-peek && cd lite-peek && unzip -oq ../lite.zip 2>/dev/null && find . -maxdepth 2 | head -25 && cd ~
echo "=== B: JAVA 11 (pentru Forge 1.16.5) ==="
if [ ! -x ~/j11/bin/java ]; then
  case $(uname -m) in aarch64) A=aarch64;; *) A=x64;; esac
  curl -sL "https://api.adoptium.net/v3/binary/latest/11/ga/linux/$A/jre/hotspot/normal/eclipse" -o j11.tgz && mkdir -p ~/j11 && tar xzf j11.tgz -C ~/j11 --strip-components=1 && rm -f j11.tgz
fi
~/j11/bin/java -version 2>&1 | head -1
echo "=== PASA 1 GATA ==="
