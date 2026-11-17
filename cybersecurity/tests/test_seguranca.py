import json
import pathlib

import pytest

from aquaguard_sec.auditoria import Auditoria, verificar_integridade
from aquaguard_sec.llm import traduzir
from aquaguard_sec.pii import Categoria, MotorPII, cnpj_valido, cpf_valido, luhn_valido
from aquaguard_sec.risco import calcular
from aquaguard_sec.taint import (AnalisadorEstatico, Contaminado, MonitorTaint, VazamentoBloqueado, contaminado_em,
                                 contaminar, sanitizar)

M = MotorPII()
RAIZ = pathlib.Path(__file__).resolve().parent.parent


def regras(texto):
    return [a.regra for a in M.analisar_texto(texto)]


# ------------------------------------------------------------- PII: positivos
@pytest.mark.parametrize("texto", ["529.982.247-25", "52998224725", "5 2 9 . 9 8 2 . 2 4 7 - 2 5", "cpf 529-982-247/25"])
def test_cpf_varios_formatos_inclusive_ofuscado(texto):
    assert "CPF" in regras(texto)


def test_validadores_matematicos():
    assert cpf_valido("529.982.247-25") and not cpf_valido("123.456.789-00") and not cpf_valido("111.111.111-11")
    assert cnpj_valido("11.222.333/0001-81") and not cnpj_valido("11.222.333/0001-80")
    assert luhn_valido("4111 1111 1111 1111") and not luhn_valido("4111 1111 1111 1112")


@pytest.mark.parametrize("texto,regra", [
    ("me liga (11) 98765-4321", "TELEFONE"), ("+55 11 912345678", "TELEFONE"),
    ("contato: joao.silva@example.com", "EMAIL"), ("minha senha: Enchente@2026", "SENHA"),
    ("token sk-test_AbCdEfGhIjKlMnOpQrSt", "TOKEN_API"), ("CID J45.0", "CID10"),
    ("RG 12.345.678-9", "RG"), ("CEP 08061-000", "CEP"), ("cartão 4111 1111 1111 1111", "CARTAO_CREDITO"),
    ("moro na Rua das Flores, 123", "ENDERECO_RESIDENCIAL"), ("Minha mãe é cadeirante", "SAUDE_CONTEXTO"),
    ("tenho asma", "SAUDE_CONTEXTO"), ("CNPJ 11.222.333/0001-81", "CNPJ"),
])
def test_regras_detectam(texto, regra):
    assert regra in regras(texto)


# ------------------------------------------------------------- PII: negativos (falsos positivos)
@pytest.mark.parametrize("texto", [
    "Rua alagada na altura do joelho", "protocolo 123.456.789-00",  # CPF com DV inválido
    "Sensor AQG-004 mediu 95 cm às 18:30", "A asma é comum no inverno",  # saúde sem vínculo pessoal
    "Nível 1234 5678 do córrego", "Ligue 199 para a Defesa Civil",
])
def test_sem_falso_positivo(texto):
    assert regras(texto) == []


def test_cpf_nao_vira_telefone_duplicado():
    assert regras("CPF 529.982.247-25") == ["CPF"]


def test_json_aninhado_e_campo_sensivel():
    payload = {"relato": {"descricao": "água entrou", "autor": {"senha": "xyz12345", "email": "a@b.com"}}, "lista": ["tel 11 98765-4321"]}
    achados = M.analisar(payload)
    caminhos = {a.caminho for a in achados}
    assert "$.relato.autor.senha" in caminhos and "$.relato.autor.email" in caminhos and "$.lista[0]" in caminhos
    assert any(a.categoria == Categoria.CREDENCIAL for a in achados)


def test_mascaramento_nunca_expoe_valor():
    t = M.mascarar_texto("CPF 529.982.247-25, senha: Enchente@2026, email joao@example.com")
    assert "529.982" not in t and "Enchente@2026" not in t and "joao@" not in t
    assert "***.***.***-25" in t and "[CREDENCIAL REMOVIDA]" in t


def test_achado_nao_guarda_valor_bruto():
    a = M.analisar_texto("CPF 529.982.247-25")[0]
    assert "529982247" not in json.dumps(a.to_dict())


