# Matriz de Requisitos — GS CitizenTech 2026.2 (Engenharia de Software, 3º ano Fev)

Fonte: PDF oficial "GS CitizenTech - 3ES Fev - FIAP 2026" (40 páginas, lido integralmente em 17/11/2026).
Orientações adicionais dos professores **não foram recebidas**; quando chegarem, esta matriz deve ser confrontada com elas
(ex.: a rubrica completa de Mobile "está na tarefa" do Teams e não consta no PDF).

## 1. Regras gerais (p. 17–24)
| # | Requisito | Atendimento |
|---|---|---|
| G1 | Prazo: **19/11/2026 às 23h55**, via Teams ou Portal do aluno, na tarefa de cada disciplina (20/11 é feriado) | Plano em `PLANO_EXECUCAO.md` |
| G2 | Equipe de até 5 alunos da mesma turma; **mesma equipe e mesma CitizenTech em todas as disciplinas** | AquaGuard em todas |
| G3 | **Somente um integrante** envia cada disciplina | Definir quem envia (checklist) |
| G4 | Nota 0–10 por disciplina | — |
| G5 | **Pitch**: vídeo de até **4 min no YouTube**, enviado na disciplina de **Testing** (prêmio Melhor GS) | Roteiro `docs/roteiros/roteiro_pitch.md` |
| G6 | Problema real de uma cidade, com **uma pessoa real que convive com ele** | `docs/pesquisa_campo.md` (a equipe deve preencher com a conversa real) |
| G7 | Protótipo que funciona; partes das disciplinas se encaixam na mesma ideia | `ARQUITETURA.md` |
| G8 | **Ficha da CitizenTech no início do README** (nome, cidade/bairro, cidadão, problema em 1 frase, como funciona, o que cada parte faz, link, indicador de impacto, ODS) | `README.md` |
| G9 | **Obrigatório:** identificar os **ODS** e explicar a contribuição (p. 14) | `README.md` (ODS 11, 13, 3, 10, 9) |
| G10 | Seis perguntas do briefing (p. 11) | `README.md` |
| G11 | IA como copiloto: **registrar prompts em `prompts.md`** e saber explicar cada linha | `prompts.md` |
| G12 | **Nada de dados pessoais reais**; dados simulados ou públicos, com origem | Dados INMET reais; relatos sintéticos identificados |
| G13 | Repositório organizado: README claro, uma pasta por parte | Estrutura atual |
| G14 | Solução simples, segura, inclusiva, acessível; funcionar fora de cenários ideais de conectividade (p. 9) | IoT offline, app offline-first, acessibilidade |

## 2. Disciplinas
### SOA e Web Services (p. 27) — Link do GitHub
Backend com estruturação do domínio, banco de dados, APIs REST, testes automatizados.
Entregáveis: repositório com código completo; README com execução, descrição e **nomes dos integrantes**; documentação de endpoints (Swagger); evidências.
| Critério | Pts | Onde |
|---|---|---|
| Estruturação do domínio | 3,0 | `backend/src/AquaGuard.Domain` |
| Conexão banco de dados | 3,0 | `backend/src/AquaGuard.Infrastructure` (EF Core + SQLite) |
| Migrações | 1,5 | `.../Dados/Migrations` |
| Documentação automática | 1,5 | Swagger `/swagger`, `backend/docs/openapi.json` |
| Testes automatizados | 1,0 | `backend/tests` (47) |

### Cybersecurity (p. 28–29) — Arquivo ZIP via Teams
Missão: 01 mapeamento de PII (CPF, saúde, senhas) no motor de parsing; 02 Taint Analysis (rastrear e bloquear vazamentos); 03 tradução via IA (LLM → alertas claros ao cidadão).
Entregar: código do módulo com regras PII; auditoria (evidências do taint em ação); dashboard atualizado (**vídeo** + **print** do painel gerando o indicador de Risco Cidadão).
| Critério | Pts | Onde |
|---|---|---|
| Robustez do motor de parsing PII | 3,0 | `cybersecurity/aquaguard_sec/pii.py` |
| Eficácia do Taint Analysis | 3,0 | `taint.py` (dinâmico + estático) |
| Inovação com IA na remediação | 2,0 | `llm.py` |
| Dashboard Executivo (Risco Cidadão) | 2,0 | `dashboard.py`, `risco.py` |
> Observação: o PDF não detalha qual "motor de parsing" existente deve ser atualizado. Implementamos um motor próprio. Confirmar com o professor.

