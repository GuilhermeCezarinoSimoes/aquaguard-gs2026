@echo off
title AquaGuard - APLICATIVO (Expo) - deixe esta janela aberta
set RAIZ=%~dp0..\..
cd /d "%RAIZ%\mobile"

rem Descobre o IP deste computador na rede Wi-Fi para o celular achar o servidor
rem (somente IP de rede local, ignorando VPN e adaptadores virtuais)
for /f "usebackq tokens=*" %%i in (`powershell -NoProfile -Command "Get-NetIPAddress -AddressFamily IPv4 | Where-Object { $_.IPAddress -match '^(192\.168\.|10\.|172\.(1[6-9]|2[0-9]|3[01])\.)' -and $_.AddressState -eq 'Preferred' -and $_.InterfaceAlias -notmatch 'vEthernet|VirtualBox|VMware|Loopback|WSL' } | Sort-Object { if ($_.PrefixOrigin -eq 'Dhcp') {0} else {1} } | Select-Object -First 1 -ExpandProperty IPAddress"`) do set IP=%%i
if not defined IP set IP=localhost
echo EXPO_PUBLIC_API_URL=http://%IP%:5080> .env

echo ============================================================
echo  AquaGuard - ligando o aplicativo
echo  Endereco do servidor usado pelo app: http://%IP%:5080
echo.
echo  1) O servidor (B_LIGAR_SERVIDOR_API) precisa estar ligado.
echo  2) Celular e computador na MESMA rede Wi-Fi.
echo  3) Quando aparecer o QR Code, abra o app "Expo Go" no celular
echo     e leia o QR Code (no iPhone, use a camera).
echo  4) Para abrir no navegador do computador, aperte a tecla  w
echo.
echo  NAO FECHE ESTA JANELA enquanto estiver usando o app.
echo ============================================================
echo.
if not exist node_modules (
  echo Instalando dependencias pela primeira vez ^(pode levar alguns minutos^)...
  call npm install
)
call npx expo start
pause
