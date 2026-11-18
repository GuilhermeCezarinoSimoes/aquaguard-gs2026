@echo off
title AquaGuard - Verificar programas instalados
echo ============================================================
echo  AquaGuard - verificando se os programas estao instalados
echo ============================================================
echo.
set FALTA=0

where dotnet >nul 2>nul
if errorlevel 1 (
  echo [FALTA] .NET 8 SDK  -  baixe em https://dotnet.microsoft.com/download/dotnet/8.0
  set FALTA=1
) else (
  dotnet --list-sdks | findstr /b "8." >nul
  if errorlevel 1 (
    echo [FALTA] .NET 8 SDK ^(existe outro .NET, mas precisa do 8^)  -  https://dotnet.microsoft.com/download/dotnet/8.0
    set FALTA=1
  ) else (
    echo [OK]    .NET 8 SDK
  )
)

where node >nul 2>nul
if errorlevel 1 (
  echo [FALTA] Node.js  -  baixe a versao LTS em https://nodejs.org
  set FALTA=1
) else (
  for /f %%v in ('node --version') do echo [OK]    Node.js %%v
)

set PY=
where python >nul 2>nul && set PY=python
if not defined PY where py >nul 2>nul && set PY=py
if not defined PY (
  echo [FALTA] Python 3  -  baixe em https://www.python.org/downloads  ^(marque "Add python.exe to PATH"^)
  set FALTA=1
) else (
  for /f "tokens=*" %%v in ('%PY% --version') do echo [OK]    %%v
)

echo.
if "%FALTA%"=="1" (
  echo Instale o que esta como FALTA, FECHE esta janela e rode de novo.
) else (
  echo Tudo certo! Pode seguir para o proximo passo.
)
echo.
pause
