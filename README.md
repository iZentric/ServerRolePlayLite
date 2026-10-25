# FunCity

**FunCity** este proiectul unei comunități Minecraft Java roleplay: un oraș viu, roluri civile, afaceri, facțiuni/mafii și survival opțional. Pachetul actual de server este Paper-only, cu pluginuri server-side și client Java nemodat — fără moduri, Forge sau motor hibrid.

## Comunitatea

- [Pagina de prezentare FunCity](community/index.html)
- [Planul de pornire a comunității și structura Discord propusă](docs/COMMUNITY-START.md)
- [Ghid de intrare pe server](docs/CUM-INTRI-PE-SERVER.md) — verifică anunțurile oficiale înainte de a folosi versiuni sau adrese din documentele istorice

**Nu există un link Discord sau o adresă de conectare confirmată în această pagină.** Le publicăm aici numai după ce proprietarul le verifică și aprobă.

## Direcția tehnică

- **Pachetul nou de server Java este Paper-only**: fără Forge, Arclight, Mohist, CatServer, moduri sau motoare hibride. Ghidul de instalare și deciziile de compatibilitate sunt în [paper_server/README.md](paper_server/README.md).
- Configurațiile și experimentele hibride mai vechi rămân în repository ca istoric; nu sunt parte din pachetul Paper și nu trebuie amestecate cu runtime-ul lui.
- Selecție strategică a fiecărui plugin și dependență: scop, suprapuneri, costuri măsurate sau nemăsurate, compatibilitate și motiv de includere.
- Testare pe copii și backup verificat înaintea schimbărilor la date persistente.
- Fără lobby/Velocity; fără promisiuni de „zero lag”, capacitate sau compatibilitate universală fără dovezi.

## Starea livrării

Codul și documentele din repository descriu mai multe etape și experimente. Un artefact cu numele FunCity nu este automat un release validat. Înainte de distribuirea unui build trebuie publicate versiunea exactă, sursa/upstream-ul, patchurile incluse, SHA-256, compatibilitatea clientului și verificările efectuate.

Pachetele și rapoartele mai vechi pot folosi numele **CUANTIC**. Ele sunt păstrate ca istoric/proveniență și nu trebuie tratate automat drept pachetul oficial FunCity curent.

## Dezvoltare

Testele Python ale proiectului pot fi rulate local astfel:

```sh
python3 -m unittest discover -s tests
```

Nu porni workflow-uri `self-hosted` pentru a testa un commit fără să verifici întâi ce comandă execută pe host. Runnerul personal poate executa cod direct pe PC-ul pe care este instalat.

## Licențe și atribuire

Motoarele, modurile și pluginurile upstream își păstrează licențele și atribuirea. Orice fork sau patch FunCity trebuie să indice baza, commitul și modificările proprii fără a prezenta codul upstream drept creație originală.
