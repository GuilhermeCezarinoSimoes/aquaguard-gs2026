# Checklist de Entregas — AquaGuard (atualizado em 17/11/2026)

Legenda: **Pendente** · **Em desenvolvimento** · **Implementada** · **Testada** · **Evidenciada** · **Bloqueada**
"Bloqueada" = depende de ação humana (conta, login, gravação, VM) — o comando/passo exato está indicado.

## Ações que só a equipe pode fazer (em ordem de prioridade)
| # | Ação | Onde está o passo a passo | Tempo estimado |
|---|---|---|---|
| 1 | Criar repositório no GitHub e enviar o código (`git push`) | seção "Publicar" abaixo | 5 min |
| 2 | Registrar a conversa com um morador real (exigência do edital) | `docs/pesquisa_campo.md` | 30 min |
| 3 | Montar o circuito no Wokwi, salvar e copiar o link | `iot/README.md` | 20 min |
| 4 | Criar projeto no Azure DevOps, importar CSVs, adicionar professor Admin, prints → PDF | `testing/README.md` | 60 min |
| 5 | Criar VM Ubuntu e rodar `00_provisionar_tudo.sh` + `04_teste_falha.sh`, salvar saídas | `operating-systems/README.md` | 60 min |
| 6 | Gravar 6 vídeos e publicar no YouTube (não listado) | `docs/roteiros/` | 2–3 h |
| 7 | (Opcional) definir `ANTHROPIC_API_KEY` e rodar a auditoria para mostrar a IA real no vídeo | `cybersecurity/README.md` | 5 min |
| 8 | Preencher links (GitHub, YouTube, Wokwi, Azure) nos READMEs e em `iot/integrantes.txt` | busque por `<inserir` | 10 min |
| 9 | Um integrante envia cada disciplina no Teams até **19/11 23h55** | tabela abaixo | 30 min |

## SOA e Web Services — Implementada · Testada · Evidenciada
| Requisito | Pts | Arquivo | Status | Evidência / teste |
|---|---|---|---|---|
| Domínio | 3,0 | `backend/src/AquaGuard.Domain` | Testada | 33 testes de unidade do domínio |
| Banco | 3,0 | `Infrastructure/Dados` | Testada | integração SQLite |
| Migrações | 1,5 | `Dados/Migrations/*InicialAquaGuard*` | Testada | aplicada no startup e nos testes |
| Swagger | 1,5 | `/swagger`, `backend/docs/openapi.json` | Evidenciada | `evidencias/backend/02_swagger_endpoints.jpg` |
| Testes | 1,0 | `backend/tests` | Evidenciada | 47/47 — `evidencias/backend/03_dotnet_test_saida.txt` |
| README com integrantes | — | `backend/README.md` | OK | — |
**Envio:** link do GitHub. **Pendência:** publicar repositório.

## C# Software Development — Implementada · Testada · Evidenciada
POO, Web API, EF Core + LINQ, Async/Await, qualidade — mapa em `backend/README.md`. **Envio:** link do GitHub.

## Mobile Development & IoT — Implementada · Testada (web) · Evidenciada
| Requisito | Status | Evidência |
|---|---|---|
| Telas/navegação (tabs, pilha, modal, rota dinâmica) | Testada | prints `mobile/docs/prints` |
| Consumo de API | Testada | app exibindo dados reais da API; relato → ocorrência #3 |
| Banco de dados (SQLite) | Implementada | web usa localStorage; **testar no celular com Expo Go** |
| Acessibilidade | Implementada | labels/roles/live regions/contraste |
| Testes | Testada | `npm test` 5/5 · `tsc` sem erros |
| README com Ficha + prints | OK | `mobile/README.md` |
| Vídeo ≤ 3 min | **Bloqueada (gravação)** | roteiro pronto |

## IA & Machine Learning — Implementada · Testada · Evidenciada
| Requisito | Status | Evidência |
|---|---|---|
| Dados reais públicos (INMET A701 2012–2025) | OK | `ml/dados/raw`, `ml/dados/README.md` |
| Modelo justificado (Random Forest) | OK | relatório §3 |
| Preparação + divisão temporal | OK | notebook §2–3 |
| 18 combinações de 3 hiperparâmetros, TimeSeriesSplit no treino | OK | `resultados_grid_search.csv`, figuras 02–03 |
| Métricas treino × teste + gráficos + overfitting | OK | `metricas_treino_teste.csv`, figuras 04–06 |
| Conclusão para o cidadão | OK | relatório §7 |
| Notebook executado, requirements | OK | `AquaGuard_ML.ipynb` (+ `.html`) |
| Vídeo ≤ 5 min (não listado) | **Bloqueada (gravação)** | roteiro pronto |

## Cybersecurity — Implementada · Testada · Evidenciada
| Requisito | Pts | Status | Evidência |
|---|---|---|---|
| Motor PII | 3,0 | Testada | 37 testes; `pii_achados.json` |
| Taint Analysis | 3,0 | Testada | `taint_dinamico.json`, `taint_estatico.json`, `auditoria.jsonl` |
| IA na remediação | 2,0 | Implementada (offline testado) | `alertas_cidadao.json` — **rodar com chave para mostrar Claude** |
| Dashboard Risco Cidadão | 2,0 | Evidenciada | `03_print_dashboard_risco_cidadao.jpg` |
| ZIP + vídeo | — | **Bloqueada (gravação/envio)** | comando do ZIP no README |

## Physical Computing — Implementada · Testada · Salva no Wokwi
| Requisito | Status |
|---|---|
| Circuito ESP32 (`diagram.json`, `sketch.ino`) | Salvo em https://wokwi.com/projects/481041117417661441 (evidências `evidencias/iot/`) |
| Integração com a solução | Mesmas regras e mesmo payload da API (comprovado com simulador de payload) |
| `integrantes.txt` | OK com link do Wokwi (falta link do vídeo) |
| Vídeo ≤ 4 min | **Pendente (gravação)** |

## Operating Systems — Testada em VM real (18/11/2026)
| Requisito | Pts | Status |
|---|---|---|
| Provisionamento de infra (rede/DNS/IP) | 2 | Testada na VM (hostname aquaguard-srv01, DNS, UFW, auditd) |
| Provisionamento da aplicação | 2 | Testada na VM (.NET 8, publish, systemd, nginx, health 200) |
| Monitoramento com alertas CPU/disco/memória | 2 | Testada (alertas CPU 92 % e disco 90 %) |
| Monitor como serviço tolerante a falhas | 1 | Testada (SIGKILL → reiniciado) |
| Logs de auditoria | 1 | Evidenciada (`evidencias/operating-systems/01_relatorio_auditoria_vm.txt`) |
| Funcionamento completo + teste de falha | 2 | **5/5 aprovados** · falta vídeo ≤ 7 min (gravar no PC do Fabrini) |

## Testing — Cadastrada no Azure
| Requisito | Status |
|---|---|
| 7 Features com descrição e critérios de aceite | Implementada (`testing/FEATURES_E_TEST_CASES.md`, CSV) |
| 25 Test Cases (13 positivos, 12 negativos) | Implementada (CSV com passos) |
| Cadastro no Azure + PDF com prints | OK — https://dev.azure.com/Fabriniaraujo2306/AquaGuard |
| Professor como Admin | **Pendente — fazer ANTES de entregar** (conta do Fabrini) |
| Pitch 4 min | **Pendente (gravação)** — persona Dona Cida em `docs/persona_dona_cida.md` |

## GitHub
Publicado: https://github.com/GuilhermeCezarinoSimoes/aquaguard-gs2026 — falta incluir os links dos vídeos.
