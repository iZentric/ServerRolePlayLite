# NO-LOGIN — 2026-10-10 13:25:44 UTC

NOLOGIN: -AuthMe -AuthMe-5.6.0.jar -FastLogin -FastLoginBukkit.jar  actorii-nu-si-au-aparut port=SUS online=NU

```
[13:23:49] [Craft Scheduler Thread - 4/WARN]: [AuthMe] No MaxMind credentials found in the configuration file! GeoIp protections will be disabled.
[13:23:49] [Craft Scheduler Thread - 4/INFO]: [AuthMe] There is no newer GEO IP database uploaded to MaxMind. Using the old one for now.
[13:23:49] [Craft Scheduler Thread - 4/WARN]: [AuthMe] Could not download GeoLiteAPI database [FileNotFoundException]: plugins/AuthMe/GeoLite2-Country.mmdb (No such file or directory)
[13:23:50] [Server thread/INFO]: [FastLogin] Hooking into auth plugin: AuthMeHook
redenumite:
AuthMe-5.6.0.jar.disabled-1791638665
AuthMe.disabled-1791638665
FastLoginBukkit.jar.disabled-1791638665
FastLogin.disabled-1791638665
```

## cum bagi logarea inapoi (aceeasi masina, un singur rand)
```
cd $HOME/cuantic-live && for f in plugins/*.disabled-*; do mv "$f" "${f%.disabled-*}"; done; echo restart >> cuantic-live/cmd.in
```
