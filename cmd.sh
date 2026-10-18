export PATH=$PATH:/usr/bin:/bin:/usr/local/bin
cd ~/cuantic-live
echo "java: $(pgrep -f 'FunCity' | tr '\n' ' ')"
ls -la boot.log start.sh 2>&1 | tail -2
echo "== tail boot.log =="; tail -15 boot.log 2>&1
echo "== teste start =="
bash -n start.sh && echo "start.sh sintaxa ok"
