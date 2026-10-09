#!/usr/bin/env python3
# CUANTIC v3 — QMS + LimitsIncrease cu smart-call bazat pe semnaturi. Citeste, cere, gata.
import inspect, traceback

out = []
def log(*a):
    s = " ".join(str(x) for x in a); print(s); out.append(s)

import oci
config = oci.config.from_file()
config["region"] = "eu-frankfurt-1"
ten = config.get("tenancy")
log("sdk", oci.__version__, "ten", ten[:28] + "...")

BASE = {
    "compartment_id": ten, "scope_id": ten, "tenancy_id": ten,
    "service_name": "compute", "limit": 500,
    "region_name": "eu-frankfurt-1", "region": "eu-frankfurt-1",
    "lifecycle_state": None, "page": None,
}

def call(fn, extra_vals=None, positional=()):
    vals = dict(BASE)
    if extra_vals: vals.update(extra_vals)
    sig = inspect.signature(fn)
    kw = {}
    for p, meta in sig.parameters.items():
        if p == "self": continue
        if p in vals and vals[p] is not None:
            kw[p] = vals[p]
        elif meta.default is inspect.Parameter.empty and meta.kind not in (meta.VAR_KEYWORD, meta.VAR_POSITIONAL):
            if p not in kw:
                return None, f"lipsa valoare pentru arg obligatoriu {p}"
    try:
        return fn(*positional, **kw), None
    except TypeError as e:
        return None, f"TypeError: {e}"
    except Exception as e:
        return None, f"ERR: {str(e)[:200]}"

# ---------- QMS ----------
from oci.limits.quotas_client import QuotasClient
import oci.limits.models as lm
qc = QuotasClient(config=config)
r, err = call(qc.list_quotas)
items = []
if r: items = r.data.items or []
else: log("list_quotas esuat:", err)
a1 = [q for q in items if "a1" in (q.name or "").lower()]
log("a1 gasite:", len(a1))
for q in a1[:8]:
    log("-", q.name, "| lim:", q.limit_value, "| uzat:", q.used_value, "| ajust:", q.is_adjustable)

chname = [x for x in dir(lm) if "changequota" in x.lower() and not x.startswith("_")]
log("modele change:", chname[:4])
if a1 and chname:
    DET = getattr(lm, chname[0])
    dp = {p for p in inspect.signature(DET.__init__).parameters if p != "self"}
    log("DET params:", sorted(dp))
    targets = {}
    for q in a1:
        n = q.name.lower()
        if "core" in n or "ocpu" in n: targets[q.name] = 4
        elif "mem" in n: targets[q.name] = 24
        elif "count" in n or "instance" in n: targets[q.name] = 4
    for name, want in targets.items():
        kw = {}
        for cand in ("desired_value", "desired_limit", "new_value", "value", "limit_value"):
            if cand in dp: kw[cand] = want; break
        for cand in ("justification", "description", "reason", "comments", "notes"):
            if cand in dp: kw[cand] = "Always Free Ampere A1 pentru server Minecraft de familie/RP (20 copii, non-comercial)"; break
        kw = {k: v for k, v in kw.items() if k in dp}
        try:
            det = DET(**kw)
        except Exception as e:
            log("DET build esuat:", str(e)[:150]); continue
        # gaseste metoda de change
        mm = [m for m in dir(qc) if "change" in m and not m.startswith("_")]
        log("metode change pe client:", mm)
        done = False
        for m in mm:
            fn = getattr(qc, m)
            res, err2 = call(fn, extra_vals={"quota_name": name, "name": name, "change_quota_details": det, "change_quota_request": det}, positional=())
            if err2 and "quota_name" not in str(err2) and "compartment" not in str(err2):
                log(f"  {m}: {err2}")
            if res:
                st = getattr(res.data, "lifecycle_state", None) or getattr(res.data, "status", "?")
                log(f"CERERE QMS TRIMISA [{m}] {name} -> {want} | state: {st}")
                done = True
                break
        if not done:
            log("QMS nu a mers pt", name, "— trec la LI")

# ---------- Limits Increase (cererea clasica din Console) ----------
try:
    from oci.limits_increase.limits_increase_client import LimitsIncreaseClient
    import oci.limits_increase.models as lim
    li = LimitsIncreaseClient(config=config)
    top = [x for x in dir(lim) if x == "CreateLimitsIncreaseRequestDetails"][0]
    it  = [x for x in dir(lim) if x == "CreateLimitsIncreaseItemRequestDetails"][0]
    TP, IP = getattr(lim, top), getattr(lim, it)
    tp = {p for p in inspect.signature(TP.__init__).parameters if p != "self"}
    ip = {p for p in inspect.signature(IP.__init__).parameters if p != "self"}
    log("TOP params:", sorted(tp)); log("ITEM params:", sorted(ip))
    reqs = []
    for lname, want in (("standard-a1-core-count", 4), ("standard-a1-memory-count", 24), ("standard-a1-instance-count", 4)):
        ik = {}
        for cand in ("service_name",): ik[cand] = "compute"
        for cand in ("limit_name", "name"):
            if cand in ip: ik[cand] = lname; break
        for cand in ("desired_value", "new_value", "value", "requested_value"):
            if cand in ip: ik[cand] = want; break
        for cand in ("justification", "description", "notes", "user_reason"):
            if cand in ip: ik[cand] = "server Minecraft copii, Always Free"; break
        for cand in ("availability_domain",):
            if cand in ip: ik[cand] = None
        ik = {k: v for k, v in ik.items() if v is not None}
        try: reqs.append(IP(**ik))
        except Exception as e: log("item build", lname, ":", str(e)[:120])
    tk = {}
    for cand in ("limits", "items", "requests", "create_limits_details", "data"):
        if cand in tp: tk[cand] = reqs; break
    for cand in ("justification", "description", "notes"):
        if cand in tp: tk[cand] = "server Minecraft pentru 20 copii (Always Free A1)"; break
    det2 = TP(**tk)
    mm2 = [m for m in dir(li) if "create" in m and not m.startswith("_")]
    log("LI metode:", mm2)
    for m in mm2:
        res, err3 = call(getattr(li, m), extra_vals={
            "create_limits_increase_request_details": det2,
            "create_limits_details": det2,
            "limits_increase_request_details": det2,
        })
        if res:
            log("LIMITE CERERE TRIMISA prin", m, "| state:", getattr(res.data, "lifecycle_state", getattr(res.data, "status", "?")), "| id:", getattr(res.data, "id", "?")[:40])
            break
        else:
            log("  ", m, "->", (err3 or "?")[:160])
except Exception:
    log("LI FAIL:\n" + traceback.format_exc()[-700:])

open("/tmp/qms.txt", "w").write("\n".join(out))
print("GATA")
