# CLOUD-SHELL 2026-10-17 13:46:35 UTC — actiune: keep
key: 1716 bytes | fp: fe:34:11:b7:f9:33:dd:bd:5c:f0:ca:aa:89:9f:f7:cb | region: eu-frankfurt-1
CLI:
{
  "data": "frmtdtikdfkz"
}
DEBUG:oci.base_client.140455235207136: 2026-10-17 13:47:17.859602+00:00: python SDK time elapsed for deserializing: 6.251000002066576e-06
DEBUG:oci.base_client.140455235207136: 2026-10-17 13:47:17.859652+00:00: Response returned
DEBUG:oci.base_client.140455235207136:time elapsed for request: 0.42732157700001494
DEBUG:oci_cli.cli_util: 2026-10-17 13:47:17.859751+00:00: time elapsed calling to_dict from render: 4.449000016393256e-06
DEBUG:oci_cli.cli_util: 2026-10-17 13:47:17.867412+00:00: total memory usage before printing: 73.9KiB (75716)
DEBUG:oci_cli.cli_util: 2026-10-17 13:47:17.867541+00:00: Time elapsed printing response data: <1ms
DEBUG:oci_cli.cli_util: 2026-10-17 13:47:17.867594+00:00: total memory usage after printing: 73.9KiB (75716)
env OCI_TENANCY is set
env OCI_REGION is set
env OCI_CLI_SUPPRESS_FILE_PERMISSIONS_WARNING is set
env OCI_USER is set
env OCI_FINGERPRINT is set
env OCI_PYTHON_SDK_NO_SERVICE_IMPORTS is set
send: b'GET /n HTTP/1.1\r\nuser-agent: Oracle-PythonSDK/2.188.0 (python 3.12.3; x86_64-Linux) Oracle-PythonCLI/3.95.0\r\naccept-encoding: gzip, deflate\r\naccept: application/json\r\nconnection: keep-alive\r\ncontent-type: application/json\r\nopc-client-request-id: DABFCF336BC24DB0A6C1D48CFA56FAAA\r\nopc-client-retries: true\r\nopc-client-info: Oracle-PythonSDK/2.188.0\r\nopc-request-id: CD2389B12D8142DC8C83849E88826C1B\r\ndate: Sat, 17 Oct 2026 13:47:17 GMT\r\nhost: objectstorage.eu-frankfurt-1.oraclecloud.com\r\nauthorization: Signature algorithm="rsa-sha256",headers="date (request-target) host",keyId="ocid1.tenancy.oc1..aaaaaaaanlzitmrgwn5f3g3iyapyiuxt2ayh43u6mdq3nszvcswrkcw5eyfa/ocid1.user.oc1..aaaaaaaafg2fu7zqt4q7kzdy7fzqbvg6wr5wj2f3yb5e452eas7cu3hbghma/fe:34:11:b7:f9:33:dd:bd:5c:f0:ca:aa:89:9f:f7:cb",signature="C6yDpRP6QBwCa/zjxLouYZCEnunkeXukncKQbxGpNHmXiFV+G4ZY39/u9fu+uII9+lfF5r1OeJuJlNbKWS8Fq/4kAxc/PurMCCWEyTqcG8+WNRE2Xj6RYzBKu9zicwumnYV6CQ/qHUqUVRmOuH8O4rqlSTslcAyuFZLH3XV8SkSntk5NXAeJVcgb18ODWIsmK9PblZ9DKRHJ+dXZS1MfGoSQTbynDA039RzV9lre9CbP3S9mXmGSyvdjs7zLkAj6+V9wzoI7FnfuUdEZa11pChu2u/J9DbXgx37cxiRjpeRL2lzb9M7go6Cn0FCPIOIEVWFed5ivHglOoNLE0FVGkw==",version="1"\r\n\r\n'
reply: 'HTTP/1.1 200 OK\r\n'
header: Content-Type: application/json
header: Content-Length: 14
header: opc-client-request-id: DABFCF336BC24DB0A6C1D48CFA56FAAA
header: date: Sat, 17 Oct 2026 13:47:17 GMT
header: opc-request-id: fra-1:5gbUtrCdi3jSDoovYn5I6A89gzAfcQs5NOoY18e8uObR1VjnZd3SAUW_S6HMDu9s
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
  File "/home/runner/work/ServerRolePlayLite/ServerRolePlayLite/scripts/oci-cloudshell.py", line 56
    def home_regiondef home_region(c):
                       ^^^^^^^^^^^
SyntaxError: expected '('
