---
name: arena-api-setup
description: Configurează în siguranță Arena API ca provider pentru un client de coding agent și distinge Coding Router de Max API și Agent Mode.
---

# Configurarea Arena API

- Folosește numai instrucțiunile oficiale de la `https://platform.arena.ai/docs/` și subpagina clientului ales.
- Arena Coding Router documentat pentru coding clients folosește aliasul `coding-router-preview`. Nu-l numi Max și nu promite comportamentul complet din Arena Agent Mode.
- API key-ul este secret: nu îl cere în chat și nu îl salva în Git. Lasă Quickstart-ul oficial să configureze acreditările local; pentru configurare manuală, folosește variabile de mediu/fișiere locale ignorate.
- Separă documentația de configurare de eligibilitate: existența unei pagini Codex/OpenCode nu garantează că o cheie free este autorizată în acele harness-uri. Verifică restricțiile afișate pentru contul/cheia concretă.
- Dacă platforma cere Request Access, nu încerca ocolirea aprobării. Nu presupune preț, acces gratuit permanent, cotă sau SLA.
- Cererea „Max via API” este separată de API-ul general/Coding Router. Auto-Mode din site nu este un model coding-router.
- Nu executa scriptul Quickstart în numele utilizatorului pe o mașină diferită de cea unde va rula clientul.
