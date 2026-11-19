# AquaGuard · Cybersecurity — Módulo de Privacidade (PII + Taint Analysis + IA)

**Integrantes:** Guilherme Cezarino Simoes (RM 557724) · Fabrini Soares (RM 557813) · João Both (RM 558690)

O AquaGuard recebe **relatos livres de cidadãos** em situação de enchente. Na pressa, as pessoas escrevem CPF, telefone,
endereço, condição de saúde ("minha mãe é cadeirante") e até senhas. Esses textos passam por logs, feed público do app,
LLM e serviços externos. Este módulo garante que **nenhum dado pessoal vaze** e mede o risco ao cidadão.

| Missão do edital | Implementação | Arquivo |
|---|---|---|
| **01 Mapeamento de PII** (3 pts) | Motor com 11 regras + detecção de saúde por contexto + detecção por nome de campo JSON. Validação matemática (CPF/CNPJ, Luhn) contra falso positivo; normalização contra ofuscação (`5 2 9 . 9 8 2 ...`); mascaramento; nunca guarda valor bruto (só hash) | `aquaguard_sec/pii.py` |
| **02 Taint Analysis** (3 pts) | **Dinâmico**: `Contaminado(str)` propaga rótulos por concatenação, f-string, format, slicing, upper…; sinks instrumentados bloqueiam saídas inseguras. **Estático**: análise de AST encontra fluxos fonte→sink sem sanitização no código | `aquaguard_sec/taint.py` |
| **03 Tradução via IA** (2 pts) | Claude (`anthropic` SDK) traduz falhas técnicas em alertas claros. O prompt é tratado como *sink*: só recebe dados mascarados; a resposta é re-sanitizada. Sem credencial, usa tradutor offline e **informa isso** no relatório | `aquaguard_sec/llm.py` |
| **Dashboard Executivo – Risco Cidadão** (2 pts) | Indicador 0–100 (peso da categoria × exposição × alcance), antes/depois, PII por categoria, fluxos bloqueados, falhas no código | `aquaguard_sec/risco.py`, `dashboard.py` |
| Auditoria | JSON Lines com **hash encadeado** (adulteração detectável) | `aquaguard_sec/auditoria.py` |

## Executar
```bash
cd cybersecurity
python -m venv .venv && .venv/Scripts/activate     # Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
python -m pytest -v                                 # 37 testes
python -m aquaguard_sec --api http://localhost:5080 --saida ../evidencias/cybersecurity
# Com IA real: defina ANTHROPIC_API_KEY antes (o relatório mostra "motor: claude:<modelo>")
```
A auditoria lê os relatos reais da API AquaGuard (se estiver no ar) + `dados/relatos_teste.json` (**dados sintéticos**;
os CPFs/cartões são números de teste públicos, não pertencem a pessoas).

## Resultados (execução de 17/11/2026 — `../evidencias/cybersecurity/`)
- 13 relatos analisados · **11 dados pessoais** detectados (3 contato, 3 saúde, 2 credenciais, 1 CPF, 1 endereço, 1 cartão).
- Taint dinâmico: **28 fluxos** que vazariam na v1 → **28 bloqueados** na v2 (banco cifrado permitido).
- Taint estático: **5 falhas** em `prototipo/pipeline_vulneravel.py` (linhas 23, 24, 27, 30, 31) e **0** em `pipeline_seguro.py`.
- **Indicador de Risco Cidadão: 92 (Crítico) → 18 (Baixo).**
- Auditoria: 54 registros, cadeia de hashes íntegra.
- Tradução: executada no modo **offline** (sem chave de API neste computador). Para demonstrar a IA no vídeo, defina
  `ANTHROPIC_API_KEY` e rode novamente.

## Entrega (ZIP)
```bash
# na raiz do repositório
powershell Compress-Archive -Path cybersecurity\aquaguard_sec,cybersecurity\prototipo,cybersecurity\dados,cybersecurity\tests,cybersecurity\README.md,cybersecurity\requirements.txt,evidencias\cybersecurity -DestinationPath entrega_cybersecurity.zip
```
Inclua também o vídeo (roteiro: `../docs/roteiros/roteiro_video_cyber.md`) e o print do dashboard
(`../evidencias/cybersecurity/03_print_dashboard_risco_cidadao.jpg`).
