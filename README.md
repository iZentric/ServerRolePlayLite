<div align="center">
  <img src="site/assets/funcity-city.webp" alt="Ilustrație FunCity: oraș în lumini cyan și magenta" width="160" height="160">
  <h1>FunCity RP Lite</h1>
  <p><strong>Un oraș nou. Povestea e a voastră.</strong></p>
  <p>Minecraft 1.16.5 · conținut modat pentru RP · funcții de comunitate prin pluginuri</p>
  <p><strong>🧪 În laborator · 📂 Dezvoltare publică · ⛔ Fără release Lite sau server public verificat</strong></p>
  <p><a href="START-AICI.md"><strong>START AICI — explicația simplă</strong></a> · <a href="site/index.html">Pagina proiectului</a> · <a href="#stadiul-real">Dovezi și stadiu</a></p>
</div>

---

## De ce FunCity?

FunCity este un proiect de **oraș roleplay construit împreună cu jucătorii**. Vrem să păstrăm conținutul primului pack — mobilier, drumuri, vehicule, arme, mâncare și emote — fără să sacrificăm elementele RP doar ca să scădem numărul de moduri. Joburile, economia, rolurile și autentificarea sunt direcții pentru **pluginuri**, nu funcții pe care le declarăm deja finalizate.

| Ce urmărim | De ce contează | Ce este verificat acum |
|---|---|---|
| **Conținut RP păstrat** | Nu promitem un „Lite” golit de obiecte și mecanici. | Cele șase JAR-uri RP lipsă au fost restaurate în același profil LowSpec; serverul cu conținut a pornit pe o copie izolată. Gameplay-ul nu este încă testat. |
| **O cale de intrare pentru PC-uri mai slabe** | Profilul LowSpec este configurat cu 5 chunkuri și maximum 2 GiB heap. | Fișierele sunt verificate pe disc, dar nu există benchmark FPS sau garanție pentru orice laptop. |
| **Optimizări server alese cu rost** | Nu adăugăm zeci de JAR-uri pentru îmbunătățiri presupuse. | RoadRunner, FerriteCore și ModernFix au trecut doar bootul pe o copie; efectul MSPT/RAM rămâne de măsurat înainte de includerea definitivă. |
| **Oraș deschis, moderare responsabilă** | CoreProtect este pentru jurnal și rollback administrativ, nu pentru protecție preventivă de teren. | Pluginul s-a activat în bootul izolat; incidentele reale și restaurarea nu sunt încă probate. |

> **Important pentru jucători:** acesta este un proiect public **în dezvoltare**, nu o invitație de conectare. Nu descărca vechile release-uri ale repo-ului ca și cum ar fi noul FunCity RP Lite. Nu există încă un pachet Lite sau o adresă de server validate pentru intrarea în joc.

## Stadiul real

| Componentă | Situație verificată | Mai lipsește |
|---|---|---|
| **Motor** | FunCity b1.0827 / Minecraft 1.16.5 a pornit în laborator cu Forge și pluginuri, folosind Guava 21 prin override JVM temporar. | Remediu de distribuție verificat pentru motor; nu este un build final. |
| **Client LowSpec** | [21 JAR-uri](https://github.com/iZentric/ServerRolePlayLite/actions/runs/39335419784) în profilul Prism existent, inclusiv cele șase de conținut/dependențe restaurate. Sunt vizibile numai LowSpec, EGK, V RP și Fabulously Optimized; alte patru profiluri sunt arhivate reversibil. | Lansare client, conectare Forge, verificarea funcțiilor RP și măsurători FPS/RAM. |
| **Server de bază** | [15 JAR-uri: 11 conținut + 4 dependențe](https://github.com/iZentric/ServerRolePlayLite/actions/runs/39333730944), șase pluginuri nominal active; pornit/oprit pe PC într-un folder temporar, exclusiv loopback. | Instalare numai după validare; serverul existent și lumea sa nu au fost modificate. |
| **Optimizări server** | [Trial PC cu 18 JAR-uri](https://github.com/iZentric/ServerRolePlayLite/actions/runs/39336314432) (cele 15 de bază + RoadRunner, FerriteCore, ModernFix), pornit/oprit curat. | A/B repetat pe copie, cu aceeași lume/sarcină și fără regresii; fără cifre MSPT sau capacitate inventate. |
| **Lansare publică** | Codul și documentația sunt vizibile în repo și în [PR-ul de lucru](https://github.com/iZentric/ServerRolePlayLite/pull/2). | Drepturi/licențe și SHA pentru toate binarele, client+server testate împreună, login prin plugin, voce, backup/restaurare, test RP și aprobare explicită. |

**Niciun test de boot nu dovedește că un jucător poate intra.** Un build de laborator nu este un server live. [Tabelul sincer al motoarelor vechi/noi și problema Guava](agent/MOTOR-TABEL-VERIFICAT.md) · [Selecția fiecărui mod de performanță](agent/SELECTIE-PERFORMANTA-PURA.md) · [Jurnalul detaliat](agent/PROGRES.md).

## Cum este organizat proiectul

```text
site/                   pagina publică statică (prezentare, nu status live)
agent/                  decizii, audituri și dovezi; unele documente sunt istorice
scripts/fc_modded_*     pregătire și boot izolat pentru conținutul serverului
scripts/fc_pc_lowspec_* modificări controlate ale profilului LowSpec existent
.github/workflows/      verificări, niciuna nu face release Lite sau pornește live automat
```

[Politica actuală pentru conținut și pluginuri](agent/PLUGIN-FIRST.md) are prioritate față de listele istorice 24/29 din documentele vechi. Un JAR găsit într-un pack vechi **nu dovedește** cine l-a creat sau dacă îl putem redistribui. Proiectul păstrează tot conținutul RP în candidatul privat, dar nu publică acele binare fără verificarea drepturilor.

## Cum poți ajuta

- Citește [progresul verificabil](agent/PROGRES.md) și raportează o eroare prin [Issues](https://github.com/iZentric/ServerRolePlayLite/issues), cu pașii de reproducere și versiunea folosită. **Nu publica loguri brute, adrese, nume de lumi, date de cont sau tokenuri.**
- Dacă deții un JAR din pack, ajută la confirmarea **sursei, licenței și SHA-ului**; prezența lui pe un PC nu este o autorizație de release.
- Pentru contribuții la cod sau documentație, propune o schimbare cu test și explică ce verifică. Nu interpreta succesul unui CI ca pe o probă de FPS, autentificare sau număr de jucători.

**Planul de lansare:** întâi auditul fiecărui binar și al licențelor → import client + conectare la server pe copie → autentificare, voce și scenarii RP → backup și restaurare probate → test A/B pentru optimizările server → abia apoi release și lansare cu acord. [Planul public de lansare](agent/PUBLICARE.md) explică exact ce este public acum și ce blochează pachetul/serverul. [Ghid pentru contribuții](CONTRIBUTING.md).

## Drepturi și siguranță

Motorul derivă din Mohist/Tenet (GPL-3.0); distribuirea unui JAR derivat necesită audit de licență, atribuire și sursă corespunzătoare. Modurile, pluginurile și imaginile pot avea drepturi diferite; **nu există o licență unică declarată pentru tot conținutul din repo**. Nu urcăm lumi, conturi, configurații private, credențiale ori JAR-uri ale altora în noul pack. Release-urile istorice deja existente în GitHub nu sunt certificarea noului Lite.

<sub>FunCity RP Lite · Minecraft 1.16.5 · construit public, testat înainte de a fi promis.</sub>