### C# Software Development (p. 30) — Link do GitHub
Projeto C#, Web API, EF Core, README, documentação de endpoints (Swagger/Scalar), evidências.
| Critério | Pts |
|---|---|
| POO | 3,0 |
| Web API | 2,5 |
| EF Core + LINQ | 1,5 |
| Async/Await | 1,0 |
| Qualidade do código | 2,0 |

### Inteligência Artificial & Machine Learning (p. 31–33) — links do repositório e vídeo no Teams
Dados **reais e públicos** (INMET, Metrô, Infosiga, SP156, IBGE…); modelo XGBoost, Random Forest, MLP, LSTM ou KMeans+PCA;
≥ **10 combinações de 3 hiperparâmetros**; validação cruzada **só no treino**; métricas de treino e teste lado a lado com gráficos;
discutir overfitting; conclusão para o cidadão. **Dados simulados não são aceitos.**
Entregáveis: pasta `ml/` com notebook **executado**, `dados/README.md`, `requirements.txt`; `RELATORIO_ML.md` (2–4 páginas); vídeo ≤ 5 min no YouTube (não listado).
| Critério | Pts |
|---|---|
| Problema e dados reais | 2,0 |
| Escolha justificada do modelo | 1,0 |
| Preparação e divisão treino/teste | 2,0 |
| Treino com diferentes parâmetros | 2,0 |
| Resultados em treino e teste | 2,0 |
| Conclusão e leitura para o cidadão | 1,0 |

### Mobile Development & IoT (p. 34) — Link do GitHub
App Expo (React Native + TypeScript + Expo Router) que resolva a jornada principal; consumir API ou mock; **salvar em banco de dados**; simples e acessível.
Entregáveis: código organizado; README com **Ficha**, instruções e **prints das telas**; link do **vídeo ≤ 3 min**.
Critérios (6, pesos na tarefa do Teams): telas e navegação, consumo de dados, banco de dados, acessibilidade, aderência ao problema, documentação.

### Operating Systems (p. 35–37) — Link do GitHub
Infra Linux provisionada automaticamente (dentro da VM) para hospedar uma aplicação WEB de outra disciplina; Shell Script, processos, systemd, monitoramento.
Entregáveis: scripts Bash, configurações, evidências, README; infraestrutura funcional; scripts de monitoramento com logs; teste de falha; **vídeo ≤ 7 min** mostrando o provisionamento automatizado.
| Critério | Pts |
|---|---|
| Provisionamento de infra (redes, DNS, IP) | 2 |
| Provisionamento da aplicação (dependências, configurações, orquestração) | 2 |
| Monitoramento com alertas de CPU, disco e memória | 2 |
| Monitoramento como serviço tolerante a falhas | 1 |
| Logs de auditoria e execução dos scripts | 1 |
| Funcionamento completo | 2 |

### Physical Computing: IoT & IoB (p. 38)
Circuito ESP32 no **Wokwi** com sensores, integrado à solução (não projeto paralelo).
Entregáveis: **link do projeto Wokwi**; **link do vídeo ≤ 4 min** (apresentar a solução, como o circuito foi incorporado e o funcionamento); **arquivo .txt com os nomes dos integrantes**.

### Testing, Compliance & QA (p. 39)
Features com descrição e critérios de aceite no **Azure Boards**; Test Cases funcionais caixa-preta positivos e negativos (objetivo, preparação, inputs, outputs, passos).
Formato: incluir o professor como **Admin** no projeto; **PDF** com o link do projeto + prints de todas as telas de Features (lista e detalhe) e Test Cases.
Avaliação: Features 50 % · Test Cases 50 %. **Pitch de 4 min também é enviado aqui.**

## 3. Vídeos exigidos
| Vídeo | Limite | Disciplina |
|---|---|---|
| Pitch geral | 4 min (YouTube) | Testing |
| ML | 5 min (YouTube não listado) | IA & ML |
| Mobile | 3 min | Mobile |
| Operating Systems | 7 min | OS |
| IoT | 4 min | Physical Computing |
| Cybersecurity | sem limite definido | Cybersecurity (vídeo do dashboard) |

## 4. Divergências / dúvidas a confirmar com professores
1. Cybersecurity: "configurar novas regras no motor de parsing" sugere um motor fornecido em aula — não está no PDF.
2. Mobile: rubrica completa só na tarefa do Teams.
3. Testing: "inserir no PDF o link do projeto" — o pitch vai no mesmo envio?
4. Página 17 cita "página web, script em Python e circuito no simulador" como protótipo mínimo — atendido com folga.
