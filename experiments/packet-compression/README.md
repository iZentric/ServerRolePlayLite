# FunCity: compressor nativ experimental, NU inclus în server.jar

[Traseul CatServer 1.16.5](https://github.com/Luohuayu/CatServer/blob/1d8d63138be77a606df2a5e940b960065948f983/patches/minecraft/net/minecraft/network/NettyCompressionEncoder.java.patch) folosește `java.util.zip.Deflater` și alocă un `byte[i]` per pachet comprimat. Ipoteză de cercetare: compresia ar putea costa CPU sub mulți clienți; **nu este încă un hotspot măsurat în lumea RP**.

[Jobul de cercetare](../../.github/workflows/funcity-native-packet-research.yml) compară Java 11 Deflater reutilizat cu Rust FFI către [libdeflate MIT](https://github.com/ebiggers/libdeflate/tree/0758d0a12d34fac281b0fe27c5155fbe753d9511), pe șase payload-uri publice, fixe (1 KiB / 32 KiB / 256 KiB, jumătate compresibile sau pseudoaleatoare), în ordinea Java/Rust/Rust/Java. Toate streamurile trebuie să treacă `zlib.decompress` și egalitatea cu datele originale; se raportează mediane **locale acelui job**, nu se publică binare, lume ori payload-uri private. Licența libdeflate rămâne a autorilor; codul lor nu este copiat în repo.

[Rularea 41580558695](https://github.com/iZentric/ServerRolePlayLite/actions/runs/41580558695) a trecut și **apelul JNI cu `ByteBuffer` direct**, printr-un shim C minimal spre aceeași bibliotecă libdeflate; streamurile fiecărui braț s-au decomprimat identic. Mediane în milisecunde pe runnerul acelui job (Java Deflater / JNI libdeflate):

| Payload public | 1 KiB | 32 KiB | 256 KiB |
|---|---:|---:|---:|
| 50% zerouri + pseudoaleator | 28,42 / 17,32 | 98,65 / 60,32 | 468,81 / 221,82 |
| Pseudoaleator | 31,44 / 16,17 | 236,87 / 114,11 | 808,24 / 387,87 |

**Nu este un benchmark în server:** libdeflate este scris în C, apelat direct din Rust în prima probă și prin C/JNI în a doua; viteză mai bună a algoritmului, nu „magia Rust”. JNI cu buffer direct este inclus în a doua probă, dar conversia unui buffer Netty/heap, alocările reale, Forge handshake, voice, simultaneitatea și comportamentul sub jucători **nu** sunt măsurate. Acesta este cel mult un candidat pentru compresie. Intră ca patch JNI opt-in, cu fallback Java, numai dacă profilul TEST 34/13 arată că firele Netty comprimă semnificativ; apoi sunt obligatorii probele de protocol, p95 tick, RSS, GC și rampa de jucători A/B/B/A. Dacă nu câștigă în motor, componenta nativă rămâne exclusă.
