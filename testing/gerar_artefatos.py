"""Fonte única das Features e Test Cases do AquaGuard.

Gera:
  * FEATURES_E_TEST_CASES.md      — documento legível (base do PDF de entrega)
  * azure_import_features.csv     — importação em Azure Boards (Boards ▸ Work items ▸ Import Work Items)
  * azure_import_test_cases.csv   — importação de Test Cases com passos (Action / Expected Result)

Executar:  python gerar_artefatos.py
"""
from __future__ import annotations

import csv
import pathlib

AQUI = pathlib.Path(__file__).resolve().parent
AREA = "AquaGuard"

FEATURES = [
    {
        "id": "F01", "titulo": "Ingestão de leituras IoT e cálculo de risco",
        "descricao": "Como Defesa Civil, quero que cada sensor ESP32 envie nível da água e chuva para a API e que o "
                     "sistema calcule automaticamente o nível de risco (Normal, Atenção, Alerta, Crítico), para "
                     "identificar pontos de alagamento em tempo real.",
        "criterios": [
            "Dado um sensor ativo cadastrado, quando o ESP32 envia POST /api/leituras com nível e chuva válidos, então a API responde 201 com a leitura e o risco calculado.",
            "O risco é o pior caso entre: nível da água (60% do limite de alerta = Atenção; limite de alerta = Alerta; limite crítico = Crítico), chuva (≥10, ≥25, ≥50 mm/h) e a regra combinada (água subindo + chuva ≥ 25 mm/h).",
            "Leituras com nível fora de 0–1000 cm, chuva fora de 0–500 mm/h ou data futura são rejeitadas (400/422) sem gravar.",
            "Leituras de sensor inexistente retornam 404; sensor inativo retorna 422.",
            "Quando a chave de dispositivo estiver configurada, requisições sem o cabeçalho X-Device-Key válido retornam 401.",
        ],
        "status": "Implementada e testada (testes automatizados de integração)",
    },
    {
        "id": "F02", "titulo": "Alertas de alagamento por bairro",
        "descricao": "Como morador de área de risco, quero receber um alerta do meu bairro quando o risco subir, com "
                     "orientação clara do que fazer, para me proteger a tempo.",
        "criterios": [
            "Quando uma leitura tiver risco ≥ Atenção e não houver alerta ativo no bairro, um alerta é criado com mensagem em linguagem simples.",
            "Se já existir alerta ativo, ele é escalado para o nível maior; nunca é rebaixado automaticamente.",
            "GET /api/alertas lista os alertas ativos (filtro por bairro), ordenados pelo nível.",
            "Um agente pode encerrar o alerta (POST /api/alertas/{id}/encerrar); encerrar duas vezes retorna 422.",
            "No app, a tela Início mostra o selo do risco (cor + ícone + texto) e as orientações do nível.",
        ],
        "status": "Implementada e testada",
    },
    {
        "id": "F03", "titulo": "Relato colaborativo de ocorrências pelo cidadão",
        "descricao": "Como cidadão, quero relatar pelo app uma rua alagada ou bueiro entupido, para avisar a "
                     "comunidade e a prefeitura.",
        "criterios": [
            "O formulário pede tipo, descrição (5–500 caracteres), gravidade (1–5) e apelido opcional; bairro vem da preferência do usuário.",
            "Relato válido é salvo no banco local do celular e enviado à API; ao confirmar, mostra o protocolo (id) em Meus relatos.",
            "Descrições com CPF, telefone ou e-mail são bloqueadas no app com mensagem explicativa (proteção de dados).",
            "A API valida as mesmas regras e responde 400/422 para dados inválidos.",
            "Status da ocorrência segue o fluxo Aberta → Em análise → Resolvida/Descartada; transições inválidas retornam 422.",
        ],
        "status": "Implementada e testada (API automatizada; app validado manualmente na web)",
    },
    {
        "id": "F04", "titulo": "Painel consolidado de risco por bairro",
        "descricao": "Como gestor da Defesa Civil, quero ver em um painel o risco atual, os alertas e as ocorrências "
                     "abertas por bairro, para priorizar o atendimento.",
        "criterios": [
            "GET /api/painel retorna risco geral, totais e uma linha por bairro (risco atual = maior risco da última leitura de cada sensor).",
            "Bairros são ordenados do maior para o menor risco.",
            "O painel web (/) atualiza a cada 10 s e exibe estado de erro se a API estiver indisponível.",
        ],
        "status": "Implementada e testada",
    },
    {
        "id": "F05", "titulo": "Gestão de sensores (pontos monitorados)",
        "descricao": "Como técnico, quero cadastrar sensores, calibrar limites e desativar pontos em manutenção.",
        "criterios": [
            "POST /api/sensores cria sensor com código único (normalizado em maiúsculas); código duplicado retorna 422.",
            "Limite crítico deve ser maior que o limite de alerta; caso contrário, 422.",
            "DELETE /api/sensores/{id} desativa sem apagar o histórico; sensor desativado não aceita leituras.",
            "GET /api/sensores/{id}/leituras retorna o histórico mais recente primeiro.",
        ],
        "status": "Implementada e testada",
    },
    {
        "id": "F06", "titulo": "Uso do app sem internet (offline-first)",
        "descricao": "Como morador de área com sinal fraco, quero consultar a última situação e registrar relatos "
                     "mesmo sem conexão.",
        "criterios": [
            "Sem conexão, o app exibe os últimos dados salvos (cache SQLite) com aviso de data/hora.",
            "Sem cache, exibe dados de demonstração com aviso explícito.",
            "Relato feito offline fica com status 'Aguardando conexão' e é enviado pelo botão 'Enviar pendentes'.",
        ],
        "status": "Implementada (validação manual)",
    },
    {
        "id": "F07", "titulo": "Proteção de dados pessoais (PII) e Indicador de Risco Cidadão",
        "descricao": "Como encarregado de dados (LGPD), quero detectar dados pessoais nos relatos e impedir que "
                     "cheguem a logs, feed público, LLM ou terceiros, medindo o risco ao cidadão.",
        "criterios": [
            "O motor detecta CPF/CNPJ (dígitos verificadores), cartão (Luhn), telefone, e-mail, endereço, senha, token e dados de saúde.",
            "Fluxos contaminados para sinks inseguros são bloqueados e registrados em auditoria com hash encadeado.",
            "O dashboard exibe o Indicador de Risco Cidadão (0–100) antes e depois da proteção.",
        ],
        "status": "Implementada e testada (37 testes pytest)",
    },
]

