---
name: safe-server-operations
description: Planifică verificări și schimbări pentru runtime-ul Minecraft fără a afecta lumea sau serverul real.
---

# Operațiuni sigure de server

- Începe cu analiză statică și teste locale; nu porni serverul sau workflow-urile de deploy automat.
- Nu folosi world/server live pentru experimente. Cere aprobare explicită și backup verificat înainte de orice schimbare persistentă.
- Nu expune consola, RCON, tokenurile sau fișierele de configurare care pot conține parole.
- Pentru fiecare schimbare propune: precondiții, copie/backup, verificare de boot/health, criteriu de succes și rollback.
- Nu declara testat un plugin sau o setare doar pentru că fișierul de configurare pare valid.
