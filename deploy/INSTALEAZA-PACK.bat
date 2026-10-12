@echo off
title Palma Lite RP - Instalator
echo ============================================
echo   PALMA LITE RP - pack pentru orice PC
echo ============================================
echo.
echo Descarc pack-ul (1-2 minute)...
powershell -Command "$ProgressPreference='SilentlyContinue'; $r=Invoke-RestMethod 'https://api.github.com/repos/iZentric/ServerRolePlayLite/releases/tags/lite'; $a=$r.assets | Where-Object { $_.name -like '*Client*.mrpack' }; Invoke-WebRequest $a.browser_download_url -OutFile \"$env:USERPROFILE\Desktop\PalmaLiteRP.mrpack\""
if exist "%USERPROFILE%\Desktop\PalmaLiteRP.mrpack" (
  echo.
  echo GATA! Pack-ul e pe Desktop: PalmaLiteRP.mrpack
  echo.
  echo CUM IL INSTALEZI (o singura data):
  echo  1. Descarca launcherul Prism: https://prismlauncher.org/download
  echo  2. Deschide Prism - Add Instance - Import - alege PalmaLiteRP.mrpack
  echo  3. Apasa Launch si intra pe server!
  echo.
  start "" "https://prismlauncher.org/download/"
) else (
  echo EROARE la descarcare - verifica internetul si incearca iar.
)
pause
