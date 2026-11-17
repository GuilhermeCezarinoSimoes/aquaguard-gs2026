# Roteiro — Vídeo de Machine Learning (máx. 5:00 · YouTube não listado)

| Tempo | Tela | Fala |
|---|---|---|
| 0:00–0:30 | README da Ficha | Problema do AquaGuard e a pergunta de ML: "com os dados de hoje, amanhã terá chuva forte (≥ 20 mm)?" Por que 20 mm. |
| 0:30–1:10 | `dados/README.md`, portal INMET | Dados reais: INMET A701 Mirante de Santana, 2012–2025, 122.736 registros horários; script de download reproduzível. |
| 1:10–2:00 | Notebook §1–2 | Formatos diferentes por ano, `-9999` → ausente, UTC → Brasília, horário → diário, dia só vale com ≥ 20 h medidas (97,9 % dos dias mantidos). Atributos: pressão e sua variação, umidade, acumulados de 3/7 dias, sazonalidade. Alvo e desbalanceamento (6,8 %). |
| 2:00–2:30 | Notebook §3–4 | Divisão **temporal** (treino 2012–2022, teste 2023–2025) e por que não embaralhar. Por que Random Forest (tabular, não linear, interpretável, `class_weight`). |
| 2:30–3:20 | Heatmap e gráfico de overfitting | 18 combinações × 3 hiperparâmetros, TimeSeriesSplit(5) só no treino, PR-AUC. Árvores sem limite: 1,000 no treino × 0,177 na validação = overfitting. Regra de 1 desvio-padrão → 150/4/30. |
| 3:20–4:15 | Tabela de métricas e figura 05 | Treino × teste lado a lado: ROC-AUC 0,85 / 0,79; PR-AUC 0,29 / 0,21 (aleatório 0,07); recall 69 %. Matriz de confusão. Importância: sazonalidade, chuva máxima horária, pressão. |
| 4:15–5:00 | Relatório §7 | Leitura para o cidadão: 51 de 74 chuvas fortes avisadas na véspera; ~1 em 6 avisos se confirma, por isso a mensagem é "chance elevada"; o sensor IoT confirma em tempo real. Limitações e próximos passos. |
