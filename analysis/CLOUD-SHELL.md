# CLOUD-SHELL 2026-10-17 12:40:41 UTC — actiune: keep
key: 1716 bytes | fp: f3:28:70:dc:e8:a1:26:de:78:13:69:60:b5:9f:f2:4d:5b:e5:53:41 | region: eu-frankfurt-1
--- CLI auth test (os ns get) ---
WARNING: Permissions on /home/runner/.oci/config are too open. 
To fix this please try executing the following command: 
oci setup repair-file-permissions --file /home/runner/.oci/config 
Alternatively to hide this warning, you may set the environment variable, OCI_CLI_SUPPRESS_FILE_PERMISSIONS_WARNING: 
export OCI_CLI_SUPPRESS_FILE_PERMISSIONS_WARNING=True

ERROR: The config file at /home/runner/.oci/config is invalid:

--- CLI raw identity ---
WARNING: Permissions on /home/runner/.oci/config are too open. 
To fix this please try executing the following command: 
oci setup repair-file-permissions --file /home/runner/.oci/config 
Alternatively to hide this warning, you may set the environment variable, OCI_CLI_SUPPRESS_FILE_PERMISSIONS_WARNING: 
export OCI_CLI_SUPPRESS_FILE_PERMISSIONS_WARNING=True

--- python keepalive ---
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
