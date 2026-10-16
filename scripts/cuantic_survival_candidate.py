#!/usr/bin/env python3
"""Make an isolated staging-only spawn-rule A/B pack from the pinned 1.7.7 ZIP.

Never installs, releases, deploys or edits the source pack. Only spawn.json
may differ; all engine/mod/plugin member bytes are verified after writing.
"""
import hashlib
import json
from pathlib import Path
import sys
from zipfile import ZipFile

from cuantic_survival_rules import review

EXPECTED_PACK = "fe1e261097d92f26c6653239a7161613e6be54b8e9f82c79739c101ce8aa8a15"
SPAWN = "config/incontrol/spawn.json"
OLD_RULES = [{"hostile": True, "maxcount": 50, "result": "deny"}]
PROFILES = {
    # Control: do not replace vanilla/Forge natural spawning with custom denies.
    "vanilla": [],
    # Experimental only; capped at 50 per 289 loaded chunks, NOT a proven safe
    # value under multiple players, mods, farms or portal gameplay.
    "scaled": [{"hostile": True,
                "mincount": {"amount": 50, "hostile": True, "perchunk": True},
                "result": "deny"}],
}


def digest(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def create_candidate(source, destination, profile, expected_sha=EXPECTED_PACK):
    source, destination = Path(source), Path(destination)
    if profile not in PROFILES:
        raise ValueError("profile must be vanilla or scaled")
    if source.resolve() == destination.resolve() or destination.exists() or destination.is_symlink():
        raise ValueError("destination must be a new, separate file")
    if digest(source) != expected_sha:
        raise ValueError("not the pinned 1.7.7 release pack; refusing to modify an unknown input")
    new = json.dumps(PROFILES[profile], ensure_ascii=False, indent=2).encode("utf-8") + b"\n"
    # Exclusive create avoids overwriting someone else's staging result.
    with ZipFile(source, "r") as original:
        names = original.namelist()
        if len(names) != len(set(names)) or names.count(SPAWN) != 1:
            raise ValueError("missing or duplicate spawn.json / archive entries")
        if json.loads(original.read(SPAWN)) != OLD_RULES:
            raise ValueError("source spawn rule differs from the audited snapshot")
        if any(f.startswith("BLOCK") for f in review(PROFILES[profile])):
            raise ValueError("candidate rule fails static survival screen")
        # Destination is only created after all input checks pass.
        with destination.open("xb") as output:
            try:
                with ZipFile(output, "w", allowZip64=True) as candidate:
                    for entry in original.infolist():
                        candidate.writestr(entry, new if entry.filename == SPAWN else original.read(entry))
                with ZipFile(destination, "r") as candidate:
                    if candidate.namelist() != names or candidate.read(SPAWN) != new:
                        raise ValueError("candidate archive failed verification")
                    for entry in original.infolist():
                        if entry.filename != SPAWN and candidate.read(entry) != original.read(entry):
                            raise ValueError(f"unexpected archive member changed: {entry.filename}")
            except Exception:
                destination.unlink(missing_ok=True)  # Only our exclusively created, incomplete output.
                raise
    return {"baseline_sha256": expected_sha, "candidate_sha256": digest(destination),
            "profile": profile, "only_allowed_change": SPAWN,
            "verdict": "STAGING_ONLY_NOT_A_GAMEPLAY_OR_MEMORY_PASS"}


if __name__ == "__main__":
    if len(sys.argv) != 4:
        sys.exit("usage: cuantic_survival_candidate.py <pinned-pack-1.7.7.zip> </tmp/NEW-staging.zip> <vanilla|scaled>")
    try:
        result = create_candidate(sys.argv[1], sys.argv[2], sys.argv[3])
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except (OSError, ValueError) as exc:
        sys.exit(f"REFUSED: {exc}")
