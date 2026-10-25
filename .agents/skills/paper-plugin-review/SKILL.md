---
name: paper-plugin-review
description: Evaluează un plugin Minecraft pentru serverul Paper FunCity înainte de a-l recomanda sau adăuga.
---

# Audit de plugin Paper

Pentru fiecare plugin propus:

1. Identifică pagina oficială a proiectului și release-ul exact; nu folosi linkuri de download din agregatoare dacă există sursă upstream.
2. Verifică explicit versiunea de Minecraft și Paper declarată, versiunea Java cerută, data release-ului și starea de mentenanță.
3. Verifică licența, dependențele, permisiunile, persistența datelor, integrarea cu celelalte pluginuri și eventualele suprapuneri.
4. Leagă fiecare afirmație importantă de sursa oficială; dacă nu este declarată compatibilitatea, spune „neverificată”, nu o ghici.
5. Propune test pe copie a serverului și plan de rollback. Nu instala JAR-uri și nu modifica `plugins.lock.json` ca decizie implicită.
6. Compară costul de memorie/tick doar prin măsurători reproductibile pe aceeași configurație; nu promite „fără lag”.
