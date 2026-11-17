# Registro de uso de IA (prompts)

O edital permite IA "como copiloto para aprender e revisar", exigindo o registro dos prompts e que **cada integrante saiba
explicar cada linha**. Usamos o **Claude Code** (Anthropic) como agente de desenvolvimento.

## Prompt 1 — 17/11/2026 (Claude Code)
**Autor:** Guilherme Cezarino Simoes
**Resumo do prompt:** "Prompt mestre" pedindo que o agente atuasse como equipe de engenharia: ler o PDF oficial completo,
extrair requisitos/rubricas, inspecionar o ambiente, montar a estrutura do repositório, planejar até 19/11 e implementar
as 8 disciplinas para a CitizenTech (proposta inicial AquaGuard — prevenção de alagamentos), com regras de não inventar
resultados, links ou evidências e não usar dados simulados no ML. Complemento: "quero que você faça tudo e deixe pronto
para entrega, sem me perguntar nada".

**O que a IA produziu (revisar e entender antes da entrega):**
| Parte | Artefatos | Como verificar |
|---|---|---|
| Requisitos | `REQUISITOS_GS.md`, `CHECKLIST_ENTREGAS.md`, `PLANO_EXECUCAO.md` | Conferir com o PDF |
| Backend | `backend/` (camadas, regras de risco, EF Core, migração, Swagger, 47 testes) | `dotnet test` |
| ML | download INMET, notebook, relatório | Reexecutar o notebook |
| IoT | `iot/wokwi/*`, simulador de payload | Simular no Wokwi |
| Mobile | `mobile/src` | `npm test`, `npx expo start` |
| Cyber | `cybersecurity/aquaguard_sec` (PII, taint, LLM, dashboard), 37 testes | `pytest`, `python -m aquaguard_sec` |
| OS | `operating-systems/scripts`, units systemd | Executar na VM |
| Testing | Features/Test Cases + CSV Azure | Importar no Azure |

**Decisões tomadas pela IA que a equipe deve validar:** escolha do AquaGuard como solução; bairro piloto Jardim Pantanal;
estação INMET A701; alvo "chuva ≥ 20 mm no dia seguinte"; Random Forest; SQLite; faixas de risco (10/25/50 mm/h e 60 %
do nível de alerta); fórmula do Indicador de Risco Cidadão.

## Uso de IA dentro do produto
- `cybersecurity/aquaguard_sec/llm.py` chama o modelo Claude (`claude-opus-5-5`, esforço baixo) para traduzir falhas
  técnicas em alertas ao cidadão. Prompt de sistema registrado na constante `SISTEMA` do arquivo. Somente dados
  mascarados são enviados.

## Próximos prompts
Registre aqui qualquer novo uso de IA (data, autor, objetivo, prompt resumido, o que foi aproveitado).
