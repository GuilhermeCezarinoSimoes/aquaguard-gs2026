@echo off
chcp 65001 >nul
set PYTHONIOENCODING=utf-8
title AquaGuard - Auditoria de seguranca (Cybersecurity)
set RAIZ=%~dp0..\..
cd /d "%RAIZ%\cybersecurity"
set PY=
where python >nul 2>nul && set PY=python
if not defined PY set PY=py
echo ============================================================
echo  AquaGuard - auditoria de privacidade (PII + Taint + IA)
echo  Se o servidor (B_LIGAR_SERVIDOR_API) estiver ligado, os
echo  relatos reais do app tambem sao analisados.
echo ============================================================
echo.
if not exist .venv (
  echo Preparando o ambiente pela primeira vez...
  %PY% -m venv .venv
  .venv\Scripts\python.exe -m pip install -q -r requirements.txt
)
echo.
echo --- 1) Testes automaticos ---
.venv\Scripts\python.exe -m pytest -q
echo.
echo --- 2) Auditoria completa ---
.venv\Scripts\python.exe -m aquaguard_sec --api http://localhost:5080 --saida ..\evidencias\cybersecurity
echo.
echo Abrindo o painel (dashboard) no navegador...
start "" "%RAIZ%\evidencias\cybersecurity\dashboard.html"
pause
