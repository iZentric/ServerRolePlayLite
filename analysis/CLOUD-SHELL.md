# CLOUD-SHELL 2026-10-17 13:50:28 UTC — actiune: keep
key: 1716 bytes | fp: fe:34:11:b7:f9:33:dd:bd:5c:f0:ca:aa:89:9f:f7:cb | region: eu-frankfurt-1
CLI:
{
  "data": "frmtdtikdfkz"
}
DEBUG:oci.base_client.140624122796544: 2026-10-17 13:50:54.038533+00:00: python SDK time elapsed for deserializing: 3.4749999997529812e-06
DEBUG:oci.base_client.140624122796544: 2026-10-17 13:50:54.038554+00:00: Response returned
DEBUG:oci.base_client.140624122796544:time elapsed for request: 0.5173083270000021
DEBUG:oci_cli.cli_util: 2026-10-17 13:50:54.038598+00:00: time elapsed calling to_dict from render: 1.6119999983743583e-06
DEBUG:oci_cli.cli_util: 2026-10-17 13:50:54.039221+00:00: total memory usage before printing: 74.2KiB (76024)
DEBUG:oci_cli.cli_util: 2026-10-17 13:50:54.039300+00:00: Time elapsed printing response data: <1ms
DEBUG:oci_cli.cli_util: 2026-10-17 13:50:54.039321+00:00: total memory usage after printing: 74.2KiB (76024)
env OCI_TENANCY is set
env OCI_REGION is set
env OCI_CLI_SUPPRESS_FILE_PERMISSIONS_WARNING is set
env OCI_USER is set
env OCI_FINGERPRINT is set
env OCI_PYTHON_SDK_NO_SERVICE_IMPORTS is set
send: b'GET /n HTTP/1.1\r\nuser-agent: Oracle-PythonSDK/2.188.0 (python 3.12.3; x86_64-Linux) Oracle-PythonCLI/3.95.0\r\naccept-encoding: gzip, deflate\r\naccept: application/json\r\nconnection: keep-alive\r\ncontent-type: application/json\r\nopc-client-request-id: 46AB5A3D811E40118F3E38355E062359\r\nopc-client-retries: true\r\nopc-client-info: Oracle-PythonSDK/2.188.0\r\nopc-request-id: 615827C6692746C3B44D23E5BF3CB877\r\ndate: Sat, 17 Oct 2026 13:50:53 GMT\r\nhost: objectstorage.eu-frankfurt-1.oraclecloud.com\r\nauthorization: Signature algorithm="rsa-sha256",headers="date (request-target) host",keyId="ocid1.tenancy.oc1..aaaaaaaanlzitmrgwn5f3g3iyapyiuxt2ayh43u6mdq3nszvcswrkcw5eyfa/ocid1.user.oc1..aaaaaaaafg2fu7zqt4q7kzdy7fzqbvg6wr5wj2f3yb5e452eas7cu3hbghma/fe:34:11:b7:f9:33:dd:bd:5c:f0:ca:aa:89:9f:f7:cb",signature="dJ4HK3/yOCPGtZm4uZCoO2QlyUkIQ+8Z86KvxeC8O4/bmQ2ilQweqbbxdkE0S1Q0GQIXvmQLxA7TynoHXbcRHE+Lu4Q0aVo3HgN3S+r5ZC9yXnMdMKQOrK60HQGCLM92FQ5jZHaMEDTzj1n9Sl+GCWjWNw6h7US8W0GqLK9sV6g+nlDMhd/fsLTjpq0CJWDS9GPOddYgSyqeferLgMBlPJol2LnrUiUOM43Gs5bXVPjfpqO/S9s+jAMFnxrc+BQanhkVItD24u1/J/7C1jum+I5jlK+4PMCZfq1vKKnKQs0eTcQSlE8WUlwzboZAiYVDgSS85BOEK1Q2VIjTEVFW2w==",version="1"\r\n\r\n'
reply: 'HTTP/1.1 200 OK\r\n'
header: Content-Type: application/json
header: Content-Length: 14
header: opc-client-request-id: 46AB5A3D811E40118F3E38355E062359
header: date: Sat, 17 Oct 2026 13:50:53 GMT
header: opc-request-id: fra-1:eX8gXHSNuB1xti-NVzfuo_qqd-83UUbwrvSwEdxPVVhdpwIqzvc547BG0fNj_CdJ
header: x-api-id: native
header: x-content-type-options: nosniff
header: strict-transport-security: max-age=31536000; includeSubDomains
header: access-control-allow-origin: *
header: access-control-allow-methods: POST,PUT,GET,HEAD,DELETE,OPTIONS
header: access-control-allow-credentials: true
header: access-control-expose-headers: access-control-allow-credentials,access-control-allow-methods,access-control-allow-origin,content-length,content-type,date,opc-client-info,opc-client-request-id,opc-request-id,strict-transport-security,x-api-id,x-content-type-options
{
  "data": "frmtdtikdfkz"
}
--- python keepalive ---
[raw user] len=76 repr='oci'..'hma'
[raw tenancy] len=79 repr='oci'..'yfa'
[raw fingerprint] len=47 repr='fe:'..':cb'
[raw region] len=14 repr='eu-'..'t-1'
[raw key_file] len=33 repr='/ho'..'pem'
[fp curat] fe:34:11:b7:f9:33:dd:bd:5c:f0:ca:aa:89:9f:f7:cb
[SDK] FAIL: RequestException: ('OCIConnectionPool(host=\'identity.eufrankfurt1.oci.oraclecloud.com\', port=443): Max retries exceeded with url: /20160918/regions (Caused by NameResolutionError("OCIConnection(host=\'identity.eufrankfurt1.oci.oraclecloud.com\', port=443): Failed to resolve \
[py headers trims]  {'Date': 'Sat, 17 Oct 2026 13:52:2...', 'Accept': 'application/json...', 'Content-Type': 'application/json...', 'Authorization': 'Signature algorithm="rsa...'}
[py-objectstorage] 401 {"code":"NotAuthenticated","message":"The required information to complete authentication was not provided."}
[sdk-signer] ESUAT: NameError: name 'oci' is not defined
[curl-objectstorage] 401 b'{"code":"NotAuthenticated","message":"The required information to complete authentication was not pr'
[AUTH-TEST compartment] HTTP 404 {
  "code" : "NotAuthorizedOrNotFound",
  "message" : "Authorization failed or requested resource not found."
}
[identity@eu-frankfurt-1] HTTP 401 {"code":"NotAuthenticated","message":"Failed to verify the HTTP(S) Signature"}
[auth] identity raspunde prin eu-frankfurt-1; HOME region: NEDESCIFRAT (vezi HTTP mai sus)
[sdk-call esuat: TypeError Signer.__init__() missing 3 required positional arguments: 'user', 'fingerprint', and 'private_key_f] -> fallback manual
[env-get] 404 {
  "code" : "NotAuthorizedOrNotFound",
  "message" : "Authorization failed or requested resource not found."
}
[sdk-call esuat: TypeError Signer.__init__() missing 3 required positional arguments: 'user', 'fingerprint', and 'private_key_f] -> fallback manual
[env-create] 404 {
  "code" : "NotAuthorizedOrNotFound",
  "message" : "Authorization failed or requested resource not found."
}
[sdk-call esuat: TypeError Signer.__init__() missing 3 required positional arguments: 'user', 'fingerprint', and 'private_key_f] -> fallback manual
[sdk-call esuat: TypeError Signer.__init__() missing 3 required positional arguments: 'user', 'fingerprint', and 'private_key_f] -> fallback manual
[session] 404 {
  "code" : "NotAuthorizedOrNotFound",
  "message" : "Authorization failed or requested resource not found."
}