# Cada caso: (id, feature, tipo, titulo, objetivo, preparacao, entradas, saida, passos[(acao, esperado)])
CASOS = [
    ("TC01", "F01", "Positivo", "Registrar leitura normal",
     "Verificar que leitura dentro dos limites é aceita com risco Normal.",
     "API em execução com seed; sensor AQG-005 (alerta 60 cm) ativo.",
     '{"codigoSensor":"AQG-005","nivelAguaCm":5,"chuvaMmH":0}', "HTTP 201; leitura.risco = Normal; alertaGerado = null.",
     [("Abrir o Swagger em /swagger e expandir POST /api/leituras", "Endpoint exibido com exemplo"),
      ("Informar o JSON de entrada e executar", "HTTP 201"),
      ("Conferir o corpo da resposta", "risco = 'Normal' e alertaGerado = null")]),
    ("TC02", "F01", "Positivo", "Leitura crítica gera alerta no bairro",
     "Verificar cálculo Crítico e criação de alerta.",
     "Sensor AQG-004 (Ipiranga, alerta 100, crítico 150) ativo; nenhum alerta ativo em Ipiranga.",
     '{"codigoSensor":"AQG-004","nivelAguaCm":160,"chuvaMmH":55}', "HTTP 201; risco = Critico; alertaGerado.bairro = Ipiranga.",
     [("Enviar POST /api/leituras com a entrada", "HTTP 201"),
      ("Verificar leitura.risco", "Critico"),
      ("Executar GET /api/alertas?bairro=Ipiranga", "Lista contém alerta ativo nível Critico")]),
    ("TC03", "F01", "Positivo", "Regra combinada água + chuva",
     "Verificar que água acima de 60% do alerta com chuva forte resulta em Alerta.",
     "Sensor AQG-004 ativo.", '{"codigoSensor":"AQG-004","nivelAguaCm":70,"chuvaMmH":30}', "risco = Alerta.",
     [("Enviar POST /api/leituras", "HTTP 201"), ("Verificar leitura.risco", "Alerta")]),
    ("TC04", "F01", "Negativo", "Nível da água fora da faixa",
     "Garantir rejeição de valores impossíveis.", "API em execução.",
     '{"codigoSensor":"AQG-001","nivelAguaCm":-5,"chuvaMmH":0}', "HTTP 400 com erro de validação; nada gravado.",
     [("Enviar POST /api/leituras com nível negativo", "HTTP 400"),
      ("Consultar GET /api/sensores/1/leituras?horas=1", "Nenhuma leitura com -5 cm")]),
    ("TC05", "F01", "Negativo", "Sensor inexistente",
     "Garantir que códigos desconhecidos são rejeitados.", "API em execução.",
     '{"codigoSensor":"XYZ-999","nivelAguaCm":10,"chuvaMmH":0}', "HTTP 404 'Sensor XYZ-999 não encontrado'.",
     [("Enviar POST /api/leituras", "HTTP 404 com ProblemDetails")]),
    ("TC06", "F01", "Negativo", "Dispositivo sem chave",
     "Garantir que só dispositivos autorizados enviam leituras.",
     "API iniciada com AquaGuard__DeviceKey configurada.",
     "POST /api/leituras sem cabeçalho X-Device-Key", "HTTP 401 'Dispositivo não autorizado'.",
     [("Enviar leitura válida sem o cabeçalho", "HTTP 401"),
      ("Reenviar com X-Device-Key correto", "HTTP 201")]),
    ("TC07", "F01", "Negativo", "Leitura em sensor desativado",
     "Garantir que pontos em manutenção não recebem dados.", "Sensor desativado via DELETE /api/sensores/{id}.",
     "POST /api/leituras para o sensor desativado", "HTTP 422 'Sensor ... está inativo'.",
     [("Executar DELETE /api/sensores/{id}", "HTTP 204"), ("Enviar leitura para o mesmo código", "HTTP 422")]),
    ("TC08", "F02", "Positivo", "Escalonamento de alerta",
     "Verificar que alerta ativo sobe de nível e não é rebaixado.",
     "Alerta ativo nível Atenção no bairro Aricanduva (sensor AQG-003).",
     "Leituras: 60 cm/12 mm/h (Atenção) e depois 145 cm/0 (Crítico) e depois 10 cm/0 (Normal)",
     "Alerta único do bairro termina no nível Critico.",
     [("Enviar as três leituras em sequência", "HTTP 201 em todas"),
      ("GET /api/alertas?bairro=Aricanduva", "Um alerta ativo, nível Critico")]),
    ("TC09", "F02", "Positivo", "App exibe alerta e orientação",
     "Verificar a tela Início para o bairro com alerta.", "App aberto; bairro Jardim Pantanal com alerta Crítico.",
     "Abrir a aba Início", "Cartão vermelho 'Perigo', orientações e o alerta listado.",
     [("Abrir o app na aba Início", "Título 'Jardim Pantanal'"),
      ("Ler o cartão de situação", "Texto 'Perigo' e 'Água na rua. Proteja-se agora.'"),
      ("Rolar até 'Alertas no bairro'", "Alerta com selo Perigo e data de emissão")]),
    ("TC10", "F02", "Negativo", "Encerrar alerta já encerrado",
     "Garantir regra de negócio de encerramento.", "Alerta id=1 encerrado.",
     "POST /api/alertas/1/encerrar (2ª vez)", "HTTP 422 'Alerta já encerrado'.",
     [("Encerrar o alerta 1", "HTTP 200, ativo = false"), ("Encerrar novamente", "HTTP 422")]),
    ("TC11", "F03", "Positivo", "Enviar relato pelo app",
     "Verificar registro e envio do relato.", "App e API em execução; bairro Jardim Pantanal.",
     "Tipo Rua alagada; descrição 'Água na altura do joelho na esquina da escola'; gravidade 3",
     "Relato aparece em Meus relatos com status Enviado e protocolo.",
     [("Abrir a aba Relatar", "Formulário exibido"), ("Preencher os campos", "Contador mostra caracteres"),
      ("Tocar em Enviar relato", "Mensagem de agradecimento"),
      ("Abrir Meus relatos", "Item com 'Enviado' e 'protocolo #N'")]),
    ("TC12", "F03", "Negativo", "Relato com CPF é bloqueado",
     "Garantir que dados pessoais não sejam publicados.", "App aberto na aba Relatar.",
     "Descrição 'Rua alagada, meu CPF 123.456.789-09'", "Mensagem 'Por segurança, não informe CPF, telefone ou e-mail'; nada enviado.",
     [("Digitar a descrição com CPF", "Texto aceito no campo"), ("Tocar em Enviar relato", "Mensagem de erro em vermelho"),
      ("Abrir Meus relatos", "Relato não aparece")]),
    ("TC13", "F03", "Negativo", "Descrição curta",
     "Validar tamanho mínimo.", "App na aba Relatar.", "Descrição 'abc'", "Mensagem 'Descreva o problema com pelo menos 5 caracteres'.",
     [("Digitar 'abc' e enviar", "Erro de validação exibido")]),
    ("TC14", "F03", "Positivo", "Fluxo de status da ocorrência",
     "Verificar a máquina de estados.", "Ocorrência aberta id=N.",
     'PATCH /api/ocorrencias/N/status {"acao":"IniciarAnalise"} e depois {"acao":"Resolver"}', "Status EmAnalise e depois Resolvida com data.",
     [("Enviar IniciarAnalise", "HTTP 200, status EmAnalise"), ("Enviar Resolver", "HTTP 200, status Resolvida, resolvidaEmUtc preenchido")]),
    ("TC15", "F03", "Negativo", "Resolver ocorrência já resolvida",
     "Garantir que ocorrência encerrada não muda.", "Ocorrência N resolvida.",
     '{"acao":"Resolver"}', "HTTP 422.", [("Enviar Resolver novamente", "HTTP 422 'Ocorrência já foi encerrada'")]),
    ("TC16", "F03", "Negativo", "Severidade inválida na API",
     "Validar faixa 1–5 na API.", "API em execução.",
     '{"tipo":"RuaAlagada","descricao":"Rua alagada","bairro":"Centro","latitude":-23.5,"longitude":-46.6,"severidade":9}',
     "HTTP 400 com erro no campo Severidade.", [("Enviar POST /api/ocorrencias", "HTTP 400")]),
    ("TC17", "F04", "Positivo", "Painel ordena bairros por risco",
     "Verificar consolidação.", "Leitura crítica registrada no Ipiranga (TC02).",
     "GET /api/painel", "riscoGeral = Critico; primeiro bairro = Ipiranga.",
     [("Executar GET /api/painel", "HTTP 200"), ("Ver bairros[0]", "Ipiranga, riscoAtual Critico")]),
    ("TC18", "F04", "Negativo", "Painel web sem API",
     "Verificar mensagem de erro amigável.", "Painel aberto; API parada.",
     "Aguardar atualização (10 s)", "Mensagem 'Não foi possível carregar os dados da API.'",
     [("Parar a API", "Serviço parado"), ("Aguardar 10 s no painel", "Mensagem de erro visível")]),
    ("TC19", "F05", "Positivo", "Cadastrar sensor",
     "Verificar criação.", "API em execução.",
     '{"codigo":"aqg-100","nome":"Ponto novo","bairro":"Centro","latitude":-23.55,"longitude":-46.63,"nivelAlertaCm":50,"nivelCriticoCm":90}',
     "HTTP 201; codigo = 'AQG-100'.", [("Enviar POST /api/sensores", "HTTP 201 e header Location"), ("GET /api/sensores?bairro=Centro", "Sensor listado")]),
    ("TC20", "F05", "Negativo", "Código de sensor duplicado",
     "Garantir unicidade.", "Sensor AQG-001 existente.", "POST /api/sensores com codigo AQG-001", "HTTP 422.",
     [("Enviar o cadastro duplicado", "HTTP 422 'Já existe um sensor com o código'")]),
    ("TC21", "F05", "Negativo", "Limite crítico menor que alerta",
     "Validar regra de calibração.", "Sensor id=1.", 'PUT /api/sensores/1/limites {"nivelAlertaCm":120,"nivelCriticoCm":80}',
     "HTTP 422.", [("Enviar a recalibração", "HTTP 422 'Nível crítico deve ser maior'")]),
    ("TC22", "F06", "Positivo", "Consulta offline com cache",
     "Verificar uso dos dados salvos.", "App aberto uma vez com internet; depois sem conexão com a API.",
     "Abrir a aba Início sem API", "Aviso amarelo 'Sem conexão. Mostrando dados salvos de <data>'.",
     [("Abrir o app com a API ativa", "Dados carregados"), ("Parar a API e puxar para atualizar", "Aviso de dados salvos e dados exibidos")]),
    ("TC23", "F06", "Positivo", "Relato offline sincroniza depois",
     "Verificar fila de envio.", "API parada.", "Relato válido", "Status 'Aguardando conexão'; após religar a API e tocar 'Enviar pendentes', status 'Enviado'.",
     [("Enviar relato com a API parada", "Mensagem 'ficou salvo no celular'"), ("Abrir Meus relatos", "Status Aguardando conexão"),
      ("Ligar a API e tocar 'Enviar pendentes'", "Status Enviado e protocolo")]),
    ("TC24", "F07", "Positivo", "Auditoria detecta e bloqueia PII",
     "Verificar motor de PII e taint.", "Ambiente Python do módulo cybersecurity.",
     "python -m aquaguard_sec --sem-llm", "PII detectadas, fluxos bloqueados, IRC antes > depois, auditoria íntegra.",
     [("Executar o comando", "Saída com 'PII detectadas' e 'bloqueados'"), ("Abrir saida/dashboard.html", "Dois medidores de IRC"),
      ("Ver 'Auditoria íntegra: True'", "Hashes válidos")]),
    ("TC25", "F07", "Negativo", "CPF com dígito inválido não é PII",
     "Garantir baixa taxa de falso positivo.", "Ambiente de testes.", "Texto 'protocolo 123.456.789-00'", "Nenhum achado.",
     [("Executar pytest -k falso_positivo", "Testes passam")]),
]


