# Dados — AquaGuard ML

## Fonte
- **Instituição:** INMET — Instituto Nacional de Meteorologia
- **Conjunto:** Banco de Dados Meteorológicos — dados históricos horários de estações automáticas
- **Link:** https://portal.inmet.gov.br/dadoshistoricos (arquivos anuais `AAAA.zip`)
- **Estação:** A701 — SÃO PAULO - MIRANTE (Mirante de Santana), código WMO A701
  - Latitude −23,4833 · Longitude −46,6167 · Altitude 792 m
- **Período utilizado:** 01/01/2012 a 31/12/2025
- **Licença/uso:** dados públicos de livre acesso disponibilizados pelo governo federal.
- **Data do download:** 17/11/2026

## Arquivos
| Arquivo | Conteúdo |
|---|---|
| `raw/INMET_A701_SAO_PAULO_MIRANTE_AAAA.csv` | CSV original do INMET (sem alterações), 1 por ano, separador `;`, decimal `,`, encoding latin-1, 8 linhas de cabeçalho |
| `download_inmet.py` | Script que baixa os ZIPs anuais e extrai somente a estação A701 |

## Variáveis (horárias)
Precipitação total (mm), pressão atmosférica (mB) e máx./mín., radiação global (kJ/m²), temperatura do ar, ponto de orvalho,
temperatura máx./mín., umidade relativa e máx./mín. (%), direção e velocidade do vento (m/s), rajada máxima (m/s).
`-9999` ou vazio = sem medição.

## Como reproduzir
```bash
python dados/download_inmet.py --inicio 2012 --fim 2025 --cache /tmp/inmet
```

## Dados pessoais
Os dados são meteorológicos; não há qualquer dado pessoal.
