| HTTP | USA | AUTH | RASPUNS |
|---|---|---|---|
| 200 | GET https://api.zampto.net/health | Authorization: Bearer zamptonet-5cba1b84ce877 | {"status":"ok","timestamp":"2026-10-08T17:53:54.880Z"}
| 200 | GET https://api.zampto.net/health | Authorization: Bearer gunoi-gunos-12345 | {"status":"ok","timestamp":"2026-10-08T17:53:55.679Z"}
| 404 | GET https://api.zampto.net/servers | Authorization: Bearer zamptonet-5cba1b84ce877 | {"success":false,"message":"Endpoint not found"}
| 404 | GET https://api.zampto.net/servers/17192 | Authorization: Bearer zamptonet-5cba1b84ce877 | {"success":false,"message":"Endpoint not found"}
| 404 | GET https://api.zampto.net/servers/17192/power | Authorization: Bearer zamptonet-5cba1b84ce877 | {"success":false,"message":"Endpoint not found"}
| 404 | GET https://api.zampto.net/servers/17192/state | Authorization: Bearer zamptonet-5cba1b84ce877 | {"success":false,"message":"Endpoint not found"}
| 404 | GET https://api.zampto.net/servers/17192/status | Authorization: Bearer zamptonet-5cba1b84ce877 | {"success":false,"message":"Endpoint not found"}
| 404 | GET https://api.zampto.net/servers/17192/restart | Authorization: Bearer zamptonet-5cba1b84ce877 | {"success":false,"message":"Endpoint not found"}
| 404 | GET https://api.zampto.net/servers/1388b9af/power | Authorization: Bearer zamptonet-5cba1b84ce877 | {"success":false,"message":"Endpoint not found"}
| 404 | GET https://api.zampto.net/servers/15254.1388b9af/power | Authorization: Bearer zamptonet-5cba1b84ce877 | {"success":false,"message":"Endpoint not found"}
| 404 | GET https://api.zampto.net/server/17192/power | Authorization: Bearer zamptonet-5cba1b84ce877 | {"success":false,"message":"Endpoint not found"}
| 404 | GET https://api.zampto.net/power/17192 | Authorization: Bearer zamptonet-5cba1b84ce877 | {"success":false,"message":"Endpoint not found"}
| 429 | GET https://api.zampto.net/servers/17192/command | Authorization: Bearer zamptonet-5cba1b84ce877 | error code: 1015
| 429 | GET https://api.zampto.net/servers/17192/actions | Authorization: Bearer zamptonet-5cba1b84ce877 | error code: 1015
| 429 | POST https://api.zampto.net/servers/17192/power | Authorization: Bearer zamptonet-5cba1b84ce877 | error code: 1015
| 429 | POST https://api.zampto.net/servers/17192/restart | Authorization: Bearer zamptonet-5cba1b84ce877 | error code: 1015
| 404 | POST https://api.zampto.net/server/17192/power | Authorization: Bearer zamptonet-5cba1b84ce877 | {"success":false,"message":"Endpoint not found"}
| 404 | POST https://api.zampto.net/power | Authorization: Bearer zamptonet-5cba1b84ce877 | {"success":false,"message":"Endpoint not found"}
| 401 | GET https://dash.zampto.net/api/servers | Cookie: next-auth.session-token=zamptonet-5cb | {"error":"Unauthorized"}
| 401 | GET https://dash.zampto.net/api/servers | Cookie: authjs.session-token=zamptonet-5cba1b | {"error":"Unauthorized"}
| 401 | GET https://dash.zampto.net/api/servers | Cookie: __Secure-next-auth.session-token=zamp | {"error":"Unauthorized"}
| 401 | GET https://dash.zampto.net/api/servers | Cookie: token=zamptonet-5cba1b84ce8770448bae3 | {"error":"Unauthorized"}
| 401 | GET https://dash.zampto.net/api/servers | Cookie: auth=zamptonet-5cba1b84ce8770448bae3d | {"error":"Unauthorized"}
| 401 | GET https://dash.zampto.net/api/servers | Cookie: session_token=zamptonet-5cba1b84ce877 | {"error":"Unauthorized"}
| 401 | GET https://dash.zampto.net/api/servers | Cookie: zamptonet_session=zamptonet-5cba1b84c | {"error":"Unauthorized"}
| 401 | GET https://dash.zampto.net/api/servers | Cookie: connect.sid=zamptonet-5cba1b84ce87704 | {"error":"Unauthorized"}

## SFTP bataie unica
BATAIE-UNICA-REUSITA
Login failed: Login incorrect
STERS-DE-PE-DISC
Login failed: Login incorrect
get: logs/latest.log: Login failed: Login incorrect
NOLOG
