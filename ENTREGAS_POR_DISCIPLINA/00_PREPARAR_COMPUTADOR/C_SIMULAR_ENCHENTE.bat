@echo off
chcp 65001 >nul
set PYTHONIOENCODING=utf-8
title AquaGuard - Simular enchente (envia leituras como o sensor ESP32)
set RAIZ=%~dp0..\..
cd /d "%RAIZ%"
set PY=
where python >nul 2>nul && set PY=python
if not defined PY set PY=py
echo ============================================================
echo  Simulando uma enchente no Jardim Pantanal (sensor AQG-001).
echo  O servidor (B_LIGAR_SERVIDOR_API) precisa estar ligado.
echo  Acompanhe o app/painel mudando de Normal para PERIGO.
echo ============================================================
echo.
%PY% iot\simulador_payload.py --cenario subindo --sensor AQG-001 --intervalo 3
echo.
pause
