@echo off
title AquaGuard - Zerar dados de demonstracao
rem Apaga o banco de DEMONSTRACAO para comecar a gravacao do zero (tudo "Normal").
rem Ele e recriado automaticamente na proxima vez que o servidor ligar.
set RAIZ=%~dp0..\..
echo Feche ANTES a janela do servidor (B_LIGAR_SERVIDOR_API).
pause
del /q "%RAIZ%\backend\src\AquaGuard.Api\aquaguard.db*" 2>nul
echo Pronto. Ligue o servidor de novo com B_LIGAR_SERVIDOR_API.
pause
