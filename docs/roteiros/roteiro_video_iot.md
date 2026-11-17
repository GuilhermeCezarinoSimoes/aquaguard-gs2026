# Roteiro — Vídeo IoT / Physical Computing (máx. 4:00)

| Tempo | Tela | Fala |
|---|---|---|
| 0:00–0:40 | README do projeto | Solução AquaGuard em 30 s: problema, cidadão, app e API. "O circuito é a estação de campo da solução, não um projeto paralelo." |
| 0:40–1:20 | Wokwi — diagrama | Componentes: HC-SR04 sobre o córrego (nível = 200 cm − distância), potenciômetro = pluviômetro, LCD, LEDs, buzzer, botão Silenciar. |
| 1:20–2:40 | Wokwi — simulação | Distância 180 → Normal (verde). 150 → Atenção (amarelo). 115 → Alerta (vermelho + bipe). 75 → Crítico (bipe contínuo). Chuva no máximo → Crítico mesmo com água baixa. Botão silencia. Serial Monitor mostra o JSON enviado. |
| 2:40–3:30 | Swagger / app | Integração: o mesmo JSON chega em `POST /api/leituras` (mostrar via túnel ngrok ou com `simulador_payload.py`) → alerta do bairro → app mostra "Perigo". As regras do firmware são as mesmas da API. |
| 3:30–4:00 | — | Valor: alerta local sem internet, dado em tempo real para a Defesa Civil, baixo custo. |
