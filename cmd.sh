export PATH=$PATH:/usr/bin:/bin:/usr/local/bin:~/bin
echo "=== CITESTE-MA ==="; head -25 ~/cuantic-live/CITESTE-MA.txt 2>/dev/null
echo "=== ADRESA ==="; cat ~/cuantic-live/ADRESA 2>/dev/null
echo "=== BIN (java?) ==="; ls ~/bin 2>/dev/null | head -6; find ~/bin -maxdepth 3 -name java -type f 2>/dev/null | head -2
echo "=== FRP ==="; ls ~/frp_0.71.0_linux_arm64 2>/dev/null | head -5; cat ~/frp*/frpc.toml ~/frp*/frpc.ini 2>/dev/null | head -12
echo "=== MAI TRASE o data? ==="; pgrep -fa java | head -3; tail -2 ~/cuantic-live/boot.log 2>/dev/null
