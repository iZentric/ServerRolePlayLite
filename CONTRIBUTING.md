# Contribuie la FunCity RP Lite

Mulțumim că vrei să ajuți. Proiectul este public **în dezvoltare**; niciun release Lite sau server public verificat nu este anunțat.

## Înainte de orice schimbare

1. Citește [README](README.md), [stadiul real](agent/PROGRES.md) și [condițiile de publicare](agent/PUBLICARE.md). Documentele vechi pot descrie experimente, nu decizia actuală.
2. Deschide un [issue](https://github.com/iZentric/ServerRolePlayLite/issues) pentru un bug sau o propunere mică, cu versiunea, pașii de reproducere și rezultatul așteptat. **Nu posta loguri brute, adrese de server, nume de lumi/jucători, capturi cu date de cont sau secrete.** Redactează înainte să publici.
3. Pentru cod, trimite un PR scurt cu motivul schimbării, testele executate și limitele testului. Respectă Minecraft 1.16.5/Forge și nu înlocui motorul hibrid cu un altul din presupunere.

## Reguli pentru artefacte

- Nu include JAR-uri, arhive de lumi, baze de date, fișiere de cont sau configurații live într-un PR. Un fișier prezent într-o arhivă veche **nu dovedește** permisiunea de a-l redistribui.
- Menționează sursa, autorul, licența, versiunea și SHA256 dacă propui un mod/plugin. Nu pretinde că este optimizarea „cea mai bună” fără A/B reprezentativ.
- Nu afirma FPS, MSPT, capacitate, autentificare sau compatibilitate în joc doar pe baza unui boot de laborator.
- Nu modifica serverul live, lumea sau profilurile Prism ale altora ca parte a unei contribuții. Testează în copie izolată, cu rollback planificat.

## Verificări de bază

```bash
PYTHONPATH=scripts PYTHONDONTWRITEBYTECODE=1 python3 scripts/fc_modded_candidate_test.py
PYTHONPATH=scripts PYTHONDONTWRITEBYTECODE=1 python3 scripts/fc_pc_lowspec_full_content_test.py
python3 site/build_site.py
```

Testele de mai sus verifică selecția și regulile de siguranță pe fișiere sintetice; **nu** pornesc Minecraft și nu certifică un release. Pentru distribuirea publică trebuie trecută separat [poarta de lansare](agent/PUBLICARE.md).
