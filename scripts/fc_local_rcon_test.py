#!/usr/bin/env python3
"""Synthetic RCON auth/list service; never contacts a real server."""
import socket
import struct
import subprocess
import tempfile
import threading
from pathlib import Path


def exact(sock, count):
    data = bytearray()
    while len(data) < count:
        chunk = sock.recv(count - len(data))
        if not chunk:
            raise RuntimeError('short request')
        data.extend(chunk)
    return data


def packet(sock):
    size = struct.unpack('<i', exact(sock, 4))[0]
    assert 10 <= size <= 65536
    body = exact(sock, size)
    assert body[-2:] == b'\0\0'
    return struct.unpack('<ii', body[:8]) + (body[8:-2].decode(),)


def reply(sock, request_id, typ, text):
    body = struct.pack('<ii', request_id, typ) + text.encode() + b'\0\0'
    sock.sendall(struct.pack('<i', len(body)) + body)


with tempfile.TemporaryDirectory(prefix='fc-rcon-fixture-') as temp:
    server = Path(temp) / 'FunCityLocal' / 'server'
    server.mkdir(parents=True)
    password = 'NEVER_PRINT_SECRET'
    with socket.socket() as listener:
        listener.bind(('127.0.0.1', 0))
        listener.listen(1)
        listener.settimeout(10)
        port = listener.getsockname()[1]
        (server / 'server.properties').write_text(
            f'enable-rcon=true\nrcon.port={port}\nrcon.password={password}\n')
        errors = []

        def serve():
            try:
                with listener.accept()[0] as conn:
                    conn.settimeout(8)
                    rid, typ, value = packet(conn)
                    assert typ == 3 and value == password
                    reply(conn, rid, 0, '')
                    reply(conn, rid, 2, '')
                    rid, typ, value = packet(conn)
                    assert typ == 2 and value == 'list'
                    reply(conn, rid, 0, '§0There are §a0§7 of a max of §a20§7 players online: SECRET_PLAYER')
            except Exception as exc:
                errors.append(str(exc))

        worker = threading.Thread(target=serve, daemon=True)
        worker.start()
        script = str(Path(__file__).with_name('fc_local_rcon.ps1'))
        result = subprocess.run(['pwsh', '-File', script, '-Server', str(server), '-Synthetic'],
                                capture_output=True, text=True, timeout=12)
        worker.join(timeout=2)
        if result.returncode or errors or worker.is_alive() or 'AUTH_OK=true PLAYER_STATE=ZERO' not in result.stdout:
            raise AssertionError('Synthetic RCON protocol/list gate failed')
        for secret in (password, 'SECRET_PLAYER', temp):
            assert secret not in result.stdout + result.stderr, 'Private RCON data leaked'
    print('PASS: synthetic local RCON auth/list; no secret or player output')
