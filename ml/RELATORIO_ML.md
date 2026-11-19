# Relatório de Machine Learning — AquaGuard

**FIAP · Global Solution 2026.2 · CitizenTech · Engenharia de Software (3º ano)**
**Integrantes:** Guilherme Cezarino Simoes (RM 557724) · Fabrini Soares (RM 557813) · João Both (RM 558690)
**Notebook executado:** [`AquaGuard_ML.ipynb`](AquaGuard_ML.ipynb) (versão HTML: `AquaGuard_ML.html`)

---

## 1. Problema e pergunta de Machine Learning

O AquaGuard ajuda moradores de bairros de São Paulo que alagam com frequência (ex.: Jardim Pantanal, Aricanduva, Ipiranga)
a se proteger. Os sensores IoT medem a água **quando ela já está subindo**; falta um aviso com **antecedência** para que a
família tire o carro da rua baixa, suspenda móveis e evite o trajeto.

> **Pergunta:** com as condições meteorológicas medidas **hoje** pela estação oficial do INMET, conseguimos prever se
> **amanhã** haverá **chuva forte (≥ 20 mm no dia)** em São Paulo?

- Tipo: **classificação binária** (1 = amanhã chove ≥ 20 mm; 0 = não).
- Por que 20 mm/dia: é a faixa em que alagamentos passam a ser frequentes na cidade e corresponde ao percentil ~93 dos
  dias da série (6,8 % dos dias) — um evento relevante, porém não raro demais para aprender.

## 2. Dados reais e públicos

| Item | Detalhe |
|---|---|
| Fonte | **INMET** — Instituto Nacional de Meteorologia, Banco de Dados Meteorológicos (dados históricos horários) |
| Link | https://portal.inmet.gov.br/dadoshistoricos |
| Estação | **A701 – São Paulo / Mirante de Santana** (lat −23,48; lon −46,62; alt. 792 m) |
| Período | **01/01/2012 a 31/12/2025** — 14 arquivos anuais, **122.736 registros horários** |
| Variáveis | precipitação, pressão, temperatura, ponto de orvalho, umidade, radiação, vento e rajada |
| Reprodução | `python dados/download_inmet.py --inicio 2012 --fim 2025` |

Nenhum dado é simulado. Detalhes em [`dados/README.md`](dados/README.md).

## 3. Escolha justificada do modelo — Random Forest

- Dados **tabulares**, ~5 mil dias, relações **não lineares** e interações (queda de pressão só “pesa” no verão): árvores
  capturam isso sem normalização.
- Robusto a **outliers** (temporais extremos de até 142 mm/dia) e a atributos correlacionados (temperatura/orvalho/umidade).
- `class_weight="balanced"` trata o desbalanceamento (6,8 % de positivos) sem criar dados sintéticos.
- Fornece **importância dos atributos**, permitindo explicar o alerta à população.
- Alternativas descartadas: **LSTM** (exige muito mais dados e é difícil de explicar), **KMeans + PCA** (não supervisionado,
  não responde a pergunta), **MLP** (menos interpretável, sem ganho esperado em tabular pequeno). XGBoost seria viável;
  priorizamos o Random Forest pela estabilidade com poucos ajustes e menor risco de sobreajuste.

## 4. Preparação e divisão treino/teste

1. **Normalização dos formatos** do INMET, que mudaram ao longo dos anos (`2012-01-01`/`00:00` × `2025/01/01`/`0000 UTC`);
   `-9999` → ausente. A radiação tem 47 % de ausências (sensor zera à noite); as demais variáveis, < 1 %.
2. **UTC → horário de Brasília** e agregação **horário → diário**.
3. **Controle de qualidade:** dia só é usado se tiver ≥ 20 das 24 horas de precipitação medidas (evita rotular como “sem chuva”
   um dia em que a estação estava desligada). Restaram **5.008 de 5.115 dias (97,9 %)**.
4. **21 atributos**, todos disponíveis até o fim do dia atual: chuva total e máxima horária, horas com chuva, acumulados de 3 e 7
   dias, pressão média/amplitude/variação, temperaturas, amplitude térmica, umidade, déficit de orvalho, radiação, vento,
   rajada e sazonalidade (seno/cosseno do dia do ano).
5. **Alvo:** `precipitação(dia+1) ≥ 20 mm`.
6. **Divisão temporal** (sem embaralhar, para não vazar o futuro):

