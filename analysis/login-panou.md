# LOGIN PANOU 2 (Thu Oct  8 18:06:08 UTC 2026)

## cerere cod email

## strings gasite in JS: power/restart/console/captcha/sitekey

## toate caile /api/ din toate chunk-urile

## logul complet al usilor
== 1) CERERE COD PE EMAIL (fara captcha?) ==
400 POST https://dash.zampto.net/api/auth/login/email-code/request -> {"error":"Security verification failed. Please complete the captcha."}
400 POST https://dash.zampto.net/api/auth/login/email-code/request -> {"error":"Security verification failed. Please complete the captcha."}
== 2) OAUTH — unde duce GitHub ==
github oauth redirect: https://github.com/login/oauth/authorize?client_id=Ov23lisnGDjw8au9CLRp&redirect_uri=https%3A%2F%2Fdash.zampto.net%2Fapi%2Fauth%2Foauth%2Fgithub%2Fcallback&state=fd77362d7b20f59387d733c02a3c4ecd059540f709edc090364b45ce9a063ddd&scope=read%3Auser+user%3Aemail
google oauth redirect: https://accounts.google.com/o/oauth2/v2/auth?client_id=343974233269-miil5n4ojcik1ifffs7t4kqctkkdb8j1.apps.googleusercontent.com&redirect_uri=https%3A%2F%2Fdash.zampto.net%2Fapi%2Fauth%2Foauth%2Fgoogle%2Fcallback&response_type=code&scope=openid+email+profile&state=4012bd82c9ccb4db5cb5de6c4b57bdb56a348f55965845cba4e56379e1cb84ef&prompt=select_account
== 3) api.zampto.net login propriu ==
404 POST https://api.zampto.net/auth/login -> {"success":false,"message":"Endpoint not found"}
404 POST https://api.zampto.net/login -> {"success":false,"message":"Endpoint not found"}
404 POST https://api.zampto.net/api/auth/login -> {"success":false,"message":"Endpoint not found"}
== 4) SCANARE PROFUNDA: toate chunk-urile JS ==
16 /tmp/pl/all-chunks.txt
