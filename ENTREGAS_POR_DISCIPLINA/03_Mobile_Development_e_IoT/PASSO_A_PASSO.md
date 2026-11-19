# 03 — Mobile Development & IoT (aplicativo)

## O que o professor pede
Um app em **React Native + TypeScript + Expo** que resolva a jornada principal do cidadão, consuma dados de uma API,
**salve em banco de dados**, seja acessível, e um README com a **Ficha da CitizenTech**, instruções e **prints das telas**.
Entrega: **link do GitHub** + **link do vídeo de até 3 minutos** com o app rodando.

| Critério | Pronto? |
|---|---|
| Telas e navegação (abas Início, Pontos, Relatar, Meus relatos + tela de detalhe + escolha de bairro) | ✅ |
| Consumo de dados (lê a API do backend) | ✅ |
| Banco de dados (SQLite no celular: relatos, preferências, cópia offline) | ✅ |
| Acessibilidade (leitor de tela, contraste, cor + ícone + texto) | ✅ |
| Aderência ao problema | ✅ |
| Documentação: `mobile\README.md` com Ficha e prints | ✅ (falta só o link do vídeo) |
| **Vídeo de até 3 min** | ❌ **você grava** |

## O que VOCÊ precisa fazer

### Passo 1 — Ligar tudo (5 min)
1. Celular e computador na **mesma rede Wi-Fi**. Instale o **Expo Go** no celular.
2. Dois cliques em `00_PREPARAR_COMPUTADOR\H_ZERAR_DADOS_DA_DEMONSTRACAO.bat` (deixa tudo "Normal" para o vídeo).
3. Dois cliques em `00_PREPARAR_COMPUTADOR\B_LIGAR_SERVIDOR_API.bat` (deixe a janela aberta; Firewall: **Permitir**).
4. Dois cliques em `00_PREPARAR_COMPUTADOR\D_LIGAR_APLICATIVO.bat`. Na 1ª vez demora uns minutos instalando.
5. Quando aparecer o **QR Code**: no Android, abra o **Expo Go ▸ Scan QR code**; no iPhone, use a **câmera**.
6. O app abre no celular. Escolha o bairro **Jardim Pantanal** (toque no nome do bairro, no topo).

> **Plano B** (se o celular não conectar): na janela do app aperte a tecla **`w`** — o app abre no navegador do computador.
> Aperte **F12** ▸ ícone de celular (canto superior esquerdo do painel) para ficar com cara de celular. Serve para o vídeo.

### Passo 2 — Gravar o vídeo (máx. 3:00) — grave a tela do celular (gravador do próprio celular) ou do computador
| Tempo | O que mostrar | O que falar (pode ler) |
|---|---|---|
| 0:00–0:20 | `mobile\README.md` aberto no GitHub (a Ficha) | "O AquaGuard avisa moradores de áreas que alagam em São Paulo. A jornada principal é: ver a situação do bairro, relatar um alagamento e acompanhar os relatos." |
| 0:20–0:50 | Tela **Início** (Normal). Dê dois cliques em `C_SIMULAR_ENCHENTE.bat` no PC e, no app, **puxe a tela para baixo** para atualizar | "Os dados vêm da nossa API em C#. Agora o sensor do córrego detectou a água subindo… e o app mudou para PERIGO, com orientações do que fazer." |
| 0:50–1:20 | Aba **Pontos** ▸ toque no primeiro ponto | "Aqui estão os pontos monitorados, com a barra do nível da água e o histórico das leituras." |
| 1:20–2:00 | Aba **Relatar**: escreva "Meu CPF é 123.456.789-09" ▸ Enviar (aparece erro) ▸ apague e escreva "Água na altura do joelho na esquina da escola" ▸ Enviar ▸ aba **Meus relatos** | "O app impede que o cidadão publique CPF ou telefone, protegendo os dados. O relato fica salvo no banco SQLite do celular e é enviado para a API, que devolve um protocolo." |
| 2:00–2:30 | Feche a janela do servidor ▸ no app, puxe para atualizar na Início (aparece aviso amarelo "Sem conexão") | "Sem internet, o app mostra os últimos dados salvos. Um relato feito offline fica guardado e é enviado depois." |
| 2:30–3:00 | (Opcional) mostre no GitHub a pasta `mobile/src/app` | "Usamos Expo Router para a navegação, TypeScript, SQLite e recursos de acessibilidade como rótulos para leitor de tela e alto contraste." |

### Passo 3 — Publicar e entregar
1. Publique o vídeo no YouTube como **Não listado** e copie o link.
2. Cole o link em `mobile\README.md` no lugar de `<inserir link do YouTube>` e envie ao GitHub
   (GitHub Desktop ▸ Commit ▸ Push — veja `00_PREPARAR_COMPUTADOR`).

## O que enviar no Teams
```
Global Solution 2026.2 – CitizenTech – AquaGuard
Integrantes: Guilherme Cezarino Simoes (RM 557724), Fabrini Soares (RM 557813) e João Both (RM 558690)
Repositório: https://github.com/GuilhermeCezarinoSimoes/aquaguard-gs2026  (app na pasta /mobile – README com Ficha, instruções e prints)
Vídeo (3 min): https://youtu.be/XXXXXXXX
```

## Deu erro?
| Problema | Solução |
|---|---|
| O Expo Go diz que a versão do projeto é incompatível | Atualize o Expo Go na loja. Se continuar, use o **Plano B** (tecla `w`, navegador) |
| O app abre mas aparece "Sem conexão… dados de demonstração" | O servidor não está ligado, ou o Firewall bloqueou. Ligue o `B_LIGAR_SERVIDOR_API.bat`, clique em Permitir no Firewall. Celular e PC precisam estar no mesmo Wi-Fi (Wi-Fi de visitante/faculdade costuma bloquear: use o roteador de casa ou o Plano B) |
| QR Code não aparece | Espere terminar a instalação; se fechar, rode o `.bat` de novo |
| `npm` não é reconhecido | Instale o Node.js LTS e reinicie o PC |
