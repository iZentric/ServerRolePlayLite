#!/usr/bin/env python3
"""Supervisor FunCity pentru staging: mentine fd-ul fifo deschis (EOF pe stdin = Mohist
se opreste frumos — lectia din CI), scrie server.pid si traieste cat JVM-ul.
Se porneste cu setsid din functity-stage.sh; supravietusie job-ului CI."""
import os
import subprocess
import time

D = os.getcwd()
LOG = os.environ.get("FUNCITY_LOG", os.path.join(D, "stage.log"))
FIFO = os.path.join(D, "console.in")
JAVA = os.environ["FUNCITY_JAVA"]
JAR = os.environ.get("FUNCITY_JARFILE", "FunCity.jar")
XMX = os.environ.get("FUNCITY_XMX", "3G")


def main():
    fd = os.open(FIFO, os.O_RDWR)  # singurul care tine scriitorul viu
    lf = open(LOG, "ab", buffering=0)
    cmd = [JAVA, "-Xms1G", f"-Xmx{XMX}", "-XX:MaxGCPauseMillis=200", "-jar", JAR, "nogui"]
    p = subprocess.Popen(cmd, stdin=fd, stdout=lf, stderr=subprocess.STDOUT,
                         start_new_session=True)
    with open(os.path.join(D, "server.pid"), "w") as f:
        f.write(str(p.pid))
    # bucla de supraveghere: tinem fd+log deschise, nu dam EOF, nu murim noi primii
    while p.poll() is None:
        time.sleep(5)
    with open(os.path.join(D, "server.pid"), "w") as f:
        f.write(f"mort:{p.returncode}")
    os.close(fd)


if __name__ == "__main__":
    main()
