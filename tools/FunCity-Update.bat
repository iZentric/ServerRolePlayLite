@echo off
title FunCity Update
setlocal
set "PRISM=%APPDATA%\PrismLauncher\instances"
rem F5 nu a trecut A/B FPS + login Forge. Ambele cai vechi ating profiluri de joc.
rem --lean-test amesteca 3 schimbari; --full reinstala packul si scoate culling.
if /I "%~1"=="--lean-test" goto blocked
if /I "%~1"=="--full" goto blocked
:blocked
echo OPRIT: updaterul vechi modifica moduri/config fara A/B izolat si rollback verificat.
echo Nicio modificare pe PC. Pastreaza packul existent pana la testul pe o copie.
exit /b 2
rem Codul legacy de mai jos este inaccesibil; nu il folosi fara un test izolat.
:full
cd /d "%TEMP%"
echo [1/4] Descarc FunCity de pe GitHub...
curl -fLso functity.zip "https://github.com/iZentric/ServerRolePlayLite/releases/download/funcity/FunCity-1.2.5.mrpack" || goto err
if exist unpack rmdir /s /q unpack
powershell -NoProfile -Command "Expand-Archive functity.zip unpack" || goto err
set DONE=0
for %%I in (FunCity CUANTIC-Client-1.7.7) do (
  call :UP "%%I"
  if errorlevel 1 goto err
)
if "%DONE%"=="0" echo NU AM GASIT nici o instanta FunCity/CUANTIC in %PRISM% & goto endf
echo.
echo INSTALATE: Oculus, Clumps si LazyDFU pastrate; Entity Culling si Out of Sight scoase reversibil.
echo FPS-ul in joc nu este masurat; nu pretindem ca merge pe orice PC vechi.
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
rem Preset client minimal: nu descarcam modurile de culling fara castig FPS dovedit.
rem Oculus, Clumps si LazyDFU raman obligatorii; nu atingem JAR-ul serverului.
powershell -NoProfile -Command "$ErrorActionPreference='Stop'; $i='%INST%\mods'; $d=Get-Content unpack\modrinth.index.json|ConvertFrom-Json; foreach($f in $d.files){ $u=$f.downloads[0]; $n=$f.filename; if(-not $n){$n=($u -split '/')[-1]}; $n=[uri]::UnescapeDataString($n); if($n -match '^(entityculling|out_of_sight)[-_].*\.jar$'){continue}; if(-not (Test-Path (Join-Path $i $n))){ curl.exe -fLso (Join-Path $i $n) $u; if($LASTEXITCODE -ne 0){throw ('descarcare esuata: '+$n)} } }" || exit /b 1
rem Copiile fizice din overrides sunt mutate reversibil in afara directorului mods.
powershell -NoProfile -Command "$ErrorActionPreference='Stop'; try { $m='%INST%\mods'; $b='%PRISM%\%~1\mods-render-backup'; foreach($f in @(Get-ChildItem -LiteralPath $m -File -Filter '*.jar' | Where-Object {$_.Name -match '^(entityculling|out_of_sight)[-_].*\.jar$'})){ New-Item -ItemType Directory -Path $b -Force | Out-Null; $dst=Join-Path $b $f.Name; if(Test-Path -LiteralPath $dst){if((Get-FileHash -LiteralPath $dst -Algorithm SHA256).Hash -ne (Get-FileHash -LiteralPath $f.FullName -Algorithm SHA256).Hash){throw ('backup conflict: '+$dst)}}else{Copy-Item -LiteralPath $f.FullName -Destination $dst -ErrorAction Stop}; Remove-Item -LiteralPath $f.FullName -ErrorAction Stop } } catch { Write-Error $_; exit 1 }" || exit /b 1
if exist unpack\overrides\config xcopy /diy /q unpack\overrides\config\* "%INST%\config\\" >nul
powershell -NoProfile -Command "$ErrorActionPreference='Stop'; try { $p='%INST%\config\oculus.properties'; if(Test-Path $p){$x=[IO.File]::ReadAllLines($p); if($x -contains 'enableShaders=true'){ $prev=$p+'.funcity-shader-prev'; if(-not (Test-Path $prev)){Copy-Item -LiteralPath $p -Destination $prev -ErrorAction Stop}; $x=@($x|ForEach-Object {if($_ -eq 'enableShaders=true'){'enableShaders=false'}else{$_}}); [IO.File]::WriteAllLines($p,[string[]]$x,[Text.UTF8Encoding]::new($false))}} } catch {Write-Error $_; exit 1}"
powershell -NoProfile -Command "$p='%PRISM%\%~1\instance.cfg'; if(Test-Path $p){ $c=@(Get-Content $p); $a='JavaArguments=-Xms256M -Xmx2500M -XX:+UseG1GC -XX:+ParallelRefProcEnabled'; $c=@($c|Where-Object{$_ -notmatch '^JavaArguments='}); ($c+$a)|Set-Content $p }"
for /f %%M in ('dir /b "%INST%\mods\*.jar" 2^>nul ^| find /c /v ""') do set N=%%M
echo [%~1] GATA: %N% moduri active.
exit /b 0
:lean
set DONE=0
for %%I in (FunCity CUANTIC-Client-1.7.7) do (
  call :LEANONE "%%I"
  if errorlevel 1 goto err
)
if "%DONE%"=="0" echo NU AM GASIT nicio instanta cu mods in %PRISM% & goto endf
echo CLIENT LITE: cele doua moduri de culling mutate in backup, shaders off, render-distance max 5.
echo FPS-ul in joc nu este masurat; comparatia cu/fara pe PC ramine necesara.
goto endf
:LEANONE
set "INST=%PRISM%\%~1\minecraft"
if not exist "%INST%\mods" exit /b 0
set /a DONE+=1
powershell -NoProfile -Command "$ErrorActionPreference='Stop'; try { $m='%INST%\mods'; $b='%PRISM%\%~1\mods-render-backup'; foreach($f in @(Get-ChildItem -LiteralPath $m -File -Filter '*.jar' | Where-Object {$_.Name -match '^(entityculling|out_of_sight)[-_].*\.jar$'})){ New-Item -ItemType Directory -Path $b -Force | Out-Null; $dst=Join-Path $b $f.Name; if(Test-Path -LiteralPath $dst){if((Get-FileHash -LiteralPath $dst -Algorithm SHA256).Hash -ne (Get-FileHash -LiteralPath $f.FullName -Algorithm SHA256).Hash){throw ('backup conflict: '+$dst)}}else{Copy-Item -LiteralPath $f.FullName -Destination $dst -ErrorAction Stop}; Remove-Item -LiteralPath $f.FullName -ErrorAction Stop } } catch { Write-Error $_; exit 1 }" || exit /b 1
rem Shaders off on the low-end path; Oculus itself stays installed for correct textures.
powershell -NoProfile -Command "$ErrorActionPreference='Stop'; try { $p='%INST%\config\oculus.properties'; if(Test-Path $p){$x=[IO.File]::ReadAllLines($p); if($x -contains 'enableShaders=true'){ $prev=$p+'.funcity-shader-prev'; if(-not (Test-Path $prev)){Copy-Item -LiteralPath $p -Destination $prev -ErrorAction Stop}; $x=@($x|ForEach-Object {if($_ -eq 'enableShaders=true'){'enableShaders=false'}else{$_}}); [IO.File]::WriteAllLines($p,[string[]]$x,[Text.UTF8Encoding]::new($false))}} } catch {Write-Error $_; exit 1}" || exit /b 1
rem On this server the view-distance is 5 chunks; do not render unloaded terrain.
rem Keep an even lower player setting. Back up only when a real change is made.
powershell -NoProfile -Command "$ErrorActionPreference='Stop'; try { $p='%INST%\options.txt'; if(Test-Path $p){ $x=[IO.File]::ReadAllLines($p); $changed=$false; for($j=0;$j -lt $x.Length;$j++){ if($x[$j] -match '^renderDistance:([0-9]+)$'){ if([int]$Matches[1] -gt 5){$x[$j]='renderDistance:5'; $changed=$true} } }; if($changed){ $prev=$p+'.funcity-render-prev'; if(-not (Test-Path $prev)){Copy-Item -LiteralPath $p -Destination $prev -ErrorAction Stop}; [IO.File]::WriteAllLines($p,[string[]]$x,[Text.UTF8Encoding]::new($false)) } } } catch { Write-Error $_; exit 1 }" || exit /b 1
exit /b 0
:endf
pause
exit /b 0
:err
echo ESUAT: descarcare sau backup incomplet; NU considera clientul actualizat. Copiile sunt in mods-render-backup si, la --full, in mods-backup daca existau.
pause