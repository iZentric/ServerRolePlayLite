#!/usr/bin/env python3
# CUANTIC v3 — QMS + LimitsIncrease cu smart-call bazat pe semnaturi. Citeste, cere, gata.
import inspect, traceback

out = []
def _safe_attr(o, *names, dflt="?"):
    for n in names:
        v = getattr(o, n, None)
        if v is not None: return v
    return dflt
def log(*a):
    s = " ".join(str(x) for x in a); print(s); out.append(s)

import oci
try:
    config = oci.config.from_file()
except Exception:
    open("/tmp/qms.txt","w").write("CONFIG FAIL:\n"+traceback.format_exc()); raise SystemExit(0)
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
try:
    from oci.limits.quotas_client import QuotasClient
except Exception:
    from oci.limits import QuotasClient
import oci.limits.models as lm
qc = QuotasClient(config=config)
r, err = call(qc.list_quotas)
items = []
if r: items = getattr(getattr(r,"data",None),"items",None) or []
else: log("list_quotas esuat:", err)
a1 = [q for q in items if "a1" in (_safe_attr(q,"name","quota_name","") or "").lower()]
log("a1 gasite:", len(a1))
for q in a1[:8]:
    log("-", _safe_attr(q,"name"), "| lim:", _safe_attr(q,"limit_value","limitValue"), "| uzat:", _safe_attr(q,"used_value","usedValue"), "| ajust:", _safe_attr(q,"is_adjustable","isAdjustable"))

chname = [x for x in dir(lm) if "changequota" in x.lower() and not x.startswith("_")]
log("modele change:", chname[:4])
if a1 and chname:
    DET = getattr(lm, chname[0])
    dp = {p for p in inspect.signature(DET.__init__).parameters if p != "self"}
    log("DET params:", sorted(dp))
    targets = {}
    for q in a1:
        n = q.name.lower()
        if "core" in n or "ocpu" in n: targets[_safe_attr(q,"name","quota_name")] = 4
        elif "mem" in n: targets[_safe_attr(q,"name","quota_name")] = 24
        elif "count" in n or "instance" in n: targets[_safe_attr(q,"name","quota_name")] = 4
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

# ---------- LI: explorare vars() + trimitere ----------
try:
    from oci.limits_increase.limits_increase_client import LimitsIncreaseClient
    import oci.limits_increase.models as lim
    li = LimitsIncreaseClient(config=config)
    TP = lim.CreateLimitsIncreaseRequestDetails
    IP = lim.CreateLimitsIncreaseItemRequestDetails
    probe = IP(service_name="compute", limit_name="standard-a1-core-count", value=4, desired_value=4, availability_domain="x")
    log("VARS item:", vars(probe))
    probe2 = TP(limits_details=[probe], limits=[probe], justification="test")
    log("VARS top:", vars(probe2))
    items = []
    for ln, wv in (("standard-a1-core-count",4),("standard-a1-memory-count",24),("standard-a1-instance-count",4)):
        items.append(IP(service_name="compute", limit_name=ln, value=wv))
    top = None
    for kw in ({"limits_details": items}, {"limits": items}, {"items": items}):
        try:
            top = TP(**kw); log("top cu", list(kw)); break
        except Exception as e:
            log("  refuz", list(kw), str(e)[:60])
    # incearca toate combinatiile de chei posibile
    sent = None
    for attempt in range(4):
        try:
            if attempt == 0: r = li.create_limits_increase_request(compartment_id=ten, create_limits_increase_request_details=top)
            elif attempt == 1: r = li.create_limits_increase_request(ten, top)
            elif attempt == 2: r = li.create_limits_increase_request(compartment_id=ten, body=top)
            else: r = li.create_limits_increase_request(ten, {"limits_details": [vars(i) for i in items]})
            sent = r; break
        except TypeError as e:
            log("attempt", attempt, "TypeError:", str(e)[:120])
        except Exception as e:
            log("attempt", attempt, ":", str(e)[:240])
    if sent:
        log("CERERE TRIMISA! data:", str(sent.data)[:300])
except Exception as e:
    log("LI FAIL:", str(e)[:300])

open("/tmp/qms.txt", "w").write("\n".join(out))
print("GATA")
