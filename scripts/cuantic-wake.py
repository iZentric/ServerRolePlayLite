#!/usr/bin/env python3
"""CUANTIC WAKE — serverul doarme, portul ramane deschis, primul contact il trezeste.

De ce exista: un host gratuit (Cloud Shell / VM Always Free) arde CPU si RAM 24/7 chiar cand
nimeni nu se joaca. Asta lasa JVM-ul OPRIT si tine doar un listener mic pe portul public.
Cand cineva da "Join", listenerul:
  1. porneste `systemctl start mc.service` (sau MC_START),
  2. asteapta portul din spate (masurat: CatServer 1.16.5 ajunge la `Done` in ~14.4 s),
  3. pune legatura intr-o teava dubla (proxy TCP pur, nu atinge protocolul Minecraft),
  4. dupa MC_IDLE_SEC fara nici o conexiune activa, opreste serverul gratios.

Doar stdlib. Port public 25565 -> server intern 127.0.0.1:25566 (in server.properties pui
server-port=25566, altfel se lupta unul pe langa altul pentru acelasi port).
"""
import os
import select
import socket
import subprocess
import threading
import time

FRONT = ("0.0.0.0", int(os.environ.get("MC_FRONT_PORT", "25565")))
BACK = ("127.0.0.1", int(os.environ.get("MC_BACK_PORT", "25566")))
START = os.environ.get("MC_START", "systemctl start mc.service")
STOP = os.environ.get("MC_STOP", "systemctl stop mc.service")
IDLE_SEC = int(os.environ.get("MC_IDLE_SEC", "900"))
BOOT_WAIT = int(os.environ.get("MC_BOOT_WAIT", "180"))
LOCK = threading.Lock()
STATE = {"conns": 0, "last": time.time(), "starting": False}


def log(*a):
    print("[wake]", time.strftime("%H:%M:%S"), *a, flush=True)


def up():
    try:
        with socket.create_connection(BACK, timeout=1.0):
            return True
    except OSError:
        return False


def wake():
    """Ridica serverul o singura data, indiferent cata lume da Join deodata."""
    if up():
        return True
    with LOCK:
        first = not STATE["starting"]
        STATE["starting"] = True
    if first:
        log("trezesc serverul:", START)
        subprocess.call(START, shell=True)
    for i in range(BOOT_WAIT):
        if up():
            log("serverul e SUS dupa %ds" % (i + 1))
            with LOCK:
                STATE["starting"] = False
            return True
        time.sleep(1)
    log("serverul NU a raspuns in %ds" % BOOT_WAIT)
    with LOCK:
        STATE["starting"] = False
    return False


def pump(a, b):
    try:
        while True:
            r, _, _ = select.select([a], [], [], 15)
            if not r:
                continue
            data = a.recv(65536)
            if not data:
                break
            b.sendall(data)
    except OSError:
        pass
    finally:
        for s in (a, b):
            try:
                s.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass


def handle(client, addr):
    with LOCK:
        STATE["conns"] += 1
        STATE["last"] = time.time()
    try:
        if not wake():
            client.close()
            return
        back = socket.create_connection(BACK, timeout=30)
        log("legat", addr[0], "| conexiuni active:", STATE["conns"])
        t = threading.Thread(target=pump, args=(client, back), daemon=True)
        t.start()
        pump(back, client)
        t.join(timeout=2)
    except OSError as e:
        log("esec legatura:", repr(e)[:120])
    finally:
        try:
            client.close()
        except OSError:
            pass
        with LOCK:
            STATE["conns"] -= 1
            STATE["last"] = time.time()


def sleeper():
    """Oprim doar cand nu exista NICI O conexiune proxata (nici macar in stabilire)."""
    while True:
        time.sleep(20)
        with LOCK:
            idle = time.time() - STATE["last"]
            conns = STATE["conns"]
        if conns == 0 and idle > IDLE_SEC and up():
            log("idle %ds fara jucatori => opresc serverul" % int(idle))
            subprocess.call(STOP, shell=True)


def main():
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind(FRONT)
    srv.listen(128)
    log("ascult pe %s:%d -> spate %s:%d | idle %ds | boot max %ds"
        % (FRONT[0], FRONT[1], BACK[0], BACK[1], IDLE_SEC, BOOT_WAIT))
    threading.Thread(target=sleeper, daemon=True).start()
    while True:
        try:
            c, addr = srv.accept()
        except OSError:
            time.sleep(1)
            continue
        threading.Thread(target=handle, args=(c, addr), daemon=True).start()


if __name__ == "__main__":
    main()
