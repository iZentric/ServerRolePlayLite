# Scara CUANTIC — candidați hibrid 1.16.5: SHA, smoke 36/14 și A/B

Run: https://github.com/iZentric/ServerRolePlayLite/actions/runs/38269915764

Runner GitHub izolat, Java 17, pack neschimbat (36 moduri + 14 pluginuri). Serverul live nu a fost atins.
Un candidat care nu ajunge la `Done` este INCOMPATIBIL, nu mai lent; fără 3 probe valide pe braț nu există verdict.

```json
{
  "method": "scară CUANTIC: descărcare cu SHA, smoke pe pack identic 36/14, A/B sintetic cu N probe pe braț, pe un runner GitHub izolat",
  "limits": "nu ating serverul live; nu declară compatibilitate cu clientul modat; un motor care nu pornește e INCOMPATIBIL, nu mai lent",
  "baseline_pack": {
    "mods": 36,
    "plugins": 14,
    "pack_sha256": "fe1e261097d92f26c6653239a7161613e6be54b8e9f82c79739c101ce8aa8a15"
  },
  "candidates": {
    "Mohist 1.16.5 (Maven Central negasit din acest runner)": {
      "url": "",
      "licence_declared": "neverificată",
      "sha256_expected": null,
      "error": "ValueError: fără URL de descărcare → candidat neidentificat, nu e scor"
    },
    "LoliServer 1.16.5 (sursa GitHub a dat 404 la verificare; licenta de confirmat)": {
      "url": "",
      "licence_declared": "neverificată",
      "sha256_expected": null,
      "error": "ValueError: fără URL de descărcare → candidat neidentificat, nu e scor"
    },
    "Magma 1.16.5 (GitLab a dat 522; proiect 1.16.x arhivat)": {
      "url": "",
      "licence_declared": "neverificată",
      "sha256_expected": null,
      "error": "ValueError: fără URL de descărcare → candidat neidentificat, nu e scor"
    }
  }
}
```
