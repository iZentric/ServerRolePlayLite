# Scara CUANTIC — candidați hibrid 1.16.5: SHA, smoke 36/14 și A/B

Run: https://github.com/iZentric/ServerRolePlayLite/actions/runs/38270505601

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
    "Mohist 1.16.5-1237 (niciun URL oficial nu a răspuns 200; Maven Central este sursa indicata de Artifice; oglinda proprie a proiectului e fallback)": {
      "url": "",
      "licence_declared": "neverificată",
      "sha256_expected": null,
      "error": "ValueError: fără URL de descărcare → candidat neidentificat, nu e scor"
    },
    "Magma 1.16.5-36.2.39-c1c5a946 (niciun URL oficial nu a răspuns 200; proiectul 1.16.x e marcat arhivat; pagina principala a dat 522 la 12 oct 2026)": {
      "url": "",
      "licence_declared": "neverificată",
      "sha256_expected": null,
      "error": "ValueError: fără URL de descărcare → candidat neidentificat, nu e scor"
    },
    "LoliServer 1.16.5 (fără sursă oficială; repository-ul GitHub Loli-Server/LoliServer a intors 404 (stins); nu luam binare de pe oglinzi neoficiale)": {
      "url": "",
      "licence_declared": "neverificată",
      "sha256_expected": null,
      "error": "ValueError: fără URL de descărcare → candidat neidentificat, nu e scor"
    }
  }
}
```
