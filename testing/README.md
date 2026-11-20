# AquaGuard · Testing, Compliance & Quality Assurance

Entregável oficial: **Features** (com descrição e critérios de aceite) e **Test Cases** funcionais caixa-preta,
positivos e negativos (objetivo, preparação, entradas, saídas esperadas e passos), **cadastrados no Azure Boards**,
com o professor como **Admin** e um **PDF** com o link do projeto + prints de todas as telas. Avaliação: Features 50 % · Test Cases 50 %.

## Conteúdo desta pasta
| Arquivo | Uso |
|---|---|
| [`FEATURES_E_TEST_CASES.md`](FEATURES_E_TEST_CASES.md) | Documento completo: 7 Features, 25 Test Cases (13 positivos, 12 negativos), matriz de rastreabilidade |
| `azure_import_features.csv` | Importação das Features no Azure Boards |
| `azure_import_test_cases.csv` | Importação dos Test Cases **com os passos** (Step Action / Step Expected) |
| `gerar_artefatos.py` | Fonte única: altere aqui e rode `python gerar_artefatos.py` para regenerar tudo |

Todas as Features correspondem a funcionalidades **implementadas** (API, app, IoT, segurança). Os casos de API
TC01–TC08, TC10, TC14–TC17 e TC19–TC21 também estão cobertos por testes automatizados em `backend/tests`.

## Passo a passo no Azure DevOps (ação da equipe — exige login)
1. https://dev.azure.com → **New project** com o nome exato `AquaGuard` (o CSV usa esse nome como Area Path) (processo **Agile**, visibilidade privada).
2. **Project settings ▸ Permissions ▸ Project Administrators ▸ Add** → e-mail do professor (perfil Admin).
3. **Boards ▸ Work items ▸ Import Work Items** → `azure_import_features.csv` → *Save items*.
4. Repita com `azure_import_test_cases.csv` (cada Test Case entra com seus passos).
   - Alternativa: **Test Plans ▸ New Test Plan** `Homologação AquaGuard` → *Add existing test cases*.
5. (Opcional, recomendado) Em cada Test Case, **Links ▸ Add link ▸ Tests** → Feature correspondente (coluna Tags indica qual).
6. Prints obrigatórios (contingência): lista de Features; detalhe de **cada** Feature; lista de Test Cases; detalhe de **cada**
   Test Case com os passos. Cole-os no documento de resposta, insira o link do projeto e **exporte em PDF**.

## Pitch (prêmio Melhor GS)
O vídeo de até 4 min no YouTube é enviado **nesta disciplina**. Pitch: https://youtu.be/eOPibyO6slw. Persona usada: `../docs/persona_dona_cida.md`.
