# Roteiro — Vídeo Mobile (máx. 3:00)

Preparação: API rodando (`dotnet run`), `python iot/simulador_payload.py --cenario enchente --sensor AQG-001` pronto
para executar; app aberto no celular (Expo Go) ou no navegador em modo celular. Ative o leitor de tela por alguns segundos.

| Tempo | Tela | Fala |
|---|---|---|
| 0:00–0:20 | README (Ficha) | Quem é o cidadão, o problema e a jornada principal. |
| 0:20–0:50 | Início | Escolher o bairro (modal, salvo no SQLite). Rodar o simulador → puxar para atualizar → cartão muda para "Perigo" com orientações. |
| 0:50–1:20 | Pontos → Detalhe | Lista com barra de nível e marcas de alerta/perigo; detalhe com gráfico das leituras vindas da API (rota `sensor/[id]`). |
| 1:20–2:00 | Relatar | Tentar enviar com CPF → bloqueio (LGPD). Corrigir, enviar → "Meus relatos" com protocolo da API. |
| 2:00–2:30 | Offline | Parar a API → aviso de dados salvos; criar relato → "Aguardando conexão"; religar → "Enviar pendentes". |
| 2:30–3:00 | Código | Estrutura `src/app` (Expo Router), `lib/api.ts`, `db/database.ts` (SQLite), acessibilidade (rótulos, live region, contraste). |
