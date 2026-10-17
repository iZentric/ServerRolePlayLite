# CLOUD-SHELL 2026-10-17 13:59:02 UTC — actiune: keep
key: 1716 bytes | fp: fe:34:11:b7:f9:33:dd:bd:5c:f0:ca:aa:89:9f:f7:cb | region: eu-frankfurt-1
CLI:
{
  "data": "frmtdtikdfkz"
}
DEBUG:oci.base_client.140187784969584: 2026-10-17 13:59:28.315627+00:00: python SDK time elapsed for deserializing: 3.466000009666459e-06
DEBUG:oci.base_client.140187784969584: 2026-10-17 13:59:28.315647+00:00: Response returned
DEBUG:oci.base_client.140187784969584:time elapsed for request: 0.6265994830000068
DEBUG:oci_cli.cli_util: 2026-10-17 13:59:28.315688+00:00: time elapsed calling to_dict from render: 1.5820000101030018e-06
DEBUG:oci_cli.cli_util: 2026-10-17 13:59:28.320008+00:00: total memory usage before printing: 74.2KiB (75964)
DEBUG:oci_cli.cli_util: 2026-10-17 13:59:28.320076+00:00: Time elapsed printing response data: <1ms
DEBUG:oci_cli.cli_util: 2026-10-17 13:59:28.320098+00:00: total memory usage after printing: 74.2KiB (75964)
env OCI_TENANCY is set
env OCI_REGION is set
env OCI_CLI_SUPPRESS_FILE_PERMISSIONS_WARNING is set
env OCI_USER is set
env OCI_FINGERPRINT is set
env OCI_PYTHON_SDK_NO_SERVICE_IMPORTS is set
send: b'GET /n HTTP/1.1\r\nuser-agent: Oracle-PythonSDK/2.188.0 (python 3.12.3; x86_64-Linux) Oracle-PythonCLI/3.95.0\r\naccept-encoding: gzip, deflate\r\naccept: application/json\r\nconnection: keep-alive\r\ncontent-type: application/json\r\nopc-client-request-id: 7EDE8CDADC7E42B7890D13ADE91B8512\r\nopc-client-retries: true\r\nopc-client-info: Oracle-PythonSDK/2.188.0\r\nopc-request-id: 493315D86D2D4C88B78C09795A361F6E\r\ndate: Sat, 17 Oct 2026 13:59:27 GMT\r\nhost: objectstorage.eu-frankfurt-1.oraclecloud.com\r\nauthorization: Signature algorithm="rsa-sha256",headers="date (request-target) host",keyId="ocid1.tenancy.oc1..aaaaaaaanlzitmrgwn5f3g3iyapyiuxt2ayh43u6mdq3nszvcswrkcw5eyfa/ocid1.user.oc1..aaaaaaaafg2fu7zqt4q7kzdy7fzqbvg6wr5wj2f3yb5e452eas7cu3hbghma/fe:34:11:b7:f9:33:dd:bd:5c:f0:ca:aa:89:9f:f7:cb",signature="T4/AE4J32tiCjKxVPFFHfEoSklTWt+8V7pBzhDncqgnjc5F+344owA3pHqWo2kpktdyEjQw+QfqK8lyXY+Tqep2F+MJPG2dZ8fIiLuo/LUv/hlboezUfpUHj1NgzOUPNp1+8IQKUGVctL69Q3o6ObUEy5fSqKCLhtaEHvbn+h5wJdQfG56aJh8AGRanrrPC/vQaaq0A46nq+dYjo5pRbk1UREo0ToSYClEIxfbR56ntoFbNYsF8CQ+jY1eVAXDxEwpO/4iogxf+pT11ZYx4+teKmiwqePAKye9sjeJg+XxCWqa/OAS0UnDoqfpZl5dUjKX/cX9BpbNBhsoAolHLKJg==",version="1"\r\n\r\n'
reply: 'HTTP/1.1 200 OK\r\n'
header: Content-Type: application/json
header: Content-Length: 14
header: opc-client-request-id: 7EDE8CDADC7E42B7890D13ADE91B8512
header: date: Sat, 17 Oct 2026 13:59:28 GMT
header: opc-request-id: fra-1:JxYPsJaIGmvkXj1qxLEa0v-VJsPLeJQbAYx5P_7ggRNG8qosfprJARPliULu6Emt
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
[py headers trims]  {'Date': 'Sat, 17 Oct 2026 14:01:0...', 'Accept': 'application/json...', 'Content-Type': 'application/json...', 'Authorization': 'Signature algorithm="rsa...'}
[py-objectstorage] 401 {"code":"NotAuthenticated","message":"The required information to complete authentication was not provided."}
[sdk-signer] ESUAT: NameError: name 'oci' is not defined
[curl-objectstorage] 401 b'{"code":"NotAuthenticated","message":"The required information to complete authentication was not pr'
[AUTH-TEST compartment] HTTP 404 {
  "code" : "NotAuthorizedOrNotFound",
  "message" : "Authorization failed or requested resource not found."
}
[identity@eu-frankfurt-1] HTTP 401 {"code":"NotAuthenticated","message":"Failed to verify the HTTP(S) Signature"}
[auth] identity raspunde prin eu-frankfurt-1; HOME region: NEDESCIFRAT (vezi HTTP mai sus)
Traceback (most recent call last):
  File "/home/runner/work/ServerRolePlayLite/ServerRolePlayLite/scripts/oci-cloudshell.py", line 192, in <module>
    main()
  File "/home/runner/work/ServerRolePlayLite/ServerRolePlayLite/scripts/oci-cloudshell.py", line 163, in main
    st, body = call("GET", c, "/20150802/cloudShell")
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/ServerRolePlayLite/ServerRolePlayLite/scripts/oci-cloudshell.py", line 35, in call
    signer = getattr(tmp, "_client", tmp).__dict__.get("_signer") or tmp._client._signer
                                                                     ^^^^^^^^^^^
AttributeError: 'ObjectStorageClient' object has no attribute '_client'
