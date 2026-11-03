# FunCity Lite — revizuiește cele 25 de moduri cu mine

Sursă: două inventare istorice identice din `diag/pc-client.txt` (25 de nume), comparate cu auditul `agent/audit-modpack.md`. **Nu este manifestul verificat al release-ului și nu dovedește că orice client intră acum în joc.** „Cost” este o prioritizare calitativă a resurselor/asseturilor, **nu** un benchmark. Pentru **fiecare mod**, procentul real FPS/RAM/timp instalare pe laptop slab este **NEMĂSURAT**; nu însumăm beneficii sau consumuri imaginare.

| # | JAR exact din inventar | Ce primește jucătorul | Cost posibil pe PC / decizie practică |
|---:|---|---|---|
| 1 | `additional-guns-0.7.1-1.16.5.jar` | Mai multe arme CGM | Conținut/asseturi; **întreabă** dacă armele addon se folosesc. Nu rupe CGM/Obfuscate. |
| 2 | `cfm-7.0.0pre22-1.16.3.jar` | Mobilier funcțional | Modele/texturi, posibil mediu; **păstrează** pentru oraș. |
| 3 | `cgm-1.2.6-1.16.5.jar` | Arme de bază | Conținut/efecte; **păstrează** dacă armele sunt în RP, cu Obfuscate. |
| 4 | `Clumps-6.0.0.28.jar` | Gruparea XP + registru compatibil | Cost mic posibil, poate reduce multe orbs; **păstrează pe client și server**; a existat eroare de registry. |
| 5 | `emotecraft-for-MC1.16.5-2.2.7-b.build.47-forge.jar` | Emote/animații RP | Cost vizual variabil; **întreabă** dacă emotele sunt folosite; depinde de animație. |
| 6 | `entitycollisionfpsfix-1.16-1.0.1.jar` | Evită calcule de coliziune pe render thread | Poate ajuta în aglomerație; **păstrează pentru test**, fără procent inventat. |
| 7 | `entityculling-forge-mc1.16.5-1.5.2.jar` | Nu desenează entități ascunse după zid | Poate crește FPS dar folosește CPU; **A/B individual** în oraș. |
| 8 | `ferritecore-2.1.1-forge.jar` | Structuri de date cu memorie mai mică | Beneficiu RAM dependent de pack; **păstrează**. |
| 9 | `lazydfu-0.1.3.jar` | Inițializare amânată la pornire | Ajută mai ales la start, **nu** FPS în joc; **păstrează**. |
| 10 | `mapperbase-1.16.5-2.4.0.0.jar` | Bibliotecă pentru Road Stuff | Cost suplimentar de bibliotecă; **păstrează cât timp păstrăm drumurile**. |
| 11 | `modernfix-forge-5.18.0+mc1.16.5.jar` | Pornire/memorie + bugfixuri | De regulă ajută, compatibilitatea mixinurilor contează; **păstrează**. |
| 12 | `modernlife-1.16.5-1.15.jar` | CCTV, mobilă, bicicletă | Modele/funcții multe; **întreabă** dacă sunt folosite în lumea RP. |
| 13 | `Modernxl 1.16.5.jar` | Mobilier decorativ | Suprapunere tematică cu CFM/Modern Life; **întreabă**, nu șterge blocuri existente. |
| 14 | `obfuscate-0.6.3-1.16.5.jar` | Bibliotecă pentru CGM/Vehicle | Nu e „degeaba”: **păstrează** dacă rămân armele sau vehiculele. |
| 15 | `oculus-mc1.16.5-1.4.7.jar` | Compatibilitate shaders/texturi cu Rubidium | Shaders OFF pe PC slab; a existat problemă de texturi fără el; **păstrează** până la probă vizuală cu/fără. |
| 16 | `out_of_sight-1.16.4-1.0.1.jar` | Limitează randarea entităților/block entities îndepărtate | Poate ajuta FPS, dar mobilierul modat dispare deja după ~24 blocuri; **A/B individual**, prioritar. |
| 17 | `pamhc2foodcore-1.16.3-1.0.2.jar` | Rețete și alimente | Conținut/recipe load; **întreabă** dacă mâncarea/economia îl folosesc. |
| 18 | `Pizzaland_v68.jar` | Conținut RP propriu neidentificat complet | Cost și licență neconfirmate; **prioritate maximă de audit**, nu elimina din lume fără backup. |
| 19 | `player-animation-lib-forge-0.4.0+1.16.5.jar` | Bibliotecă pentru animații/emote | Cost dependent de Emotecraft; **păstrează** dacă rămân emotele. |
| 20 | `radon-0.8.0a.jar` | Optimizare iluminare | Poate reduce costul luminii, mixinuri trebuie testate; **păstrează**. |
| 21 | `roadstuff-1.16.5-4.3.0.jar` | Blocuri/materiale pentru drumuri | Conținut vizibil în oraș; **păstrează** dacă există drumuri salvate; cere Mapper Base. |
| 22 | `rubidium-mc1.16.5-0.2.13.jar` | Renderer optimizat | Candidat important pentru GPU integrat, câștigul diferă după laptop; **păstrează**. |
| 23 | `selene-1.16.5-1.9.0.jar` | Bibliotecă pentru Supplementaries | **Păstrează** cât timp există decorațiunile respective. |
| 24 | `supplementaries-1.16.5-0.18.4b.jar` | Obiecte/decorațiuni RP | Conținut vizual; **păstrează** dacă folosit în oraș, cu Selene. |
| 25 | `vehicle-mod-0.45.2-1.16.5 (1).jar` | Vehicule și combustibil | Pot costa la randare/trafic; **păstrează**: funcție centrală de RP, cu Obfuscate. |

**Cifre care sunt chiar verificabile:** 11/25 (44%) conținut RP, 4/25 (16%) biblioteci, 6/25 (24%) optimizare/pornire, 3/25 (12%) vizibilitate, 1/25 (4%) Clumps. **Aceste procente sunt din numărul JAR-urilor, NU din FPS, RAM sau dimensiunea instalării.** Din cele 25, **0 au un procent individual de câștig/consum măsurat pentru laptopul vizat** — zero *măsurători*, nu zero efect. Procentul real se calculează numai `100 × (valoare fără mod − valoare cu mod) / valoare fără mod` pe același laptop/scenă, repetat; pentru FPS unde „mai mare e mai bine” se inversează comparația.

**Spune-mi în special ce nu folosiți:** armele din Additional Guns, emotele, CCTV/bicicletele Modern Life, mobilierul ModernXL, mâncarea Pam, conținutul Pizzaland, plus dacă acceptați pop-in la mobilier pentru Out of Sight. Răspunsul tău alege candidații de **test**, nu șterge automat blocuri, moduri sau JAR-uri din release. CoreProtect și modurile server-only nu fac parte din cele 25 pentru client.
