@echo off
title AquaGuard - SERVIDOR (API) - deixe esta janela aberta
set RAIZ=%~dp0..\..
cd /d "%RAIZ%\backend\src\AquaGuard.Api"
echo ============================================================
echo  AquaGuard - ligando o servidor (API)
echo.
echo  NAO FECHE ESTA JANELA enquanto estiver usando o app/painel.
echo  Para desligar: feche a janela ou aperte Ctrl+C.
echo.
echo  Se o Windows perguntar sobre o Firewall, clique em PERMITIR.
echo  Em alguns segundos o navegador abre o painel.
echo ============================================================
echo.
start "" /min cmd /c "timeout /t 25 /nobreak >nul & start http://localhost:5080 & start http://localhost:5080/swagger"
dotnet run --launch-profile http --no-launch-browser
echo.
echo O servidor parou. Se apareceu erro em vermelho acima, veja "Deu erro?" no PASSO_A_PASSO.
pause
