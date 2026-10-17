# CLOUD-SHELL 2026-10-17 13:24:18 UTC — actiune: keep
key: 1716 bytes | fp: fe:34:11:b7:f9:33:dd:bd:5c:f0:ca:aa:89:9f:f7:cb | region: eu-frankfurt-1
CLI:
{
  "data": "frmtdtikdfkz"
}
DEBUG:oci.base_client.139877992882464: 2026-10-17 13:25:00.208785+00:00: python SDK time elapsed for deserializing: 5.199000000288834e-06
DEBUG:oci.base_client.139877992882464: 2026-10-17 13:25:00.208825+00:00: Response returned
DEBUG:oci.base_client.139877992882464:time elapsed for request: 0.6937836560000079
DEBUG:oci_cli.cli_util: 2026-10-17 13:25:00.208917+00:00: time elapsed calling to_dict from render: 3.5759999974516177e-06
DEBUG:oci_cli.cli_util: 2026-10-17 13:25:00.217001+00:00: total memory usage before printing: 73.9KiB (75688)
DEBUG:oci_cli.cli_util: 2026-10-17 13:25:00.217103+00:00: Time elapsed printing response data: <1ms
DEBUG:oci_cli.cli_util: 2026-10-17 13:25:00.217148+00:00: total memory usage after printing: 73.9KiB (75688)
env OCI_TENANCY is set
env OCI_REGION is set
env OCI_CLI_SUPPRESS_FILE_PERMISSIONS_WARNING is set
env OCI_USER is set
env OCI_FINGERPRINT is set
env OCI_PYTHON_SDK_NO_SERVICE_IMPORTS is set
send: b'GET /n HTTP/1.1\r\nuser-agent: Oracle-PythonSDK/2.188.0 (python 3.12.3; x86_64-Linux) Oracle-PythonCLI/3.95.0\r\naccept-encoding: gzip, deflate\r\naccept: application/json\r\nconnection: keep-alive\r\ncontent-type: application/json\r\nopc-client-request-id: B0C8157C4BD34385A0E0293843D8491F\r\nopc-client-retries: true\r\nopc-client-info: Oracle-PythonSDK/2.188.0\r\nopc-request-id: ACEBCC023F0841B19489655E2B9F48C6\r\ndate: Sat, 17 Oct 2026 13:24:59 GMT\r\nhost: objectstorage.eu-frankfurt-1.oraclecloud.com\r\nauthorization: Signature algorithm="rsa-sha256",headers="date (request-target) host",keyId="ocid1.tenancy.oc1..aaaaaaaanlzitmrgwn5f3g3iyapyiuxt2ayh43u6mdq3nszvcswrkcw5eyfa/ocid1.user.oc1..aaaaaaaafg2fu7zqt4q7kzdy7fzqbvg6wr5wj2f3yb5e452eas7cu3hbghma/fe:34:11:b7:f9:33:dd:bd:5c:f0:ca:aa:89:9f:f7:cb",signature="IucoTZ+Nb7ky0+UVQqFaloR8kYbgml4TZvPEYpS0Y3THmb/Ln7yKnYddogzUhOAMjFTXh81BPJ3xUTOaOtOAEy1R8gEL6FO8xDpVyZHJQwt+SypvCnE8jD2//Tn1MqGAiDninnBBORzN+Eg0lgJtkL0bJIceK3Mwjv/nfpZTFB1BGDoo7eENtFITFQKtDjJU3bBskOdgq4wUcSTypjUXhSUyRGohBXBuO+3qTTsTgrl9HLJl8pmTKD2H2hNrjbAl446q7np2/lvdOBTjPxgBO9qHsPNfZrT8C8GHLxFGguSemOHs6L/zGnsleeqT6RrU1H6Lo7XMM8PxxvCPqBo1tg==",version="1"\r\n\r\n'
reply: 'HTTP/1.1 200 OK\r\n'
header: Content-Type: application/json
header: Content-Length: 14
header: opc-client-request-id: B0C8157C4BD34385A0E0293843D8491F
header: date: Sat, 17 Oct 2026 13:25:00 GMT
header: opc-request-id: fra-1:S__j-oF_djo5AX7j7jr3gS87I-c8_tJlyqL26l_mlVKjWAVhGwhKq65wjtb0iTEh
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
[AUTH-TEST compartment] HTTP 404 {
  "code" : "NotAuthorizedOrNotFound",
  "message" : "Authorization failed or requested resource not found."
}
[identity@eu-frankfurt-1] HTTP 401 {"code":"NotAuthenticated","message":"Failed to verify the HTTP(S) Signature"}
[auth] identity raspunde prin eu-frankfurt-1; HOME region: NEDESCIFRAT (vezi HTTP mai sus)
[env-get] 404 {
  "code" : "NotAuthorizedOrNotFound",
  "message" : "Authorization failed or requested resource not found."
}
[env-create] 404 {
  "code" : "NotAuthorizedOrNotFound",
  "message" : "Authorization failed or requested resource not found."
}
[session] 404 {
  "code" : "NotAuthorizedOrNotFound",
  "message" : "Authorization failed or requested resource not found."
}
