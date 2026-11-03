# CLOUD-SHELL 2026-10-17 14:09:58 UTC — actiune: keep
key: 1716 bytes | fp: fe:34:11:b7:f9:33:dd:bd:5c:f0:ca:aa:89:9f:f7:cb | region: eu-frankfurt-1
CLI:
{
  "data": "frmtdtikdfkz"
}
DEBUG:oci.base_client.140039913363200: 2026-10-17 14:10:30.377823+00:00: python SDK time elapsed for deserializing: 4.115999999498854e-06
DEBUG:oci.base_client.140039913363200: 2026-10-17 14:10:30.377851+00:00: Response returned
DEBUG:oci.base_client.140039913363200:time elapsed for request: 0.6238774610000064
DEBUG:oci_cli.cli_util: 2026-10-17 14:10:30.377917+00:00: time elapsed calling to_dict from render: 3.356000000565018e-06
DEBUG:oci_cli.cli_util: 2026-10-17 14:10:30.378662+00:00: total memory usage before printing: 74.2KiB (75960)
DEBUG:oci_cli.cli_util: 2026-10-17 14:10:30.378740+00:00: Time elapsed printing response data: <1ms
DEBUG:oci_cli.cli_util: 2026-10-17 14:10:30.378768+00:00: total memory usage after printing: 74.2KiB (75960)
env OCI_TENANCY is set
env OCI_REGION is set
env OCI_CLI_SUPPRESS_FILE_PERMISSIONS_WARNING is set
env OCI_USER is set
env OCI_FINGERPRINT is set
env OCI_PYTHON_SDK_NO_SERVICE_IMPORTS is set
send: b'GET /n HTTP/1.1\r\nuser-agent: Oracle-PythonSDK/2.188.0 (python 3.12.3; x86_64-Linux) Oracle-PythonCLI/3.95.0\r\naccept-encoding: gzip, deflate\r\naccept: application/json\r\nconnection: keep-alive\r\ncontent-type: application/json\r\nopc-client-request-id: 9B9F677D85E44955BAA0AADE3D153254\r\nopc-client-retries: true\r\nopc-client-info: Oracle-PythonSDK/2.188.0\r\nopc-request-id: 65ADDD234C1343C19BE700448826FD7E\r\ndate: Sat, 17 Oct 2026 14:10:29 GMT\r\nhost: objectstorage.eu-frankfurt-1.oraclecloud.com\r\nauthorization: Signature algorithm="rsa-sha256",headers="date (request-target) host",keyId="ocid1.tenancy.oc1..aaaaaaaanlzitmrgwn5f3g3iyapyiuxt2ayh43u6mdq3nszvcswrkcw5eyfa/ocid1.user.oc1..aaaaaaaafg2fu7zqt4q7kzdy7fzqbvg6wr5wj2f3yb5e452eas7cu3hbghma/fe:34:11:b7:f9:33:dd:bd:5c:f0:ca:aa:89:9f:f7:cb",signature="lcD+Z18FY+Jh3YLCzzbuv71ibSf6ivf1hMgohikN9DPgOtDZ7dbv8y4Ox/y0z4wemLuNOLA47k868h6ggFAq1RRyhcb7J8Ov456lfwMgUbgbW2yocpjNSklTryBHXLzfrRgewb16RDUPaFavKM2P+FIewJdV3KjGKr+ZKlmu4u3JqcO28gIL4HvOsOh/Q95SgUm4T15Ia4DVnLuLiFyDHj5n2Gme58fkBCGrZIwQFWqWkgI24Mv6/MPHRmEazXjZsaBHV4htMoU3Sizxj8Cx2qAZw6e3A2fnhbGvmBkvTkJGbKruXuweDGNY64ibhcL2VwyZiXJpUZFKmpa70yRb7g==",version="1"\r\n\r\n'
reply: 'HTTP/1.1 200 OK\r\n'
header: Content-Type: application/json
header: Content-Length: 14
header: opc-client-request-id: 9B9F677D85E44955BAA0AADE3D153254
header: date: Sat, 17 Oct 2026 14:10:30 GMT
header: opc-request-id: fra-1:uxPVyGHbEflzKPWj8Q_PHfRH0U8KsfcfzUHwNxt0N5ZxvggQNzSyBFmNpsfrO-Op
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
[py headers trims]  {'Date': 'Sat, 17 Oct 2026 14:12:0...', 'Accept': 'application/json...', 'Content-Type': 'application/json...', 'Authorization': 'Signature algorithm="rsa...'}
[py-objectstorage] 401 {"code":"NotAuthenticated","message":"The required information to complete authentication was not provided."}
[sdk-signer] ESUAT: NameError: name 'oci' is not defined
[curl-objectstorage] 401 b'{"code":"NotAuthenticated","message":"The required information to complete authentication was not pr'
[AUTH-TEST compartment] HTTP 404 {
  "code" : "NotAuthorizedOrNotFound",
  "message" : "Authorization failed or requested resource not found."
}
[identity@eu-frankfurt-1] HTTP 401 {"code":"NotAuthenticated","message":"Failed to verify the HTTP(S) Signature"}
[auth] identity raspunde prin eu-frankfurt-1; HOME region: NEDESCIFRAT (vezi HTTP mai sus)
[semnaturi Signer]: ['api_key', 'create_signers', 'do_request_sign', 'from_config', 'private_key', 'validate_request', 'without_content_headers']
[oci.auth.signers]: ['EphemeralResourcePrincipalSigner', 'EphemeralResourcePrincipalV21Signer', 'EphemeralResourcePrincipalsDelegationTokenSigner', 'InstancePrincipalsDelegationTokenSigner', 'InstancePrincipalsSecurityTokenSigner', 'KeyPairSigner', 'NestedResourcePrincipals', 'OauthExchangeTokenSigner', 'OkeWorkloadIdentityResourcePrincipalSigner', 'PKCS11RequestSigner', 'PKCS11Signer', 'ResourcePrincipalsDelegationTokenSigner', 'ResourcePrincipalsFederationSigner', 'SecurityTokenSigner', 'TokenExchangeSigner', 'X509FederationClientBasedSecurityTokenSigner', 'ephemeral_resource_principals_delegation_token_signer', 'ephemeral_resource_principals_signer', 'ephemeral_resource_principals_v21_signer', 'get_oke_workload_identity_resource_principal_signer', 'get_resource_principal_delegation_token_signer', 'get_resource_principals_signer', 'instance_principals_delegation_token_signer', 'instance_principals_security_token_signer', 'key_pair_signer', 'nested_resource_principals_signer', 'oauth_exhange_token_signer', 'oke_workload_identity_resource_principal_signer', 'pkcs11_signer', 'resource_principals_delegation_token_signer', 'resource_principals_federation_signer', 'resource_principals_signer', 'security_token_signer', 'token_exchange_signer']
Traceback (most recent call last):
  File "/home/runner/work/ServerRolePlayLite/ServerRolePlayLite/scripts/oci-cloudshell.py", line 211, in <module>
    main()
  File "/home/runner/work/ServerRolePlayLite/ServerRolePlayLite/scripts/oci-cloudshell.py", line 182, in main
    st, body = call("GET", c, "/20150802/cloudShell")
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/ServerRolePlayLite/ServerRolePlayLite/scripts/oci-cloudshell.py", line 48, in call
    q.headers = hm
    ^
UnboundLocalError: cannot access local variable 'q' where it is not associated with a value
