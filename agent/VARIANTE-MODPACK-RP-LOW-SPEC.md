# Trei variante de client FunCity RP pentru PC-uri slabe (Forge 1.16.5)

22 octombrie 2026 · [rețete exacte JSON](FUNCITY-RP-VARIANTE-LOWSPEC.json) · [generator local Prism](../scripts/fc_rp_lowspec_variants.ps1).

**Ce livrează această schimbare:** trei variante de *profil Prism reproductibile*, cu generator fail-closed și fixture de test, pornind numai din JAR-urile deja aflate în profilele locale Lite / Embeddium TEST. **Nu sunt arhive `.mrpack` cu JAR-uri gata de descărcat**: acele binare private/licențele/modurile de conținut nu sunt în acest repository. Nu pretind că profilele noi au trecut Forge login/FPS. [Proba hosted](https://github.com/iZentric/ServerRolePlayLite/actions/runs/39685147630) a trecut; [prima încercare PC](https://github.com/iZentric/ServerRolePlayLite/actions/runs/39685243472) s-a oprit. [Recontrolul PC **doar read-only**](https://github.com/iZentric/ServerRolePlayLite/actions/runs/39685431492) a confirmat `PRISM_ACTIVE=True`, Lite exact 22 JAR-uri, Embeddium TEST 22 și **zero variante noi create**. Nu forțăm închiderea și nu reluăm automat încercarea. Profilul `Freeroam 1.0.0`, Lite 22 funcțional, Embeddium TEST existent, lumea și serverul live rămân neatinse.

## Diferența reală, nu funcții puse „de dragul listei”

| Variantă Prism *nouă*, dacă este creată local | JAR-uri | Modificări **numai în copia nouă** față de Lite-ul funcțional | Pentru cine / riscul specific |
|---|---:|---|---|
| **FunCity RP LowSpec Rubidium** (`low_rubidium`) | 22 | **Niciun JAR schimbat**. Aceleași Rubidium 0.2.13, TexTrue Rubidium Options 1.0.8, Oculus 1.4.7 și toate modurile RP. Preset grafic 5/Fast. | **Recomandarea inițială:** izolează beneficiul setărilor pentru PC slab, cu cel mai mic risc pentru texturile RP. Oculus rămâne chiar fără shaderpack: eliminarea sa a fost asociată în audit cu texturi defecte. |
| **FunCity RP LowSpec fara Oculus TEST** (`no_oculus_test`) | 21 | Exact ca prima, dar **scoate numai** `oculus-mc1.16.5-1.4.7.jar` din copie. Nu scoate niciun mod de conținut. | **Test opțional:** fără funcția de shader; totuși poate strica textura mobilierului/modurilor. Compară vizual cu prima variantă *înainte* de orice recomandare. Scăderea numărului de JAR-uri nu garantează FPS. |
| **FunCity RP LowSpec Embeddium fara Oculus TEST** (`embeddium_test`) | 21 | Față de Lite: scoate **trei** JAR-uri `rubidium-mc1.16.5-0.2.13.jar`, `TextruesRubidiumOptions-1.0.8-mc1.16.5.jar`, `oculus-mc1.16.5-1.4.7.jar`; adaugă **exact două** din TEST: `embeddium-0.3.18+mc1.16.5.jar`, `textrue_embeddium_options-0.1.1+mc1.16.5.jar`. | **Test condiționat:** compară-l cu varianta de 21 JAR-uri Rubidium (fără Oculus), astfel opțiunile și shader-ele rămân egale și se schimbă numai rendererul + interfața sa necesară. Dacă apar probleme fără Oculus, oprește proba: folosește TEST Embeddium existent, care păstrează Oculus. |

**Comune tuturor:** arme CGM/Additional Guns/Obfuscate, mobilier CFM/ModernLife/ModernXL/Pizzaland, vehicule, drumuri + Mapper Base, Emotecraft + player-animation-lib, mâncare, Supplementaries + Selene, voce, ModernFix, FerriteCore și LazyDFU. Exact cele șase excluderi client aprobate pentru Lite rămân excluse. **Nimic nu este șters din lumea/serverul existent.** Nu se adaugă *Dynamic FPS*, *FPS Reducer*, *Distant Horizons*, Halogen, Clumps sau vreun add-on de randare „pentru orice eventualitate”. Serverul are deja view-distance 5.

**Preset identic în cele trei profile:** render distance 5, Fast, particule **Decreased** (nu le ascunde complet: efectele RP rămân), mipmap 0, umbrele entităților Off. Acesta **nu este un mod de reducere a FPS-ului**, nici o limitare FPS. Shaderpackurile nu sunt copiate și nici activate. Nu forțăm aceeași memorie Java/rezoluție pe PC-uri diferite. `options.txt` nou nu copiază rezoluția, keybindurile, resourcepackurile ori conturile/salvările private; pentru comparație corectă trebuie verificată și egalizată manual rezoluția, alocarea RAM, orice resourcepack RP local și celelalte opțiuni dacă diferă. Lipsa unui resourcepack local poate schimba aspectul chiar dacă JAR-urile RP sunt identice.

## Creare locală fără a modifica profilele existente

Generatorul PowerShell creează **câte o variantă la apel**, cu verificare exactă a celor 22 de nume Lite, SHA la copiere, interdicție pentru JAR-uri extra/symlinkuri, cale țintă nouă, metadate Prism păstrate și staging în același folder. Pentru Embeddium verifică și egalitatea SHA a celor 20 de JAR-uri comune, perechea binară pin-uită din inventarul anterior al discului E: și `mods.toml` pe PC. Nu descarcă, nu pornește serverul și nu închide forțat Prism. **Rularea cu `-Synthetic` este numai pentru fixture-ul de Linux**, nu pentru Windows.

Pe PC-ul proprietarului, **după închiderea normală a Prism și a clientului**, din checkout-ul repo-ului, Windows PowerShell (fără `-Synthetic`):

```powershell
$lite = 'C:\Users\Administrator\AppData\Roaming\PrismLauncher\instances\FunCity RP Lite'
$test = 'C:\Users\Administrator\AppData\Roaming\PrismLauncher\instances\FunCity RP Lite Embeddium TEST'
& .\scripts\fc_rp_lowspec_variants.ps1 -Variant low_rubidium -Lite $lite
& .\scripts\fc_rp_lowspec_variants.ps1 -Variant no_oculus_test -Lite $lite
& .\scripts\fc_rp_lowspec_variants.ps1 -Variant embeddium_test -Lite $lite -EmbeddiumTest $test
```

**Nu rula toate comenzile automat dacă primul preflight a eșuat.** Dacă oricare destinație există deja, scriptul refuză suprascrierea. Pentru a economisi spațiu, poți crea mai întâi numai varianta recomandată, apoi pe cele de TEST doar dacă vrei comparația. Dacă o copie de test nu este bună, revino prin simpla selectare a profilului Lite existent, fără modificări ale lui; nu șterge în grabă profilul defect cât jocul rulează.

## Cum alegem câștigătorul (fără cifre inventate)

1. Prima probă: `LowSpec Rubidium` 22 — pornește, verifică autentificarea/încărcarea, arme, mobilier/Pizzaland, vehicule, emote, drumuri, voce cu doi clienți și orice resourcepack RP local. **Aceste verificări încă nu au fost făcute pentru profilele noi.**
2. Dacă vrei să testezi scoaterea shaderelor, compară `fara Oculus TEST` 21 la aceleași setări. Dacă texturile/entitățile sunt defecte, rămâi la varianta 22. Dacă nu se vede o îmbunătățire repetabilă, nici acel JAR nu trebuie eliminat doar pentru a reduce cifra 22→21.
3. Numai dacă testul fără Oculus este vizual corect, compară cele două variante de 21 JAR-uri, **aceeași rezoluție, lume, scenă RP, resurse și preset**, repetate A/B: FPS median, 1% low/frame-time, RAM, calitatea texturilor și voice/join. Embeddium existent a primit doar feedback «cam la fel» fără condiții grafice egale; nu îl promovăm din presupuneri. Dacă varianta 21 eșuează, se poate compara separat 22 Rubidium cu Embeddium TEST **păstrând Oculus în ambele**.

**Verdict actual:** prima variantă (22 JAR-uri Rubidium la 5/Fast) este candidatul preferat pentru PC slab fiindcă nu sacrifică funcții RP pentru un câștig nemăsurat. Cele două variante de 21 sunt probe controlate, **nu modpackuri finalizate/jucate/testate pe PC**. Un pack RP cu mai puține JAR-uri poate fi *mai lent* sau poate strica decorațiuni; alegerea finală cere probă în joc.