def gerar_markdown() -> str:
    linhas = ["# AquaGuard · Testing, Compliance & Quality Assurance", "",
              "**Integrantes:** Guilherme Cezarino Simoes (RM 557724) · Fabrini Soares (RM 557813) · João Both (RM 558690)  ",
              "**Projeto Azure DevOps:** [https://dev.azure.com/Fabriniaraujo2306/AquaGuard](https://dev.azure.com/Fabriniaraujo2306/AquaGuard)  ",
              f"**Totais:** {len(FEATURES)} Features · {len(CASOS)} Test Cases "
              f"({sum(c[2] == 'Positivo' for c in CASOS)} positivos, {sum(c[2] == 'Negativo' for c in CASOS)} negativos) · caixa-preta", "",
              "## Features", ""]
    for f in FEATURES:
        linhas += [f"### {f['id']} — {f['titulo']}", "", f"**Descrição:** {f['descricao']}", "", "**Critérios de aceite:**", ""]
        linhas += [f"{i}. {c}" for i, c in enumerate(f["criterios"], 1)]
        tcs = ", ".join(c[0] for c in CASOS if c[1] == f["id"])
        linhas += ["", f"**Test Cases:** {tcs}  ", f"**Situação:** {f['status']}", ""]
    linhas += ["## Test Cases", ""]
    for c in CASOS:
        tc, feat, tipo, titulo, obj, prep, ent, saida, passos = c
        linhas += [f"### {tc} — {titulo} ({tipo})", "", "| Campo | Conteúdo |", "|---|---|",
                   f"| Feature | {feat} |", f"| Objetivo | {obj} |", f"| Preparação | {prep} |",
                   f"| Entradas | `{ent}` |" if ent.startswith(("{", "POST", "GET", "PATCH", "PUT", "python")) else f"| Entradas | {ent} |",
                   f"| Saída esperada | {saida} |", "", "| # | Passo | Resultado esperado |", "|---|---|---|"]
        linhas += [f"| {i} | {a} | {e} |" for i, (a, e) in enumerate(passos, 1)]
        linhas.append("")
    linhas += ["## Matriz de rastreabilidade", "", "| Feature | Positivos | Negativos | Automação |", "|---|---|---|---|"]
    for f in FEATURES:
        pos = [c[0] for c in CASOS if c[1] == f["id"] and c[2] == "Positivo"]
        neg = [c[0] for c in CASOS if c[1] == f["id"] and c[2] == "Negativo"]
        linhas.append(f"| {f['id']} {f['titulo']} | {', '.join(pos)} | {', '.join(neg)} | {f['status']} |")
    return "\n".join(linhas) + "\n"


