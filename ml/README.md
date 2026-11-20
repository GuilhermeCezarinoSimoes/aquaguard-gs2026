# AquaGuard · Inteligência Artificial & Machine Learning

**Pergunta:** com os dados de hoje da estação INMET A701 (São Paulo), amanhã haverá chuva forte (≥ 20 mm)?

| Entregável | Arquivo |
|---|---|
| Notebook executado | [`AquaGuard_ML.ipynb`](AquaGuard_ML.ipynb) · cópia em HTML `AquaGuard_ML.html` |
| Relatório (2–4 páginas) | [`RELATORIO_ML.md`](RELATORIO_ML.md) |
| Dados e fonte | [`dados/README.md`](dados/README.md) · `dados/raw/` |
| Dependências | [`requirements.txt`](requirements.txt) |
| Resultados | `resultados_grid_search.csv`, `metricas_treino_teste.csv`, `resumo_modelo.json`, `figuras/` |
| Modelo treinado | `modelo_chuva_forte.joblib` |
| Vídeo (até 5 min, YouTube não listado) | Enviado no Teams da disciplina |

## Como executar
```bash
cd ml
python -m venv .venv
# Windows: .venv\Scripts\activate   |   Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
python construir_notebook.py                       # (re)gera o .ipynb a partir do código-fonte
jupyter nbconvert --to notebook --execute --inplace AquaGuard_ML.ipynb
```

## Resumo dos resultados (teste 2023–2025)
Random Forest (150 árvores, profundidade 4, folha mínima 30), 18 combinações de 3 hiperparâmetros com `TimeSeriesSplit(5)` no treino.
ROC-AUC **0,79** · PR-AUC **0,21** (aleatório 0,07) · Recall **69 %** · Precisão **18 %**.
O AquaGuard teria avisado na véspera 51 dos 74 dias de chuva forte do período de teste.