| Conjunto | Período | Dias | Positivos |
|---|---|---|---|
| Treino | 2012 → 2022 | 3.974 | 266 (6,7 %) |
| Teste | 2023 → 2025 | 1.034 | 74 (7,2 %) |

## 5. Treino com diferentes hiperparâmetros

- **3 hiperparâmetros, 18 combinações:** `n_estimators` ∈ {150, 400} × `max_depth` ∈ {4, 8, None} × `min_samples_leaf` ∈ {1, 10, 30}.
- **Validação cruzada só no treino**, com `TimeSeriesSplit(5)` (cada dobra valida em anos posteriores aos usados no ajuste).
- Métrica principal: **PR-AUC** (adequada a classes raras); também registramos ROC-AUC e F1. Tabela completa em
  `resultados_grid_search.csv` e gráficos `figuras/02_*` e `figuras/03_*`.
- **Critério de escolha — regra de 1 desvio-padrão:** as combinações praticamente empatam na validação (PR-AUC 0,167–0,177,
  desvio ≈ 0,04). As árvores sem limite de profundidade chegam a **PR-AUC 1,000 no treino** (decoram os dados) para o mesmo
  resultado na validação. Escolhemos, entre as que estão a até 1 desvio do melhor, a de **menor gap treino-validação**:
  **`n_estimators=150, max_depth=4, min_samples_leaf=30`**.
- **Limiar de decisão = 0,56**, escolhido maximizando o F1 nas previsões *out-of-fold* do treino (o teste não foi usado).

## 6. Resultados em treino e teste

| Métrica | Treino (ajuste completo) | Treino (CV out-of-fold) | **Teste 2023–2025** |
|---|---|---|---|
| ROC-AUC | 0,845 | 0,760 | **0,792** |
| PR-AUC (aleatório = 0,072) | 0,286 | 0,164 | **0,208** |
| Recall (chuvas fortes avisadas) | 0,786 | 0,600 | **0,689** |
| Precisão (avisos confirmados) | 0,191 | 0,159 | **0,179** |
| F1 | 0,308 | 0,251 | **0,284** |
| Acurácia balanceada | 0,774 | 0,687 | **0,723** |

Gráficos: `figuras/04_metricas_treino_teste.png`, `figuras/05_confusao_roc_pr.png` (matriz de confusão, ROC e PR) e
`figuras/06_importancia_atributos.png`.

**Overfitting.** A combinação mais complexa (400/None/1) mostra overfitting clássico: PR-AUC 1,000 no treino × 0,177 na
validação. O modelo escolhido tem gap pequeno (0,286 no treino × 0,208 no teste) e o teste ficou **dentro da faixa** da
validação cruzada (0,164 ± 0,04), indicando que generaliza para anos não vistos. O teste ser um pouco melhor que a CV é
compatível com a variação entre anos (2023–2025 tiveram verões com chuvas fortes bem marcadas).

**Atributos mais importantes:** sazonalidade (verão), chuva máxima horária de hoje, pressão média, temperatura mínima
(noites quentes e úmidas) e chuva acumulada em 3 dias — coerente com a meteorologia de São Paulo (calor + umidade + frentes).

## 7. Conclusão e leitura para o cidadão

No período de teste (≈ 2,8 anos) houve **74 dias de chuva forte**:

- O AquaGuard teria avisado **na véspera em 51 deles (69 %)**.
- **23 (31 %) passariam sem aviso** — chuvas de verão muito localizadas, difíceis de prever com uma única estação.
- Houve **234 avisos que não se confirmaram** (~83/ano; ~1 em cada 6 avisos se confirma). Por isso o aviso é apresentado
  como **“chance elevada de chuva forte amanhã”**, nunca como certeza.
- Em **76 % dos dias normais** o morador não recebe nenhum aviso.

**O que isso significa para o morador:** com um dia de antecedência ele fica sabendo de ~7 em cada 10 chuvas fortes — tempo
para se preparar. O modelo **não substitui** o sensor IoT e os relatos dos vizinhos: ele é a **1ª camada (antecipação)**; o
sensor no córrego é a **2ª camada (confirmação em tempo real)**, que dispara o alerta crítico no app.

**Limitações e próximos passos:** uma única estação (Mirante de Santana, zona norte) representa a cidade inteira; incluir
estações do CGE/CEMADEN, radar meteorológico e previsões numéricas deve aumentar a precisão. O modelo deve ser re-treinado
anualmente e monitorado (drift climático).
