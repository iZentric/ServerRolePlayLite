#!/usr/bin/env python3
# CUANTIC — cere cresterea limitelor A1: QMS (oci.limits.QuotasClient) si fallback
# pe Service Limits Increase (oci.limits_increase). Auto-introspectie + inkercari multiple.
import sys, json, inspect, traceback

out = []
def log(*a):
    s = " ".join(str(x) for x in a)
    print(s); out.append(s)

import oci
log("sdk:", oci.__version__)
config = oci.config.from_file()
config["region"] = "eu-frankfurt-1"
ten = config.get("tenancy")

# ---------- 1) QMS ----------
try:
    from oci.limits.quotas_client import QuotasClient
    c = QuotasClient(config=config)
    r = c.list_quotas(scope_id=ten, service_name="compute", limit=1000)
    items = r.data.items or []
    a1 = [q for q in items if "a1" in (q.name or "").lower()]
    log("QMS: listate", len(items), "— a1:", len(a1))
    for q in a1:
        log("-", q.name, "| lim:", q.limit_value, "| uzat:", q.used_value, "| ajustabil:", q.is_adjustable)
    if a1:
        import oci.limits.models as lm
        chname = [x for x in dir(lm) if "changequota" in x.lower()]
        log("modele change:", chname[:5])
        DET = getattr(lm, chname[0]) if chname else None
        wanted = {}
        for q in a1:
            n = q.name.lower()
            if "core" in n or "ocpu" in n: wanted[q.name] = 4
            elif "memory" in n or "mem" in n: wanted[q.name] = 24
            elif "count" in n or "instance" in n: wanted[q.name] = 4
        log("tinich:", wanted)
        if DET:
            args = list(inspect.signature(DET.__init__).parameters)
            log("Detalii args:", [a for a in args if a != "self"])
            for name, want in wanted.items():
                sent = False
                for kwargs in (
                    {"desired_value": want, "justification": "Always Free Minecraft pentru 20 copii"},
                    {"desired_value": want},
                    {"desired_limit": want, "justification": "Always Free Minecraft"},
                    {"desired_value": want, "request_description": "Always Free Minecraft server for 20 kids, non-commercial"},
                ):
                    try:
                        d = DET(**kwargs)
                        try:
                            rr = c.change_quota(scope_id=ten, quota_name=name, change_quota_details=d)
                        except TypeError:
                            rr = c.change_quota(ten, name, d)
                        log("CERERE QMS OK:", name, "->", want, "| state:", getattr(rr.data, "lifecycle_state", "?"))
                        sent = True
                        break
                    except TypeError as e:
                        log("  shape esuat pt", name, ":", str(e)[:100])
                    except Exception as e:
                        log("  ERR", name, ":", str(e)[:160])
                        break
                if not sent:
                    log("nu am reusat cererea pt", name)
except Exception:
    log("QMS SECTION FAIL:\n" + traceback.format_exc()[-800:])

# ---------- 2) LimitsIncrease fallback ----------
try:
    from oci.limits_increase.limits_increase_client import LimitsIncreaseClient
    li = LimitsIncreaseClient(config=config)
    import oci.limits_increase.models as lim
    cands = [x for x in dir(lim) if "create" in x.lower() and ("detail" in x.lower() or "request" in x.lower())]
    subs = [x for x in dir(lim) if "resourcelimit" in x.lower() or "servicelimit" in x.lower() or "limitresource" in x.lower()]
    log("LI create-modele:", cands[:6], "| subs:", subs[:6])
    Create = getattr(lim, cands[0]) if cands else None
    Sub = None
    for sname in subs + [x for x in dir(lim) if "resource" in x.lower()]:
        S = getattr(lim, sname, None)
        try:
            ps = list(inspect.signature(S.__init__).parameters)
            if any("name" in p for p in ps) and any("value" in p.lower() for p in ps):
                Sub = S; log("SUB ALES:", sname, ps); break
        except Exception:
            pass
    if Create and Sub:
        try:
            items_req = []
            for lname, want in (("standard-a1-core-count", 4), ("standard-a1-memory-count", 24), ("standard-a1-instance-count", 4)):
                sp = list(inspect.signature(Sub.__init__).parameters)
                kw = {}
                for cand in ("service_name","limit_name","value","availability_domain","resource_name","limit"):
                    if cand in sp:
                        if cand == "service_name": kw[cand] = "compute"
                        if cand == "limit_name": kw[cand] = lname
                        if cand == "resource_name": kw[cand] = lname
                        if cand == "value": kw[cand] = want
                        if cand == "limit": kw[cand] = want
                items_req.append(Sub(**kw))
            cp = list(inspect.signature(Create.__init__).parameters)
            kw2 = {}
            for cand in ("service_limit_resources","limits_details","items","justification","description","user_notes"):
                if cand in cp:
                    if cand in ("service_limit_resources","limits_details","items"): kw2[cand] = items_req
                    else: kw2[cand] = "Always Free A1 pentru serverul de Minecraft al copiilor (20 jucatori, non-commercial)"
            det = Create(**kw2)
            try:
                rr = li.create_limits_increase(compartment_id=ten, create_limits_details=det)
            except TypeError:
                rr = li.create_limits_increase(ten, det)
            log("LIMITE CERERE TRIMISA:", getattr(rr.data, "lifecycle_state", getattr(rr.data, "status", "?")), "| id:", getattr(rr.data, "id", "?"))
        except Exception as e:
            log("LI create ERR:", str(e)[:300])
            log(traceback.format_exc()[-400:])
    else:
        log("LI: nu-am gasit modelele necesite")
except Exception:
    log("LI SECTION FAIL:\n" + traceback.format_exc()[-500:])

open("/tmp/qms.txt", "w").write("\n".join(out))
print("GATA")
