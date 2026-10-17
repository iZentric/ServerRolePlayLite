# CLOUD-SHELL 2026-10-17 13:55:13 UTC — actiune: keep
key: 1716 bytes | fp: fe:34:11:b7:f9:33:dd:bd:5c:f0:ca:aa:89:9f:f7:cb | region: eu-frankfurt-1
CLI:
{
  "data": "frmtdtikdfkz"
}
DEBUG:oci.base_client.140296046357024: 2026-10-17 13:55:56.053010+00:00: python SDK time elapsed for deserializing: 5.3199999996422775e-06
DEBUG:oci.base_client.140296046357024: 2026-10-17 13:55:56.053069+00:00: Response returned
DEBUG:oci.base_client.140296046357024:time elapsed for request: 0.6313969569999927
DEBUG:oci_cli.cli_util: 2026-10-17 13:55:56.053169+00:00: time elapsed calling to_dict from render: 3.10599999409078e-06
DEBUG:oci_cli.cli_util: 2026-10-17 13:55:56.059607+00:00: total memory usage before printing: 73.9KiB (75668)
DEBUG:oci_cli.cli_util: 2026-10-17 13:55:56.059697+00:00: Time elapsed printing response data: <1ms
DEBUG:oci_cli.cli_util: 2026-10-17 13:55:56.059739+00:00: total memory usage after printing: 73.9KiB (75668)
env OCI_TENANCY is set
env OCI_REGION is set
env OCI_CLI_SUPPRESS_FILE_PERMISSIONS_WARNING is set
env OCI_USER is set
env OCI_FINGERPRINT is set
env OCI_PYTHON_SDK_NO_SERVICE_IMPORTS is set
send: b'GET /n HTTP/1.1\r\nuser-agent: Oracle-PythonSDK/2.188.0 (python 3.12.3; x86_64-Linux) Oracle-PythonCLI/3.95.0\r\naccept-encoding: gzip, deflate\r\naccept: application/json\r\nconnection: keep-alive\r\ncontent-type: application/json\r\nopc-client-request-id: C353AFA9DDC147EF887F5529B7F4CC63\r\nopc-client-retries: true\r\nopc-client-info: Oracle-PythonSDK/2.188.0\r\nopc-request-id: 72D05B1B730148D9B8434313A1C08B6F\r\ndate: Sat, 17 Oct 2026 13:55:55 GMT\r\nhost: objectstorage.eu-frankfurt-1.oraclecloud.com\r\nauthorization: Signature algorithm="rsa-sha256",headers="date (request-target) host",keyId="ocid1.tenancy.oc1..aaaaaaaanlzitmrgwn5f3g3iyapyiuxt2ayh43u6mdq3nszvcswrkcw5eyfa/ocid1.user.oc1..aaaaaaaafg2fu7zqt4q7kzdy7fzqbvg6wr5wj2f3yb5e452eas7cu3hbghma/fe:34:11:b7:f9:33:dd:bd:5c:f0:ca:aa:89:9f:f7:cb",signature="0+IQjRtj65E/rNKH+zzHL0gi3dP8xK31bvf/vUU3Go+46uyPXuuEyOB+DU0qoWJU0FBC++3eaf4SYHEQU1n2o6YBnP8C9JryrmYkXBHzUXIrPpxHyNNA3/2L8OxJPj+utC4fUVElPLGqhYECsSXQFQIH8GiRZUhJg60hqBi9fJtFq3lB+JXYFRjwJ8ApxNHyy/a5Ryul7pqVk3QtPZS//V5r6H0vlPFgvknfoAZs1f9vCCmJcl++TXAX//+5J3pxQXeLAvdWx6BJy04opwSAMovUM08UCp/lH/RPtA20HA1GDIvzjs0FDMwe3JSerJe1TLcEWG45YFMb/sEpEhd51g==",version="1"\r\n\r\n'
reply: 'HTTP/1.1 200 OK\r\n'
header: Content-Type: application/json
header: Content-Length: 14
header: opc-client-request-id: C353AFA9DDC147EF887F5529B7F4CC63
header: date: Sat, 17 Oct 2026 13:55:55 GMT
header: opc-request-id: fra-1:-ZUP_GQQUMyoFiGDLWibwyumyTllY3lGV2NKbojjoZcEm_B7AdcvVSuoeG7FBX_k
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
[py headers trims]  {'Date': 'Sat, 17 Oct 2026 13:57:2...', 'Accept': 'application/json...', 'Content-Type': 'application/json...', 'Authorization': 'Signature algorithm="rsa...'}
[py-objectstorage] 401 {"code":"NotAuthenticated","message":"The required information to complete authentication was not provided."}
[sdk-signer] ESUAT: NameError: name 'oci' is not defined
[curl-objectstorage] 401 b'{"code":"NotAuthenticated","message":"The required information to complete authentication was not pr'
[AUTH-TEST compartment] HTTP 404 {
  "code" : "NotAuthorizedOrNotFound",
  "message" : "Authorization failed or requested resource not found."
}
[identity@eu-frankfurt-1] HTTP 401 {"code":"NotAuthenticated","message":"Failed to verify the HTTP(S) Signature"}
[auth] identity raspunde prin eu-frankfurt-1; HOME region: NEDESCIFRAT (vezi HTTP mai sus)
[sdk-call esuat: AttributeError type object 'Signer' has no attribute 'from_config_file'] -> fallback manual
[env-get] 404 {
  "code" : "NotAuthorizedOrNotFound",
  "message" : "Authorization failed or requested resource not found."
}
[sdk-call esuat: AttributeError type object 'Signer' has no attribute 'from_config_file'] -> fallback manual
[env-create] 404 {
  "code" : "NotAuthorizedOrNotFound",
  "message" : "Authorization failed or requested resource not found."
}
[sdk-call esuat: AttributeError type object 'Signer' has no attribute 'from_config_file'] -> fallback manual
[sdk-call esuat: AttributeError type object 'Signer' has no attribute 'from_config_file'] -> fallback manual
[session] 404 {
  "code" : "NotAuthorizedOrNotFound",
  "message" : "Authorization failed or requested resource not found."
}
