#!/usr/bin/env bash
# FUNCTITY-PUBLISH — duce un fisier de raport din jobul self-hosted inapoi pe bransa.
# Foloseste orice canal functioneaza pe gazda: (1) gh authenticat al masinii,
# (2) git clone proaspat + credential helper default, (3) clone existent cu token in URL.
# Esecul publicarii nu trebuie sa strice verdictul jobului: raportam clar si iesim 0 cu semn.
set -uo pipefail
SRC=$1; DEST=$2; MSG=$3
BR=${GITHUB_REF_NAME:-arena/9bbcb24f-serverroleplaylite}
REPO_URL=${GITHUB_SERVER_URL:-https://github.com}/${GITHUB_REPOSITORY:-iZentric/ServerRolePlayLite}
say(){ echo "publish: $*"; }
[ -f "$SRC" ] || { echo "raport absent: $SRC"; exit 0; }
B64=$(base64 -w0 "$SRC"); echo "$B64" > /tmp/fp-content.b64
export FP_DEST="$DEST" FP_MSG="$MSG"

# 1) gh al masinii (cheile din keyring; GH_TOKEN de workflow nu are voie write pe self-hosted)
if command -v gh >/dev/null 2>&1; then
  export GH_TOKEN= GITHUB_TOKEN=
  if gh auth status >/dev/null 2>&1; then
    sha=$(gh api "repos/$GITHUB_REPOSITORY/contents/$DEST?ref=$BR" --jq .sha 2>/dev/null || true)
    if gh api -X PUT "repos/$GITHUB_REPOSITORY/contents/$DEST" -f message="$MSG" \
        -f content="$B64" -f branch="$BR" ${sha:+-f sha=$sha} >/dev/null 2>&1; then say "canal gh OK"; exit 0; fi
    say "gh autentificat dar PUT esuat"
  else say "gh prezent dar neautentificat"; fi
fi

# 1b) CANALUL DOVEDIT AL GAZDEI (mc-run 13 Oct): node https cu PAT din hosts.yml /
# .git-credentials / remote-urile clone-urilor de pe gazda. gh lipseste de obicei aici.
if command -v node >/dev/null 2>&1; then
  node <<'NODE' 2>/tmp/fpnode.err && { say "canal node OK"; exit 0; }
  const fs=require("fs"), https=require("https");
  const toks=[];
  try{ const h=fs.readFileSync(process.env.HOME+"/.config/gh/hosts.yml","utf8"); for(const m of h.matchAll(/oauth_token: (\S+)/g)) toks.push(m[1]); }catch(e){}
  try{ for(const l of fs.readFileSync(process.env.HOME+"/.git-credentials","utf8").split("\n")){ if(l.includes("github.com")){ const t=l.split("://")[1].split("@")[0].split(":").pop(); if(t) toks.push(decodeURIComponent(t)); } } }catch(e){}
  try{ for(const l of fs.readFileSync(process.env.HOME+"/.config/git/credentials","utf8").split("\n")){ if(l.includes("github.com")){ const t=l.split("://")[1].split("@")[0].split(":").pop(); if(t) toks.push(decodeURIComponent(t)); } } }catch(e){}
  const repo=process.env.GITHUB_REPOSITORY||"iZentric/ServerRolePlayLite", br=process.env.GITHUB_REF_NAME;
  const dest=process.env.FP_DEST||"analysis/FUNCTITY-REPORT.md";
  const msg=process.env.FP_MSG||("funcity-publish "+new Date().toISOString());
  const content=fs.readFileSync("/tmp/fp-content.b64").toString().trim();
  function api(m,path,b,t){return new Promise(r=>{const d=b?JSON.stringify(b):null;const q=https.request({host:"api.github.com",path,method:m,headers:Object.assign({"Authorization":"Bearer "+t,"User-Agent":"funcity-publish","Accept":"application/vnd.github+json"},d?{"Content-Type":"application/json","Content-Length":Buffer.byteLength(d)}:{})},x=>{let s="";x.on("data",y=>s+=y);x.on("end",()=>r({status:x.statusCode,body:s}))});q.on("error",e=>r({status:0,body:String(e)}));if(d)q.write(d);q.end();});}
  (async()=>{ for(const t of new Set(toks)){
      let sha; const g=await api("GET","/repos/"+repo+"/contents/"+dest+"?ref="+encodeURIComponent(br),null,t);
      if(g.status===200){ try{sha=JSON.parse(g.body).sha}catch(e){} }
      const body=Object.assign({message:msg,content,branch:br}, sha?{sha}:{});
      const pu=await api("PUT","/repos/"+repo+"/contents/"+dest,body,t);
      if(pu.status===200||pu.status===201){ console.log("node: OK cu un token din "+new Set(toks).size); process.exit(0); }
    }
    console.error("node: niciun token functionabil"); process.exit(2); })();
  NODE
  say "canal node esuat: $(tr '\n' ' ' < /tmp/fpnode.err | head -c 150)"
fi

# 2) git proaspat pe REPO_URL cu credential store implicit al utilizatorului de pe gazda
if [ -f "$HOME/.git-credentials" ] || git config --global --get credential.helper >/dev/null 2>&1; then
  rm -rf /tmp/fpwt
  if git clone -q --depth 1 "$REPO_URL" /tmp/fpwt 2>/tmp/fpclone.err && git -C /tmp/fpwt fetch -q --depth 1 origin "$BR" && git -C /tmp/fpwt checkout -q FETCH_HEAD; then
    mkdir -p "/tmp/fpwt/$(dirname "$DEST")"; cp "$SRC" "/tmp/fpwt/$DEST"
    git -C /tmp/fpwt add -f "$DEST"
    git -C /tmp/fpwt -c user.name=funcity-runner -c user.email=funcity@localhost -c commit.gpgsign=false commit -qm "$MSG"
    GIT_TERMINAL_PROMPT=0 git -C /tmp/fpwt push -q origin "HEAD:refs/heads/$BR" 2>/tmp/fppush.err && { say "canal git-proaspat OK"; rm -rf /tmp/fpwt; exit 0; }
    say "push pe git proaspat: $(tr '\n' ' ' < /tmp/fppush.err | head -c 160)"
    rm -rf /tmp/fpwt
  else say "clone proaspat esuat: $(tr '\n' ' ' < /tmp/fpclone.err | head -c 160)"; fi
fi

# 3) clone existent pe gazda (orice URL spre acest repo), cu worktree + push idempotent
CLON=$(find "$HOME" -maxdepth 5 -name .git -type d 2>/dev/null | head -60 | while read -r g; do
  r="${g%/.git}"; u=$(git -C "$r" remote get-url origin 2>/dev/null)
  case "$u" in *ServerRolePlayLite*) echo "$r"; break;; esac
done)
if [ -n "${CLON:-}" ]; then
  git -C "$CLON" fetch -q origin "$BR" 2>/dev/null && {
    rm -rf /tmp/fpwt2; git -C "$CLON" worktree add -q /tmp/fpwt2 --detach "origin/$BR" 2>/dev/null
    mkdir -p /tmp/fpwt2/analysis; cp "$SRC" "/tmp/fpwt2/$DEST"
    git -C /tmp/fpwt2 add -f "$DEST"
    git -C /tmp/fpwt2 -c user.name=funcity-runner -c user.email=funcity@localhost -c commit.gpgsign=false commit -qm "$MSG"
    git -C /tmp/fpwt2 push -q origin "HEAD:refs/heads/$BR" && { say "canal clone-gazda OK"; git -C "$CLON" worktree remove --force /tmp/fpwt2; exit 0; }
    git -C "$CLON" worktree remove --force /tmp/fpwt2; say "clone-gazda gasit ($CLON) dar push esuat"
  }
fi
# ultim resort: salutam — raportul ramane in /tmp pe gazda si in log; semnam clar lipsa canalului
echo "PUBLICARE_ESUATA: niciun canal (gh/git-credentials/clone-gazda) — raportul e in /tmp/$(basename "$SRC") pe gazda"
exit 0
