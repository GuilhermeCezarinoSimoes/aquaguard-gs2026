# 08 — Testing, Compliance & Quality Assurance (+ PITCH + conversa com morador)

Esta pasta tem **3 tarefas**:
- **A.** Cadastrar Features e Test Cases no **Azure DevOps** e gerar o **PDF** (nota da matéria).
- **B.** Conversar com um **morador real** (o edital exige para todo o projeto — usado no pitch).
- **C.** Gravar o **PITCH de 4 minutos** (vale o prêmio "Melhor GS" e é enviado **nesta** matéria).

## O que o professor pede
- **Features** (funcionalidades) com descrição e **critérios de aceite**, no **Azure Boards** → 50 % da nota.
- **Test Cases** (casos de teste) positivos e negativos, com objetivo, preparação, entradas, saídas esperadas e passos → 50 %.
- Colocar o professor como **Admin** do projeto, e um **PDF** com o link do projeto + **prints de todas as telas**.

**O que já está pronto (nesta pasta):**
| Arquivo | O que é |
|---|---|
| `FEATURES_E_TEST_CASES.md` | Todo o conteúdo escrito: 7 Features e 25 Test Cases (13 positivos, 12 negativos) |
| `azure_import_features.csv` | Arquivo para importar as 7 Features no Azure de uma vez |
| `azure_import_test_cases.csv` | Arquivo para importar os 25 Test Cases **com os passos** de uma vez |

---

## A. Azure DevOps (≈ 1 hora)

### A1. Criar o projeto
1. Entre em https://dev.azure.com com uma conta Microsoft (pode ser o e-mail da FIAP ou um Outlook/Hotmail).
   Na primeira vez, ele pede para criar uma **organização** (ex.: `aquaguard-gs`) — aceite.
2. **+ New project**:
   - Project name: **`AquaGuard`** (exatamente assim — os arquivos usam esse nome)
   - Visibility: **Private**
   - **Advanced ▸ Work item process: Agile**
   - **Create**.

### A2. Colocar o professor como Admin
1. Canto inferior esquerdo: **Organization settings** ▸ **Users** ▸ **Add users**.
2. Users: e-mail do professor (pergunte no Teams se não souber) · Access level: **Basic** ·
   Add to projects: **AquaGuard** · Azure DevOps Groups: **Project Administrators** ▸ **Add**.

### A3. Importar as Features
1. Dentro do projeto: menu **Boards ▸ Work items**.
2. Botão **Import Work Items** (fica no topo; se não aparecer, clique nos `…`).
3. **Choose file** ▸ `azure_import_features.csv` (desta pasta) ▸ **Import**.
4. Aparece uma tabela com 7 itens ▸ **Save items**. ✅
5. Se der erro de "Area Path": você não usou o nome `AquaGuard` no projeto. Abra o CSV no **Bloco de Notas**, use
   Ctrl+H para trocar `AquaGuard` (na coluna Area Path) pelo nome do seu projeto, salve e importe de novo.

### A4. Importar os Test Cases
1. Mesmo lugar: **Import Work Items** ▸ `azure_import_test_cases.csv` ▸ **Import** ▸ **Save items**.
   Entram 25 Test Cases, cada um com seus passos ("Steps").
2. Confira abrindo um deles (ex.: TC01): na aba **Steps** devem aparecer as linhas de Ação e Resultado esperado.

### A5. (Recomendado, 15 min) Ligar cada Test Case à sua Feature
Abra um Test Case ▸ no painel **Related Work** clique **Add link ▸ Existing item** ▸ Link type **Tests** ▸ digite o número
da Feature correspondente (o campo **Tags** do Test Case diz qual, ex.: `F01`) ▸ OK ▸ **Save**.
(A Feature F01 é a de título "F01 - Ingestão de leituras…", e assim por diante.)

### A6. Tirar os prints e montar o PDF
1. Abra o **Word** (ou Google Docs) e crie um documento com:
   - Título: "Global Solution 2026.2 – AquaGuard – Testing, Compliance & QA"
   - Integrantes: Guilherme Cezarino Simoes e Fabrini Soares
   - **Link do projeto Azure:** copie da barra do navegador (ex.: `https://dev.azure.com/aquaguard-gs/AquaGuard`)
2. Prints (tecla **Windows + Shift + S** ▸ selecione a área ▸ Ctrl+V no Word):
   - **Boards ▸ Work items**, com filtro de tipo **Feature**: a **lista** das 7 Features.
   - **Cada Feature aberta** (descrição + critérios de aceite) — 7 prints.
   - A **lista** dos Test Cases (filtro tipo **Test Case**).
   - **Cada Test Case aberto** mostrando a aba **Steps** — 25 prints (dá para colocar 2 por página).