# ------------------------------------------------------------- Taint dinâmico
def test_propagacao_de_taint():
    c = contaminar("Meu CPF é 529.982.247-25", "teste")
    assert isinstance(c, Contaminado) and "CPF" in c.rotulos
    for derivado in (c + "!", "x" + c, c.upper(), c[3:], "{}".format(c), f"msg {c}", "%s" % c):
        assert "CPF" in contaminado_em(derivado), derivado


def test_texto_limpo_nao_e_contaminado():
    assert not isinstance(contaminar("Rua alagada", "t"), Contaminado)


def test_sink_inseguro_bloqueia_e_seguro_permite():
    mon = MonitorTaint(Auditoria(), modo="bloquear")
    saida = []

    @mon.sink("log")
    def log(m): saida.append(m)

    @mon.sink("banco", seguro=True)
    def banco(m): saida.append(m)

    dado = contaminar({"d": "tenho asma, CPF 529.982.247-25"}, "r")
    with pytest.raises(VazamentoBloqueado):
        log(f"recebido {dado['d']}")
    banco(dado)
    log(sanitizar(dado))  # após sanitizar o fluxo é permitido
    assert len(saida) == 2 and "529.982" not in str(saida[1])
    assert [e.decisao for e in mon.eventos] == ["bloqueado", "permitido", "permitido"]


def test_modo_sanitizar_entrega_dado_mascarado():
    mon = MonitorTaint(Auditoria(), modo="sanitizar")
    saida = []

    @mon.sink("feed")
    def feed(m): saida.append(m)

    feed(contaminar("contato 11 98765-4321", "r"))
    assert "98765" not in saida[0]


# ------------------------------------------------------------- Taint estático
def test_estatico_encontra_vulnerabilidades_e_aprova_versao_segura():
    an = AnalisadorEstatico()
    vuln = an.analisar_caminho(RAIZ / "prototipo" / "pipeline_vulneravel.py")
    linhas_vuln = {i for i, l in enumerate((RAIZ / "prototipo" / "pipeline_vulneravel.py").read_text(encoding="utf-8").splitlines(), 1) if "# VULN:" in l}
    assert {f.linha for f in vuln} == linhas_vuln
    assert an.analisar_caminho(RAIZ / "prototipo" / "pipeline_seguro.py") == []


def test_estatico_reatribuicao_limpa_taint():
    codigo = "x = input()\nx = 'fixo'\nprint(x)\ny = input()\nprint(mascarar(y))\nz = y + '!'\nprint(z)\n"
    assert [f.linha for f in AnalisadorEstatico().analisar_codigo(codigo)] == [7]


# ------------------------------------------------------------- Auditoria, risco, LLM
def test_auditoria_detecta_adulteracao(tmp_path):
    arq = tmp_path / "a.jsonl"
    aud = Auditoria(arq)
    aud.registrar("x", {"a": 1})
    aud.registrar("y", {"b": 2})
    assert verificar_integridade(arq) == (True, 2)
    arq.write_text(arq.read_text(encoding="utf-8").replace('"a": 1', '"a": 9'), encoding="utf-8")
    assert verificar_integridade(arq)[0] is False


def test_irc_cai_quando_fluxos_sao_bloqueados():
    achados = M.analisar_texto("CPF 529.982.247-25 senha: abcdef12")
    v1 = MonitorTaint(Auditoria(), modo="observar")
    v2 = MonitorTaint(Auditoria(), modo="bloquear")
    for mon in (v1, v2):
        f = mon.sink("log")(lambda m: None)
        try:
            f(contaminar("senha: abcdef12", "r"))
        except VazamentoBloqueado:
            pass
    antes, depois = calcular(achados, v1.eventos, []), calcular([], v2.eventos, [])
    assert 0 <= depois.valor < antes.valor <= 100


def test_llm_offline_nao_recebe_nem_devolve_pii(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.delenv("ANTHROPIC_AUTH_TOKEN", raising=False)
    t = traduzir([{"id": "F1", "categoria": "identificador", "evidencia": "CPF 529.982.247-25"}])
    assert t.motor.startswith("offline") and t.alertas[0]["titulo"]
    assert "529.982" not in json.dumps(t.alertas, ensure_ascii=False)
