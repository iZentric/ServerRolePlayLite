# HARTA PAGINI (Thu Oct  8 18:14:08 UTC 2026)

## ws/wss/socket

## /api/ paths (toate)
"/api/auth/login"
"/api/auth/login/email-code/request"
"/api/auth/login/email-code/verify"
"/api/auth/oauth/discord"
"/api/auth/oauth/github"
"/api/auth/oauth/google"
"/api/auth/passkey/login/begin"
"/api/auth/passkey/login/finish"
"/api/auth/recover-password/request"
"/api/auth/recover-password/reset"

## power/stop/restart context
"u">typeof AbortController?AbortController:function(){var e=[],t=this.signal={aborted:!1,addEventListener:function(t,n){e.push(n)}};this.abort=fun
),t.data.set(e,n)),n},cacheSignal:function(){return lt(li).controller.signal}},uk="function"==typeof WeakMap?WeakMap:Map,uS=0,uE=null,ux=null,u_=0
,0,t&&t.temporaryReferences?t.temporaryReferences:void 0,r,n);if(t&&t.signal){var l=t.signal;if(l.aborted)a(l.reason);else{var u=function(){a(l.re
let y=fetch(h,{credentials:"same-origin",headers:t,priority:r||void 0,signal:l}),v=a?(u=y,c=t,g(u,{callServer:i.callServer,findSourceMapURL:s.find
headers=new tb(t.headers)),this.method=t.method,this.mode=t.mode,this.signal=t.signal,r||null==t._bodyInit||(r=t._bodyInit,t.bodyUsed=!0)}else thi
(e.method||this.method||"GET"),this.mode=e.mode||this.mode||null,this.signal=e.signal||this.signal,this.referrer=null,("GET"===this.method||"HEAD"
ction hb(t,e){return new Promise(function(r,n){var o=new ub(t,e);if(o.signal&&o.signal.aborted)return n(new lb("Aborted","AbortError"));var i=new 
e="blob"),o.headers.forEach(function(t,e){i.setRequestHeader(e,t)}),o.signal&&(o.signal.addEventListener("abort",a),i.onreadystatechange=function(
setTimeout(()=>e.abort(),t),n=await fetch(a,{method:"GET",mode:"cors",signal:e.signal,cache:"no-cache"});clearTimeout(o);let s=performance.now()-r
3));return await fetch(e+"/favicon.ico",{method:"HEAD",mode:"no-cors",signal:a.signal,cache:"no-cache"}),clearTimeout(r),!1}catch{return!0}}),s=(o
syncDynamicErrorWithStack=r)}function S(e,t,r,n){if(!1===n.controller.signal.aborted){w(e,t,n);let a=n.dynamicTracking;a&&null===a.syncDynamicErro
,"__NEXT_ERROR_CODE",{value:"E721",enumerable:!1,configurable:!0})),e.signal}function $(e){switch(e.type){case"prerender":case"prerender-runtime":
ick)(()=>t.abort())):(0,h.scheduleOnNextTick)(()=>t.abort())}return t.signal;case"prerender-client":case"prerender-ppr":case"prerender-legacy":cas
troller.abort(e)}let e=new AbortController;return this.controller=e,e.signal}cancelCeremony(){if(this.controller){let e=Error("Manually cancelling
dentials?.map(i)},y={};g&&(y.mediation="conditional"),y.publicKey=x,y.signal=l.createNewAbortSignal();try{a=await navigator.credentials.create(y)}
 missing required publicKey property");if("AbortError"===e.name){if(t.signal instanceof AbortSignal)return new o({message:"Registration ceremony w
ted');x.mediation="conditional",g.allowCredentials=[]}x.publicKey=g,x.signal=l.createNewAbortSignal();try{c=await navigator.credentials.get(x)}cat
 missing required publicKey property");if("AbortError"===e.name){if(t.signal instanceof AbortSignal)return new o({message:"Authentication ceremony

## header/auth in fetch
BustingSearchParam)(h,t);let y=fetch(h,{credentials:"same-origin",headers:t,priority:r||voi
ror("Already read");this.url=t.url,this.credentials=t.credentials,e.headers||(this.headers=
sed=!0)}else this.url=String(t);if(this.credentials=e.credentials||this.credentials||"same-
i.open(o.method,o.url,!0),"include"===o.credentials?i.withCredentials=!0:"omit"===o.credent
rn"font"===e?"":"string"==typeof t?"use-credentials"===t?t:"":void 0}r.__DOM_INTERNALS_DO_N
?"string"==typeof(t=t.crossOrigin)?"use-credentials"===t?t:"":void 0:null,i.d.C(e,t))},r.pr
eNewAbortSignal();try{a=await navigator.credentials.create(y)}catch(e){throw function({erro
=!0)return new o({message:"Discoverable credentials were required but no available authenti
eNewAbortSignal();try{c=await navigator.credentials.get(x)}catch(e){throw function({error:e
o_device_id";function r(){let e;return{"x-device-id":((e=localStorage.getItem(t))||(e="x
c.CardDescription,{children:"Enter your credentials to access your account"})]}),(0,r.jsxs)
