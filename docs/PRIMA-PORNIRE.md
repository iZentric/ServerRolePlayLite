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
