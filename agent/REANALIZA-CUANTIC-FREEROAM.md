# FunCity RP Lite — reevaluare de la CUANTIC la Freeroam (20.10.2026)

**Cerința actuală a proprietarului:** păstrează toate modurile originalului **cu excepția celor șase autorizate explicit**, iar profilul Prism ales pentru instalarea viitoare este `Freeroam 1.0.0` însuși. Această alegere înlocuiește interdicția anterioară de a modifica originalul **doar pentru etapa finală, reversibilă, după verificări**. Nu autorizează ștergerea altor fișiere, editarea lumilor, conturilor, arhivei sau serverului live. Nu există instalare executată.

## Ce învățăm din etapele vechi

| Etapă | Dovada utilă | Ce nu dovedește |
|---|---|---|
| [Arhiva CUANTIC](https://github.com/iZentric/ServerRolePlayLite/blob/b1ec20c/docs/ENGINE-PACK-AUDIT.md) | Inventarul istoric: 36 moduri server și 14 pluginuri, distinct de un client. | Nu este packul client Freeroam și nici configurația live. Nu copiem serverul peste client. |
| [Captura FunCity → LowSpec](CONTROL-MODURI-ORIGINALE.md) | FunCity client istoric 25 nume; LowSpec 21 JAR-uri la ultima probă PC. Șase JAR-uri RP/dependențe restaurate și laborator server 15/6 și 18/6 pornite. | Nu este comparație cu Freeroam și nu dovedește login Forge, voce, funcții RP sau FPS. |
| [Motoare și A/B](MOTOR-TABEL-VERIFICAT.md) | FunCity, două CatServer și Arclight au pornit în stage 15/6; Mist nu. CatServer a folosit mai puțin CPU în proba sintetică de 30 s, RSS suprapus. | Nu a fost testat cu această selecție Freeroam, client conectat, jucători ori MSPT. Nu alegem motorul live pe această bază. |
| [Freeroam declarat](FREEROAM-LISTA-DECLARATA.json) | Proprietarul a furnizat 28 nume. [Se cer exact șase excluderi](FUNCITY-RP-LITE-SELECTIE.json): CTM, DynamicSurroundings, InGameAccountSwitcher, Lightfall Client, Not Enough Animations și biblioteca obligatorie TRansliterationLib. **22 de nume** rămân din listă. | Nu avem inventarul și SHA real din profil. [Jobul de citire PC](https://github.com/iZentric/ServerRolePlayLite/actions/runs/39439372232) a fost anulat înaintea pașilor Windows; sandboxul nu montează profilul. Dacă pe PC există alte JAR-uri, nu le ștergem în orb. |

## Alegerea responsabilă acum

- **Client 1.16.5/Forge:** selecția declarată de 22, fără JAR-uri noi. Păstrăm conținutul RP, vocea, bibliotecile modurilor păstrate, Rubidium+TexTrue, FerriteCore, ModernFix, LazyDFU și Oculus. Perechea Not Enough Animations + TRansliterationLib se exclude **împreună** conform ultimei aprobări. Entity Culling și Embeddium rămân amânate; nu le adăugăm și nu pretindem „cel mai rapid”. FPS în joc activ este nemăsurat.
- **Risc client/server:** scoaterea Lightfall Client poate opri conectarea la un proxy Lightfall; scoaterea CTM poate afecta resurse/texturi. Nici restul dependențelor nu sunt auditate pe JAR-urile Freeroam reale. Păstrarea vocii client nu dovedește că modul/UDP și pluginurile sunt pregătite pe server.
- **Server și RP:** baza FunCity b1.0827 are dovadă doar de boot în laborator, inclusiv problema Guava rezolvată prin override doar acolo. Autentificarea prin plugin încă nu este implementată/verificată în pachetul final; CoreProtect oferă jurnal/rollback, nu protecție preventivă. Nu schimbăm motorul ori lumea live ca să „ne jucăm” fără backup, login și verificarea registrului Forge.

## Poarta pentru profilul Freeroam ales

1. Mai întâi **inventar read-only** al profilului exact: existență și nume JAR; `scripts/fc_freeroam_target_preflight.py` calculează hashuri în memorie, dar produce numai verdict/cifre fără căi sau SHA publicate. **Fără SHA de referință nu certifică identitatea binarelor**, iar dependențele trebuie auditate separat. La orice JAR suplimentar, lipsă, ambiguu ori suspect **oprim** și investigăm; nu forțăm 28/22 prin ștergere. Calea Windows este necunoscută sandboxului; nu o căutăm în alte profiluri.
2. Pentru instalare ar fi necesare PC/runner funcțional, Prism și Minecraft **oprite**, spațiu și backup local privat/restaurare probată a profilului înaintea oricărei operații. Nu încărcăm lumi/loguri/conturi în artefacte GitHub; nu scriem un workflow care șterge automat JAR-uri. Mutarea doar a celor șase într-un backup local reversibil și verificarea SHA pentru toate celelalte ar necesita un pas separat, testat pe copie. Profilul ales de proprietar poate avea date importante, deci nu improvizăm în lipsa inventarului.
3. Testăm pe server **izolat** Forge 1.16.5, potrivirea modurilor/handshake, conectare, login prin plugin, voce, funcții RP, închidere/restart, restaurarea backupului; apoi FPS/RAM în joc activ. Abia după un server exact identificat și probe, stabilim dacă se poate intra pe cel existent. Nu avem acum dovada adresei/versiunii/serverului live și nu pretindem că jucăm în locul proprietarului.

**Stare reală:** manifestul și testele sintetice există în repo; accesul direct la PC lipsește, jobul Windows de inventar a fost anulat, iar dispatch-ul workflow-ului a primit anterior 403. Niciun profil, lume sau server nu a fost atins în această reevaluare. „Cel mai bun” este un obiectiv de comparat pe dovezi de gameplay, nu o garanție dintr-o listă de moduri.
