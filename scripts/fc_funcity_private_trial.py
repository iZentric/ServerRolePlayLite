#!/usr/bin/env python3
"""Run TWO Java 11 boots against a disposable copy of the owner's PRIVATE RP pack.

Linux isolated lab only. Never uploads data, changes the supplied source copy,
connects to a host, or publishes a JAR. Does not test clients/voice/capacity.
"""
import argparse
import hashlib
import os
from pathlib import Path
import re
import shutil
import signal
import socket
import subprocess
import sys
import time
import zipfile

from fc_funcity_compiled_engine_gate import InvalidEngine, check_packaged
from fc_funcity_java11_smoke import inspect
from fc_funcity_runtime_seed import InvalidSeed, validate_runtime

MARKER = 'FUNCITY_INACTIVE_ISOLATED_COPY_V1\n'
CRITICAL = {'server-ip', 'server-port', 'white-list', 'enable-rcon', 'enable-query',
            'max-players', 'level-name', 'online-mode'}
SHIELD = {'server-ip': '127.0.0.1', 'white-list': 'true', 'enable-rcon': 'false',
          'enable-query': 'false', 'max-players': '2'}


class TrialRejected(ValueError):
    pass


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as source:
        for block in iter(lambda: source.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def descendant(path, parent):
    return path == parent or parent in path.parents


def inventory(root):
    """Reject links/special files; hash private data in memory only, never print it."""
    result = {}
    for base, dirs, files in os.walk(root, followlinks=False):
        for name in dirs + files:
            path = Path(base) / name
            if path.is_symlink() or not (path.is_file() or path.is_dir()):
                raise TrialRejected('links or special files in copy are not permitted')
        for name in files:
            path = Path(base) / name
            result[str(path.relative_to(root))] = sha(path)
    if not result:
        raise TrialRejected('empty source copy')
    return result


def properties(text, port):
    lines = text.splitlines()
    values = {}
    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith(('#', '!')) or '=' not in stripped:
            continue
        key, val = (part.strip() for part in line.split('=', 1))
        if key in CRITICAL and key in values:
            raise TrialRejected('duplicate critical server property: ' + key)
        values[key] = val
    world = values.get('level-name', 'world')
    if not world or world in ('.', '..') or '/' in world or '\\' in world:
        raise TrialRejected('invalid world name')
    if values.get('online-mode') != 'false':
        raise TrialRejected('this RP offline-auth trial requires online-mode=false in source copy')
    changes = dict(SHIELD, **{'server-port': str(port)})
    output = [line for line in lines
              if not (line.strip() and not line.lstrip().startswith(('#', '!'))
                      and line.split('=', 1)[0].strip() in changes)]
    output += [key + '=' + val for key, val in changes.items()]
    return world, '\n'.join(output) + '\n'


def port_is_unused(port):
    if not 1024 <= port <= 65535:
        raise TrialRejected('port must be unprivileged')
    with socket.socket() as sock:
        try:
            sock.bind(('127.0.0.1', port))
        except OSError as exc:
            raise TrialRejected('loopback port is not free') from exc


def preflight(source, output, engine, expected_sha, port, runtime_seed):
    raw_source, raw_output, raw_engine = map(lambda p: Path(p).absolute(),
                                             (source, output, engine))
    if raw_source.is_symlink() or raw_output.is_symlink() or raw_engine.is_symlink():
        raise TrialRejected('direct symlink paths are not permitted')
    source = raw_source.resolve(strict=False)
    output = raw_output.resolve(strict=False)  # Canonicalize symlinked ancestors.
    engine = raw_engine.resolve(strict=False)
    raw_seed = Path(runtime_seed).absolute()
    if raw_seed.is_symlink():
        raise TrialRejected('linked runtime seed refused')
    runtime_seed = raw_seed.resolve(strict=False)
    repo = Path(__file__).resolve().parents[1]
    if (not source.is_dir()
            or output.exists() or not output.parent.is_dir()
            or descendant(output, source) or descendant(source, output)
            or descendant(output, repo) or descendant(source, repo)
            or descendant(runtime_seed, source) or descendant(source, runtime_seed)
            or descendant(output, runtime_seed) or descendant(runtime_seed, output)
            or descendant(runtime_seed, repo)):
        raise TrialRejected('require isolated source/seed and NEW output outside repo')
    before = inventory(source)  # Reject links before opening ANY files under the copy.
    if not (source / '.funcity-isolated-copy').is_file() or (source / '.funcity-isolated-copy').read_text() != MARKER:
        raise TrialRejected('inactive-source-copy marker missing')
    if (source / 'eula.txt').read_text().strip().lower() != 'eula=true':
        raise TrialRejected('source copy must already have accepted the EULA')
    if not re.fullmatch(r'[0-9a-f]{64}', expected_sha) or not engine.is_file() or engine.is_symlink():
        raise TrialRejected('local candidate JAR or expected SHA-256 missing')
    if descendant(engine, source) or descendant(engine, output):
        raise TrialRejected('candidate JAR must be outside input/output copy')
    if sha(engine) != expected_sha:
        raise TrialRejected('candidate SHA-256 mismatch')
    seed_folders = validate_runtime(runtime_seed, expected_sha)
    try:
        check_packaged(engine)
    except (InvalidEngine, OSError, KeyError, zipfile.BadZipFile) as exc:
        raise TrialRejected('candidate nested FunCity/Forge classes not verified') from exc
    p = source / 'server.properties'
    if not p.is_file():
        raise TrialRejected('source server.properties missing')
    world, safe_properties = properties(p.read_text(encoding='utf-8'), port)
    if (not (source / world / 'level.dat').is_file()
            or len(list((source / 'mods').glob('*.jar'))) != 34
            or len(list((source / 'plugins').glob('*.jar'))) != 13
            or not (source / 'server.jar').is_file()):
        raise TrialRejected('world or full 34-mod/13-plugin pack or rollback engine missing')
    port_is_unused(port)
    return source, output, engine, safe_properties, before, runtime_seed, seed_folders


def prepare(source, output, engine, expected_sha, port, runtime_seed):
    source, output, engine, safe_properties, before, runtime_seed, seed_folders = preflight(
        source, output, engine, expected_sha, port, runtime_seed)
    # Refuse to overwrite even a directory created between preflight and copytree.
    shutil.copytree(source, output, symlinks=False)
    try:
        if inventory(output) != before or inventory(source) != before:
            raise TrialRejected('source/output SHA inventory differs; no trial started')
        # Keep original Mohist runtime separately; CatServer's first boot needs
        # its OWN launcher libraries while network egress is disabled.
        prior = output / '.funcity-prior-runtime'
        if prior.exists() or prior.is_symlink():
            raise TrialRejected('reserved rollback runtime path already exists')
        prior.mkdir()
        for folder in seed_folders:
            if (output / folder).exists():
                (output / folder).replace(prior / folder)
            shutil.copytree(runtime_seed / folder, output / folder)
        # Only the NEW output is edited; the supplied copy and its rollback engine remain untouched.
        (output / 'server.jar').replace(output / 'server-before-funcity-trial.jar')
        shutil.copyfile(engine, output / 'server.jar')
        if sha(output / 'server.jar') != expected_sha:
            raise TrialRejected('staged candidate checksum mismatch')
        (output / 'server.properties').write_text(safe_properties, encoding='utf-8')
        (output / '.funcity-isolated-copy').unlink()
    except Exception:
        # Preserve output for forensics; never erase a partially staged world.
        raise
    return output


def java_is_11(java):
    result = subprocess.run([str(java), '-version'], capture_output=True, timeout=15)
    text = (result.stderr + result.stdout).decode('utf-8', errors='replace')
    if result.returncode or not re.search(r'\bversion "11(?:[.\+"]|$)', text):
        raise TrialRejected('Java 11 runtime required')


def namespace_supported():
    """Prove Linux can create an egress-free network namespace BEFORE copying."""
    if not shutil.which('unshare') or not shutil.which('ip'):
        raise TrialRejected('unshare and iproute2 required for isolated boot')
    try:
        result = subprocess.run(['unshare', '--user', '--map-root-user', '--net', '--',
                                 'sh', '-c', 'ip link set lo up'],
                                capture_output=True, timeout=10)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise TrialRejected('network namespace cannot be created') from exc
    if result.returncode:
        raise TrialRejected('network namespace cannot bring up isolated loopback')


def isolated_java_command(java):
    # There is NO host network interface inside this new namespace. Plugins
    # cannot reach external DBs/webhooks/auth APIs from a copied configuration.
    return ['unshare', '--user', '--map-root-user', '--net', '--',
            'sh', '-c', 'ip link set lo up && exec "$@"', 'sh', str(java),
            '-Xms256m', '-Xmx2G', '-jar', 'server.jar', 'nogui']


def boot_once(java, output, attempt, timeout, settle_seconds=30):
    log = output / ('funcity-private-trial-' + str(attempt) + '.log')
    with log.open('wb') as stream:
        process = subprocess.Popen(isolated_java_command(java),
                                   cwd=output, stdin=subprocess.PIPE, stdout=stream,
                                   stderr=subprocess.STDOUT, start_new_session=True)
        deadline = time.monotonic() + timeout
        try:
            reached_done = fatal = sent_stop = False
            done_at = None
            while time.monotonic() < deadline:
                if log.stat().st_size > 32 * 1024 * 1024:
                    break  # A noisy/crashing server is not safe to call a pass.
                reached_done, fatal = inspect(log.read_text(encoding='utf-8', errors='replace'))
                if reached_done and done_at is None:
                    done_at = time.monotonic()
                if (fatal or process.poll() is not None or
                        (done_at is not None and time.monotonic() - done_at >= settle_seconds)):
                    break
                time.sleep(1)
            settled = done_at is not None and time.monotonic() - done_at >= settle_seconds
            if settled and not fatal and process.poll() is None:
                process.stdin.write(b'stop\n')
                process.stdin.flush()
                sent_stop = True
            process.stdin.close()
            try:
                process.wait(timeout=60 if reached_done else 3)
            except subprocess.TimeoutExpired:
                pass
            if log.stat().st_size > 32 * 1024 * 1024:
                return False
            final_done, final_fatal = inspect(log.read_text(encoding='utf-8', errors='replace'))
            return sent_stop and final_done and not final_fatal and process.returncode == 0
        finally:
            if process.poll() is None:
                os.killpg(process.pid, signal.SIGKILL)
                process.wait(timeout=10)
            if not process.stdin.closed:
                process.stdin.close()


def trial(java, source, output, engine, expected_sha, runtime_seed, port=25595, timeout=900):
    java_is_11(java)   # Fail before copying data if the runtime is wrong.
    namespace_supported()  # Mandatory isolation, not an operator claim.
    if timeout < 1:
        raise TrialRejected('invalid timeout')
    staged = prepare(source, output, engine, expected_sha, port, runtime_seed)
    for attempt in (1, 2):
        if not boot_once(java, staged, attempt, timeout):
            raise TrialRejected('private boot/stop ' + str(attempt) + ' failed; inspect LOCAL log only')
        print('PRIVATE_FULL_PACK_BOOT_' + str(attempt) + '=PASS mods=34 plugins=13 client=NOT_TESTED')
    return True


if __name__ == '__main__':
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--java', required=True, type=Path)
    cli.add_argument('--source-copy', required=True, type=Path)
    cli.add_argument('--output', required=True, type=Path)
    cli.add_argument('--engine', required=True, type=Path)
    cli.add_argument('--runtime-seed', required=True, type=Path)
    cli.add_argument('--sha256', required=True)
    cli.add_argument('--port', type=int, default=25595)
    cli.add_argument('--timeout', type=int, default=900)
    args = cli.parse_args()
    try:
        trial(args.java, args.source_copy, args.output, args.engine, args.sha256,
              args.runtime_seed, args.port, args.timeout)
    except (OSError, TrialRejected, subprocess.TimeoutExpired, InvalidEngine, InvalidSeed) as exc:
        print('PRIVATE_TRIAL_REJECTED: ' + type(exc).__name__ +
              ' (details and logs remain on the local isolated machine)', file=sys.stderr)
        sys.exit(2)
