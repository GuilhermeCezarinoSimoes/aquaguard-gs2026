# 00 — Preparar o computador (e o link do GitHub)

## Parte 1 — Instalar os programas (uma vez só, ~30 min)
Baixe e instale **nesta ordem**, sempre clicando em "Avançar/Next" com as opções padrão:

| # | Programa | Onde baixar | Atenção |
|---|---|---|---|
| 1 | **.NET 8 SDK** (roda o servidor) | https://dotnet.microsoft.com/download/dotnet/8.0 → coluna **SDK 8.0.x** → "Windows x64" | Precisa ser o **SDK**, não o "Runtime" |
| 2 | **Node.js LTS** (roda o app) | https://nodejs.org → botão **LTS** | — |
| 3 | **Python 3.12** (IA e segurança) | https://www.python.org/downloads | Na 1ª tela marque ✅ **"Add python.exe to PATH"** |
| 4 | **GitHub Desktop** (publicar o projeto) | https://desktop.github.com | Faça login com a conta GitHub |
| 5 | **Expo Go** no CELULAR | Play Store / App Store, busque "Expo Go" | — |

Depois de instalar tudo, **reinicie o computador** e dê dois cliques em **`A_VERIFICAR_PROGRAMAS.bat`**.
Tem que aparecer `[OK]` nas três linhas. Se aparecer `[FALTA]`, instale o que falta.

> Quando der dois cliques num `.bat`, o Windows pode mostrar "O Windows protegeu o computador".
> Clique em **"Mais informações" ▸ "Executar assim mesmo"**. São só atalhos de texto deste projeto
> (dá para abrir com o Bloco de Notas e ver o que fazem).

## Parte 2 — Os atalhos de dois cliques desta pasta
| Atalho | O que faz | Quando usar |
|---|---|---|
| `A_VERIFICAR_PROGRAMAS.bat` | Confere se os programas estão instalados | Antes de tudo |
| `B_LIGAR_SERVIDOR_API.bat` | Liga o servidor e abre o **painel** e o **Swagger** no navegador | Vídeos de Mobile, IoT, Cyber e para prints |
| `C_SIMULAR_ENCHENTE.bat` | Envia leituras de uma enchente (igual ao sensor) para o servidor | Para mostrar o alerta aparecendo |
| `D_LIGAR_APLICATIVO.bat` | Liga o app e mostra o QR Code para o Expo Go | Vídeo de Mobile e Pitch |
| `E_AUDITORIA_SEGURANCA.bat` | Roda os testes e a auditoria de segurança e abre o dashboard | Vídeo de Cybersecurity |
| `F_GERAR_ZIP_CYBERSECURITY.bat` | Cria o ZIP que vai para o Teams de Cyber | Entrega de Cyber |
| `G_ABRIR_RELATORIO_ML.bat` | Abre o notebook de IA já executado e o relatório | Vídeo de ML |
| `H_ZERAR_DADOS_DA_DEMONSTRACAO.bat` | Volta o servidor ao estado inicial (tudo "Normal") | Antes de gravar um vídeo |

**Teste rápido (5 min) para ver se tudo funciona:**
1. Dois cliques em `B_LIGAR_SERVIDOR_API.bat` → espere ~30 s → o navegador abre o painel "AquaGuard".
   (Se o Firewall perguntar, clique **Permitir acesso**.)
2. Dois cliques em `C_SIMULAR_ENCHENTE.bat` → no painel, o Jardim Pantanal fica **Crítico** (atualiza a cada 10 s).
Funcionou? Ótimo, o computador está pronto.

## Parte 3 — O projeto no GitHub (JÁ PUBLICADO ✅)
**Link do GitHub (é este que vai no Teams):**
### https://github.com/GuilhermeCezarinoSimoes/aquaguard-gs2026

Os textos prontos de todas as pastas já usam esse link. O repositório é **público** (o professor abre sem login).

### Colocar os links dos vídeos/Wokwi/Azure no GitHub (no fim, quando tiver todos)
Abra estes arquivos no Bloco de Notas, procure (Ctrl+F) por **`<inserir`** ou **`PREENCHER`** e troque pelo link certo:
- `mobile\README.md` — link do vídeo do app
- `ml\README.md` — link do vídeo de ML
- `iot\integrantes.txt` — link do Wokwi e do vídeo de IoT
- `testing\FEATURES_E_TEST_CASES.md` — link do projeto Azure

Para enviar as alterações ao GitHub, escolha **um** dos jeitos:
- **Jeito fácil:** mande os links para o **Guilherme** pelo WhatsApp e ele atualiza.
- **Você mesmo:** o Guilherme precisa te dar permissão primeiro: no site do repositório ▸ **Settings ▸ Collaborators ▸
  Add people** ▸ seu usuário do GitHub (você aceita o convite que chega por e-mail). Depois, no **GitHub Desktop**:
  **File ▸ Add local repository** ▸ escolha a pasta **`GS`** (ela já vem ligada ao repositório do Guilherme) ▸
  escreva "Adiciona links" em **Summary** ▸ **Commit to main** ▸ **Push origin**.
  ⚠️ **Não** clique em "Publish repository" se aparecer: isso criaria uma cópia na sua conta.

> **Se o link pedir login ou não abrir:** avise o Guilherme — o repositório pode ter sido deixado privado sem querer
> (Settings ▸ General ▸ Danger Zone ▸ Change visibility ▸ Public).

## Deu erro?
| Problema | Solução |
|---|---|
| `dotnet` não é reconhecido | Instale o **.NET 8 SDK** e **reinicie o computador** |
| `python` não é reconhecido | Reinstale o Python marcando **"Add python.exe to PATH"** |
| A janela do servidor fecha na hora | Abra o `cmd`, arraste o `B_LIGAR_SERVIDOR_API.bat` para dentro e aperte Enter para ver a mensagem de erro |
| "porta 5080 já está em uso" | O servidor já está ligado em outra janela. Feche as janelas pretas e tente de novo |
| GitHub Desktop pede para "create a repository" | Você escolheu a pasta errada: tem que ser a pasta `GS` (que contém `README.md`, `backend`, `mobile`…) |
