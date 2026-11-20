# AquaGuard · Physical Computing: IoT & IoB (ESP32 + Wokwi)

**Integrantes:** Guilherme Cezarino Simoes (RM 557724) · Fabrini Soares (RM 557813) · João Both (RM 558690) (ver [`integrantes.txt`](integrantes.txt))

## Papel do circuito na CitizenTech
O AquaGuard avisa moradores de áreas que alagam. O ESP32 é a **estação de campo** instalada sobre um córrego, galeria ou
boca de lobo (ponto AQG-001 — Córrego Três Pontes, Jardim Pantanal). Ele:

1. **Mede o nível da água** com um sensor ultrassônico HC-SR04 instalado 2 m acima do fundo (nível = 200 cm − distância).
2. **Mede a intensidade de chuva** (potenciômetro representando o pluviômetro, 0–100 mm/h).
3. **Calcula o risco no próprio dispositivo** (Normal, Atenção, Alerta, Crítico) com as **mesmas regras do backend C#** —
   continua alertando quem está na rua mesmo **sem internet** (requisito do briefing: “continuar relevante fora dos
   cenários ideais de conectividade”).
4. **Sinaliza localmente**: LEDs verde/amarelo/vermelho, LCD 16x2 (nível, chuva, risco, status Wi-Fi) e buzzer (Alerta/Crítico).
5. **Envia a leitura** (JSON) para a API AquaGuard → banco de dados → alerta do bairro → **app do cidadão**.
6. **Botão “Silenciar”** desliga o buzzer por 5 min (IoB: o agente/morador confirma que está ciente).

```
HC-SR04 + pluviômetro ─► ESP32 (regra local + LEDs/LCD/buzzer) ─HTTP POST─► API C# ─► SQLite ─► App mobile / Painel web
```

## Componentes e ligações
| Componente | Pino do componente | ESP32 |
|---|---|---|
| HC-SR04 (nível da água) | VCC / GND / TRIG / ECHO | 5V / GND / GPIO 5 / GPIO 18 |
| Potenciômetro (chuva) | VCC / GND / SIG | 3V3 / GND / GPIO 34 (ADC) |
| LCD 1602 I2C | VCC / GND / SDA / SCL | 5V / GND / GPIO 21 / GPIO 22 |
| LED verde (Normal) + 220 Ω | A / C | GPIO 25 / GND |
| LED amarelo (Atenção/Alerta) + 220 Ω | A / C | GPIO 26 / GND |
| LED vermelho (Alerta/Crítico) + 220 Ω | A / C | GPIO 27 / GND |
| Buzzer | + / − | GPIO 14 / GND |
| Botão “Silenciar” | 1 / 2 | GPIO 4 (INPUT_PULLUP) / GND |

## Regras de risco (idênticas a `backend/.../RegrasRisco.cs`)
| Nível | Água (AQG-001: alerta 80 cm, crítico 120 cm) | Chuva |
|---|---|---|
| Normal | < 48 cm | < 10 mm/h |
| Atenção | ≥ 48 cm (60 % do alerta) | ≥ 10 mm/h |
| Alerta | ≥ 80 cm, ou ≥ 48 cm com chuva ≥ 25 | ≥ 25 mm/h |
| Crítico | ≥ 120 cm, ou ≥ 80 cm com chuva ≥ 25 | ≥ 50 mm/h |

Robustez: mediana de 5 leituras (filtra ruído), detecção de falha do sensor (sem eco → não envia dado inválido),
reconexão Wi-Fi automática, contador de falhas de envio sem perder o alerta local.

## Como montar no Wokwi
1. Acesse https://wokwi.com → **New Project → ESP32**.
2. Substitua `sketch.ino` e `diagram.json` pelos arquivos de [`wokwi/`](wokwi/).
3. Em **Library Manager**, adicione **LiquidCrystal I2C** (ou adicione `libraries.txt`).
4. Clique em ▶. Durante a simulação, clique no **HC-SR04** e diminua a distância (ex.: 150 → 70 cm = 130 cm de água)
   e gire o **potenciômetro** para simular chuva. Observe LEDs, LCD, buzzer e o **Serial Monitor**.
5. **Salve** o projeto (precisa estar logado) e cole o link em `integrantes.txt`.

### Integração com a API (opcional na demo)
- O Wokwi web acessa a internet pelo Wi-Fi `Wokwi-GUEST`, mas **não alcança o `localhost`** do seu computador.
  Para enviar à API: exponha a API com um túnel (ex.: `ngrok http 5080`) e cole a URL em `API_URL`
  (`https://<seu-tunel>/api/leituras`); ou rode a API na VM Linux com IP público.
- Sem `API_URL`, o firmware funciona em **modo offline** e imprime o JSON no Serial Monitor.
- Para demonstrar a integração no computador local, [`simulador_payload.py`](simulador_payload.py) envia o **mesmo
  JSON** do ESP32 à API (evidência: `../evidencias/backend/04_integracao_payload_esp32.txt`).

## Testes do circuito (roteiro manual no Wokwi)
| # | Ação no simulador | Resultado esperado |
|---|---|---|
| 1 | Distância 180 cm, pot. no mínimo | LCD “Normal”, LED verde, sem buzzer |
| 2 | Distância 150 cm (50 cm de água) | “Atencao”, LED amarelo |
| 3 | Distância 115 cm (85 cm de água) | “Alerta”, amarelo + vermelho, bipe curto |
| 4 | Distância 75 cm (125 cm de água) | “Critico”, vermelho, bipe contínuo |
| 5 | Distância 180 cm, pot. no máximo (100 mm/h) | “Critico” por chuva |
| 6 | Em Crítico, pressionar “Silenciar” | Buzzer para; LEDs/LCD continuam |
| 7 | `API_URL` vazio | Serial mostra `[leitura] {...}` (modo offline) |
| 8 | `API_URL` válido | Serial mostra `[api] 201 risco_api=...` |

## Status de validação
- ✅ Em 17/11/2026 o `diagram.json` e o `sketch.ino` foram carregados num projeto novo do Wokwi (sem login): o diagrama
  renderizou com todas as ligações, o firmware **compilou** com a biblioteca LiquidCrystal I2C e a simulação **iniciou**
  (LCD exibiu "AquaGuard"; Serial: `[wifi] conectando..... ok 10.10.0.2` e
  `[leitura] {"codigoSensor":"AQG-001","nivelAguaCm":48.7,"chuvaMmH":0.0} risco_local=Atencao` — com o sensor a 150 cm,
  48,7 cm de água ≥ 60 % do nível de alerta = Atenção, exatamente como a API calcula).
  Print: `../evidencias/iot/01_wokwi_compilado_executando.jpg`.
- ✅ Regras de risco idênticas às do backend (cobertas pelos testes `CalculadoraRiscoTests`).
- ✅ Projeto salvo no Wokwi: https://wokwi.com/projects/481041117417661441
- ✅ Vídeo de demonstração: https://youtu.be/l-SpJSgWnFc
  (print: `../evidencias/iot/02_wokwi_projeto_salvo.jpg`).
