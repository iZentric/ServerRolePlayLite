| HTTP | USA | AUTH | RASPUNS |
|---|---|---|---|
| 404 | GET https://api.zampto.net/ | X-Client: probe | {"success":false,"message":"Not found"}
| 404 | GET https://api.zampto.net/openapi.json | X-Client: probe | {"success":false,"message":"Endpoint not found"}
| 404 | GET https://api.zampto.net/swagger.json | X-Client: probe | {"success":false,"message":"Endpoint not found"}
| 404 | GET https://api.zampto.net/docs | X-Client: probe | {"success":false,"message":"Endpoint not found"}
| 404 | GET https://api.zampto.net/api-docs | X-Client: probe | {"success":false,"message":"Endpoint not found"}
| 200 | GET https://api.zampto.net/health | X-Client: probe | {"status":"ok","timestamp":"2026-10-08T17:52:01.309Z"}
| 404 | GET https://api.zampto.net/status | X-Client: probe | {"success":false,"message":"Endpoint not found"}
| 404 | GET https://api.zampto.net/v1 | X-Client: probe | {"success":false,"message":"Endpoint not found"}
| 404 | GET https://api.zampto.net/api | X-Client: probe | {"success":false,"message":"Endpoint not found"}
| 401 | POST https://api.zampto.net/servers/17192/power | Authorization: zamptonet-5cba1b84ce8770448bae | {"success":false,"message":"Invalid Authorization format. Use: Bearer <token>"}
| 401 | POST https://api.zampto.net/servers/17192/power | Authorization: Token zamptonet-5cba1b84ce8770 | {"success":false,"message":"Invalid Authorization format. Use: Bearer <token>"}
| 401 | POST https://api.zampto.net/servers/17192/power | Authorization: zamptonet zamptonet-5cba1b84ce | {"success":false,"message":"Invalid Authorization format. Use: Bearer <token>"}
| 401 | GET https://api.zampto.net/servers/17192 | Authorization: zamptonet-5cba1b84ce8770448bae | {"success":false,"message":"Invalid Authorization format. Use: Bearer <token>"}
| 401 | GET https://api.zampto.net/servers/17192/power | Authorization: zamptonet-5cba1b84ce8770448bae | {"success":false,"message":"Invalid Authorization format. Use: Bearer <token>"}
| 401 | GET https://api.zampto.net/servers | Authorization: zamptonet-5cba1b84ce8770448bae | {"success":false,"message":"Invalid Authorization format. Use: Bearer <token>"}
| 401 | GET https://dash.zampto.net/api/servers | Authorization: zamptonet-5cba1b84ce8770448bae | {"error":"Unauthorized"}
| 401 | GET https://dash.zampto.net/api/servers | Authorization: Token zamptonet-5cba1b84ce8770 | {"error":"Unauthorized"}
| 404 | GET https://dash.zampto.net/api/servers/17192 | Authorization: zamptonet-5cba1b84ce8770448bae | <!DOCTYPE html><html lang="en" translate="no" class="notranslate antialiased geist_mono_b4d4e0d7-module__vc6T-a__variable font-sans inter_b2991b2-module__9mH_6q__variable"><head><meta charSet="utf-8"/><meta name="viewpor
| 404 | POST https://dash.zampto.net/api/servers/17192/power | Authorization: zamptonet-5cba1b84ce8770448bae | <!DOCTYPE html><html lang="en" translate="no" class="notranslate antialiased geist_mono_b4d4e0d7-module__vc6T-a__variable font-sans inter_b2991b2-module__9mH_6q__variable"><head><meta charSet="utf-8"/><meta name="viewpor