3. **Arquivo ▸ Salvar como ▸ PDF**. Nome: `AquaGuard_Testing_Azure.pdf`.

> Dica para ganhar tempo: abra os itens em sequência e use Windows + Shift + S em cada um. São ~35 prints (~30 min).

---

## B. Conversa com um morador (≈ 20 min) — exigência do edital
O edital diz que o problema tem que ter **uma pessoa real que convive com ele**. Converse com alguém que já passou por
alagamento (familiar, vizinho, colega de trabalho). Pode ser por WhatsApp ou ligação.
1. Abra `docs\pesquisa_campo.md` (pasta principal do projeto) e faça as perguntas que estão lá.
2. **Anote as respostas de verdade** (não invente). Não escreva nome completo, telefone nem endereço da pessoa —
   use um apelido e o bairro.
3. Salve o arquivo e envie ao GitHub. Use 1 frase dessa conversa no início do pitch.

---

## C. PITCH (máx. 4:00) — vídeo no YouTube
Melhor com os **dois integrantes** falando. Pode ser gravação da tela + voz, ou vocês aparecendo + telas.
Antes: ligue `B_LIGAR_SERVIDOR_API.bat` e `D_LIGAR_APLICATIVO.bat`; tenha o Wokwi aberto; rode
`H_ZERAR_DADOS_DA_DEMONSTRACAO.bat` antes para começar com tudo "Normal".

| Tempo | Mostrar | Falar (pode ler) |
|---|---|---|
| 0:00–0:30 | Foto de rua alagada (tirada por vocês, ou de site com uso livre) | "Em São Paulo, quem mora perto de um córrego só descobre a enchente quando a água já está na porta." + 1 frase da conversa com o morador. |
| 0:30–0:50 | `README.md` (Ficha) | "Nosso cidadão é o morador do Jardim Pantanal. O alerta da cidade é geral; ninguém avisa se a SUA rua vai alagar. Atendemos os ODS 11 e 13." |
| 0:50–1:20 | Diagrama do `README.md` | "O AquaGuard une um sensor no córrego, um servidor que calcula o risco, um app para o morador e uma previsão com dados reais do INMET." |
| 1:20–1:50 | Wokwi rodando: diminua a distância do sensor | "O sensor mede a água; quando sobe, acende o vermelho e apita — mesmo sem internet." |
| 1:50–2:30 | App: rode `C_SIMULAR_ENCHENTE.bat` e mostre a Início virando PERIGO; tente relatar com CPF (bloqueia) | "O app avisa o que fazer, recebe relatos e protege os dados pessoais." |
| 2:30–2:55 | `ml\figuras\04_metricas_treino_teste.png` | "Com 14 anos de dados do INMET, avisamos na véspera 7 de cada 10 chuvas fortes. Não é perfeito — por isso o sensor confirma." |
| 2:55–3:20 | Dashboard de segurança (92 → 18) | "Protegemos a privacidade: o risco ao cidadão caiu de 92 para 18. E o servidor Linux se recupera sozinho. São 89 testes automáticos e 25 casos de teste." |
| 3:20–3:45 | — | "Para crescer: sensores de baixo custo em cada córrego crítico, em parceria com a Defesa Civil e as associações de bairro." |
| 3:45–4:00 | — | "AquaGuard: o aviso que chega antes da água. Guilherme Cezarino Simoes e Fabrini Soares." |

---

## O que enviar no Teams (Testing)
- **Anexo:** `AquaGuard_Testing_Azure.pdf`
- **Texto:**
```
Global Solution 2026.2 – CitizenTech – AquaGuard – Testing, Compliance & QA
Integrantes: Guilherme Cezarino Simoes e Fabrini Soares
Projeto Azure DevOps (professor incluído como Admin): https://dev.azure.com/XXXX/AquaGuard
PDF com os prints das Features e dos Test Cases em anexo.
PITCH (4 min): https://youtu.be/XXXXXXXX
Repositório: https://github.com/SEU-USUARIO/aquaguard-gs2026
```

## Deu erro?
| Problema | Solução |
|---|---|
| Não acho "Import Work Items" | Boards ▸ **Work items** (não "Boards"). Fica na barra superior; em telas pequenas, dentro de `…` |
| Erro "TF… Area Path" | Veja A3, passo 5 |
| Test Case importou sem passos | Abra o CSV no Excel e confira se as colunas "Test Step", "Step Action", "Step Expected" estão lá; importe de novo. Plano B: copie os passos de `FEATURES_E_TEST_CASES.md` manualmente na aba Steps |
| Professor não consegue entrar | Confirme que ele foi adicionado com Access level **Basic** e no grupo **Project Administrators** |
