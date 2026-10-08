# LEGEA RUST (regula suprema a proiectului)

**Orice decizie din acest proiect se judeca cu O SINGURA intrebare:**

> "E cea mai apropiata de Rust varianta care EXISTA — adica cel mai mic consum
> posibil — pe care MERG modurile SI pluginurile noastre?"

## Cele 3 articole:
1. **CONSUM MINIM OVERALL** — server + client modpack, amandoua. Orice piesa
   noua trebuie sa scada consumul sau sa fie taiata.
2. **FUNCTIONAREA E SUPREMA** — "mai rapid pe hartie dar mort" pierde mereu in
   fata lui "aproape la fel de rapid si VIU". (De-aia CatServer > Mist.)
3. **DOVADA, NU PAREREA** — nimic nu se declara mai rapid fara bancul de probe
   (test-server.yml) sau spark pe copii reali.

4. **PRAGUL SURVIVAL (intangibil)** — oricat strangem, jocul ramane survival
   adevarat LANGA jucatori: mobi care apar noaptea linga tine, foame, pericol,
   farming posibil. Taiem doar ce e DEPARTE de jucatori si ce nu se vede.
   Daca vreodata o taietura face jocul sa se simta gol => se da inapoi, fara
   discutie. (Manete de siguranta: plafon 40->55, spawn-range 3->4.)

## Cum se aplica automat:
- pack-rules.json = singura sursa de adevar; build-ul face si serverul si
  clientul din ea => regula se aplica AUTOMAT la amandoua.
- Tribunalul jarurilor testeaza fiecare schimbare pe Java-ul real Zampto.
- Post-lansare: spark decide urmatoarea taietura, niciodata moda sau graba.

*Sigilata la cererea patronului: "cel mai mic posibil si modificat sa mearga."*
