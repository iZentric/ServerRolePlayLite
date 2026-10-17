# CLOUD-SHELL 2026-10-17 14:01:51 UTC — actiune: keep
key: 1716 bytes | fp: fe:34:11:b7:f9:33:dd:bd:5c:f0:ca:aa:89:9f:f7:cb | region: eu-frankfurt-1
CLI:
{
  "data": "frmtdtikdfkz"
}
DEBUG:oci.base_client.139869050518416: 2026-10-17 14:02:30.930705+00:00: python SDK time elapsed for deserializing: 4.990000007865092e-06
DEBUG:oci.base_client.139869050518416: 2026-10-17 14:02:30.930746+00:00: Response returned
DEBUG:oci.base_client.139869050518416:time elapsed for request: 0.69471981800001
DEBUG:oci_cli.cli_util: 2026-10-17 14:02:30.930834+00:00: time elapsed calling to_dict from render: 3.3459999997376144e-06
DEBUG:oci_cli.cli_util: 2026-10-17 14:02:30.931906+00:00: total memory usage before printing: 73.9KiB (75688)
DEBUG:oci_cli.cli_util: 2026-10-17 14:02:30.931996+00:00: Time elapsed printing response data: <1ms
DEBUG:oci_cli.cli_util: 2026-10-17 14:02:30.932038+00:00: total memory usage after printing: 73.9KiB (75688)
env OCI_TENANCY is set
env OCI_REGION is set
env OCI_CLI_SUPPRESS_FILE_PERMISSIONS_WARNING is set
env OCI_USER is set
env OCI_FINGERPRINT is set
env OCI_PYTHON_SDK_NO_SERVICE_IMPORTS is set
send: b'GET /n HTTP/1.1\r\nuser-agent: Oracle-PythonSDK/2.188.0 (python 3.12.3; x86_64-Linux) Oracle-PythonCLI/3.95.0\r\naccept-encoding: gzip, deflate\r\naccept: application/json\r\nconnection: keep-alive\r\ncontent-type: application/json\r\nopc-client-request-id: 935DB698A3B34EFFB2008AC2CDD477EC\r\nopc-client-retries: true\r\nopc-client-info: Oracle-PythonSDK/2.188.0\r\nopc-request-id: 4C4B769976164D8FA0C26EA10B2DC8CB\r\ndate: Sat, 17 Oct 2026 14:02:30 GMT\r\nhost: objectstorage.eu-frankfurt-1.oraclecloud.com\r\nauthorization: Signature algorithm="rsa-sha256",headers="date (request-target) host",keyId="ocid1.tenancy.oc1..aaaaaaaanlzitmrgwn5f3g3iyapyiuxt2ayh43u6mdq3nszvcswrkcw5eyfa/ocid1.user.oc1..aaaaaaaafg2fu7zqt4q7kzdy7fzqbvg6wr5wj2f3yb5e452eas7cu3hbghma/fe:34:11:b7:f9:33:dd:bd:5c:f0:ca:aa:89:9f:f7:cb",signature="YU67hbrAG/L0/ygfv9z03iAVUVETZcr58L7UJtKHRNG4i874I2pOnROHJZ+wLn9IXtXglapj0gdMwGUua4W2dStPIAzVAZ9oLNlF8332C+GSeFC4HGY5szbfRjQ6DQqqizLEbfKAxU4b2wdntTfzbzxiyJUX5Clmz4vdByXSwSfhy7R+Y04d61MdHLVBTcjAp16hahCiX8/TI1qiqOpPG2Zu2XFl/nvIwyfxTVEgF5jWBVEm2mc7ttLDIpinAaGDmCI5PLxrm/YZJ7DtKKs8Ym1XFRvDAshibp1d2FkDY6R8qkSmrSPAJjV9xaOBXO9oJxINYob/fzK1bpjYjo1sWg==",version="1"\r\n\r\n'
reply: 'HTTP/1.1 200 OK\r\n'
header: Content-Type: application/json
header: Content-Length: 14
header: opc-client-request-id: 935DB698A3B34EFFB2008AC2CDD477EC
header: date: Sat, 17 Oct 2026 14:02:30 GMT
header: opc-request-id: fra-1:KcqxhViCd8ZXi5v5lofrvnVtq3giRisPLWtmkI_b9y46EPMrza6OyjIfa_wo2tjN
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
[py headers trims]  {'Date': 'Sat, 17 Oct 2026 14:04:0...', 'Accept': 'application/json...', 'Content-Type': 'application/json...', 'Authorization': 'Signature algorithm="rsa...'}
[py-objectstorage] 401 {"code":"NotAuthenticated","message":"The required information to complete authentication was not provided."}
[sdk-signer] ESUAT: NameError: name 'oci' is not defined
[curl-objectstorage] 401 b'{"code":"NotAuthenticated","message":"The required information to complete authentication was not pr'
[AUTH-TEST compartment] HTTP 404 {
  "code" : "NotAuthorizedOrNotFound",
  "message" : "Authorization failed or requested resource not found."
}
[identity@eu-frankfurt-1] HTTP 401 {"code":"NotAuthenticated","message":"Failed to verify the HTTP(S) Signature"}
[auth] identity raspunde prin eu-frankfurt-1; HOME region: NEDESCIFRAT (vezi HTTP mai sus)
[cloudshell.eu-frankfurt-1.oci.oraclecloud.com] ERR AttributeError 'Signer' object has no attribute 'sign'
[cloudshell.eu-frankfurt-1.oraclecloud.com] ERR AttributeError 'Signer' object has no attribute 'sign'
[api.eu-frankfurt-1.cloudshell.oci.oraclecloud.com] ERR AttributeError 'Signer' object has no attribute 'sign'
[env-get] 0 'Signer' object has no attribute 'sign'
[cloudshell.eu-frankfurt-1.oci.oraclecloud.com] ERR AttributeError 'Signer' object has no attribute 'sign'
[cloudshell.eu-frankfurt-1.oraclecloud.com] ERR AttributeError 'Signer' object has no attribute 'sign'
[api.eu-frankfurt-1.cloudshell.oci.oraclecloud.com] ERR AttributeError 'Signer' object has no attribute 'sign'
[session] 0 'Signer' object has no attribute 'sign'
