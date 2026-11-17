# AquaGuard — CitizenTech de prevenção de alagamentos

**FIAP · Global Solution 2026.2 · Desafio CitizenTech · Engenharia de Software — 3º ano**

**Integrantes**
1. Guilherme Cezarino Simoes
2. Fabrini Soares

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
| **Link do repositório** | _<inserir após publicar no GitHub>_ |
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

## Entregas por disciplina
| Disciplina | Pasta | Como executar | Estado |
|---|---|---|---|
| SOA e Web Services | [`backend/`](backend/README.md) | `dotnet test` · `dotnet run` | Implementada e testada |
| C# Software Development | [`backend/`](backend/README.md) | idem | Implementada e testada |
| Mobile Development & IoT | [`mobile/`](mobile/README.md) | `npx expo start` | Implementada e testada (web); falta vídeo |
| IA & Machine Learning | [`ml/`](ml/README.md) | notebook executado | Implementada e testada; falta vídeo |
| Cybersecurity | [`cybersecurity/`](cybersecurity/README.md) | `python -m aquaguard_sec` | Implementada e testada; falta vídeo/ZIP |
| Physical Computing | [`iot/`](iot/README.md) | Wokwi | Implementada; falta simular no Wokwi, link e vídeo |
| Operating Systems | [`operating-systems/`](operating-systems/README.md) | `00_provisionar_tudo.sh` na VM | Implementada; falta executar na VM e vídeo |
| Testing & QA | [`testing/`](testing/README.md) | importar CSVs no Azure | Documentada; falta cadastrar no Azure, PDF e pitch |

Situação detalhada e pendências: [CHECKLIST_ENTREGAS.md](CHECKLIST_ENTREGAS.md) · Requisitos do edital: [REQUISITOS_GS.md](REQUISITOS_GS.md) ·
Plano: [PLANO_EXECUCAO.md](PLANO_EXECUCAO.md) · Roteiros de vídeo: [`docs/roteiros/`](docs/roteiros) · Uso de IA: [prompts.md](prompts.md)

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
