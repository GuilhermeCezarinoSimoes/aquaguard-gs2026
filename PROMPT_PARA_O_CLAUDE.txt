# PROMPT PARA COLAR NO CLAUDE — terminar a Global Solution "AquaGuard"

> **Como usar (para quem vai terminar o trabalho):**
> - **Melhor opção — Claude Code** (app Claude para Windows/Mac, aba "Code", ou o `claude` no terminal): abra a pasta `GS`
>   (a que veio no ZIP) como pasta de trabalho e cole **todo o texto abaixo da linha**. Ele consegue ler os arquivos,
>   rodar os atalhos e te guiar.
> - **Alternativa — claude.ai no navegador:** abra uma conversa nova, **anexe** o arquivo
>   `GUIA_PARA_TERMINAR_O_PROJETO.html` (e, se quiser, este arquivo) e cole o texto abaixo da linha.
> - Copie a partir de "INÍCIO DO PROMPT" até "FIM DO PROMPT".

---

INÍCIO DO PROMPT

Você vai me ajudar a **terminar e entregar** um trabalho da faculdade que já está quase pronto. Eu **não sou da área de
tecnologia** (sou leigo): me explique tudo em português simples, **um passo por vez**, dizendo exatamente onde clicar e o
que digitar, e espere eu confirmar antes de ir para o próximo passo. Quando eu colar uma mensagem de erro, me diga a
causa provável e a solução em linguagem simples.

## 1. Contexto do trabalho
- **Faculdade/curso:** FIAP · Engenharia de Software · 3º ano (turma Fev) · **Global Solution 2026.2 — desafio "CitizenTech"**
  (criar tecnologia que resolve um problema real de uma cidade).
- **Integrantes do grupo:** **Guilherme Cezarino Simoes (RM 557724)**, **Fabrini Soares (RM 557813)** e **João Both (RM 558690)**. O **João** é o responsável pelas entregas no Teams e pelos vídeos.
- **Prazo final:** **quinta-feira, 19/11/2026, às 23h55**, no **Microsoft Teams** — cada matéria tem sua tarefa; **só UMA
  pessoa do grupo envia cada matéria**. 20/11 é feriado.
- **Projeto:** **AquaGuard** — avisa moradores de São Paulo quando a rua deles vai alagar. Bairro piloto: **Jardim Pantanal**
  (Zona Leste), com pontos também em Aricanduva, Ipiranga e Pacaembu.
  - Problema em uma frase: "Quem mora perto de córregos de São Paulo só percebe a enchente quando a água já está na
    porta, sem tempo de proteger a família e os bens."
  - ODS da ONU: 11 (cidades sustentáveis, meta 11.5), 13 (clima), 3 (saúde), 10 (desigualdades), 9 (infraestrutura).
- **Uso de IA:** permitido pelo edital como copiloto, desde que registrado no arquivo `prompts.md` e que os integrantes
  saibam explicar o projeto. **Registre neste arquivo o uso que fizermos aqui** (data, objetivo, resumo).

## 2. Links e documentos
- **Repositório GitHub (público, é o "link do GitHub" das entregas):** https://github.com/GuilhermeCezarinoSimoes/aquaguard-gs2026
  - Dono: Guilherme. Para **enviar alterações** (ex.: colocar links dos vídeos), é preciso que o Guilherme me adicione como
    colaborador (Settings ▸ Collaborators) **ou** que eu mande os links para ele atualizar. Não crie outro repositório.
