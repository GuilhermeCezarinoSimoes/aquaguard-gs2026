# 05 — Cybersecurity

## O que o professor pede
Um módulo que (1) **encontra dados pessoais** (CPF, saúde, senhas…) nos textos, (2) **rastreia** para onde esses dados vão e
**bloqueia vazamentos** ("Taint Analysis"), (3) usa **IA** para explicar os problemas em linguagem simples para o cidadão, e
(4) um **painel (dashboard)** com o indicador de **Risco Cidadão**.
Entrega no Teams: **arquivo ZIP** com o código + evidências da auditoria + **vídeo** e **print** do painel.

| Critério | Pontos | Pronto? |
|---|---|---|
| Robustez do motor de PII | 3,0 | ✅ (detecta 11 tipos de dado; 37 testes) |
| Eficácia do Taint Analysis | 3,0 | ✅ (28 vazamentos bloqueados; 5 falhas achadas no código vulnerável) |
| Inovação com IA na remediação | 2,0 | ✅ (usa o Claude se houver chave; senão, modo offline — o painel mostra qual foi usado) |
| Dashboard Executivo (Risco Cidadão) | 2,0 | ✅ (92 → 18) |
| ZIP + vídeo | — | ❌ **você gera e grava** |

Print do painel já pronto: `evidencias\cybersecurity\03_print_dashboard_risco_cidadao.jpg`.

## Entendendo em 1 minuto
No AquaGuard, as pessoas escrevem relatos como "Minha mãe é cadeirante, meu CPF é …". Se isso for parar num log, no feed
público do app ou num serviço externo, é **vazamento de dado pessoal** (LGPD).
- **Motor de PII:** procura CPF (confere os dígitos, para não confundir com número de protocolo), telefone, e-mail,
  endereço, cartão, senha, chave de API e informações de saúde.
- **Taint Analysis:** "pinta" o texto que tem dado pessoal. Onde quer que ele vá (copiado, juntado com outro texto…),
  a tinta vai junto. Se tentar sair por uma "porta insegura" (log, feed, IA de terceiros), é **bloqueado**.
  Também lê o código-fonte e aponta as linhas perigosas (`prototipo\pipeline_vulneravel.py`).
- **IA:** transforma o erro técnico em aviso claro, ex.: "Com seu CPF, golpistas podem abrir contas em seu nome".
  Só manda para a IA o texto **já mascarado**.
- **Risco Cidadão (0 a 100):** soma a gravidade dos dados expostos. Sem proteção: **92 (Crítico)**; com proteção: **18 (Baixo)**.

## O que VOCÊ precisa fazer
### Passo 1 — Rodar a auditoria (3 min)
1. (Opcional, deixa mais completo) Ligue o servidor: `00_PREPARAR_COMPUTADOR\B_LIGAR_SERVIDOR_API.bat`.
2. Dois cliques em `00_PREPARAR_COMPUTADOR\E_AUDITORIA_SEGURANCA.bat`. Na 1ª vez instala o necessário (1–2 min).
   Deve aparecer **"37 passed"** e depois o resumo (PII detectadas, bloqueados, IRC antes/depois) e o painel abre no navegador.

> **Quer mostrar a IA de verdade (Claude)?** Precisa de uma chave da Anthropic (console.anthropic.com, é paga).
> Abra o `cmd`, digite `set ANTHROPIC_API_KEY=sua-chave` e, na mesma janela, arraste o `E_AUDITORIA_SEGURANCA.bat` e
> aperte Enter. O painel passará a mostrar "motor: claude…". **Sem chave também vale**: o modo offline é honesto e
> está explicado no README.

### Passo 2 — Gerar o ZIP (1 min)
Dois cliques em `00_PREPARAR_COMPUTADOR\F_GERAR_ZIP_CYBERSECURITY.bat`.
O arquivo **`entrega_cybersecurity_AquaGuard.zip`** aparece **nesta pasta** (`05_Cybersecurity`).

### Passo 3 — Gravar o vídeo (sugestão: até 5 min)
| Tempo | Mostrar | Falar |
|---|---|---|
| 0:00–0:30 | Este guia, seção "Entendendo em 1 minuto" | O problema dos dados pessoais nos relatos. |
| 0:30–1:30 | `cybersecurity\aquaguard_sec\pii.py` aberto (role a lista `REGRAS`) e `cybersecurity\dados\relatos_teste.json` | As regras de detecção; os relatos de teste são inventados. |
| 1:30–2:30 | `cybersecurity\prototipo\pipeline_vulneravel.py` (linhas com `# VULN`) e `pipeline_seguro.py` | A versão insegura e a corrigida. |
| 2:30–3:15 | Rodar `E_AUDITORIA_SEGURANCA.bat` ao vivo | 37 testes passando; 11 dados pessoais; 28 vazamentos bloqueados; auditoria íntegra. |
| 3:15–4:30 | O **dashboard** no navegador (role até o fim) | Risco 92 → 18; dados por categoria; alertas para o cidadão; tabela de bloqueios; falhas no código. |
| 4:30–5:00 | `cybersecurity\aquaguard_sec\llm.py` (início) | A IA só recebe dados mascarados e a resposta é verificada de novo. |

Publique no YouTube (Não listado).

## O que enviar no Teams
- **Anexo:** `entrega_cybersecurity_AquaGuard.zip` (desta pasta)
- **Anexo:** `evidencias\cybersecurity\03_print_dashboard_risco_cidadao.jpg` (o print do painel)
- **Texto:**
```
Global Solution 2026.2 – CitizenTech – AquaGuard – Cybersecurity
Integrantes: Guilherme Cezarino Simoes (RM 557724), Fabrini Soares (RM 557813) e João Both (RM 558690)
ZIP: código do módulo (regras PII, Taint Analysis, tradução por IA, dashboard) + evidências da auditoria
Vídeo do dashboard: https://youtu.be/XXXXXXXX
Repositório: https://github.com/GuilhermeCezarinoSimoes/aquaguard-gs2026 (pasta /cybersecurity)
Resultado: Indicador de Risco Cidadão 92 (Crítico) -> 18 (Baixo); 28 vazamentos bloqueados; 37 testes aprovados.
```

## Deu erro?
| Problema | Solução |
|---|---|
| "python não é reconhecido" | Reinstale o Python marcando "Add python.exe to PATH" e reinicie |
| Aparece "API indisponível" no meio do texto | Normal se o servidor estiver desligado; a auditoria continua com os relatos de teste |
| O ZIP não foi criado | Rode o `.bat` de novo com a pasta `05_Cybersecurity` fechada no Explorer |
