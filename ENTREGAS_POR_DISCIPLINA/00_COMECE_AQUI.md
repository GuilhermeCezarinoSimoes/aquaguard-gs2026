# COMECE AQUI — Guia para terminar a Global Solution (AquaGuard)

Olá! Este guia foi feito para **quem não é da área**. Siga na ordem, sem pular etapas.
Tudo que é programação **já está pronto e testado**. O que falta são tarefas de "clicar, gravar e enviar".

**Prazo final: quinta-feira, 19/11/2026, às 23h55** (no Teams de cada matéria).
**Integrantes do grupo:** Guilherme Cezarino Simoes · Fabrini Soares

---

## 1. O que é o projeto (em 1 minuto)
O **AquaGuard** avisa os moradores de São Paulo quando a rua deles vai alagar.
- Um **sensor** (simulado no site Wokwi) fica em cima do córrego e mede a altura da água e a chuva.
- Um **servidor** (a "API") recebe essas medidas, calcula o perigo e cria um **alerta para o bairro**.
- Um **aplicativo de celular** mostra o alerta e deixa o morador **avisar** que a rua alagou.
- Um programa de **inteligência artificial** usa 14 anos de dados reais do clima para avisar **na véspera** se vai chover forte.
- Um módulo de **segurança** impede que dados pessoais (CPF, telefone…) escritos nos avisos vazem.
- Um **servidor Linux** roda tudo sozinho e se recupera se algo cair.

Explicação mais completa (para responder perguntas do professor): [`EXPLICACAO_SIMPLES.md`](EXPLICACAO_SIMPLES.md).

---

## 2. Como as pastas estão organizadas
```
GS\                                  ← pasta do projeto inteiro
├── ENTREGAS_POR_DISCIPLINA\         ← VOCÊ VAI TRABALHAR AQUI
│   ├── 00_COMECE_AQUI.md            ← este arquivo
│   ├── 00_PREPARAR_COMPUTADOR\      ← o que instalar + atalhos de dois cliques (.bat)
│   ├── 01_SOA_e_Web_Services\
│   ├── 02_CSharp_Software_Development\
│   ├── 03_Mobile_Development_e_IoT\
│   ├── 04_Inteligencia_Artificial_e_Machine_Learning\
│   ├── 05_Cybersecurity\
│   ├── 06_Operating_Systems\
│   ├── 07_Physical_Computing_IoT_e_IoB\
│   └── 08_Testing_Compliance_e_QA\   ← aqui também vai o vídeo do PITCH
├── backend\  mobile\  ml\  cybersecurity\  iot\  operating-systems\  testing\   ← código (NÃO MEXA)
└── evidencias\                      ← prints e resultados já gerados
```
Cada pasta de matéria tem um arquivo **`PASSO_A_PASSO.md`** dizendo exatamente:
1. o que o professor pede;
2. o que já está pronto;
3. o que **você** precisa fazer (com cada clique);
4. **o que enviar no Teams** (com a mensagem pronta para copiar).

> ⚠️ **Não mova nem renomeie** as pastas de código (`backend`, `mobile`, etc.). Os programas dependem desses nomes.
> As pastas de matéria são o "mapa" — elas apontam para o código certo.

**Como abrir os arquivos `.md`:** dê dois cliques. Se o Windows perguntar, escolha **Bloco de Notas**. Fica mais bonito no
VS Code (https://code.visualstudio.com — botão direito no arquivo ▸ "Open Preview") ou no próprio GitHub depois de publicado.

---

## 3. Ordem recomendada (do mais rápido ao mais demorado)
| # | Tarefa | Pasta | Tempo | Precisa de |
|---|---|---|---|---|
| 1 | Instalar os programas | `00_PREPARAR_COMPUTADOR` | 30 min | internet |
| 2 | ✅ **Já feito:** projeto publicado em https://github.com/GuilhermeCezarinoSimoes/aquaguard-gs2026 | — | 0 | — |
| 3 | Conversar com um morador (o edital exige) | `08_Testing...` ▸ parte do pitch | 20 min | celular |
| 4 | Wokwi: montar o circuito e salvar o link | `07_Physical_Computing...` | 20 min | conta Wokwi (grátis) |
| 5 | Gravar vídeo do IoT (4 min) | `07_Physical_Computing...` | 30 min | gravador de tela |
| 6 | Gravar vídeo do Machine Learning (5 min) | `04_Inteligencia...` | 30 min | — |
| 7 | Gravar vídeo do App (3 min) | `03_Mobile...` | 40 min | celular com Expo Go |
| 8 | Cybersecurity: gerar ZIP + vídeo | `05_Cybersecurity` | 30 min | — |
| 9 | Azure DevOps: cadastrar e gerar PDF | `08_Testing...` | 1 h | conta Microsoft |
| 10 | Linux na máquina virtual + vídeo (7 min) | `06_Operating_Systems` | 2 h | 8 GB de RAM livres no PC |
| 11 | Gravar o PITCH (4 min) | `08_Testing...` | 40 min | — |
| 12 | Enviar tudo no Teams | cada pasta | 30 min | conta FIAP |

**Dica:** se o tempo apertar, entregue primeiro as matérias que só pedem link do GitHub
(**SOA**, **C#**) — elas já estão 100% prontas: é só enviar o texto da pasta delas.

---

## 4. Como gravar a tela (vale para todos os vídeos)
- **Mais fácil (Windows 11):** abra a **Ferramenta de Captura** (tecla Windows, digite "Captura") ▸ ícone de **filmadora** ▸
  "Novo" ▸ selecione a tela ▸ grave. O vídeo fica em `Vídeos\Gravações de tela`.
- **Alternativa:** OBS Studio (https://obsproject.com) — mais completo.
- Fale devagar e mostre o que está falando. **Respeite o tempo máximo** (cronometre).
- **Publicar no YouTube:** youtube.com ▸ ícone de câmera "Criar" ▸ "Enviar vídeo" ▸ escolha o arquivo ▸
  em **Visibilidade** escolha **"Não listado"** ▸ Publicar ▸ copie o link.

## 5. Como enviar no Teams
Abra o **Teams** ▸ equipe da turma ▸ aba **Tarefas** (ou "Atividades") ▸ abra a tarefa da matéria ▸
cole o link/anexe o arquivo ▸ **Entregar**. **Só UMA pessoa do grupo envia cada matéria.**

## 6. Lista final (marque com X)
- [x] Projeto publicado no GitHub — https://github.com/GuilhermeCezarinoSimoes/aquaguard-gs2026
- [ ] 01 SOA — enviado
- [ ] 02 C# — enviado
- [ ] 03 Mobile — vídeo: ______________________ — enviado
- [ ] 04 Machine Learning — vídeo: ______________________ — enviado
- [ ] 05 Cybersecurity — ZIP + vídeo: ______________________ — enviado
- [ ] 06 Operating Systems — vídeo: ______________________ — enviado
- [ ] 07 Physical Computing — Wokwi: ______________ vídeo: ______________ — enviado
- [ ] 08 Testing — PDF do Azure + PITCH: ______________________ — enviado

Se algo der errado, veja a seção **"Deu erro?"** no final de cada `PASSO_A_PASSO.md`.
