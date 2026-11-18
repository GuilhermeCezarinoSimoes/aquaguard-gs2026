# 04 — Inteligência Artificial & Machine Learning

## O que o professor pede
Transformar o problema numa pergunta de IA e responder com **dados reais e públicos**. Treinar um modelo
(escolhemos **Random Forest**), testar **pelo menos 10 combinações de 3 hiperparâmetros** (fizemos 18), comparar treino e
teste com gráficos e explicar o resultado para o cidadão.
Entrega no Teams: **link do repositório** + **link do vídeo de até 5 min no YouTube (Não listado)**.

| Critério | Pontos | Pronto? |
|---|---|---|
| Problema e dados reais (INMET, 2012–2025) | 2,0 | ✅ |
| Escolha justificada do modelo | 1,0 | ✅ |
| Preparação e divisão treino/teste | 2,0 | ✅ |
| Treino com diferentes parâmetros (18 combinações) | 2,0 | ✅ |
| Resultados de treino e teste com gráficos | 2,0 | ✅ |
| Conclusão para o cidadão | 1,0 | ✅ |
| **Vídeo até 5 min** | — | ❌ **você grava** |

Tudo está em `ml\`: notebook **já executado** (`AquaGuard_ML.ipynb`, e a cópia `AquaGuard_ML.html` que abre no navegador),
relatório `RELATORIO_ML.md`, dados em `ml\dados\`, gráficos em `ml\figuras\`.
**Você NÃO precisa rodar nada** — só abrir e explicar.

## Resumo para você entender (leia antes de gravar)
- **Pergunta:** "Com o clima medido hoje, amanhã vai cair chuva forte (20 mm ou mais) em São Paulo?" 20 mm é quando os
  alagamentos começam a ser frequentes.
- **Dados:** INMET (instituto oficial de meteorologia), estação A701 – Mirante de Santana (SP), de 2012 a 2025.
  São 122.736 medições, uma por hora: chuva, pressão do ar, temperatura, umidade, vento.
- **Preparação:** juntamos as horas em dias; descartamos dias com a estação desligada; criamos informações como
  "a pressão caiu desde ontem?" e "quanto choveu nos últimos 3 dias?".
- **Divisão:** treina com 2012–2022 e **testa** com 2023–2025 (anos que o modelo nunca viu) — como prever o futuro de verdade.
- **Modelo:** Random Forest = muitas "árvores de decisão" votando. Bom para tabelas, explica quais dados importam.
- **18 combinações:** número de árvores (150 ou 400) × profundidade (4, 8 ou sem limite) × tamanho mínimo da folha (1, 10, 30).
- **Overfitting ("decoreba"):** as árvores sem limite tiraram nota máxima no treino e nota baixa na validação — decoraram.
  Escolhemos a combinação mais simples que empatava no desempenho: **150 árvores, profundidade 4, folha 30**.
- **Resultado no teste:** dos **74 dias** de chuva forte em 2023–2025, o modelo avisou na véspera **51 (69 %)**.
  ROC-AUC 0,79 (0,5 seria chute; 1,0 perfeito).
- **Para o cidadão:** "Com um dia de antecedência você fica sabendo de 7 em cada 10 chuvas fortes. O aviso é de 'chance
  elevada', porque às vezes ele erra; o sensor no córrego confirma em tempo real."

## O que VOCÊ precisa fazer
1. Dois cliques em `00_PREPARAR_COMPUTADOR\G_ABRIR_RELATORIO_ML.bat` (abre o notebook no navegador e o relatório).
2. Grave a tela seguindo o roteiro abaixo (máx. **5:00**).
3. Publique no YouTube como **Não listado**; cole o link em `ml\README.md` (onde está "LINK A PREENCHER") e envie ao GitHub.

### Roteiro do vídeo (role o notebook enquanto fala)
| Tempo | Onde rolar no notebook | Fala |
|---|---|---|
| 0:00–0:30 | Topo ("Vai cair chuva forte amanhã…") | Problema do AquaGuard e a pergunta. |
| 0:30–1:10 | Tabela "Dados reais e públicos" + abrir https://portal.inmet.gov.br/dadoshistoricos | De onde vêm os dados, período, quantidade. |
| 1:10–2:00 | Seções 1 e 2 (carga e preparação) + gráfico de sazonalidade | Limpeza, horas → dias, chuva forte é mais comum no verão, só 6,8 % dos dias. |
| 2:00–2:30 | Seções 3 e 4 | Divisão por anos e por que Random Forest. |
| 2:30–3:20 | Seção 5: tabela das 18 combinações e os 2 gráficos | As combinações, o overfitting e a escolha. |
| 3:20–4:15 | Seção 6: tabela treino × teste, gráfico de barras, matriz de confusão, curvas | Resultados lado a lado. |
| 4:15–5:00 | Seção 7 e `RELATORIO_ML.md` §7 | O que significa para o cidadão e limitações. |

## O que enviar no Teams
```
Global Solution 2026.2 – CitizenTech – AquaGuard
Integrantes: Guilherme Cezarino Simoes e Fabrini Soares
Repositório: https://github.com/SEU-USUARIO/aquaguard-gs2026  (pasta /ml: notebook executado, RELATORIO_ML.md, dados/README.md, requirements.txt)
Vídeo (5 min, não listado): https://youtu.be/XXXXXXXX
```

## Deu erro?
- O `.html` abre em branco: abra direto `ml\AquaGuard_ML.html` com o Chrome/Edge (botão direito ▸ Abrir com).
- No GitHub o `.ipynb` às vezes demora a carregar — é normal; dá para recarregar a página.
