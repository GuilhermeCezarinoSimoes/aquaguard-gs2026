@echo off
title AquaGuard - Gerar ZIP de Cybersecurity
set RAIZ=%~dp0..\..
cd /d "%RAIZ%"
set DESTINO=%RAIZ%\ENTREGAS_POR_DISCIPLINA\05_Cybersecurity\entrega_cybersecurity_AquaGuard.zip
if exist "%DESTINO%" del "%DESTINO%"
powershell -NoProfile -Command "Compress-Archive -Path 'cybersecurity\aquaguard_sec','cybersecurity\prototipo','cybersecurity\dados','cybersecurity\tests','cybersecurity\README.md','cybersecurity\requirements.txt','evidencias\cybersecurity' -DestinationPath '%DESTINO%'"
if exist "%DESTINO%" (
  echo ZIP criado em:
  echo   %DESTINO%
  explorer /select,"%DESTINO%"
) else (
  echo Nao foi possivel criar o ZIP.
)
pause
