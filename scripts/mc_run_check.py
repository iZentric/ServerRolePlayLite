#!/usr/bin/env python3
"""Verificator de pornire pentru serverul 1.16.5 care ruleaza pe runner.

NU e un server publicat: e dovada ca pack-ul din release boot-uieste, raspunde
la ping, are rcon functional si stă sub memorie. Face patru lucruri:
 1. asteapta linia „Done (X.Xs)!\" din consola (esec = crash/eveniment fatal);
 2. Server List Ping local (JSON status, fara login — online-mode e false oricum);
 3. rcon: list, uptime, version (soak de cateva secunde cu mostre de RSS intre comenzi);
 4. stop frumos prin rcon, altfel SIGTERM, apoi raport in summary.json.

 Nimic secret nu parase runner-ul de aici: fisierul publicat e redactat separat,
 in workflow, cu scrub() din rp_archive_inspect.
"""
from __future__ import annotations

import argparse
import json
import re
import signal
import socket
import struct
import subprocess
import sys
import time

BOOT_OK = re.compile(r"Done \((\d+(?:\.\d+)?)s\)! For help")
BOOT_FAIL = re.compile(
    r"(---- Minecraft Crash Report ----"
    r"|Failed to start the minecraft server"
    r"|To see this crash report permanently, please"
    r"|A fatal error has occurred"
    r"|Encountered an unexpected exception"
    r"|Exception in thread \"main\")"
)


def read_text(path: str) -> str:
    try:
        with open(path, encoding="utf-8", errors="replace") as fh:
            return fh.read()
    except OSError:
        return ""


# ---------- protocolul minim de status Minecraft (SLP, protocol -1) ----------

def _varint(n: int) -> bytes:
    out = bytearray()
    n &= 0xFFFFFFFF  # varint semnat in protocol
    while True:
        b = n & 0x7F
        n >>= 7
        out.append(b | (0x80 if n else 0))
        if not n:
            return bytes(out)


def _read_varint(sock: socket.socket) -> int:
    n = 0
    shift = 0
    while True:
        chunk = sock.recv(1)
        if not chunk:
            raise OSError("conexiune inchisa la varint")
        b = chunk[0]
        n |= (b & 0x7F) << shift
        if not (b & 0x80):
            return n
        shift += 7
        if shift > 35:
            raise ValueError("varint prea lung")


def slp_status(port: int, timeout: float = 8.0) -> dict:
    with socket.create_connection(("127.0.0.1", port), timeout=timeout) as s:
        s.settimeout(timeout)
        host = b"127.0.0.1"
        hs = _varint(0) + _varint(-1) + _varint(len(host)) + host + struct.pack(">H", port) + _varint(1)
        s.sendall(_varint(len(hs)) + hs)
        s.sendall(_varint(1) + b"\x00")
        ln = _read_varint(s)
        buf = b""
        while len(buf) < ln:
            chunk = s.recv(min(65536, ln - len(buf)))
            if not chunk:
                raise OSError("raspuns trunchiat")
            buf += chunk
        return json.loads(buf.decode("utf-8"))


# ---------------------------- RCON (Source, mic) ----------------------------

class Rcon:
    def __init__(self, port: int, password: str, timeout: float = 10.0):
        self.s = socket.create_connection(("127.0.0.1", port), timeout=timeout)
        self.s.settimeout(timeout)
        self._id = 0
        ok = self._auth(password)
        if not ok:
            self.s.close()
            raise PermissionError("rcon: parola respinsa")

    def _send(self, ptype: int, body: bytes) -> int:
        self._id += 1
        payload = struct.pack("<ii", self._id, ptype) + body + b"\x00\x00"
        self.s.sendall(struct.pack("<i", len(payload)) + payload)
        return self._id

    def _recv(self) -> tuple[int, int, str]:
        raw = b""
        while len(raw) < 4:
            c = self.s.recv(4 - len(raw))
            if not c:
                raise OSError("rcon inchis")
            raw += c
        (ln,) = struct.unpack("<i", raw)
        data = b""
        while len(data) < ln:
            c = self.s.recv(min(65536, ln - len(data)))
            if not c:
                raise OSError("rcon trunchiat")
            data += c
        rid, ptype = struct.unpack("<ii", data[:8])
        return rid, ptype, data[8:].rstrip(b"\x00").decode("utf-8", "replace")

    def _auth(self, password: str) -> bool:
        self._send(3, password.encode())
        rid, _, _ = self._recv()
        return rid != -1

    def cmd(self, line: str) -> str:
        self._send(2, line.encode())
        _, _, out = self._recv()
        return out.strip() or "(fara iesire)"

    def close(self):
        try:
            self.s.close()
        except OSError:
            pass


