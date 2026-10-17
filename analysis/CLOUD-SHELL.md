# CLOUD-SHELL 2026-10-17 13:04:31 UTC — actiune: keep
key: 1716 bytes | fp: f3:28:70:dc:e8:a1:26:de:78:13:69:60:b5:9f:f2:4d:5b:e5:53:41 | region: eu-frankfurt-1
--- config exact ---
[DEFAULT]$
user=ocid1.user.oc1..aaaaaaaafg2fu7zqt4q7kzdy7fzqbvg6wr5wj2f3yb5e452eas7cu3hbghma$
$
tenancy=ocid1.tenancy.oc1..aaaaaaaanlzitmrgwn5f3g3iyapyiuxt2ayh43u6mdq3nszvcswrkcw5eyfa$
$
region=eu-frankfurt-1$
fingerprint=f3:28:70:dc:e8:a1:26:de:78:13:69:60:b5:9f:f2:4d:5b:e5:53:41$
key_file=/home/runner/.oci/oci_api_key.pem$
--- CLI auth test (os ns get, debug) ---
DEBUG:oci_cli.cli_metrics: 2026-10-17 13:04:58.812126+00:00: Metrics is not enabled
Linux-6.17.0-1022-azure-x86_64-with-glibc2.39
System name: Linux
System release : 6.17.0-1022-azure
System version: #22-Ubuntu SMP Mon Jul 27 17:24:03 UTC 2026

DEBUG:oci_cli.cli_util:Config File: dict_keys(['log_requests', 'additional_user_agent', 'pass_phrase', 'user', 'tenancy', 'region', 'fingerprint', 'key_file'])
DEBUG:oci_cli.cli_util:region: Environment Variable or Parameter
env OCI_TENANCY is set
env OCI_REGION is set
env OCI_CLI_SUPPRESS_FILE_PERMISSIONS_WARNING is set
env OCI_USER is set
env OCI_FINGERPRINT is set
env OCI_PYTHON_SDK_NO_SERVICE_IMPORTS is set
ERROR: The config file at /home/runner/.oci/config is invalid:

+Config Errors+-----------+----------------------------------------------------------------------------------+
| Key         | Error     | Hint                                                                             |
+-------------+-----------+----------------------------------------------------------------------------------+
+-------------+-----------+----------------------------------------------------------------------------------+
--- python keepalive ---
[SDK] FAIL: InvalidConfig: {'fingerprint': 'malformed'}
[identity@eu-frankfurt-1] HTTP 401 {
  "code" : "NotAuthenticated",
  "message" : "The required information to complete authentication was not provided or 
[identity@us-ashburn-1] HTTP 401 {
  "code" : "NotAuthenticated",
  "message" : "The required information to complete authentication was not provided or 
[identity@eu-frankfurt-1] HTTP 401 {
  "code" : "NotAuthenticated",
  "message" : "The required information to complete authentication was not provided or 
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
