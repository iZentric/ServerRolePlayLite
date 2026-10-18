@echo off
title FunCity Update
setlocal
cd /d "%TEMP%"
set "PRISM=%APPDATA%\PrismLauncher\instances"
echo [1/4] Descarc FunCity de pe GitHub...
curl -fLso functity.zip "https://github.com/iZentric/ServerRolePlayLite/releases/download/funcity/FunCity-1.2.3.mrpack" || goto err
if exist unpack rmdir /s /q unpack
powershell -NoProfile -Command "Expand-Archive functity.zip unpack" || goto err
set DONE=0
for %%I in (FunCity CUANTIC-Client-1.7.7) do call :UP "%%I"
if "%DONE%"=="0" echo NU AM GASIT nici o instanta FunCity/CUANTIC in %PRISM% & goto endf
echo.
echo GATA: gameplay + optimizari active, cu LazyDFU si Oculus; fara Dynamic FPS.
goto endf
:UP
set "INST=%PRISM%\%~1\minecraft"
if not exist "%INST%\mods" mkdir "%INST%\mods" 2>nul
if not exist "%INST%\mods" exit /b 0
set /a DONE+=1
echo [%~1] backup (o data) + curat vechi...
if not exist "%INST%\mods-backup" xcopy /iy /q "%INST%\mods\*.jar" "%INST%\mods-backup\\" >nul
del /q "%INST%\mods\*.jar" 2>nul
xcopy /iy /q unpack\overrides\mods\*.jar "%INST%\mods\\" >nul
powershell -NoProfile -Command "$i='%INST%\mods'; $d=Get-Content unpack\modrinth.index.json|ConvertFrom-Json; foreach($f in $d.files){ $u=$f.downloads[0]; $n=$f.filename; if(-not $n){$n=($u -split '/')[-1]}; $n=[uri]::UnescapeDataString($n); if(-not (Test-Path (Join-Path $i $n))){ curl.exe -fLso (Join-Path $i $n) $u } }" 2>nul
if exist unpack\overrides\config xcopy /diy /q unpack\overrides\config\* "%INST%\config\\" >nul
powershell -NoProfile -Command "$p='%PRISM%\%~1\instance.cfg'; if(Test-Path $p){ $c=@(Get-Content $p); $a='JavaArguments=-Xms1G -Xmx2500M -XX:+UseG1GC -XX:+ParallelRefProcEnabled'; $c=@($c|Where-Object{$_ -notmatch '^JavaArguments='}); ($c+$a)|Set-Content $p }"
for /f %%M in ('dir /b "%INST%\mods\*.jar" 2^>nul ^| find /c /v ""') do set N=%%M
echo [%~1] GATA: %N% moduri active.
exit /b 0
:endf
pause
exit /b 0
:err
echo ESUAT: n-am putut descarca de pe GitHub. Verifica netul si ruleaza din nou.
pause