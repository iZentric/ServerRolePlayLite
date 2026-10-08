# 🚀 PRIMA PORNIRE — lipești astea O SINGURĂ DATĂ în consola din panou

## 1. Fă-te șef:
```
op NUMELE_TAU
lp user NUMELE_TAU permission set * true
```

## 2. Profilul SURVIVAL CUSTOM PALMA (se salvează pe veci în lume):
```
gamerule doInsomnia false
gamerule mobGriefing false
gamerule doFireTick false
gamerule keepInventory true
gamerule maxEntityCramming 8
gamerule announceAdvancements false
```

### Ce face fiecare (de ce așa au serverele mari de copii):
| Regula | Efect |
|---|---|
| doInsomnia false | FĂRĂ fantome enervante noaptea (și minus entități = minus lag) |
| mobGriefing false | creeperii NU mai fac găuri în oraș / construcțiile copiilor (explozia tot doare, dar blocurile rămân) |
| doFireTick false | focul nu se întinde — nimeni nu arde orașul din joacă |
| keepInventory true | copiii NU-și pierd lucrurile la moarte = fără plâns, fără grămezi de iteme pe jos (= și anti-lag) |
| maxEntityCramming 8 | fără ferme de înghesuit animale care fac lag |
| announceAdvancements false | chatul nu e spamat cu realizări |

> Vrei survival mai dur mai târziu? `gamerule keepInventory false` și gata — orice regulă se schimbă live, oricând.

## 3. Verifică sănătatea serverului (după 10 min cu copii pe el):
```
spark tps
spark healthreport
```
TPS 20 = perfect. Sub 17 = îmi zici și operez.

## 4. Sistemul de conturi (serverul primeste si TLauncher si premium):
Copiii la prima intrare: `/register parola parola` — apoi mereu: `/login parola`
Skin pe cont nepremium: `/skin set NumeJucatorPremium`
⚠️ Fiind server deschis (offline-mode), NU da niciodata OP fara ca AuthMe sa fie activ!

## 5. Voice chat-ul (modul are nevoie de un port UDP):
Panou → Network: daca poti adauga o alocare UDP (24454), pune-o si scrie portul in
`config/voicechat/voicechat-server.properties` (port=24454). Daca nu se poate, jocul
merge perfect si fara voce.

## 6. Logare automata premium (FastLogin):
- Copil cu cont PREMIUM: intra AUTOMAT, fara parola (FastLogin il verifica la Mojang)
- Comanda `/premium` - un jucator isi marcheaza singur contul ca premium
- Nepremium (TLauncher): raman pe /register + /login (AuthMe)
- Daca serverul nu porneste din cauza ProtocolLib (hibridele-s sensibile): sterge
  plugins/ProtocolLib.jar si plugins/FastLoginBukkit.jar - totul revine la AuthMe simplu.

## 7. GRANITA LUMII (lipeste si astea la prima pornire):
```
worldborder center 0 0
worldborder set 2000
```
## 8. Pre-generarea DIN MERS (optional, dupa ce intri):
```
chunky radius 800
chunky start
```
(genereaza harta incet in fundal; opresti oricand cu `chunky pause`)
