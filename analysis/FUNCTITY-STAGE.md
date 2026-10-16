== SONDA EXTERNA 25565 ==
{"version": {"name": "Mohist 1.16.5", "protocol": 754}, "players": {"online": 1, "max": 25}}
== SONDA EXTERNA 25566 ==
STATUS FAILED: timed out

# FUNCTITY-STAGE 2026-10-16 21:31:12 UTC — gazda → artefact → relay

```
mod automat din marker: autowake port=25565 jar=b1.0827
== AUTOWAKE hook (.bashrc) ==
  hook scris in ~/.bashrc
c.sh SUS -> hook nu face nimic (corect)
  R 
  R # FUNCITY-AUTOWAKE: self-heal la deschidere de shell (ruleaza DOAR daca supervisorul e jos)
  R if ! pgrep -f "bash .*[/]c[.]sh" >/dev/null 2>&1; then ( setsid bash "$HOME/c.sh" >> "$HOME/cuantic-live/sup.log" 2>&1 </dev/null & ) ; fi
RC=0
```
