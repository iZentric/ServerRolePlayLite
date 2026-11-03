# FunCity: compressor nativ experimental, NU inclus în server.jar

[Traseul CatServer 1.16.5](https://github.com/Luohuayu/CatServer/blob/1d8d63138be77a606df2a5e940b960065948f983/patches/minecraft/net/minecraft/network/NettyCompressionEncoder.java.patch) folosește `java.util.zip.Deflater` și alocă un `byte[i]` per pachet comprimat. Ipoteză de cercetare: compresia ar putea costa CPU sub mulți clienți; **nu este încă un hotspot măsurat în lumea RP**.

[Jobul de cercetare](../../.github/workflows/funcity-native-packet-research.yml) compară Java 11 Deflater reutilizat cu Rust FFI către [libdeflate MIT](https://github.com/ebiggers/libdeflate/tree/0758d0a12d34fac281b0fe27c5155fbe753d9511), pe șase payload-uri publice, fixe (1 KiB / 32 KiB / 256 KiB, jumătate compresibile sau pseudoaleatoare), în ordinea Java/Rust/Rust/Java. Toate streamurile trebuie să treacă `zlib.decompress` și egalitatea cu datele originale; se raportează mediane **locale acelui job**, nu se publică binare, lume ori payload-uri private. Licența libdeflate rămâne a autorilor; codul lor nu este copiat în repo.

[Rularea 41580558695](https://github.com/iZentric/ServerRolePlayLite/actions/runs/41580558695) a trecut și **apelul JNI cu `ByteBuffer` direct**, printr-un shim C minimal spre aceeași bibliotecă libdeflate; streamurile fiecărui braț s-au decomprimat identic. Mediane în milisecunde pe runnerul acelui job (Java Deflater / JNI libdeflate):

| Payload public | 1 KiB | 32 KiB | 256 KiB |
|---|---:|---:|---:|
| 50% zerouri + pseudoaleator | 28,42 / 17,32 | 98,65 / 60,32 | 468,81 / 221,82 |
| Pseudoaleator | 31,44 / 16,17 | 236,87 / 114,11 | 808,24 / 387,87 |

**Nu este un benchmark în server:** libdeflate este scris în C, apelat direct din Rust în prima probă și prin C/JNI în a doua; viteză mai bună a algoritmului, nu „magia Rust”. JNI cu buffer direct este inclus în a doua probă, dar conversia unui buffer Netty/heap, alocările reale, Forge handshake, voice, simultaneitatea și comportamentul sub jucători **nu** sunt măsurate. Acesta este cel mult un candidat pentru compresie. Intră ca patch JNI opt-in, cu fallback Java, numai dacă profilul TEST 34/13 arată că firele Netty comprimă semnificativ; apoi sunt obligatorii probele de protocol, p95 tick, RSS, GC și rampa de jucători A/B/B/A. Dacă nu câștigă în motor, componenta nativă rămâne exclusă.

## Costul din jurul compresorului — probă suplimentară, **nu Netty real**

[`PacketPipelineBench.java`](PacketPipelineBench.java) compară două căi pe **aceleași șase intrări publice**, fiecare cu sursă `heap` și `direct`, într-un job Java 11 în ordine J/N/N/J. Java copiază intrarea într-un `byte[]` nou, folosește `Deflater` reutilizat și scrie printr-un buffer de 8192 B într-o ieșire directă nouă per pachet. JNI folosește sursa directă fără copie de intrare, ori alocă/copiază într-un buffer direct dacă sursa este în heap, apoi scrie în aceeași formă de ieșire directă nouă. Alocarea ieșirii și copierea intrării sunt **în regiunea cronometrată**; scrierea fișierului de verificare nu este. Fiecare rezultat (48 streamuri) trebuie să treacă decomprimarea zlib și egalitatea exactă cu intrarea. Comparați numai cele două brațe ale **aceluiași rând și job**; dimensiunile de pachet sunt artificiale, nu distribuția reală de pe RP.

Acesta modelează intenționat costul de staging, nu implementarea `ByteBuf` sau frame-ul VarInt din CatServer: poate avea alți allocatori, buffer compozit, praguri și pachete necomprimate. Nici diferențele dintre alocatori, GC/JIT și threadurile Netty simultane nu sunt controlate ca într-un server real. **Nu adăugați JNI în engine doar din acest rezultat.** Selecția rămâne: (1) Java existent — sigur dacă Netty nu e hotspot sau staging elimină câștigul; (2) JNI opt-in + fallback Java — numai după profil privat/benchmark integrat; (3) rescriere Rust a motorului — incompatibilă ca înlocuitor direct Forge+Bukkit 1.16.5. Etapele următoare sunt profilul privat Netty ≥100 eșantioane cu clienți și apoi test A/B/B/A al motorului pe TEST; fără aceste probe nu este un câștig de capacitate.

[Proba găzduită 41586292839](https://github.com/iZentric/ServerRolePlayLite/actions/runs/41586292839) a trecut toate **48** streamurile de model (șase intrări × heap/direct × J/N/N/J). Mediane **numai în acest job**, timp total al buclei în ms (Java / JNI), inclusiv copierea necesară și ieșirea nouă per pachet:

| Intrare publică | heap 1 KiB | direct 1 KiB | heap 32 KiB | direct 32 KiB | heap 256 KiB | direct 256 KiB |
|---|---:|---:|---:|---:|---:|---:|
| Mix | 10,55 / 7,58 | 11,38 / 5,95 | 19,56 / 13,83 | 20,50 / 11,15 | 76,66 / 38,69 | 76,00 / 35,79 |
| Pseudoaleator | 9,96 / 8,00 | 11,38 / 5,64 | 40,21 / 22,73 | 40,22 / 19,90 | 129,38 / 63,28 | 134,72 / 61,61 |

**Interpretare:** staging-ul modelat nu a eliminat avantajul JNI pe aceste intrări, dar alocările directe din Java nu imită allocatorul Netty, distribuția de mărimi nu este măsurată pe RP, iar comparația nu este un trial de capacitate. Nu se extrapolează milisecundele la jucători; cele două joburi JNI au *alte* bucle și nu se compară ca durată absolută. Analizorul [JFR local](../../scripts/fc_funcity_jfr_hotspots.py) numără acum separat eșantioanele CPU Netty care conțin `java.util.zip.Deflater` sau `Inflater` oriunde în stivă, pentru a stabili dacă există un motiv să trecem la integrare; procentul este din eșantioanele **Netty**, nu din timpul total al serverului.

**Corecție de siguranță din poarta 281:** cercetarea folosește acum `libdeflate_zlib_compress_bound()` pentru capacitatea bufferului JNI; presupunerea anterioară `input + 1024` nu era un contract. Poarta respinge un buffer cu un octet sub bound și un header VarInt corupt. Prima rulare a noii matrice [41587394760](https://github.com/iZentric/ServerRolePlayLite/actions/runs/41587394760) a eșuat înainte de verdict; versiunea corectată trebuie rerulată, fără a declara motorul integrat sau validat.
