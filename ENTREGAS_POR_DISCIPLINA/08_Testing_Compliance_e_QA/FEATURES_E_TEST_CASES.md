# AquaGuard · Testing, Compliance & Quality Assurance

**Integrantes:** Guilherme Cezarino Simoes · Fabrini Soares  
**Projeto Azure DevOps:** [https://dev.azure.com/Fabriniaraujo2306/AquaGuard](https://dev.azure.com/Fabriniaraujo2306/AquaGuard)  
**Totais:** 7 Features · 25 Test Cases (12 positivos, 13 negativos) · caixa-preta

## Features

### F01 — Ingestão de leituras IoT e cálculo de risco

**Descrição:** Como Defesa Civil, quero que cada sensor ESP32 envie nível da água e chuva para a API e que o sistema calcule automaticamente o nível de risco (Normal, Atenção, Alerta, Crítico), para identificar pontos de alagamento em tempo real.

**Critérios de aceite:**

1. Dado um sensor ativo cadastrado, quando o ESP32 envia POST /api/leituras com nível e chuva válidos, então a API responde 201 com a leitura e o risco calculado.
2. O risco é o pior caso entre: nível da água (60% do limite de alerta = Atenção; limite de alerta = Alerta; limite crítico = Crítico), chuva (≥10, ≥25, ≥50 mm/h) e a regra combinada (água subindo + chuva ≥ 25 mm/h).
3. Leituras com nível fora de 0–1000 cm, chuva fora de 0–500 mm/h ou data futura são rejeitadas (400/422) sem gravar.
4. Leituras de sensor inexistente retornam 404; sensor inativo retorna 422.
5. Quando a chave de dispositivo estiver configurada, requisições sem o cabeçalho X-Device-Key válido retornam 401.

**Test Cases:** TC01, TC02, TC03, TC04, TC05, TC06, TC07  
**Situação:** Implementada e testada (testes automatizados de integração)

### F02 — Alertas de alagamento por bairro

**Descrição:** Como morador de área de risco, quero receber um alerta do meu bairro quando o risco subir, com orientação clara do que fazer, para me proteger a tempo.

**Critérios de aceite:**

1. Quando uma leitura tiver risco ≥ Atenção e não houver alerta ativo no bairro, um alerta é criado com mensagem em linguagem simples.
2. Se já existir alerta ativo, ele é escalado para o nível maior; nunca é rebaixado automaticamente.
3. GET /api/alertas lista os alertas ativos (filtro por bairro), ordenados pelo nível.
4. Um agente pode encerrar o alerta (POST /api/alertas/{id}/encerrar); encerrar duas vezes retorna 422.
5. No app, a tela Início mostra o selo do risco (cor + ícone + texto) e as orientações do nível.

**Test Cases:** TC08, TC09, TC10  
**Situação:** Implementada e testada

### F03 — Relato colaborativo de ocorrências pelo cidadão

**Descrição:** Como cidadão, quero relatar pelo app uma rua alagada ou bueiro entupido, para avisar a comunidade e a prefeitura.

**Critérios de aceite:**

1. O formulário pede tipo, descrição (5–500 caracteres), gravidade (1–5) e apelido opcional; bairro vem da preferência do usuário.
2. Relato válido é salvo no banco local do celular e enviado à API; ao confirmar, mostra o protocolo (id) em Meus relatos.
3. Descrições com CPF, telefone ou e-mail são bloqueadas no app com mensagem explicativa (proteção de dados).
4. A API valida as mesmas regras e responde 400/422 para dados inválidos.
5. Status da ocorrência segue o fluxo Aberta → Em análise → Resolvida/Descartada; transições inválidas retornam 422.

**Test Cases:** TC11, TC12, TC13, TC14, TC15, TC16  
**Situação:** Implementada e testada (API automatizada; app validado manualmente na web)

### F04 — Painel consolidado de risco por bairro

**Descrição:** Como gestor da Defesa Civil, quero ver em um painel o risco atual, os alertas e as ocorrências abertas por bairro, para priorizar o atendimento.

**Critérios de aceite:**

1. GET /api/painel retorna risco geral, totais e uma linha por bairro (risco atual = maior risco da última leitura de cada sensor).
2. Bairros são ordenados do maior para o menor risco.
3. O painel web (/) atualiza a cada 10 s e exibe estado de erro se a API estiver indisponível.

**Test Cases:** TC17, TC18  
**Situação:** Implementada e testada

### F05 — Gestão de sensores (pontos monitorados)

**Descrição:** Como técnico, quero cadastrar sensores, calibrar limites e desativar pontos em manutenção.

**Critérios de aceite:**

1. POST /api/sensores cria sensor com código único (normalizado em maiúsculas); código duplicado retorna 422.
2. Limite crítico deve ser maior que o limite de alerta; caso contrário, 422.
3. DELETE /api/sensores/{id} desativa sem apagar o histórico; sensor desativado não aceita leituras.
4. GET /api/sensores/{id}/leituras retorna o histórico mais recente primeiro.

**Test Cases:** TC19, TC20, TC21  
**Situação:** Implementada e testada

### F06 — Uso do app sem internet (offline-first)

**Descrição:** Como morador de área com sinal fraco, quero consultar a última situação e registrar relatos mesmo sem conexão.

**Critérios de aceite:**

1. Sem conexão, o app exibe os últimos dados salvos (cache SQLite) com aviso de data/hora.
2. Sem cache, exibe dados de demonstração com aviso explícito.
3. Relato feito offline fica com status 'Aguardando conexão' e é enviado pelo botão 'Enviar pendentes'.

**Test Cases:** TC22, TC23  
**Situação:** Implementada (validação manual)

### F07 — Proteção de dados pessoais (PII) e Indicador de Risco Cidadão

**Descrição:** Como encarregado de dados (LGPD), quero detectar dados pessoais nos relatos e impedir que cheguem a logs, feed público, LLM ou terceiros, medindo o risco ao cidadão.

**Critérios de aceite:**

1. O motor detecta CPF/CNPJ (dígitos verificadores), cartão (Luhn), telefone, e-mail, endereço, senha, token e dados de saúde.
2. Fluxos contaminados para sinks inseguros são bloqueados e registrados em auditoria com hash encadeado.
3. O dashboard exibe o Indicador de Risco Cidadão (0–100) antes e depois da proteção.

**Test Cases:** TC24, TC25  
**Situação:** Implementada e testada (37 testes pytest)

## Test Cases

### TC01 — Registrar leitura normal (Positivo)

| Campo | Conteúdo |
|---|---|
| Feature | F01 |
| Objetivo | Verificar que leitura dentro dos limites é aceita com risco Normal. |
| Preparação | API em execução com seed; sensor AQG-005 (alerta 60 cm) ativo. |
| Entradas | `{"codigoSensor":"AQG-005","nivelAguaCm":5,"chuvaMmH":0}` |
| Saída esperada | HTTP 201; leitura.risco = Normal; alertaGerado = null. |

| # | Passo | Resultado esperado |
|---|---|---|
| 1 | Abrir o Swagger em /swagger e expandir POST /api/leituras | Endpoint exibido com exemplo |
| 2 | Informar o JSON de entrada e executar | HTTP 201 |
| 3 | Conferir o corpo da resposta | risco = 'Normal' e alertaGerado = null |

### TC02 — Leitura crítica gera alerta no bairro (Positivo)

| Campo | Conteúdo |
|---|---|
| Feature | F01 |
| Objetivo | Verificar cálculo Crítico e criação de alerta. |
| Preparação | Sensor AQG-004 (Ipiranga, alerta 100, crítico 150) ativo; nenhum alerta ativo em Ipiranga. |
| Entradas | `{"codigoSensor":"AQG-004","nivelAguaCm":160,"chuvaMmH":55}` |
| Saída esperada | HTTP 201; risco = Critico; alertaGerado.bairro = Ipiranga. |

| # | Passo | Resultado esperado |
|---|---|---|
| 1 | Enviar POST /api/leituras com a entrada | HTTP 201 |
| 2 | Verificar leitura.risco | Critico |
| 3 | Executar GET /api/alertas?bairro=Ipiranga | Lista contém alerta ativo nível Critico |

### TC03 — Regra combinada água + chuva (Positivo)

| Campo | Conteúdo |
|---|---|
| Feature | F01 |
| Objetivo | Verificar que água acima de 60% do alerta com chuva forte resulta em Alerta. |
| Preparação | Sensor AQG-004 ativo. |
| Entradas | `{"codigoSensor":"AQG-004","nivelAguaCm":70,"chuvaMmH":30}` |
| Saída esperada | risco = Alerta. |

| # | Passo | Resultado esperado |
|---|---|---|
| 1 | Enviar POST /api/leituras | HTTP 201 |
| 2 | Verificar leitura.risco | Alerta |

### TC04 — Nível da água fora da faixa (Negativo)

| Campo | Conteúdo |
|---|---|
| Feature | F01 |
| Objetivo | Garantir rejeição de valores impossíveis. |
| Preparação | API em execução. |
| Entradas | `{"codigoSensor":"AQG-001","nivelAguaCm":-5,"chuvaMmH":0}` |
| Saída esperada | HTTP 400 com erro de validação; nada gravado. |

| # | Passo | Resultado esperado |
|---|---|---|
| 1 | Enviar POST /api/leituras com nível negativo | HTTP 400 |
| 2 | Consultar GET /api/sensores/1/leituras?horas=1 | Nenhuma leitura com -5 cm |

### TC05 — Sensor inexistente (Negativo)

| Campo | Conteúdo |
|---|---|
| Feature | F01 |
| Objetivo | Garantir que códigos desconhecidos são rejeitados. |
| Preparação | API em execução. |
| Entradas | `{"codigoSensor":"XYZ-999","nivelAguaCm":10,"chuvaMmH":0}` |
| Saída esperada | HTTP 404 'Sensor XYZ-999 não encontrado'. |

| # | Passo | Resultado esperado |
|---|---|---|
| 1 | Enviar POST /api/leituras | HTTP 404 com ProblemDetails |

### TC06 — Dispositivo sem chave (Negativo)

| Campo | Conteúdo |
|---|---|
| Feature | F01 |
| Objetivo | Garantir que só dispositivos autorizados enviam leituras. |
| Preparação | API iniciada com AquaGuard__DeviceKey configurada. |
| Entradas | `POST /api/leituras sem cabeçalho X-Device-Key` |
| Saída esperada | HTTP 401 'Dispositivo não autorizado'. |

| # | Passo | Resultado esperado |
|---|---|---|
| 1 | Enviar leitura válida sem o cabeçalho | HTTP 401 |
| 2 | Reenviar com X-Device-Key correto | HTTP 201 |

### TC07 — Leitura em sensor desativado (Negativo)

| Campo | Conteúdo |
|---|---|
| Feature | F01 |
| Objetivo | Garantir que pontos em manutenção não recebem dados. |
| Preparação | Sensor desativado via DELETE /api/sensores/{id}. |
| Entradas | `POST /api/leituras para o sensor desativado` |
| Saída esperada | HTTP 422 'Sensor ... está inativo'. |

| # | Passo | Resultado esperado |
|---|---|---|
| 1 | Executar DELETE /api/sensores/{id} | HTTP 204 |
| 2 | Enviar leitura para o mesmo código | HTTP 422 |

### TC08 — Escalonamento de alerta (Positivo)

| Campo | Conteúdo |
|---|---|
| Feature | F02 |
| Objetivo | Verificar que alerta ativo sobe de nível e não é rebaixado. |
| Preparação | Alerta ativo nível Atenção no bairro Aricanduva (sensor AQG-003). |
| Entradas | Leituras: 60 cm/12 mm/h (Atenção) e depois 145 cm/0 (Crítico) e depois 10 cm/0 (Normal) |
| Saída esperada | Alerta único do bairro termina no nível Critico. |

| # | Passo | Resultado esperado |
|---|---|---|
| 1 | Enviar as três leituras em sequência | HTTP 201 em todas |
| 2 | GET /api/alertas?bairro=Aricanduva | Um alerta ativo, nível Critico |

### TC09 — App exibe alerta e orientação (Positivo)

| Campo | Conteúdo |
|---|---|
| Feature | F02 |
| Objetivo | Verificar a tela Início para o bairro com alerta. |
| Preparação | App aberto; bairro Jardim Pantanal com alerta Crítico. |
| Entradas | Abrir a aba Início |
| Saída esperada | Cartão vermelho 'Perigo', orientações e o alerta listado. |

| # | Passo | Resultado esperado |
|---|---|---|
| 1 | Abrir o app na aba Início | Título 'Jardim Pantanal' |
| 2 | Ler o cartão de situação | Texto 'Perigo' e 'Água na rua. Proteja-se agora.' |
| 3 | Rolar até 'Alertas no bairro' | Alerta com selo Perigo e data de emissão |

### TC10 — Encerrar alerta já encerrado (Negativo)

| Campo | Conteúdo |
|---|---|
| Feature | F02 |
| Objetivo | Garantir regra de negócio de encerramento. |
| Preparação | Alerta id=1 encerrado. |
| Entradas | `POST /api/alertas/1/encerrar (2ª vez)` |
| Saída esperada | HTTP 422 'Alerta já encerrado'. |

| # | Passo | Resultado esperado |
|---|---|---|
| 1 | Encerrar o alerta 1 | HTTP 200, ativo = false |
| 2 | Encerrar novamente | HTTP 422 |

### TC11 — Enviar relato pelo app (Positivo)

| Campo | Conteúdo |
|---|---|
| Feature | F03 |
| Objetivo | Verificar registro e envio do relato. |
| Preparação | App e API em execução; bairro Jardim Pantanal. |
| Entradas | Tipo Rua alagada; descrição 'Água na altura do joelho na esquina da escola'; gravidade 3 |
| Saída esperada | Relato aparece em Meus relatos com status Enviado e protocolo. |

| # | Passo | Resultado esperado |
|---|---|---|
| 1 | Abrir a aba Relatar | Formulário exibido |
| 2 | Preencher os campos | Contador mostra caracteres |
| 3 | Tocar em Enviar relato | Mensagem de agradecimento |
| 4 | Abrir Meus relatos | Item com 'Enviado' e 'protocolo #N' |

### TC12 — Relato com CPF é bloqueado (Negativo)

| Campo | Conteúdo |
|---|---|
| Feature | F03 |
| Objetivo | Garantir que dados pessoais não sejam publicados. |
| Preparação | App aberto na aba Relatar. |
| Entradas | Descrição 'Rua alagada, meu CPF 123.456.789-09' |
| Saída esperada | Mensagem 'Por segurança, não informe CPF, telefone ou e-mail'; nada enviado. |

| # | Passo | Resultado esperado |
|---|---|---|
| 1 | Digitar a descrição com CPF | Texto aceito no campo |
| 2 | Tocar em Enviar relato | Mensagem de erro em vermelho |
| 3 | Abrir Meus relatos | Relato não aparece |

### TC13 — Descrição curta (Negativo)

| Campo | Conteúdo |
|---|---|
| Feature | F03 |
| Objetivo | Validar tamanho mínimo. |
| Preparação | App na aba Relatar. |
| Entradas | Descrição 'abc' |
| Saída esperada | Mensagem 'Descreva o problema com pelo menos 5 caracteres'. |

| # | Passo | Resultado esperado |
|---|---|---|
| 1 | Digitar 'abc' e enviar | Erro de validação exibido |

### TC14 — Fluxo de status da ocorrência (Positivo)

| Campo | Conteúdo |
|---|---|
| Feature | F03 |
| Objetivo | Verificar a máquina de estados. |
| Preparação | Ocorrência aberta id=N. |
| Entradas | `PATCH /api/ocorrencias/N/status {"acao":"IniciarAnalise"} e depois {"acao":"Resolver"}` |
| Saída esperada | Status EmAnalise e depois Resolvida com data. |

| # | Passo | Resultado esperado |
|---|---|---|
| 1 | Enviar IniciarAnalise | HTTP 200, status EmAnalise |
| 2 | Enviar Resolver | HTTP 200, status Resolvida, resolvidaEmUtc preenchido |

### TC15 — Resolver ocorrência já resolvida (Negativo)

| Campo | Conteúdo |
|---|---|
| Feature | F03 |
| Objetivo | Garantir que ocorrência encerrada não muda. |
| Preparação | Ocorrência N resolvida. |
| Entradas | `{"acao":"Resolver"}` |
| Saída esperada | HTTP 422. |

| # | Passo | Resultado esperado |
|---|---|---|
| 1 | Enviar Resolver novamente | HTTP 422 'Ocorrência já foi encerrada' |

### TC16 — Severidade inválida na API (Negativo)

| Campo | Conteúdo |
|---|---|
| Feature | F03 |
| Objetivo | Validar faixa 1–5 na API. |
| Preparação | API em execução. |
| Entradas | `{"tipo":"RuaAlagada","descricao":"Rua alagada","bairro":"Centro","latitude":-23.5,"longitude":-46.6,"severidade":9}` |
| Saída esperada | HTTP 400 com erro no campo Severidade. |

| # | Passo | Resultado esperado |
|---|---|---|
| 1 | Enviar POST /api/ocorrencias | HTTP 400 |

### TC17 — Painel ordena bairros por risco (Positivo)

| Campo | Conteúdo |
|---|---|
| Feature | F04 |
| Objetivo | Verificar consolidação. |
| Preparação | Leitura crítica registrada no Ipiranga (TC02). |
| Entradas | `GET /api/painel` |
| Saída esperada | riscoGeral = Critico; primeiro bairro = Ipiranga. |

| # | Passo | Resultado esperado |
|---|---|---|
| 1 | Executar GET /api/painel | HTTP 200 |
| 2 | Ver bairros[0] | Ipiranga, riscoAtual Critico |

### TC18 — Painel web sem API (Negativo)

| Campo | Conteúdo |
|---|---|
| Feature | F04 |
| Objetivo | Verificar mensagem de erro amigável. |
| Preparação | Painel aberto; API parada. |
| Entradas | Aguardar atualização (10 s) |
| Saída esperada | Mensagem 'Não foi possível carregar os dados da API.' |

| # | Passo | Resultado esperado |
|---|---|---|
| 1 | Parar a API | Serviço parado |
| 2 | Aguardar 10 s no painel | Mensagem de erro visível |

### TC19 — Cadastrar sensor (Positivo)

| Campo | Conteúdo |
|---|---|
| Feature | F05 |
| Objetivo | Verificar criação. |
| Preparação | API em execução. |
| Entradas | `{"codigo":"aqg-100","nome":"Ponto novo","bairro":"Centro","latitude":-23.55,"longitude":-46.63,"nivelAlertaCm":50,"nivelCriticoCm":90}` |
| Saída esperada | HTTP 201; codigo = 'AQG-100'. |

| # | Passo | Resultado esperado |
|---|---|---|
| 1 | Enviar POST /api/sensores | HTTP 201 e header Location |
| 2 | GET /api/sensores?bairro=Centro | Sensor listado |

### TC20 — Código de sensor duplicado (Negativo)

| Campo | Conteúdo |
|---|---|
| Feature | F05 |
| Objetivo | Garantir unicidade. |
| Preparação | Sensor AQG-001 existente. |
| Entradas | `POST /api/sensores com codigo AQG-001` |
| Saída esperada | HTTP 422. |

| # | Passo | Resultado esperado |
|---|---|---|
| 1 | Enviar o cadastro duplicado | HTTP 422 'Já existe um sensor com o código' |

### TC21 — Limite crítico menor que alerta (Negativo)

| Campo | Conteúdo |
|---|---|
| Feature | F05 |
| Objetivo | Validar regra de calibração. |
| Preparação | Sensor id=1. |
| Entradas | `PUT /api/sensores/1/limites {"nivelAlertaCm":120,"nivelCriticoCm":80}` |
| Saída esperada | HTTP 422. |

| # | Passo | Resultado esperado |
|---|---|---|
| 1 | Enviar a recalibração | HTTP 422 'Nível crítico deve ser maior' |

### TC22 — Consulta offline com cache (Positivo)

| Campo | Conteúdo |
|---|---|
| Feature | F06 |
| Objetivo | Verificar uso dos dados salvos. |
| Preparação | App aberto uma vez com internet; depois sem conexão com a API. |
| Entradas | Abrir a aba Início sem API |
| Saída esperada | Aviso amarelo 'Sem conexão. Mostrando dados salvos de <data>'. |

| # | Passo | Resultado esperado |
|---|---|---|
| 1 | Abrir o app com a API ativa | Dados carregados |
| 2 | Parar a API e puxar para atualizar | Aviso de dados salvos e dados exibidos |

### TC23 — Relato offline sincroniza depois (Positivo)

| Campo | Conteúdo |
|---|---|
| Feature | F06 |
| Objetivo | Verificar fila de envio. |
| Preparação | API parada. |
| Entradas | Relato válido |
| Saída esperada | Status 'Aguardando conexão'; após religar a API e tocar 'Enviar pendentes', status 'Enviado'. |

| # | Passo | Resultado esperado |
|---|---|---|
| 1 | Enviar relato com a API parada | Mensagem 'ficou salvo no celular' |
| 2 | Abrir Meus relatos | Status Aguardando conexão |
| 3 | Ligar a API e tocar 'Enviar pendentes' | Status Enviado e protocolo |

### TC24 — Auditoria detecta e bloqueia PII (Positivo)

| Campo | Conteúdo |
|---|---|
| Feature | F07 |
| Objetivo | Verificar motor de PII e taint. |
| Preparação | Ambiente Python do módulo cybersecurity. |
| Entradas | `python -m aquaguard_sec --sem-llm` |
| Saída esperada | PII detectadas, fluxos bloqueados, IRC antes > depois, auditoria íntegra. |

| # | Passo | Resultado esperado |
|---|---|---|
| 1 | Executar o comando | Saída com 'PII detectadas' e 'bloqueados' |
| 2 | Abrir saida/dashboard.html | Dois medidores de IRC |
| 3 | Ver 'Auditoria íntegra: True' | Hashes válidos |

### TC25 — CPF com dígito inválido não é PII (Negativo)

| Campo | Conteúdo |
|---|---|
| Feature | F07 |
| Objetivo | Garantir baixa taxa de falso positivo. |
| Preparação | Ambiente de testes. |
| Entradas | Texto 'protocolo 123.456.789-00' |
| Saída esperada | Nenhum achado. |

| # | Passo | Resultado esperado |
|---|---|---|
| 1 | Executar pytest -k falso_positivo | Testes passam |

## Matriz de rastreabilidade

| Feature | Positivos | Negativos | Automação |
|---|---|---|---|
| F01 Ingestão de leituras IoT e cálculo de risco | TC01, TC02, TC03 | TC04, TC05, TC06, TC07 | Implementada e testada (testes automatizados de integração) |
| F02 Alertas de alagamento por bairro | TC08, TC09 | TC10 | Implementada e testada |
| F03 Relato colaborativo de ocorrências pelo cidadão | TC11, TC14 | TC12, TC13, TC15, TC16 | Implementada e testada (API automatizada; app validado manualmente na web) |
| F04 Painel consolidado de risco por bairro | TC17 | TC18 | Implementada e testada |
| F05 Gestão de sensores (pontos monitorados) | TC19 | TC20, TC21 | Implementada e testada |
| F06 Uso do app sem internet (offline-first) | TC22, TC23 |  | Implementada (validação manual) |
| F07 Proteção de dados pessoais (PII) e Indicador de Risco Cidadão | TC24 | TC25 | Implementada e testada (37 testes pytest) |
