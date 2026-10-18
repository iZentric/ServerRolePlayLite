export PATH=$PATH:/usr/bin:/bin:/usr/local/bin
cd ~/cuantic-live
echo "== PLUGINI complete =="; ls plugins/*.jar 2>/dev/null | xargs -n1 basename 2>/dev/null
echo "== directoare plugini =="; ls -d plugins/*/ 2>/dev/null | xargs -n1 basename 2>/dev/null | tr '\n' ' '; echo
echo "== suspecti: cine sunt =="
for j in "mods/bwncr-1.16.5-3.10.16.jar" "mods/mapperbase-1.16.5-2.4.0.0.jar" "mods/Modernxl 1.16.5.jar" "mods/SeleneChat-0.2.0-all.jar" "mods/Pizzaland_v68.jar"; do
  [ -f "$j" ] || { echo "LIPSA: $j"; continue; }
  echo "--- $j"
  unzip -p "$j" META-INF/mods.toml 2>/dev/null | grep -aE "modId|displayName|loader" | head -5
done
echo "== cine cere lib-urile (modId referentiit in dependencies) =="
for lib in bwncr mapperbase obfuscate selene; do
  who=""; cnt=0
  for f in mods/*.jar; do
    base=$(basename "$f")
    [ "$base" = "$lib"* ] && continue
    if unzip -p "$f" META-INF/mods.toml 2>/dev/null | grep -aqE "modId *= *\"$lib\""; then who="$who $base"; cnt=$((cnt+1)); fi
  done
  echo "lib '$lib': cerut de $cnt:$who"
done
