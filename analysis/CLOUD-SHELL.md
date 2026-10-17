# CLOUD-SHELL 2026-10-17 13:29:52 UTC — actiune: keep
key: 1716 bytes | fp: fe:34:11:b7:f9:33:dd:bd:5c:f0:ca:aa:89:9f:f7:cb | region: eu-frankfurt-1
CLI:
{
  "data": "frmtdtikdfkz"
}
DEBUG:oci.base_client.140351457027488: 2026-10-17 13:30:34.173306+00:00: python SDK time elapsed for deserializing: 6.2910000053761905e-06
DEBUG:oci.base_client.140351457027488: 2026-10-17 13:30:34.173370+00:00: Response returned
DEBUG:oci.base_client.140351457027488:time elapsed for request: 0.43026159099999006
DEBUG:oci_cli.cli_util: 2026-10-17 13:30:34.173478+00:00: time elapsed calling to_dict from render: 3.836999994177859e-06
DEBUG:oci_cli.cli_util: 2026-10-17 13:30:34.178461+00:00: total memory usage before printing: 73.9KiB (75636)
DEBUG:oci_cli.cli_util: 2026-10-17 13:30:34.178578+00:00: Time elapsed printing response data: <1ms
DEBUG:oci_cli.cli_util: 2026-10-17 13:30:34.178632+00:00: total memory usage after printing: 73.9KiB (75636)
env OCI_TENANCY is set
env OCI_REGION is set
env OCI_CLI_SUPPRESS_FILE_PERMISSIONS_WARNING is set
env OCI_USER is set
env OCI_FINGERPRINT is set
env OCI_PYTHON_SDK_NO_SERVICE_IMPORTS is set
send: b'GET /n HTTP/1.1\r\nuser-agent: Oracle-PythonSDK/2.188.0 (python 3.12.3; x86_64-Linux) Oracle-PythonCLI/3.95.0\r\naccept-encoding: gzip, deflate\r\naccept: application/json\r\nconnection: keep-alive\r\ncontent-type: application/json\r\nopc-client-request-id: 55EC3731F14A452C88C0EA13AB497112\r\nopc-client-retries: true\r\nopc-client-info: Oracle-PythonSDK/2.188.0\r\nopc-request-id: 97B59DA34A1C41D3AA9005B759B0A2DD\r\ndate: Sat, 17 Oct 2026 13:30:33 GMT\r\nhost: objectstorage.eu-frankfurt-1.oraclecloud.com\r\nauthorization: Signature algorithm="rsa-sha256",headers="date (request-target) host",keyId="ocid1.tenancy.oc1..aaaaaaaanlzitmrgwn5f3g3iyapyiuxt2ayh43u6mdq3nszvcswrkcw5eyfa/ocid1.user.oc1..aaaaaaaafg2fu7zqt4q7kzdy7fzqbvg6wr5wj2f3yb5e452eas7cu3hbghma/fe:34:11:b7:f9:33:dd:bd:5c:f0:ca:aa:89:9f:f7:cb",signature="uZMHYe/WbjiCfZZQXt3Tl45rMGiztGN2CUeZf7rq7FASPr0ba2AzyplqrYNOX2fMlCT/HiW4tWeToScoTr3cXfKgaCBiL2XU4S1XFC+UBCoXTn1NYC1Zt1adDUwb27vDiLBfr6TbiYaGNPdZ2JVrLoipksRoYa6fboEbt20hY4CbzU2l2GRFjkS6GxkQvj0gn+QgZCfs4LeJ9dqzrAK0s7Rvb4Nmmg0Ce/vWTkFXDtYAwJzlFv6C9O83OVof3WK0oAjbz694aSNjr9PkCh4NJJ0dN+SXVLg8QToyZj+UM814Itbnwr2cHbXv1Cg3ZK/M/zO5DVQBiN23/dkI0TCCnQ==",version="1"\r\n\r\n'
reply: 'HTTP/1.1 200 OK\r\n'
header: Content-Type: application/json
header: Content-Length: 14
header: opc-client-request-id: 55EC3731F14A452C88C0EA13AB497112
header: date: Sat, 17 Oct 2026 13:30:34 GMT
header: opc-request-id: fra-1:cadMq-drpkkKgziNvTgTyDZ9qxwNX7UwXYtjPCv_eh3uwVQY0FQN362NMG3MQaqJ
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
