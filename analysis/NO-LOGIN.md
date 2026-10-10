# NO-LOGIN — 2026-10-10 10:54:09 UTC

NOLOGIN: deja-scoase  actorii-nu-si-au-aparut port=SUS online=DA

```
redenumite:
AuthMe-5.6.0.jar.disabled-1791629307
AuthMe.disabled-1791629307
FastLoginBukkit.jar.disabled-1791629307
FastLogin.disabled-1791629307
```

## cum bagi logarea inapoi (aceeasi masina, un singur rand)
```
cd $HOME/cuantic-live && for f in plugins/*.disabled-*; do mv "$f" "${f%.disabled-*}"; done; echo restart >> cuantic-live/cmd.in
```
