# RP Lite: un proprietar pentru fiecare funcție, fără dubluri presupuse

**Alegere de proiect, NU configurație live:** ținta clientului rămâne 24 moduri cu Simple Voice Chat; pe server folosim `agent/DECIZII.md` (29 JAR-uri păstrate din cele 36 istorice, nu un pack server instalat). Nu scot conținutul din lume ca să reduc artificial numărul JAR-urilor. Baza istorică de pluginuri este ZIP-ul CUANTIC `lite` (14 nume); nu identifică ce rulează acum pe FunCity. Auditul automat `scripts/fc_plugin_audit.py` verifică SHA-ul arhivei, cele 14 JAR-uri unice, `plugin.yml`, dependențe și comenzi declarate; **nu** vede configul încărcat, lumea sau jucătorii.

## Proprietar unic de rol în ținta FunCity

| Rol RP | Proprietar propus | Limita suprapunerii și decizia |
|---|---|---|
| Permisiuni/grupuri | LuckPerms | Nu folosim fișierul `permissions.yml` drept al doilea sistem de ranguri. |
| Comenzi uzuale, home/spawn și economie de bază | EssentialsX + EssentialsXSpawn | Spawn nu e auditor de incidente; pluginul de job/economie, dacă există efectiv, se validează cu Vault înainte de a adăuga alt sistem financiar. |
| Chat text | EssentialsXChat | Voice Chat este canalul vocal separat, nu înlocuitor de chat sau moderator. |
| Reguli pe zone (spawn, mafii/poliție), editare administrativă | WorldGuard + WorldEdit | Un set de reguli regionale; **fără ClaimChunk** (claims ale jucătorilor), fără import de regiuni de pe serverele de referință fără lume/permisiuni. |
| Incidente și rollback verificabil | CoreProtect (cerință, nu în cele 14 istorice) | Nu e un plugin de protecție preventivă; WorldGuard nu îl înlocuiește. Binarul v21.2 era pinuit numai în staging de test, nu este dovedit instalat pe live. |
| API-uri de integrare | Vault; ProtocolLib doar dacă un plugin păstrat îl cere | API ≠ economie/permisiuni/antigrief de sine stătătoare. Citește `plugin.yml` și probează boot/login înainte de a scoate ProtocolLib. |
| Aspectul jucătorilor | SkinsRestorer, dacă politica de identitate îl cere | Rol vizual distinct; existența sa nu demonstrează autentificare sigură pe `online-mode=false` în repo. |

**Candidaturi de simplificare, nu eliminări demonstrate:**

1. `EssentialsXAntiBuild`: poate aplica restricții globale la blocuri, în timp ce WorldGuard gestionează reguli de regiune și LuckPerms acordă drepturi. **Nu sunt același plugin.** Îl scoatem din *copia B* numai dacă regulile active, comenzile și permisiunile arată că nu are un rol neacoperit; test de plasare/spargere pe spawn, zona mafii și în oraș, inclusiv blocuri modate și jucător fără rang. La diferențe de siguranță, îl păstrăm.
2. `EssentialsXProtect`: poate opri evenimente globale, în timp ce WorldGuard aplică reguli pe regiuni. Îl scoatem din *copia C* separat numai după inventarul regulilor active și probe de foc/explozii/mobi + rollback CoreProtect; nu scoatem ambele pluginuri simultan și nu eliminăm WorldGuard pe presupunerea că Essentials îl substituie.
3. `ProtocolLib`, `SkinsRestorer` și `Vault` nu sunt redundante doar fiindcă există alt plugin. Scoaterea se face numai după auditul dependențelor din JAR-uri și testarea funcțiilor care le folosesc. `Chunky` și `spark` sunt instrumente de laborator, nu pluginuri/moduri permanente; `Cuantic-Brand` este identitate veche, iar `claimchunk` contrazice orașul deschis — acestea sunt deja SCOASE din ținta normală.

**Nu spunem că ținta are deja joburi funcționale:** arhiva fără căi are fișiere de meniu `Jobs.yml`/`aJobs.yml`, dar packul de 14 pluginuri CUANTIC nu enumeră un provider de joburi. Mai întâi verificăm pe copia reală ce comandă deschide meniul, care plugin acordă recompensa, cum persistă banii și ce permisiune o limitează. Dacă providerul lipsește, nu inventăm o integrare, nu introducem un plugin nou doar din numele fișierului și nu declarăm RP validat.

## Internet slab / instalare simplă

Auditul hosted [39266263549](https://github.com/iZentric/ServerRolePlayLite/actions/runs/39266263549) măsoară pentru candidatul client ZIP **135.771.416 B** și **32.537.149 B** downloaduri remote *declarate* în manifest (total aritmetic **168.308.565 B**, fără Minecraft/Forge/alte costuri; nu este timp de instalare măsurat). `Pizzaland_v68.jar` (~83 MB comprimați) și `Modernxl 1.16.5.jar` (~35,4 MB comprimați) domină arhiva. Fără scanare de lume/registry nu eliminăm mobilierul sau conținutul orașului pentru o promisiune falsă de download rapid. Un `.mrpack` unic, SHA pentru fișierele remote, fără JAR-uri server-only pe client sau două copii ale aceluiași mod; nu repachetăm JAR-uri ARR fără drepturi și nu scoatem iconul duplicat înainte de verificarea brandingului la import. Pentru net slab, verificarea practică este importul curat și reinstalarea cu cache/descărcări reale, nu numărul de JAR-uri.

**Poartă:** backup/restore pe copie, pluginuri/dependențe fără conflicte, 3 porniri/braț pentru fiecare scoatere, login Forge și voce UDP, scenariu job–economie–mafii/poliție, CoreProtect și rollback, FPS/RAM/rețea pe laptop modest. Până atunci P04/P06 rămân păstrate conform `agent/DECIZII.md`; nu schimbăm PC, release ori live. Un server „perfect” nu rezultă dintr-un inventar de ZIP sau dintr-un test de parser.
