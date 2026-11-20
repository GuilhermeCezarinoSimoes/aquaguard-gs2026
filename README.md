# AquaGuard — CitizenTech de prevenção de alagamentos

**FIAP · Global Solution 2026.2 · Desafio CitizenTech · Engenharia de Software — 3º ano**

**Integrantes**
1. Guilherme Cezarino Simoes - RM 557724
2. Fabrini Soares - RM 557813
3. João Both - RM 558690

---

## Ficha da CitizenTech
| | |
|---|---|
| **Nome da CitizenTech** | AquaGuard |
| **Cidade e bairro** | São Paulo (SP) — Jardim Pantanal, Zona Leste (piloto), com pontos também em Aricanduva, Ipiranga e Pacaembu |
| **Cidadão beneficiado** | Moradores de áreas que alagam com frequência — famílias, idosos, pessoas com deficiência — e quem passa diariamente por essas ruas |
| **Problema, em uma frase** | Quem mora perto de córregos de São Paulo só percebe a enchente quando a água já está na porta, sem tempo de proteger a família e os bens. |
| **Como funciona** | Um sensor ESP32 no córrego mede a água e a chuva e alerta no local; a API calcula o risco e emite o alerta do bairro; o app mostra a situação e o que fazer e recebe relatos dos moradores; um modelo de ML com dados reais do INMET avisa na véspera quando há chance de chuva forte. |
| **O que cada parte faz** | **IoT** mede e sinaliza no local · **API C#** aplica as regras, guarda os dados e emite alertas · **App** informa e recebe relatos · **ML** antecipa chuva forte · **Cybersecurity** protege dados pessoais dos relatos · **Linux** hospeda, monitora e se recupera de falhas · **Testing** define e valida as funcionalidades |
| **Link do repositório** | [https://github.com/GuilhermeCezarinoSimoes/aquaguard-gs2026](https://github.com/GuilhermeCezarinoSimoes/aquaguard-gs2026) |
| **Indicador de impacto** | Antecedência do aviso (véspera pelo ML; minutos pelo sensor); % de chuvas fortes avisadas na véspera (**69 %** no teste 2023–2025); nº de relatos resolvidos; tempo entre alerta e resposta da Defesa Civil |
| **ODS conectados** | **11** Cidades e comunidades sustentáveis (meta 11.5: reduzir mortes e perdas por desastres, incluindo os relacionados à água) · **13** Ação contra a mudança do clima (13.1: resiliência a riscos climáticos) · **3** Saúde e bem-estar (prevenção de afogamentos e leptospirose) · **10** Redução das desigualdades (as periferias são as mais atingidas) · **9** Infraestrutura resiliente (monitoramento de baixo custo) |

### Seis perguntas do briefing
1. **Quem é o cidadão?** O morador de áreas baixas próximas a córregos — no Jardim Pantanal, várias ruas ficam na várzea do Tietê.
2. **Qual problema?** Falta de aviso antecipado e localizado: o alerta geral da cidade não diz se *a sua rua* vai alagar.
3. **Como funciona?** Sensor + regras de risco + alerta no app + relato colaborativo + previsão de véspera (ver diagrama).
4. **Tecnologias?** ESP32 (Wokwi), C#/.NET 8 + EF Core + SQLite, React Native/Expo, Python (scikit-learn), Linux (Bash/systemd/nginx), Claude API.
5. **Ecossistema?** Moradores e associações de bairro (relatos), Defesa Civil/CGE (alertas e atendimento), subprefeitura (zeladoria de bueiros), escolas e UBS (pontos de apoio).
6. **Impacto medido e ampliado?** Indicadores acima; ampliar com sensores de baixo custo em cada córrego crítico e integração com estações CEMADEN/CGE.

---

## Arquitetura
```
  ESP32 (Wokwi)                 ┌──────────────── VM Linux (nginx + systemd + monitor) ───────────────┐
  HC-SR04 + pluviômetro ─HTTP──►│ API C# .NET 8 ──EF Core──► SQLite                                    │
  LEDs/LCD/buzzer (offline)     │   ├─ /api/leituras → risco → alerta do bairro                         │
                                │   ├─ /api/ocorrencias  ◄──── App Expo (SQLite local, offline-first)   │
                                │   └─ painel web + Swagger                                              │
                                └──────────────────────────────────────────────────────────────────────┘
  INMET A701 (2012–2025) ──► Notebook ML (Random Forest) ──► "chance de chuva forte amanhã"
  Relatos/payloads ──► Módulo Cyber (PII + Taint + IA) ──► Dashboard Risco Cidadão
```
Detalhes e o que está integrado × demonstrado separadamente: [ARQUITETURA.md](ARQUITETURA.md).

## Guia para os professores — onde avaliar cada disciplina
Cada disciplina tem uma pasta com README próprio. Os vídeos (YouTube, não listados) foram enviados no Teams de cada disciplina.

| Disciplina | Pasta | Comece por |
|---|---|---|
| SOA e Web Services | [`backend/`](backend) | [backend/README.md](backend/README.md) — seção "Mapa dos critérios" (SOA) |
| C# Software Development | [`backend/`](backend) | [backend/README.md](backend/README.md) — seção "Mapa dos critérios" (C#) |
| Mobile Development & IoT | [`mobile/`](mobile) | [mobile/README.md](mobile/README.md) · [vídeo](https://youtu.be/iYA2yNLnnn8) |
| IA & Machine Learning | [`ml/`](ml) | [ml/AquaGuard_ML.ipynb](ml/AquaGuard_ML.ipynb) e [ml/RELATORIO_ML.md](ml/RELATORIO_ML.md) |
| Cybersecurity | [`cybersecurity/`](cybersecurity) | [cybersecurity/README.md](cybersecurity/README.md) |
| Physical Computing: IoT & IoB | [`iot/`](iot) | [iot/README.md](iot/README.md) · [Wokwi](https://wokwi.com/projects/481041117417661441) · [vídeo](https://youtu.be/l-SpJSgWnFc) |
| Operating Systems | [`operating-systems/`](operating-systems) | [operating-systems/README.md](operating-systems/README.md) |
| Testing, Compliance & QA | [`testing/`](testing) | [testing/FEATURES_E_TEST_CASES.md](testing/FEATURES_E_TEST_CASES.md) · [Azure DevOps](https://dev.azure.com/Fabriniaraujo2306/AquaGuard) |

### SOA e Web Services
| Critério | Onde está |
|---|---|
| Estruturação do domínio | [`backend/src/AquaGuard.Domain`](backend/src/AquaGuard.Domain) — entidades, value objects, regras de risco |
| Conexão com banco | [`backend/src/AquaGuard.Infrastructure/Dados`](backend/src/AquaGuard.Infrastructure/Dados) — EF Core + SQLite, repositórios |
| Migrações | [`backend/src/AquaGuard.Infrastructure/Dados/Migrations`](backend/src/AquaGuard.Infrastructure/Dados/Migrations) |
| Documentação (Swagger) | `/swagger` ao executar a API · [`backend/docs/openapi.json`](backend/docs/openapi.json) · [print](evidencias/backend/02_swagger_endpoints.jpg) |
| Testes | [`backend/tests`](backend/tests) — 47 testes · [saída](evidencias/backend/03_dotnet_test_saida.txt) |

### C# Software Development
| Critério | Onde está |
|---|---|
| POO | [`backend/src/AquaGuard.Domain`](backend/src/AquaGuard.Domain) — herança, polimorfismo (`Risco/RegrasRisco.cs`), encapsulamento |
| Web API | [`backend/src/AquaGuard.Api/Controllers`](backend/src/AquaGuard.Api/Controllers) |
| EF Core + LINQ | [`backend/src/AquaGuard.Infrastructure`](backend/src/AquaGuard.Infrastructure) — `Repositorios/`, `Consultas/PainelConsultas.cs` |
| Async/Await | Toda a pilha: controllers → [`Servicos.cs`](backend/src/AquaGuard.Application/Servicos/Servicos.cs) → repositórios |
| Qualidade | Camadas + DI, tratamento global de erros ([`TratadorExcecoes.cs`](backend/src/AquaGuard.Api/Infra/TratadorExcecoes.cs)), 47 testes |

### Mobile Development & IoT
| Critério | Onde está |
|---|---|
| Telas e navegação | [`mobile/src/app`](mobile/src/app) — abas, pilha, rota dinâmica `sensor/[id]`, modal `bairro` |
| Consumo de API | [`mobile/src/lib/api.ts`](mobile/src/lib/api.ts), [`servicos.ts`](mobile/src/lib/servicos.ts) |
| Banco de dados local (SQLite) | [`mobile/src/db/database.ts`](mobile/src/db/database.ts) |
| Acessibilidade | [`mobile/src/ui`](mobile/src/ui) — rótulos, papéis, contraste, cor + ícone + texto |
| Testes e prints | [`mobile/tests`](mobile/tests) · [`mobile/docs/prints`](mobile/docs/prints) |

### IA & Machine Learning
| Critério | Onde está |
|---|---|
| Dados reais e públicos (INMET A701, 2012–2025) | [`ml/dados/README.md`](ml/dados/README.md) · `ml/dados/raw/` |
| Modelo, preparação e divisão temporal | [`ml/AquaGuard_ML.ipynb`](ml/AquaGuard_ML.ipynb) (executado; versão [HTML](ml/AquaGuard_ML.html)) |
| Hiperparâmetros (18 combinações) | [`ml/resultados_grid_search.csv`](ml/resultados_grid_search.csv) · [`ml/figuras`](ml/figuras) |
| Métricas treino × teste e overfitting | [`ml/metricas_treino_teste.csv`](ml/metricas_treino_teste.csv) · figuras 04–06 |
| Relatório e conclusão para o cidadão | [`ml/RELATORIO_ML.md`](ml/RELATORIO_ML.md) |

### Cybersecurity
| Critério | Onde está |
|---|---|
| Motor de PII | [`cybersecurity/aquaguard_sec/pii.py`](cybersecurity/aquaguard_sec/pii.py) |
| Taint Analysis | [`taint.py`](cybersecurity/aquaguard_sec/taint.py) · [`prototipo/`](cybersecurity/prototipo) (versão vulnerável × segura) |
| IA na remediação | [`llm.py`](cybersecurity/aquaguard_sec/llm.py) |
| Dashboard Risco Cidadão | [`dashboard.py`](cybersecurity/aquaguard_sec/dashboard.py) · [dashboard gerado](evidencias/cybersecurity/dashboard.html) · [print](evidencias/cybersecurity/03_print_dashboard_risco_cidadao.jpg) |
| Testes e evidências | [`cybersecurity/tests`](cybersecurity/tests) — 37 testes · [`evidencias/cybersecurity`](evidencias/cybersecurity) |

### Physical Computing: IoT & IoB
| Critério | Onde está |
|---|---|
| Circuito ESP32 | [Projeto no Wokwi](https://wokwi.com/projects/481041117417661441) · [`iot/wokwi/sketch.ino`](iot/wokwi/sketch.ino) · [`diagram.json`](iot/wokwi/diagram.json) |
| Integração com a solução | Mesmo JSON enviado para `POST /api/leituras` · [`iot/simulador_payload.py`](iot/simulador_payload.py) · [evidência](evidencias/backend/04_integracao_payload_esp32.txt) |
| Integrantes e links | [`iot/integrantes.txt`](iot/integrantes.txt) |
| Prints | [`evidencias/iot`](evidencias/iot) |

### Operating Systems
| Critério | Onde está |
|---|---|
| Provisionamento de infraestrutura (rede/DNS/IP) | [`01_provisionar_infra.sh`](operating-systems/scripts/01_provisionar_infra.sh) |
| Provisionamento da aplicação | [`02_provisionar_app.sh`](operating-systems/scripts/02_provisionar_app.sh) · [`systemd/aquaguard-api.service`](operating-systems/systemd/aquaguard-api.service) |
| Monitoramento (CPU/disco/memória) | [`03_monitor.sh`](operating-systems/scripts/03_monitor.sh) |
| Monitor como serviço tolerante a falhas | [`systemd/aquaguard-monitor.service`](operating-systems/systemd/aquaguard-monitor.service) |
| Logs de auditoria | [`lib/comum.sh`](operating-systems/scripts/lib/comum.sh) · [`05_relatorio_auditoria.sh`](operating-systems/scripts/05_relatorio_auditoria.sh) |
| Funcionamento completo e teste de falha | [`00_provisionar_tudo.sh`](operating-systems/scripts/00_provisionar_tudo.sh) · [`04_teste_falha.sh`](operating-systems/scripts/04_teste_falha.sh) · [relatório da VM](evidencias/operating-systems/01_relatorio_auditoria_vm.txt) · [5/5 aprovados](evidencias/operating-systems/02_teste_falha_5_aprovados.log) · [prints](evidencias/operating-systems) · [vídeo](https://youtu.be/FTKr15VJtFg) |

### Testing, Compliance & QA
| Critério | Onde está |
|---|---|
| Features com descrição e critérios de aceite (7) | [`testing/FEATURES_E_TEST_CASES.md`](testing/FEATURES_E_TEST_CASES.md) · [Azure Boards](https://dev.azure.com/Fabriniaraujo2306/AquaGuard) |
| Test Cases positivos e negativos (25) | mesmo arquivo · CSVs importados no Azure ([features](testing/azure_import_features.csv), [test cases](testing/azure_import_test_cases.csv)) |
| PDF com prints do Azure e pitch | enviados no Teams da disciplina |

Arquitetura e integrações: [ARQUITETURA.md](ARQUITETURA.md) · Persona usada no pitch: [docs/persona_dona_cida.md](docs/persona_dona_cida.md) ·
Uso de IA (exigido pelo edital): [prompts.md](prompts.md)

## Início rápido (demonstração integrada no computador)
```bash
# 1. API + painel web
cd backend && dotnet run --project src/AquaGuard.Api --launch-profile http     # http://localhost:5080
# 2. Simular uma enchente com o mesmo payload do ESP32
python iot/simulador_payload.py --cenario enchente
# 3. App
cd mobile && npm install && npx expo start
# 4. Auditoria de privacidade
cd cybersecurity && python -m aquaguard_sec
```

## Dados
Nenhum dado pessoal real. Dados meteorológicos **reais e públicos** do INMET (ML); pontos de monitoramento em locais reais
de São Paulo com dispositivos **simulados**; relatos de teste **sintéticos** (identificados como tal).
