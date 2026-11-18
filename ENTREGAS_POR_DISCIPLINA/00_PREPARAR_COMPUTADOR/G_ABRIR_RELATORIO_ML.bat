@echo off
rem Abre o notebook de Machine Learning ja executado (versao para navegador) e o relatorio
set RAIZ=%~dp0..\..
start "" "%RAIZ%\ml\AquaGuard_ML.html"
start "" notepad "%RAIZ%\ml\RELATORIO_ML.md"
