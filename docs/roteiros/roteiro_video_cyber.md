# Roteiro — Vídeo Cybersecurity (dashboard + taint em ação)

| Tempo | Tela | Fala |
|---|---|---|
| 0:00–0:30 | App (Relatar) | Contexto: na enchente, pessoas escrevem CPF, telefone, endereço e saúde nos relatos. |
| 0:30–1:30 | `pii.py` e `pytest -k "regras or falso"` | Motor PII: 11 regras + saúde por contexto + campos JSON; validação de dígitos (CPF/CNPJ/Luhn); ofuscação; falso positivo "protocolo 123.456.789-00" não é CPF. |
| 1:30–2:30 | `prototipo/pipeline_vulneravel.py` × `pipeline_seguro.py`; `taint.py` | Taint dinâmico (propagação em f-string/concatenação; sink bloqueia) e estático (AST aponta as linhas 23, 24, 27, 30, 31; zero na versão segura). |
| 2:30–3:15 | Terminal: `python -m aquaguard_sec --api http://localhost:5080` (com `ANTHROPIC_API_KEY` se disponível) | Execução: 11 PII, 28 vazamentos bloqueados, auditoria com hash encadeado íntegra. |
| 3:15–4:15 | `dashboard.html` | Indicador de Risco Cidadão 92 → 18; PII por categoria; alertas em linguagem simples (motor exibido); fluxos bloqueados com origem. |
| 4:15–4:45 | `llm.py` | O prompt do LLM é um sink: só recebe dado mascarado; a resposta é re-sanitizada. |
