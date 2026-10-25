#!/usr/bin/env python3
"""Download the newest stable build of a pinned Paper version from Fill v3."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import tempfile
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

API_ROOT = "https://fill.papermc.io/v3/projects/paper"
DEFAULT_VERSION = "26.2"
USER_AGENT = "FunCity-Paper-Setup/1.0 (https://github.com/iZentric/ServerRolePlayLite)"


def fetch_json(url: str) -> Any:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
    with urllib.request.urlopen(request, timeout=45) as response:
        return json.load(response)


def stable_builds(payload: Any) -> list[dict[str, Any]]:
    if not isinstance(payload, list):
        raise ValueError("Fill v3 response was not a build list")
    builds = [item for item in payload if isinstance(item, dict) and item.get("channel") == "STABLE"]
    return sorted(builds, key=lambda item: int(item.get("id", -1)), reverse=True)


def get_build(version: str) -> dict[str, Any]:
    if not re.fullmatch(r"\d+\.\d+(?:\.\d+)?", version):
        raise ValueError(f"Invalid Paper version: {version!r}")
    builds = stable_builds(fetch_json(f"{API_ROOT}/versions/{version}/builds"))
    for build in builds:
        file_info = build.get("downloads", {}).get("server:default", {})
        checksum = file_info.get("checksums", {}).get("sha256", "")
        url = file_info.get("url", "")
        name = file_info.get("name", "")
        if build.get("id") is not None and re.fullmatch(r"[0-9a-fA-F]{64}", checksum) and url.startswith("https://fill-data.papermc.io/") and name.endswith(".jar"):
            return {"version": version, "build": int(build["id"]), "name": name, "sha256": checksum.lower(), "url": url}
    raise ValueError(f"Fill v3 returned no valid stable Paper build for Minecraft {version}")


def download_and_verify(build: dict[str, Any], target: Path, *, force: bool = False) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists() and not force:
        raise FileExistsError(f"Refusing to overwrite {target}; pass --force to replace it")
    request = urllib.request.Request(build["url"], headers={"User-Agent": USER_AGENT})
    digest = hashlib.sha256()
    fd, temporary_name = tempfile.mkstemp(prefix=f".{target.name}.", suffix=".part", dir=target.parent)
    try:
        with os.fdopen(fd, "wb") as output, urllib.request.urlopen(request, timeout=180) as response:
            while chunk := response.read(1024 * 1024):
                digest.update(chunk)
                output.write(chunk)
        actual = digest.hexdigest()
        if actual != build["sha256"]:
            raise ValueError(f"SHA-256 mismatch: Fill says {build['sha256']}, downloaded {actual}; file not installed")
        os.replace(temporary_name, target)
    except Exception:
        try:
            os.unlink(temporary_name)
        except FileNotFoundError:
            pass
        raise


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--version", default=DEFAULT_VERSION, help=f"Minecraft version (default: {DEFAULT_VERSION}); do not upgrade until the plugin lock is rechecked")
    parser.add_argument("--target", type=Path, default=Path(__file__).resolve().parent / "runtime" / "paper.jar")
    parser.add_argument("--force", action="store_true", help="replace an existing JAR")
    args = parser.parse_args(argv)
    try:
        build = get_build(args.version)
        download_and_verify(build, args.target, force=args.force)
    except (OSError, ValueError, urllib.error.URLError, json.JSONDecodeError) as error:
        print(f"Paper download failed: {error}", file=sys.stderr)
        return 1
    print(f"Installed Paper {build['version']} build {build['build']} to {args.target}")
    print(f"SHA-256 verified: {build['sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
