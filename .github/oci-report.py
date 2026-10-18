import json,base64,os,subprocess,urllib.request
tok=os.environ.get("GT") or os.environ.get("GITHUB_TOKEN")
repo=os.environ["GITHUB_REPOSITORY"]
br=os.environ["GITHUB_REF_NAME"]
try: content=open("/tmp/rep.txt","rb").read()
except Exception: content=b"(trace absent - report rula prea devreme)"
sha=None
cur=subprocess.run(["curl","-s","-H",f"Authorization: bearer {tok}",
  f"https://api.github.com/repos/{repo}/contents/diag/oci-run.txt?ref={br}"],capture_output=True,text=True).stdout
try: sha=json.loads(cur).get("sha")
except Exception: pass
body={"message":"oci trace","content":base64.b64encode(content).decode(),"branch":br}
if sha: body["sha"]=sha
req=urllib.request.Request(f"https://api.github.com/repos/{repo}/contents/diag/oci-run.txt",
  data=json.dumps(body).encode(),
  headers={"Authorization":f"bearer {tok}","Accept":"application/vnd.github+json","User-Agent":"vm"},method="PUT")
try:
  r=urllib.request.urlopen(req,timeout=30); print("report:",r.status)
except Exception as e:
  print("report FAIL",e, getattr(e,'read',lambda:b'')()[:200])
