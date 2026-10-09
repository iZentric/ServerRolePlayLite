# NET — 2026-10-09 19:29:46 UTC
```
core: True net: True
instante RUNNING: Evovv/VM.Standard.E2.1.Micro, iZen/VM.Standard.E2.1.Micro
tinta: iZen VM.Standard.E2.1.Micro nuekvkosqq
vnic: xvakaonqdq privat: 10.0.0.7 public: 158.101.162.54
IP_PUBLIC= 158.101.162.54
security lists in nkrk4hvobq : security list for private subnet-n8n0vcn, Default Security List for n8n0vcn
security list: AttributeError: 'TcpOptions' object has no attribute 'destination_port'
GATA
---- brute ----
instanta: iZen VM.Standard.E2.1.Micro
Traceback (most recent call last):
  File "scripts/net.py", line 33, in <module>
    vnic = net.get_vnic(a.vnic_id).data; nsgs = list(a.network_security_group_ids or []); break
AttributeError: 'VnicAttachment' object has no attribute 'network_security_group_ids'
rc=1
```
