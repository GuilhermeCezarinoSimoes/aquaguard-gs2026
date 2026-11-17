# Arquitetura — AquaGuard

## Componentes
| Componente | Tecnologia | Responsabilidade |
|---|---|---|
| Estação IoT | ESP32, HC-SR04, potenciômetro (pluviômetro), LCD I2C, LEDs, buzzer, botão — Wokwi | Medir nível/chuva, calcular risco localmente (funciona offline), sinalizar e enviar `POST /api/leituras` |
| API | ASP.NET Core 8, EF Core 8, SQLite, Swagger | Domínio, regras de risco, alertas, ocorrências, painel, autenticação de dispositivo |
| Painel web | HTML/JS servido pela API (`wwwroot`) | Visão da Defesa Civil; aplicação web hospedada na VM Linux |
| App | Expo SDK 58, React Native, TypeScript, Expo Router, expo-sqlite | Jornada do cidadão: situação do bairro, pontos, relato, histórico; offline-first |
| ML | Python, pandas, scikit-learn (Random Forest), dados INMET A701 | Probabilidade de chuva forte (≥ 20 mm) no dia seguinte |
| Segurança | Python (motor PII, taint dinâmico/estático, Claude API, dashboard) | Proteger dados pessoais dos relatos e medir o Risco Cidadão |
| Infra | Ubuntu, Bash, systemd, nginx, ufw, auditd | Provisionar, hospedar, monitorar e recuperar de falhas |

## Fluxo principal
1. ESP32 mede (mediana de 5 amostras) → calcula o risco local → LEDs/LCD/buzzer.
2. A cada 10 s envia `{"codigoSensor","nivelAguaCm","chuvaMmH"}` com `X-Device-Key`.
3. `LeituraServico` valida, aplica `CalculadoraRisco` (pior caso entre as regras), grava, cria/escala o alerta do bairro.
4. App e painel consultam `/api/painel`, `/api/alertas`, `/api/sensores`.
5. Cidadão relata → grava no SQLite do celular → `POST /api/ocorrencias` (sincroniza quando houver rede).

## Mesma regra em todas as pontas
As faixas de risco (60 % do nível de alerta → Atenção; nível de alerta → Alerta; nível crítico → Crítico; chuva 10/25/50 mm/h;
regra combinada) estão em `backend/src/AquaGuard.Domain/Risco/RegrasRisco.cs` e replicadas no firmware
(`iot/wokwi/sketch.ino`, `calcularRisco`) — o dispositivo alerta mesmo sem internet e a API confirma.

## Integrado × demonstrado separadamente (transparência)
| Ligação | Situação |
|---|---|
| App ⇄ API C# | **Integrado e testado** (relato criado no app gerou ocorrência #3 na API) |
| Painel web ⇄ API | **Integrado e testado** |
| ESP32 → API | Firmware pronto para HTTP(S). No Wokwi web, o simulador não alcança `localhost`; requer túnel (ngrok) ou a API na VM com IP público. Integração comprovada com `iot/simulador_payload.py`, que envia **o mesmo JSON** |
| API na VM Linux | Scripts prontos; execução na VM pendente (máquina de desenvolvimento sem Linux) |
| ML → App | **Demonstração separada**: o notebook gera o modelo (`modelo_chuva_forte.joblib`); servir a previsão no app é o próximo passo |
| Cyber → API | A auditoria lê os relatos reais da API (`GET /api/ocorrencias`); o app já bloqueia CPF/telefone/e-mail na origem. O pipeline com taint é um protótipo Python que reproduz os destinos dos dados |

## Decisões
- **SQLite** na API: zero configuração, roda igual em Windows e na VM; trocar por SQL Server/PostgreSQL é mudar o provider.
- **Alertas não são rebaixados automaticamente**: segurança primeiro — um agente encerra o alerta.
- **ProblemDetails + 422** para regra de negócio violada e **400** para payload inválido.
- **Offline-first no app**: relato é salvo antes de enviar.
- **Divisão temporal** no ML (sem embaralhar) e regra de 1 desvio-padrão para escolher o modelo menos sobreajustado.