def gerar_csvs() -> None:
    with open(AQUI / "azure_import_features.csv", "w", newline="", encoding="utf-8-sig") as fh:
        w = csv.writer(fh)
        w.writerow(["Work Item Type", "Title", "Description", "Acceptance Criteria", "Area Path", "Tags"])
        for f in FEATURES:
            w.writerow(["Feature", f"{f['id']} - {f['titulo']}", f["descricao"],
                        "<ol>" + "".join(f"<li>{c}</li>" for c in f["criterios"]) + "</ol>", AREA, "AquaGuard;GS2026"])
    with open(AQUI / "azure_import_test_cases.csv", "w", newline="", encoding="utf-8-sig") as fh:
        w = csv.writer(fh)
        w.writerow(["ID", "Work Item Type", "Title", "Test Step", "Step Action", "Step Expected", "Area Path", "Description", "Tags"])
        for c in CASOS:
            tc, feat, tipo, titulo, obj, prep, ent, saida, passos = c
            desc = (f"<b>Objetivo:</b> {obj}<br><b>Preparação:</b> {prep}<br><b>Entradas:</b> {ent}<br>"
                    f"<b>Saída esperada:</b> {saida}<br><b>Feature:</b> {feat} · <b>Tipo:</b> {tipo} (caixa-preta)")
            w.writerow(["", "Test Case", f"{tc} - {titulo} [{tipo}]", "", "", "", AREA, desc, f"{feat};{tipo}"])
            for i, (acao, esperado) in enumerate(passos, 1):
                w.writerow(["", "", "", i, acao, esperado, "", "", ""])


if __name__ == "__main__":
    (AQUI / "FEATURES_E_TEST_CASES.md").write_text(gerar_markdown(), encoding="utf-8")
    gerar_csvs()
    print(f"{len(FEATURES)} features e {len(CASOS)} test cases gerados.")
