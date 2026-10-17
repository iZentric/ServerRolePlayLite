#!/usr/bin/env python3
# Pazonic Oracle Cloud Shell: prin chei API (fara browser) deschide sesiune = activitate
# -> ceasul de 7 zile se resetaza. Ruleaza pe hosted cu secretele OCI din repo.
import subprocess, sys, os, json, time, datetime, base64, urllib.request, urllib.error
D = os.path.expanduser("~/.oci")
def cfg():
    c = {}
    for l in open(f"{D}/config"):
        if "=" in l:
            k, v = l.split("=", 1); c[k.strip()] = v.strip()
    return c
def hdr(method, path, host, c, body=None):
    date = datetime.datetime.now(datetime.timezone.utc).strftime("%a, %d %b %Y %H:%M:%S GMT")
    sign = f'"(request-target)": {method.lower()} {path}\nhost: {host}\ndate: {date}'
    sig = subprocess.run(["openssl","dgst","-sha256","-sign",c["key_file"]],
                         input=sign.encode(), capture_output=True)
    if sig.returncode != 0:
        raise RuntimeError("sign: " + sig.stderr.decode()[:150])
    b64 = subprocess.run(["openssl","base64","-A"], input=sig.stdout, capture_output=True).stdout.decode()
    keyid = f'{c.get("tenancy","")}/{c["user"]}/{c["fingerprint"]}'
    auth = (f'Signature algorithm="rsa-sha256",headers="(request-target) host date",'
            f'keyId="{keyid}",signature="{b64}",version="1"')
    h = {"Date": date, "Accept": "application/json", "Content-Type": "application/json",
         "Authorization": auth}
    if body is not None:
        import hashlib
        h["x-content-sha256"] = base64.b64encode(hashlib.sha256(body.encode()).digest()).decode()
    return h
def call(method, c, path, body=None):
    host = f"cloudshell.{c['region']}.oci.oraclecloud.com"
    req = urllib.request.Request(f"https://{host}{path}", method=method,
                                 headers=hdr(method, path, host, c, body),
                                 data=body.encode() if body else None)
    try:
        with urllib.request.urlopen(req, timeout=40) as r:
            t = r.read(900).decode()
            return r.status, t
    except urllib.error.HTTPError as e:
        return e.code, e.read(400).decode()
    except Exception as e:
        return -1, str(e)[:200]
def home_region(c):
    # GET /regions e PUBLIC (fara auth) — NU testeaza semnatura. Testul real: GetCompartmentById(tenancy).
    import urllib.parse
    probe = c.get("region") or "eu-frankfurt-1"
    host = f"identity.{probe}.oci.oraclecloud.com"
    path = f"/20160918/compartment/{c['tenancy']}"
    req = urllib.request.Request(f"https://{host}{path}", method="GET", headers=hdr("GET", path, host, c))
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            d = json.loads(r.read(50000).decode())
            nm = d.get("name", "?")
            print(f"[AUTH-TEST compartment] 200 OK, tenancy='{nm}' => SEMNATURA CORECTA in {probe}")
    except urllib.error.HTTPError as e:
        print(f"[AUTH-TEST compartment] HTTP {e.code} {e.read(200).decode()[:160]}")
    # home region din lista publica (merge si fara auth)
    for probe in (c.get("region"), "us-ashburn-1"):
        if not probe: continue
        host = f"identity.{probe}.oci.oraclecloud.com"
        path = "/20160918/regions"
        req = urllib.request.Request(f"https://{host}{path}", method="GET", headers=hdr("GET", path, host, c))
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                data = json.loads(r.read(200000).decode())
                names = [x["name"] for x in data.get("data", [])]
                if names:
                    return probe, names[0]
        except urllib.error.HTTPError as e:
            body = e.read(200).decode()
            print(f"[identity@{probe}] HTTP {e.code} {body[:120]}")
            if e.code in (401, 404) and "sign" in body.lower(): return probe, None
        except Exception as e:
            print(f"[identity@{probe}] {e}")
    return probe, None
def sdk_probe():
    try:
        import oci
    except ImportError:
        print("[SDK] oci nelansat (pip a esuat pe hosted)"); return False
    c = cfg()
    for k in ("user","tenancy","fingerprint","region","key_file"):
        v = c.get(k,"")
        print(f"[raw {k}] len={len(v)} repr={v[:3]!r}..{v[-3:]!r}")
    # scriem config curat, valorile taiate de orice caracter invizibil
    import re as _re
    clean = {}
    for k in ("user","tenancy","fingerprint","region","key_file"):
        v = c.get(k,"")
        if k == "fingerprint": v = _re.sub(r'[^0-9a-fA-F:]', '', v).lower()
        elif k == "key_file": v = v.strip()
        else: v = _re.sub(r'[^a-zA-Z0-9._]', '', v)
        clean[k] = v
    with open(os.path.expanduser("~/.oci/config2"), "w") as f:
        f.write("[DEFAULT]\n" + "\n".join(f"{k}={v}" for k, v in clean.items()) + "\n")
    print(f"[fp curat] {clean['fingerprint']}")
    try:
        cc = oci.config.from_file(os.path.expanduser("~/.oci/config2"))
        oci.config.validate_config(cc)
        ic = oci.identity.IdentityClient(cc)
        r = ic.list_regions()
        print(f"[SDK] OK, home region: {r.data[0].name}")
        return True
    except Exception as e:
        print(f"[SDK] FAIL: {type(e).__name__}: {str(e)[:260]}")
        return False
def main():
    c = cfg(); mode = sys.argv[1] if len(sys.argv) > 1 else "keep"
    sdk_probe()
    tried, home = home_region(c)
    print(f"[auth] identity raspunde prin {tried}; HOME region: {home or 'NEDESCIFRAT (vezi HTTP mai sus)'}")
    if home and home != c.get("region"):
        c["region"] = home
        print(f"[region] schimb in home: {home}")
    st, body = call("GET", c, "/20150802/cloudShell")
    print(f"[env-get] {st} {body[:200]}")
    if st == 404 or "NotFound" in body:
        st2, b2 = call("POST", c, "/20150802/cloudShell", json.dumps({"numPublicKeys": 1}))
        print(f"[env-create] {st2} {b2[:200]}")
        st, body = call("GET", c, "/20150802/cloudShell")
    if mode == "status":
        return
    # cheie efemera pt sesiune
    subprocess.run(["openssl","ecparam","-name","prime256v1","-genkey","-noout","-out","/tmp/sk.pem"],check=True,capture_output=True)
    pub = subprocess.run(["openssl","ec","-in","/tmp/sk.pem","-pubout"],capture_output=True).stdout.decode()
    os.remove("/tmp/sk.pem")
    det = {"createPublicKeyRequest":{"description":"functity-keepalive","keyAlgorithm":"ECDSA_P256","publicKey":pub}}
    st3, b3 = call("POST", c, "/20150802/cloudShell/sessions", json.dumps(det))
    print(f"[session] {st3} {b3[:200]}")
    if st3 in (200, 201, 202):
        try:
            sid = json.loads(b3)["id"]
            for i in range(6):
                time.sleep(10)
                stg, bg = call("GET", c, f"/20150802/cloudShell/sessions/{sid}")
                try: lc = json.loads(bg).get("lifecycleState","?")
                except Exception: lc = "?"
                print(f"[wait {i*10}s] {stg} {lc}")
                if lc in ("ACTIVE", "FAILED", "DELETED"): break
            std, bd = call("DELETE", c, f"/20150802/cloudShell/sessions/{sid}")
            print(f"[terminate] {std} {bd[:120]}")
        except Exception as e:
            print("[parse]", e)
main()
