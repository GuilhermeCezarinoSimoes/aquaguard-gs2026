# AquaGuard explicado de forma simples

Use este texto para entender o projeto e responder perguntas. **O edital pede que todos saibam explicar o projeto inteiro.**

## O problema
Em bairros como o **Jardim Pantanal** (Zona Leste de São Paulo), perto do Rio Tietê, a rua alaga quase todo verão.
O alerta da cidade é geral ("chuva forte em SP"), mas não diz se **a sua rua** vai encher. O morador só percebe quando a
água já está na porta e perde móveis, carro, documentos — e corre risco de doenças (leptospirose) e afogamento.

**Frase do problema:** "Quem mora perto de córregos de São Paulo só percebe a enchente quando a água já está na porta,
sem tempo de proteger a família e os bens."

## A solução, peça por peça
| Peça | O que faz, em palavras simples | Matéria |
|---|---|---|
| **Sensor (ESP32)** | Uma plaquinha eletrônica com um "sonar" (igual ao sensor de ré do carro) fica em cima do córrego e mede a distância até a água. Se a água sobe, a distância diminui. Também mede a chuva. Acende luz verde/amarela/vermelha e apita. Funciona **mesmo sem internet**. | Physical Computing |
| **API (servidor)** | Um programa que fica ligado recebendo as medidas dos sensores. Ele decide o nível de perigo (Normal, Atenção, Alerta, Perigo), guarda tudo num banco de dados e cria o alerta do bairro. | C# e SOA |
| **Aplicativo** | No celular, o morador escolhe o bairro e vê "Situação agora: PERIGO — água na rua, procure um lugar alto". Pode **relatar** "rua alagada" ou "bueiro entupido". Se estiver sem internet, o relato fica guardado e é enviado depois. | Mobile |
| **Previsão (IA)** | Um modelo de Machine Learning estudou **14 anos de dados reais** da estação do INMET (instituto oficial do clima) em São Paulo. Com os dados de hoje, ele diz se **amanhã** deve chover forte (≥ 20 mm). Acertou o aviso de **7 em cada 10** chuvas fortes no teste. | IA & ML |
| **Segurança** | Na pressa, as pessoas escrevem CPF, telefone, endereço ou doença no relato. O módulo detecta esses dados e **bloqueia** que eles vazem para lugares públicos. Calcula um "Risco Cidadão" de 0 a 100: caiu de **92 para 18** com a proteção. | Cybersecurity |
| **Servidor Linux** | Scripts que instalam e configuram tudo sozinhos num computador Linux. Se o programa cair, ele **volta sozinho em segundos**. Um vigia mede CPU, memória e disco e avisa se passar do limite. | Operating Systems |
| **Testes** | Lista das funcionalidades e dos testes que comprovam que elas funcionam, cadastrados no Azure (ferramenta da Microsoft). | Testing |

## Números para decorar
- 5 sensores em pontos reais de alagamento (simulados).
- 89 testes automáticos passando (47 do servidor, 37 de segurança, 5 do app).
- 14 anos de dados do INMET (2012–2025), mais de 122 mil medições por hora.
- Previsão: avisou 51 de 74 dias de chuva forte (69 %).
- Segurança: Risco Cidadão 92 → 18.
- Testing: 7 funcionalidades e 25 casos de teste.

## ODS da ONU (o edital exige citar)
- **ODS 11 – Cidades sustentáveis:** reduzir mortes e perdas em desastres (meta 11.5).
- **ODS 13 – Ação contra a mudança do clima:** cidades mais preparadas para chuvas extremas.
- **ODS 3 – Saúde:** menos afogamentos e leptospirose.
- **ODS 10 – Menos desigualdade:** as periferias são as mais atingidas.

## Perguntas que o professor pode fazer
- **"Por que o sensor calcula o risco sozinho se a API também calcula?"** — Porque na enchente a internet pode cair; o
  sensor continua apitando para quem está na rua.
- **"Os dados do ML são reais?"** — Sim, do INMET, estação A701 (Mirante de Santana). Nada simulado.
- **"O modelo é perfeito?"** — Não: chuva de verão é muito localizada. Por isso o aviso diz "chance elevada" e o sensor
  confirma em tempo real.
- **"Usaram IA para fazer?"** — Sim, como copiloto, permitido pelo edital. Está registrado em `prompts.md`.
- **"E os dados pessoais?"** — Não usamos dados reais de ninguém. Os relatos de teste são inventados e identificados como tal.

## Pequeno glossário
- **API:** programa que conversa com outros programas pela internet.
- **Banco de dados:** onde as informações ficam guardadas.
- **GitHub:** site onde se guarda e compartilha código. O "link do GitHub" é o endereço do projeto lá.
- **Wokwi:** site que simula circuitos eletrônicos.
- **Expo Go:** app que roda nosso aplicativo no celular sem precisar instalar pela loja.
- **Máquina virtual (VM):** um "computador dentro do computador", usado para rodar o Linux.
- **Swagger:** página automática que documenta e testa a API.
