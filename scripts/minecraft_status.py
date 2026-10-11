#!/usr/bin/env python3
"""Safe local Minecraft status ping (NOT a modded login/handshake)."""
import json
import socket
import struct
import sys


def v(n):
    out = bytearray()
    while True:
        part = n & 127
        n >>= 7
        out.append(part | (128 if n else 0))
        if not n:
            return bytes(out)


def readvar(sock):
    number = 0
    for i in range(5):
        byte = sock.recv(1)
        if not byte:
            raise EOFError("server closed during status query")
        number |= (byte[0] & 127) << (7 * i)
        if byte[0] < 128:
            return number
    raise ValueError("invalid status length")


def status(host="127.0.0.1", port=25565):
    with socket.create_connection((host, port), timeout=5) as sock:
        sock.settimeout(5)
        payload = v(0) + v(754) + v(len(host)) + host.encode() + struct.pack(">H", port) + v(1)
        sock.sendall(v(len(payload)) + payload + b"\x01\x00")  # handshake then status request
        length = readvar(sock)
        if not (1 <= length <= 1024 * 1024):
            raise ValueError("invalid status payload size")
        data = bytearray()
        while len(data) < length:
            chunk = sock.recv(length - len(data))
            if not chunk:
                raise EOFError("short status response")
            data.extend(chunk)
        if readvar_from_bytes(data) != 0:
            raise ValueError("unexpected packet id")
        size, index = readvar_from_bytes(data[1:], return_index=True)
        if size > 1024 * 1024 or len(data) != 1 + index + size:
            raise ValueError("invalid JSON length")
        response = json.loads(data[1 + index:1 + index + size])
        return {"version": response.get("version", {}), "players": {
            "online": response.get("players", {}).get("online"),
            "max": response.get("players", {}).get("max")}}


def readvar_from_bytes(data, return_index=False):
    result = 0
    for i in range(min(5, len(data))):
        result |= (data[i] & 127) << (7 * i)
        if data[i] < 128:
            return (result, i + 1) if return_index else result
    raise ValueError("invalid VarInt")


if __name__ == "__main__":
    try:
        print(json.dumps(status(), ensure_ascii=False))
    except Exception as exc:
        print(f"STATUS FAILED: {exc}")
        sys.exit(1)
