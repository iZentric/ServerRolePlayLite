#!/usr/bin/env python3
# Paznicul Oracle Cloud Shell: semneaza cereri OCI REST (RSA-SHA256) si deschide/închide
# o sesiune de Cloud Shell = activitate näcontata -> ceasul de 7 zile se reseteaza.
import subprocess, sys, os, datetime, urllib.request, urllib.error
D = os.path.expanduser("~/.oci")
def cfg():
    c = {}
    for l in open(f"{D}/config"):
        if "=" in l: k,v = l.split("=",1); c[k.strip()] = v.strip()
    return c
def sig(method, path, host, c):
    date = datetime.datetime.now(datetime.timezone.utc).strftime("%a, %d %b %Y %H:%M:%S GMT")
    req = f'"(request-target)": {method} {path}\nhost: {host}\ndate: {date}'
    p = subprocess.run(["openssl","dgst","-sha256","-sign",c["key_file"]],
                       input=req.encode(), capture_output=True)
    if p.returncode != 0: raise RuntimeError("openssl sign: "+p.stderr.decode()[:120])
    s = subprocess.run(["openssl","base64","-A"], input=p.stdout, capture_output=True).stdout.decode()
    hdr = (f'Signature headers="(request-target) host date", '
           f'algorithm="rsa-sha256", keyId="{c["user"]}", fingerprint="{c["fingerprint"]}", '
           f'signature="{s}"')
    return {"Date": date, "Host": host, "Authorization": hdr, "Accept": "application/json",
            "Content-Type": "application/json"}
def call(method, c, path, body=None):
    host = f"cloudshell.{c['region']}.oraclecloud.com"
    url = f"https://{host}{path}"
    req = urllib.request.Request(url, method=method, headers=sig(method, path, host, c),
                                 data=body.encode() if body else None)
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status, r.read(600).decode()
    except urllib.error.HTTPError as e:
        return e.code, e.read(300).decode()
    except Exception as e:
        return -1, str(e)[:200]
def main():
    c = cfg(); mode = sys.argv[1] if len(sys.argv)>1 else "keep"
    st, body = call("GET", c, "/20150802/cloudShell")
    print(f"env get: {st} {body[:160]}")
    if mode == "keep":
        # sesiune = activitate; daca nu exista, cream; dam 20s si terminam curat
        if st in (404,) or "not found" in body.lower() or "NOT_FOUND" in body:
            st2, b2 = call("POST", c, "/20150802/cloudShell", '{"numPublicKeys": 0}')
            print(f"env create: {st2} {b2[:160]}")
        st3, b3 = call("POST", c, "/20150802/cloudShell/sessions", "{}")
        print(f"session: {st3} {b3[:160]}")
        if st3 in (200,201,202):
            import json as J, time
            try:
                sid = J.loads(b3)["id"]
                time.sleep(20)
                st4, _ = call("DELETE", c, f"/20150802/cloudShell/sessions/{sid}")
                print(f"terminate: {st4}")
            except Exception as e:
                print("sid parse:", e)
main()
