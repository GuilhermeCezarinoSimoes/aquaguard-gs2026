# 07 — Physical Computing: IoT & IoB (circuito ESP32 no Wokwi)

## O que o professor pede
Um circuito com **ESP32 no site Wokwi**, ligado à solução do grupo (não um projeto separado).
Entrega no Teams: **link do projeto no Wokwi** + **link do vídeo de até 4 min** + **arquivo .txt com os nomes dos integrantes**.

| Item | Pronto? |
|---|---|
| Circuito (`diagram.json`) e programa (`sketch.ino`) — **já testados no Wokwi: compilam e funcionam** | ✅ |
| `integrantes.txt` | ✅ (falta colar os links) |
| **Link do Wokwi** | ❌ você salva na sua conta |
| **Vídeo de até 4 min** | ❌ você grava |

Os 3 arquivos estão **nesta pasta**: `sketch.ino`, `diagram.json`, `integrantes.txt`.

## Entendendo o circuito
- **ESP32:** a "plaquinha-computador" com Wi-Fi.
- **HC-SR04 (sensor ultrassônico):** fica 2 metros acima do fundo do córrego e mede a distância até a água.
  **Nível da água = 200 cm − distância.** Ex.: distância 150 → 50 cm de água.
- **Potenciômetro (botão giratório):** faz o papel do **medidor de chuva** (0 a 100 mm por hora).
- **LCD:** mostra a altura da água, a chuva e o nível de risco.
- **LEDs:** verde = Normal · amarelo = Atenção/Alerta · vermelho = Alerta/Crítico.
- **Buzzer:** apita em Alerta e Crítico. **Botão azul "Silenciar":** cala o apito por 5 minutos.
- O ESP32 envia os dados para o servidor do AquaGuard (a mesma API que o app usa) e decide o risco **sozinho**, mesmo sem internet.

| Distância no sensor | Água | Resultado |
|---|---|---|
| 180 cm | 20 cm | **Normal** (verde) |
| 150 cm | 50 cm | **Atenção** (amarelo) |
| 115 cm | 85 cm | **Alerta** (amarelo + vermelho + bipe curto) |
| 75 cm | 125 cm | **Crítico** (vermelho + bipe longo) |
| qualquer + chuva no máximo | — | **Crítico** por chuva |

## O que VOCÊ precisa fazer
### Passo 1 — Montar e salvar no Wokwi (15 min)
1. Entre em https://wokwi.com ▸ **Sign in** (pode entrar com a conta Google) .
2. Abra o endereço **https://wokwi.com/projects/new/esp32** (ou, na página inicial, "Start from scratch" ▸ **ESP32**).
   Abre um projeto novo com uma placa ESP32.
3. Aba **`sketch.ino`** (à esquerda): clique dentro do texto ▸ **Ctrl+A** ▸ **Delete**.
   Abra o arquivo `sketch.ino` **desta pasta** com o Bloco de Notas ▸ **Ctrl+A** ▸ **Ctrl+C** ▸ volte ao Wokwi ▸ **Ctrl+V**.
4. Aba **`diagram.json`**: mesma coisa (Ctrl+A, Delete, colar o conteúdo do `diagram.json` desta pasta).
   O desenho do circuito à direita muda e aparecem todos os componentes e fios.
5. Aba **Library Manager** ▸ botão **+** (azul) ▸ digite `LiquidCrystal I2C` ▸ clique em **LiquidCrystal I2C** (o primeiro).
6. Clique em **SAVE** (topo). Dê o nome **"AquaGuard - Estação IoT"**.
7. Copie o endereço da barra do navegador (algo como `https://wokwi.com/projects/123456789…`). **Esse é o link do Wokwi.**
   Teste numa janela anônima (Ctrl+Shift+N).
8. Cole o link no `integrantes.txt` **desta pasta** e também em `iot\integrantes.txt`.

### Passo 2 — Testar (5 min)
1. Clique no botão verde **▶** (Start). A 1ª vez demora de 30 s a 2 min ("Compiling…").
2. Quando rodar: clique **no sensor HC-SR04** (o de "dois olhos") ▸ aparece uma barra de **distância** ▸ arraste para mudar.
   Siga a tabela acima e veja LEDs, LCD e buzzer mudarem.
3. Clique **no potenciômetro** e gire para o máximo → vira Crítico por causa da chuva.
4. Embaixo aparece o **Serial Monitor** com linhas como `[leitura] {"codigoSensor":"AQG-001",...} risco_local=Atencao`
   — é a mensagem que vai para o servidor.

### Passo 3 — Gravar o vídeo (máx. 4:00)
| Tempo | Mostrar | Falar |
|---|---|---|
| 0:00–0:40 | `README.md` do projeto no GitHub (Ficha) | "O AquaGuard avisa quando a rua vai alagar. O circuito é a estação de campo que fica no córrego." |
| 0:40–1:20 | O circuito no Wokwi (parado) | Explique cada componente (seção "Entendendo o circuito"). |
| 1:20–2:40 | Simulação rodando: mude a distância 180 → 150 → 115 → 75; gire a chuva; aperte Silenciar | Narre a mudança de Normal até Crítico e o que cada luz significa. |
| 2:40–3:30 | Serial Monitor + (no PC) ligue `B_LIGAR_SERVIDOR_API.bat` e `C_SIMULAR_ENCHENTE.bat`, mostre o painel ficando Crítico | "Esta é a mesma mensagem JSON que o ESP32 envia. Quando chega à API, ela cria o alerta do bairro e o app do morador mostra PERIGO. As regras do sensor são as mesmas da API." |
| 3:30–4:00 | — | "O sensor avisa no local mesmo sem internet, custa pouco e dá dados em tempo real para a Defesa Civil." |

> Por que usamos o simulador no PC para mostrar a API? O Wokwi do site não consegue acessar um servidor que roda no seu
> computador (`localhost`). O `C_SIMULAR_ENCHENTE.bat` manda **exatamente a mesma mensagem** que o ESP32 mandaria.

## O que enviar no Teams
- **Anexo:** `integrantes.txt` (desta pasta, já com os links)
- **Texto:**
```
Global Solution 2026.2 – CitizenTech – AquaGuard – Physical Computing
Integrantes: Guilherme Cezarino Simoes e Fabrini Soares
Projeto Wokwi: https://wokwi.com/projects/XXXXXXXX
Vídeo (4 min): https://youtu.be/XXXXXXXX
Código e documentação: https://github.com/GuilhermeCezarinoSimoes/aquaguard-gs2026 (pasta /iot)
```

## Deu erro?
| Problema | Solução |
|---|---|
| Erro "LiquidCrystal_I2C.h: No such file" | Faltou o passo 5 (Library Manager) |
| Fica muito tempo em "Compiling" | Fila do site grátis; espere até 2–3 min ou recarregue a página |
| Simulação muito lenta | Normal no Wokwi grátis; espere alguns segundos entre as mudanças |
| O desenho ficou sem componentes | O `diagram.json` não foi colado inteiro. Repita o passo 4 com Ctrl+A |
| Serial mostra "falhou (modo offline)" | Sem problema: o circuito funciona offline (é uma qualidade do projeto) |