- **Guia completo para leigo (abre no navegador):** `GUIA_PARA_TERMINAR_O_PROJETO.html` (na raiz da pasta `GS`).
- **Guias por matéria (mesmo conteúdo, em Markdown):** `ENTREGAS_POR_DISCIPLINA\<pasta da matéria>\PASSO_A_PASSO.md`.
- **Visão geral e Ficha da CitizenTech:** `README.md` · **Arquitetura:** `ARQUITETURA.md`
- **Requisitos oficiais extraídos do edital (PDF de 40 páginas):** `REQUISITOS_GS.md` · **Status/pendências:** `CHECKLIST_ENTREGAS.md`
- **Explicação simples do projeto:** `ENTREGAS_POR_DISCIPLINA\EXPLICACAO_SIMPLES.md`
- **Roteiros de vídeo:** `docs\roteiros\` (também dentro de cada PASSO_A_PASSO) · **Conversa com morador (modelo):** `docs\pesquisa_campo.md`
- **Wokwi (salvo e testado):** https://wokwi.com/projects/481041117417661441
- **Azure DevOps:** https://dev.azure.com/Fabriniaraujo2306/AquaGuard (conta do Fabrini; falta incluir o professor como Admin)
- **Ainda NÃO existem:** links dos vídeos no YouTube.

## 3. Estrutura da pasta `GS` (não mova nem renomeie as pastas de código)
```
GS\
├── GUIA_PARA_TERMINAR_O_PROJETO.html   ← guia completo
├── LEIA-ME_PRIMEIRO.txt · README.md · REQUISITOS_GS.md · ARQUITETURA.md · CHECKLIST_ENTREGAS.md · PLANO_EXECUCAO.md · prompts.md
├── ENTREGAS_POR_DISCIPLINA\
│   ├── 00_PREPARAR_COMPUTADOR\   ← atalhos .bat de dois cliques + guia de instalação
│   ├── 01_SOA_e_Web_Services\  02_CSharp_Software_Development\  03_Mobile_Development_e_IoT\
│   ├── 04_Inteligencia_Artificial_e_Machine_Learning\  05_Cybersecurity\  06_Operating_Systems\
│   ├── 07_Physical_Computing_IoT_e_IoB\   (sketch.ino, diagram.json, integrantes.txt)
│   └── 08_Testing_Compliance_e_QA\        (CSVs do Azure, FEATURES_E_TEST_CASES.md)
├── backend\            API em C# .NET 8 (SOA + C#)
├── mobile\             App Expo / React Native / TypeScript
├── ml\                 Machine Learning (notebook executado, relatório, dados INMET)
├── cybersecurity\      Módulo de privacidade (Python)
├── iot\                Circuito ESP32 (Wokwi) + simulador do sensor
├── operating-systems\  Scripts Bash/systemd para Linux
├── testing\            Features e Test Cases
├── docs\               Roteiros de vídeo e modelo da pesquisa de campo
└── evidencias\         Prints e resultados já gerados
```

## 4. O que JÁ FOI FEITO e testado (não refaça)
| Matéria | Situação | Detalhes |
|---|---|---|
| **SOA e Web Services** | ✅ **Pronta para enviar** | `backend\`: domínio, EF Core + SQLite, migração `InicialAquaGuard`, Swagger em `/swagger`, **47 testes passando**. Evidências em `evidencias\backend\` |
| **C# Software Development** | ✅ **Pronta para enviar** | Mesmo backend: POO (herança, interfaces, Strategy), Web API (15 endpoints), EF Core + LINQ, async/await, DI, ProblemDetails |
| **Mobile Development & IoT** | ✅ App pronto · ❌ falta vídeo (3 min) | Expo SDK 58 + Expo Router + TypeScript + SQLite (expo-sqlite), acessibilidade, offline. Testado no navegador ligado à API. 5 testes + typecheck + expo-doctor 20/20. Prints em `mobile\docs\prints\` |
| **IA & Machine Learning** | ✅ Pronta · ❌ falta vídeo (5 min) | Dados reais INMET estação A701 (2012–2025, 122.736 registros horários). Random Forest, 18 combinações de 3 hiperparâmetros, TimeSeriesSplit no treino. Teste 2023–2025: ROC-AUC 0,79; avisou 51 de 74 chuvas fortes (69 %). Notebook executado `ml\AquaGuard_ML.ipynb` (+ `.html`), `ml\RELATORIO_ML.md` |
| **Cybersecurity** | ✅ Pronta · ZIP já gerado · ❌ falta vídeo | Motor de PII (11 regras), Taint Analysis dinâmico e estático, tradução por IA (modo offline sem chave; usa Claude se houver `ANTHROPIC_API_KEY`), Indicador de Risco Cidadão **92 → 18**. **37 testes passando**. ZIP: `ENTREGAS_POR_DISCIPLINA\05_Cybersecurity\entrega_cybersecurity_AquaGuard.zip`. Print: `evidencias\cybersecurity\03_print_dashboard_risco_cidadao.jpg` |
| **Physical Computing (Wokwi)** | ✅ Circuito testado · ❌ falta salvar link + vídeo (4 min) | ESP32 + HC-SR04 + potenciômetro (chuva) + LCD I2C + 3 LEDs + buzzer + botão. **Compilou e rodou no Wokwi** (evidência `evidencias\iot\01_wokwi_compilado_executando.jpg`), mas o projeto não foi salvo (precisa conta). Biblioteca: LiquidCrystal I2C |
| **Operating Systems** | ✅ **Testado em VM real (18/11): 5/5 testes de falha** · ❌ falta vídeo (7 min, VM no PC do Fabrini) | `operating-systems\scripts\00..05`: infra (hostname, DNS, IP, UFW, auditd), app (.NET, publish, systemd, nginx), monitor CPU/mem/disco com alertas, serviço tolerante a falhas, teste de falha (5 cenários), relatório de auditoria. Evidências em `evidencias\operating-systems\`. |
| **Testing, Compliance & QA** | ✅ Conteúdo pronto · ❌ falta Azure + PDF + PITCH | 7 Features e 25 Test Cases (13 positivos, 12 negativos) em `ENTREGAS_POR_DISCIPLINA\08_Testing_Compliance_e_QA\` com CSVs para importar no Azure Boards. O **pitch de 4 min** é enviado nesta matéria |

**Atalhos de dois cliques (Windows)** em `ENTREGAS_POR_DISCIPLINA\00_PREPARAR_COMPUTADOR\` — todos testados:
`A_VERIFICAR_PROGRAMAS` · `B_LIGAR_SERVIDOR_API` (abre painel em http://localhost:5080 e Swagger) · `C_SIMULAR_ENCHENTE`
(envia leituras como o sensor; termina em PERIGO) · `D_LIGAR_APLICATIVO` (QR Code para o Expo Go; tecla `w` abre no navegador) ·
`E_AUDITORIA_SEGURANCA` · `F_GERAR_ZIP_CYBERSECURITY` · `G_ABRIR_RELATORIO_ML` · `H_ZERAR_DADOS_DA_DEMONSTRACAO`.

Programas necessários no PC: **.NET 8 SDK**, **Node.js LTS**, **Python 3.12** (marcar "Add to PATH"), **GitHub Desktop**
(opcional), **Expo Go** no celular, **VirtualBox** + **Ubuntu Server 24.04** (só para Operating Systems).

## 5. O que FALTA fazer (em ordem de prioridade)
1. **Enviar agora SOA e C#** no Teams (só precisam do link do GitHub; textos prontos nas pastas 01 e 02).
2. **Conversa com um morador real** que já passou por alagamento → preencher `docs\pesquisa_campo.md` com as respostas
   **verdadeiras** (sem nome completo/telefone/endereço). O edital exige; usar 1 frase no pitch.
3. **Wokwi:** criar conta, colar `sketch.ino` e `diagram.json`, adicionar a biblioteca **LiquidCrystal I2C**, salvar,
   copiar o link → `integrantes.txt` (pasta 07 e `iot\`). Gravar vídeo de 4 min. Enviar: link Wokwi + vídeo + `integrantes.txt`.
4. **Vídeo de ML** (5 min, YouTube **não listado**) mostrando o notebook e o relatório. Enviar: link do repositório + vídeo.
5. **Vídeo do App** (3 min) com o app no celular (Expo Go) ou no navegador. Enviar: link do repositório + vídeo.
6. **Cybersecurity:** gravar vídeo do dashboard. Enviar: ZIP + print do painel + link do vídeo.
7. **Azure DevOps:** criar projeto chamado exatamente **`AquaGuard`** (processo **Agile**), adicionar o professor como
   **Project Administrator** (Access level Basic), importar `azure_import_features.csv` e depois `azure_import_test_cases.csv`
   (Boards ▸ Work items ▸ Import Work Items), tirar prints da lista e de cada item, montar **PDF** com o link do projeto.
8. **Operating Systems:** VirtualBox + Ubuntu Server 24.04 (4 GB RAM, 2 CPUs, 30 GB; NAT com portas 2222→22 e 8080→80;
   marcar OpenSSH na instalação), conectar com `ssh aluno@localhost -p 2222`, clonar o repositório e rodar
   `sudo bash operating-systems/scripts/00_provisionar_tudo.sh`, depois `04_teste_falha.sh` e `05_relatorio_auditoria.sh`.
   Gravar vídeo de 7 min. **Se algum script falhar, me ajude a ler o erro e corrigir.**
9. **PITCH** (4 min, YouTube) — roteiro na pasta 08. Enviar junto com Testing.
10. **Colocar os links** (vídeos, Wokwi, Azure) nos arquivos que têm `<inserir` ou `PREENCHER`:
    `mobile\README.md`, `ml\README.md`, `iot\integrantes.txt`, `ENTREGAS_POR_DISCIPLINA\07_...\integrantes.txt`,
    `testing\FEATURES_E_TEST_CASES.md` — e enviar ao GitHub (ou mandar os links ao Guilherme).
11. **Enviar cada matéria no Teams** e marcar a lista final do guia.

## 6. Regras importantes (siga sempre)
- **Não invente nada:** nem links, nem resultados de testes, nem respostas da entrevista, nem prints. Se algo não foi feito,
  diga que não foi feito.
- **Não refaça o que já está pronto** e **não mova/renomeie** as pastas de código. Antes de mudar qualquer arquivo de código,
  me explique o motivo e peça minha confirmação.
- **Nada de dados pessoais reais** no projeto (regra do edital). Os relatos de teste são inventados e identificados.
- Não crie um novo repositório no GitHub; o oficial é o do Guilherme (link acima).
- Não peça minhas senhas. Logins (GitHub, Wokwi, Azure, YouTube, Teams) eu mesmo faço.
- Respeite os tempos máximos dos vídeos: pitch 4 min · ML 5 min · Mobile 3 min · OS 7 min · IoT 4 min.
- Priorize pelo prazo: o que garante nota com menos esforço primeiro (SOA e C#), Linux cedo (é o mais arriscado).
- Ao final de cada etapa, me diga o que foi concluído e qual é o próximo passo.

## 7. Comece assim
1. Se você tem acesso aos arquivos: leia `GUIA_PARA_TERMINAR_O_PROJETO.html` (ou os `PASSO_A_PASSO.md`), `CHECKLIST_ENTREGAS.md`
   e `REQUISITOS_GS.md`, e confirme em poucas linhas que entendeu o projeto e o que falta.
   Se não tem acesso aos arquivos: use o guia que anexei e as informações acima.
2. Pergunte quanto tempo eu tenho disponível hoje e amanhã e se meu computador tem pelo menos 8 GB de RAM (para a máquina
   virtual do Linux).
3. Monte comigo um plano por horário até 19/11 às 23h55 e comece pelo passo 1 da seção 5.

FIM DO PROMPT
