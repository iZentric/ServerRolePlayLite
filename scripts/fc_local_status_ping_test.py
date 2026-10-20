#!/usr/bin/env python3
"""Synthetic Minecraft 1.16.5 status server; no real server, account or world."""
import json
import socket
import subprocess
import threading
from pathlib import Path


def varint(value):
    out = bytearray()
    while True:
        byte = value & 127
        value >>= 7
        out.append(byte | (128 if value else 0))
        if not value:
            return bytes(out)


def exact(sock, count):
    data = bytearray()
    while len(data) < count:
        chunk = sock.recv(count - len(data))
        if not chunk:
            raise RuntimeError('incomplete request')
        data.extend(chunk)
    return bytes(data)


def readvar(sock):
    value = 0
    for shift in range(0, 35, 7):
        byte = exact(sock, 1)[0]
        value |= (byte & 127) << shift
        if byte < 128:
            return value
    raise RuntimeError('bad varint')


def main():
    script = str(Path(__file__).with_name('fc_local_status_ping.ps1'))
    subprocess.run(['pwsh', '-File', script, '-SelfTest'], check=True, capture_output=True)
    with socket.socket() as listener:
        listener.bind(('127.0.0.1', 0))
        listener.listen(1)
        listener.settimeout(8)
        port = listener.getsockname()[1]
        failures = []

        def reply():
            try:
                with listener.accept()[0] as conn:
                    conn.settimeout(5)
                    handshake = exact(conn, readvar(conn))
                    if not handshake.startswith(b'\x00') or not handshake.endswith(b'\x01'):
                        raise RuntimeError('not status handshake')
                    if exact(conn, readvar(conn)) != b'\x00':
                        raise RuntimeError('not status request')
                    response = json.dumps({'version': {'name': '1.16.5', 'protocol': 754},
                        'players': {'online': 0, 'max': 20, 'sample': [{'name': 'SECRET_PLAYER'}]},
                        'description': {'text': 'SECRET_MOTD'}}).encode()
                    payload = b'\x00' + varint(len(response)) + response
                    conn.sendall(varint(len(payload)) + payload)
            except Exception as exc:
                failures.append(str(exc))

        worker = threading.Thread(target=reply, daemon=True)
        worker.start()
        result = subprocess.run(['pwsh', '-File', script, '-Port', str(port)],
                                capture_output=True, text=True, timeout=8)
        worker.join(timeout=2)
        if failures or worker.is_alive() or result.returncode or \
           'STATUS_PING=READY PROTOCOL=754 PLAYERS_ONLINE=0' not in result.stdout or \
           'SECRET' in result.stdout or 'SECRET' in result.stderr:
            raise AssertionError('Synthetic status ping failed or leaked private payload')
    print('PASS: local protocol status responds; only version/player count reported, no names/MOTD')


if __name__ == '__main__':
    main()
