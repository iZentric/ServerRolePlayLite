#!/usr/bin/env python3
# CUANTIC — cere cresterea de limita A1 direct prin OCI SDK (QMS), ocolind CLI-ul batran
import sys, json, traceback

out = []
def log(*a):
    s = " ".join(str(x) for x in a)
    print(s); out.append(s)

try:
    import oci, pkgutil
    log("sdk:", oci.__version__)
    mods = [m.name for m in pkgutil.iter_modules(oci.__path__)]
    cand = [m for m in mods if "quota" in m.lower() or "limit" in m.lower()]
    log("module candidate:", cand)
    config = oci.config.from_file()  # cloud shell are config + token de user
    ten = config.get("tenancy")
    log("tenancy:", ten[:24], "...")
except Exception:
    log("IMPORT/CONFIG ESUAZ:\n" + traceback.format_exc()); open("/tmp/qms.txt","w").write("\n".join(out)); sys.exit(0)

if not cand:
    log("QMS nu exista in acest SDK — ramane optiunea Console/tichet.")
    open("/tmp/qms.txt","w").write("\n".join(out)); sys.exit(0)

try:
    signer = None
    try:
        signer = oci.signer_signers.iam_signer  # noop guard
    except Exception:
        pass
    client = None
    for modname in ("quotas", "limits", *[c for c in cand if c not in ("quotas","limits")]):
        try:
            mod = __import__("oci."+modname, fromlist=["*"])
            clsnames = [x for x in dir(mod) if "client" in x.lower() and not x.startswith("_")]
            log(f"mod {modname}: clase:", clsnames[:6])
            for cls in clsnames:
                try:
                    c = getattr(mod, cls)(config=config, signer=signer)
                    client = c
                    log("CLIENT MONTAT:", modname + "." + cls)
                    break
                except Exception as e:
                    log("  ", cls, "->", str(e)[:120])
            if client: break
        except Exception as e:
            log("mod ", modname, " lipsa: ", str(e)[:80])
    if client is None:
        log("Niciun client de quotas construit.")
        open("/tmp/qms.txt","w").write("\n".join(out)); sys.exit(0)
    meths = [m for m in dir(client) if not m.startswith("_") and callable(getattr(client,m))]
    log("metode:", meths)
    # listare
    lq = getattr(client, "list_quotas", None) or getattr(client, "list_service_quotas", None) or getattr(client, "list_quotas", None)
    if lq:
        try:
            r = lq(scope_id=ten, service_name="compute", limit=200)
            data = r.data.items or []
            a1 = [q for q in data if "a1" in (q.name or "").lower()]
            log(f"listate {len(data)}; a1: {len(a1)}")
            for q in a1:
                log("-", q.name, "| limit:", getattr(q,"limit_value",None), "| used:", getattr(q,"used_value",None), "| adjustable:", getattr(q,"is_adjustable",None))
        except Exception:
            log("list_quotas esua cu kwargs, incerc alt shape:\n", traceback.format_exc()[-400:])
            try:
                r = lq(ten)
                data = r.data.items or []
                a1 = [q for q in data if "a1" in (q.name or "").lower()]
                log("fallback: listate", len(data), "a1:", len(a1))
                for q in a1:
                    log("-", q.name, "|", getattr(q,"limit_value",None))
            except Exception:
                log("si fallback la fel:\n", traceback.format_exc()[-400:])
                data = []
    else:
        data = []
    # cerere de change
    ch = getattr(client, "change_quota", None) or getattr(client, "create_quota_change_request", None) or getattr(client, "request_quota_change", None)
    if ch:
        targets = {}
        for q in data:
            n = (q.name or "")
            if "a1" not in n.lower(): continue
            if "core" in n.lower() or "ocpu" in n.lower(): targets[n] = 4
            elif "memory" in n.lower(): targets[n] = 24
            elif "instance" in n.lower() or "count" in n.lower(): targets[n] = 4
        for name, want in targets.items():
            try:
                det = None
                for clsmod in ("oci.quotas.models","oci."+cand[0]+".models"):
                    try:
                        m = __import__(clsmod, fromlist=["*"])
                        for cn in dir(m):
                            if "change" in cn.lower() and "detail" in cn.lower():
                                det = getattr(m, cn)(quota_name=name, desired_value=want, justification="Minecraft server Always Free pentru 20 copii; home lab non-commercial", requested_by_principal=None)
                                break
                    except Exception:
                        pass
                    if det: break
                if det is None:
                    log("nu gasesc modelul de ChangeQuotaDetails — metoda exista dar nu pot construi body:", name)
                    continue
                rr = ch(ten, det)
                log("CERERE TRIMISA pt", name, "->", want, "| status:", getattr(rr.data,"lifecycle_state",getattr(rr.data,"status","?")))
            except Exception as e:
                log("change esua pt", name, ":", str(e)[:200])
                log(traceback.format_exc()[-300:])
except Exception:
    log("EXCEPTIE GENERALA:\n" + traceback.format_exc()[-1200:])

open("/tmp/qms.txt","w").write("\n".join(out))
print("GATA-FISIER /tmp/qms.txt")
