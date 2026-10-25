#!/usr/bin/env bash
set -u

HERE="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
RUNTIME="$HERE/runtime"
JAR="$RUNTIME/paper.jar"

if [[ ! -f "$JAR" ]]; then
  echo "Missing $JAR. Run: python3 '$HERE/download_paper.py'" >&2
  exit 1
fi
if [[ ! -f "$RUNTIME/eula.txt" ]] || ! grep -Eiq '^eula[[:space:]]*=[[:space:]]*true[[:space:]]*$' "$RUNTIME/eula.txt"; then
  echo "EULA not accepted. Read $RUNTIME/eula.txt and set eula=true only if you agree." >&2
  exit 1
fi
if ! command -v java >/dev/null 2>&1; then
  echo "Java 25 is required for Paper 26.2; install it and put java on PATH." >&2
  exit 1
fi
java_version="$(java -version 2>&1 | awk -F '"' 'NR == 1 { print $2; exit }')"
java_major="${java_version%%.*}"
if ! [[ "$java_major" =~ ^[0-9]+$ ]] || (( java_major < 25 )); then
  echo "Paper 26.2 requires Java 25 or newer; detected: ${java_version:-unknown}." >&2
  exit 1
fi

memory_bytes=""
for file in /sys/fs/cgroup/memory.max /sys/fs/cgroup/memory/memory.limit_in_bytes; do
  if [[ -r "$file" ]]; then
    value="$(cat "$file")"
    if [[ "$value" =~ ^[0-9]+$ ]] && (( value > 0 && value < 1152921504606846976 )); then
      memory_bytes="$value"
      break
    fi
  fi
done
if [[ -z "$memory_bytes" ]] && [[ -r /proc/meminfo ]]; then
  memory_kib="$(awk '/^MemTotal:/ {print $2; exit}' /proc/meminfo)"
  memory_bytes=$((memory_kib * 1024))
fi
if [[ -z "$memory_bytes" ]]; then
  echo "Could not detect system/cgroup RAM. Set PAPER_HEAP_GB explicitly and retry." >&2
  exit 1
fi

total_gb=$((memory_bytes / 1024 / 1024 / 1024))
if [[ -n "${PAPER_HEAP_GB:-}" ]]; then
  heap_gb="$PAPER_HEAP_GB"
else
  heap_gb=$((total_gb - 2))
fi
if ! [[ "$heap_gb" =~ ^[1-9][0-9]*$ ]]; then
  echo "Detected ${total_gb} GiB RAM; total RAM minus 2 GiB leaves no usable heap. Set PAPER_HEAP_GB only if you understand the host memory limit." >&2
  exit 1
fi

printf 'Paper heap: %s GiB (detected RAM: %s GiB; reserve target: 2 GiB)\n' "$heap_gb" "$total_gb"
cd "$RUNTIME"
while true; do
  java \
    "-Xms${heap_gb}G" "-Xmx${heap_gb}G" \
    -XX:+UseG1GC \
    -XX:+ParallelRefProcEnabled \
    -XX:MaxGCPauseMillis=200 \
    -XX:+UnlockExperimentalVMOptions \
    -XX:+DisableExplicitGC \
    -XX:+AlwaysPreTouch \
    -XX:G1NewSizePercent=30 \
    -XX:G1MaxNewSizePercent=40 \
    -XX:G1HeapRegionSize=8M \
    -XX:G1ReservePercent=20 \
    -XX:G1HeapWastePercent=5 \
    -XX:G1MixedGCCountTarget=4 \
    -XX:InitiatingHeapOccupancyPercent=15 \
    -XX:G1MixedGCLiveThresholdPercent=90 \
    -XX:G1RSetUpdatingPauseTimePercent=5 \
    -XX:SurvivorRatio=32 \
    -XX:+PerfDisableSharedMem \
    -XX:MaxTenuringThreshold=1 \
    -jar "$JAR" --nogui
  code=$?
  if (( code == 0 )); then
    exit 0
  fi
  echo "Paper exited with status $code; auto-restarting in 15 seconds. Press Ctrl+C to cancel." >&2
  sleep 15
done