# ------------------------------- resurse Java --------------------------------

def java_pid() -> int | None:
    try:
        out = subprocess.run(["pgrep", "-n", "-f", "java"], capture_output=True, text=True, timeout=5).stdout
        pid = int(out.strip() or 0)
        return pid or None
    except Exception:
        return None


def rss_mib(pid: int | None) -> float:
    if not pid:
        return 0.0
    try:
        for line in open(f"/proc/{pid}/status", encoding="ascii"):
            if line.startswith("VmRSS:"):
                return round(int(line.split()[1]) / 1024.0, 1)
    except OSError:
        pass
    return 0.0


# --------------------------------- main --------------------------------------

def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--log", required=True, help="fisierul de consola (stdout+stderr java)")
    ap.add_argument("--wait", type=int, default=540, help="secunde maxime de asteptare dupa Done (")
    ap.add_argument("--port", type=int, default=25565)
    ap.add_argument("--rcon-port", type=int, default=0)
    ap.add_argument("--rcon-pass", default="")
    ap.add_argument("--soak", type=int, default=45, help="secunde de stat sub sarcina minima")
    ap.add_argument("--out", default="summary.json")
    args = ap.parse_args(argv)

    summary: dict = {"state": "unknown", "boot_seconds": None, "max_rss_mib": 0.0,
                     "soak": args.soak, "slp": None, "rcon": {}, "errors": []}
    t0 = time.time()
    pid = None
    while time.time() - t0 < args.wait:
        txt = read_text(args.log)
        m = BOOT_OK.search(txt)
        if m:
            summary["state"] = "booted"
            summary["boot_seconds"] = float(m.group(1))
            break
        f = BOOT_FAIL.search(txt)
        if f:
            summary["state"] = "crash"
            summary["errors"].append(f.group(1))
            break
        time.sleep(3)

    pid = java_pid()

    if summary["state"] == "booted":
        try:
            st = slp_status(args.port)
            players = st.get("players", {})
            summary["slp"] = {"description": str(st.get("description", ""))[:160],
                              "version": st.get("version", {}).get("name"),
                              "online": players.get("online"), "max": players.get("max")}
        except Exception as exc:  # noqa: BLE001
            summary["errors"].append(f"slp: {exc}")

        rc = None
        if args.rcon_port and args.rcon_pass:
            try:
                rc = Rcon(args.rcon_port, args.rcon_pass)
                for c in ("list", "uptime", "version"):
                    try:
                        summary["rcon"][c] = rc.cmd(c)[:300]
                    except Exception as exc:  # noqa: BLE001
                        summary["errors"].append(f"rcon {c}: {exc}")
                        break
            except Exception as exc:  # noqa: BLE001
                summary["errors"].append(f"rcon: {exc}")
                rc = None

        deadline = time.time() + args.soak
        samples = []
        while time.time() < deadline:
            samples.append(rss_mib(pid))
            time.sleep(5)
        summary["max_rss_mib"] = max(samples) if samples else rss_mib(pid)

        if rc:
            try:
                rc.cmd("stop")
            except Exception:  # noqa: BLE001
                pass
            rc.close()

    if pid:
        for _ in range(20):
            try:
                subprocess.run(["kill", "-0", str(pid)], check=True)
            except Exception:  # noqa: BLE001
                break
            time.sleep(3)
        else:
            try:
                subprocess.run(["kill", "-TERM", str(pid)], check=False)
                time.sleep(10)
            except Exception:  # noqa: BLE001
                pass
        if summary["state"] == "unknown":
            summary["state"] = "timeout"
            try:
                subprocess.run(["pkill", "-9", "-f", "java"], check=False)
            except Exception:  # noqa: BLE001
                pass

    with open(args.out, "w", encoding="utf-8") as fh:
        json.dump(summary, fh, ensure_ascii=False, indent=1)
    print(json.dumps(summary, ensure_ascii=False)[:800])
    return 0 if summary["state"] == "booted" else 2


if __name__ == "__main__":
    sys.exit(main())
