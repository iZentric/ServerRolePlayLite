#!/usr/bin/env bash
# Build the patched CatServer candidate privately on isolated Linux with JDK 17
# (build) and JDK 11 (smoke). Never publishes a JAR, touches a host or overwrites
# an existing directory. Workdir and resulting binary stay on THIS machine.
set -Eeuo pipefail
stage=preflight
trap 'rc=$?; echo "::error title=FunCity private build::STAGE_FAILED stage=$stage exit=$rc; private Gradle/server logs not uploaded" >&2' ERR
if [ "$#" -ne 2 ]; then
  echo 'usage: bash scripts/fc_funcity_build_private.sh NEW_OUTSIDE_REPO_WORKDIR JAVA11_BIN' >&2
  exit 2
fi
repo="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)"
parent="$(cd "$(dirname "$1")" && pwd -P)"
root="$parent/$(basename "$1")"
java11="$2"
case "$root/" in "$repo/"*) echo 'refusing a workdir inside the public repository' >&2; exit 2;; esac
if [ -e "$root" ] || [ -L "$root" ] || [ ! -f "$java11" ]; then
  echo 'new workdir and existing Java 11 executable required' >&2
  exit 2
fi
for tool in git python3 sha256sum java realpath; do command -v "$tool" >/dev/null || exit 2; done
java11="$(realpath "$java11")"  # Remain correct after cd into pinned source.
if ! java -version 2>&1 | head -n 1 | grep -Eq '(openjdk|java) version "17([.+"]|$)'; then
  echo 'JDK 17 must be active for the upstream build' >&2
  exit 2
fi
if ! "$java11" -version 2>&1 | head -n 1 | grep -Eq '(openjdk|java) version "11([.+"]|$)'; then
  echo 'Java 11 executable required for smoke test' >&2
  exit 2
fi
mkdir "$root"
stage=clone
source_dir="$root/source"
log="$root/private-build.log"
git clone -q --depth 1 --filter=blob:none --branch 23.05.26-1 \
  https://github.com/Luohuayu/CatServer.git "$source_dir"
test "$(git -C "$source_dir" rev-parse HEAD)" = '1d8d63138be77a606df2a5e940b960065948f983'
test -s "$source_dir/LICENSE" && grep -q 'LESSER GENERAL PUBLIC LICENSE' "$source_dir/LICENSE"
stage=patch
for patch in 0001-funcity-operator-identity.patch 0002-preserve-forge-block-place-cancellation.patch; do
  git -C "$source_dir" apply --check "$repo/functity/catserver/patches/$patch"
  git -C "$source_dir" apply "$repo/functity/catserver/patches/$patch"
done
python3 "$repo/scripts/fc_funcity_bridge_patch_test.py" --source \
  "$source_dir/src/main/java/catserver/server/CatServerEventHandler.java"
grep -Fq 'serverName = "FunCity"' "$source_dir/src/main/java/org/bukkit/craftbukkit/v1_16_R3/CraftServer.java"
grep -Fq 'getLogger("FunCity")' "$source_dir/src/main/java/catserver/server/CatServer.java"
grep -Fq 'new CatServerConfig("catserver.yml")' "$source_dir/src/main/java/catserver/server/CatServer.java"
cd "$source_dir"
sed -i -e 's/-XX:MaxPermSize=512m//g' \
       -e 's/-Xmx3G/-Xmx5G/g' \
       -e 's/org.gradle.parallel=true/org.gradle.parallel=false/' \
       -e 's/org.gradle.configureondemand=true/org.gradle.configureondemand=false/' \
       gradle.properties
grep -Fq 'org.gradle.parallel=false' gradle.properties
grep -Fq 'org.gradle.configureondemand=false' gradle.properties
stage=setup
for attempt in 1 2; do
  if ./gradlew --no-daemon --no-parallel --max-workers=1 setup > "$log" 2>&1; then
    break
  fi
  if [ "$attempt" -eq 1 ] && python3 "$repo/scripts/fc_funcity_setup_retry.py" "$log"; then
    echo 'SETUP_TRANSIENT_NETWORK_RETRY=1'
    sleep 15
    continue
  fi
  python3 "$repo/scripts/fc_gradle_failure_classifier.py" "$log"
  echo '::error title=FunCity private build::STAGE_FAILED stage=setup; no binary promoted' >&2
  exit 2
done
cat >> build.gradle <<'GRADLE'
project(':forge') {
    tasks.withType(JavaCompile).configureEach {
        options.fork = true
        options.forkOptions.memoryMaximumSize = '4g'
    }
}
GRADLE
sed -i 's/-Xmx5G/-Xmx2G/g' gradle.properties
stage=compile
if ! ./gradlew --no-daemon --no-parallel --max-workers=1 buildCatServer >> "$log" 2>&1; then
  python3 "$repo/scripts/fc_gradle_failure_classifier.py" "$log"
  echo '::error title=FunCity private build::STAGE_FAILED stage=compile; no binary promoted' >&2
  exit 2
fi
jars=(projects/forge/build/libs/CatServer-1.16.5-*-server.jar)
if [ "${#jars[@]}" -ne 1 ] || [ ! -s "${jars[0]}" ]; then
  echo 'expected one compiled launcher' >&2
  exit 2
fi
stage=compiled_gate
python3 "$repo/scripts/fc_funcity_compiled_engine_gate.py" \
  "${jars[0]}" projects/forge/build/classes/java/main
stage=empty_java11_boot
python3 "$repo/scripts/fc_funcity_java11_smoke.py" "$java11" "${jars[0]}"
stage=private_copy
# Copy ONLY to a new PRIVATE local workdir; refuse a pre-existing target.
result="$root/FunCityEngine-private-trial.jar"
cp -n "${jars[0]}" "$result"
test -s "$result" && cmp -s "${jars[0]}" "$result"
echo "PRIVATE_CANDIDATE_BUILD_PASS sha256=$(sha256sum "$result" | cut -d' ' -f1) binary=$result rp_pack=NOT_TESTED client=NOT_TESTED no_artifact_uploaded=true"
