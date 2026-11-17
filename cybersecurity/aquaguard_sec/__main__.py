"""CLI de auditoria do AquaGuard.

    python -m aquaguard_sec --api http://localhost:5080 --saida ../evidencias/cybersecurity

Etapas: coleta (API + relatos de teste) → parsing de PII → Taint dinâmico (v1 observa x v2 bloqueia)
→ Taint estático no código → tradução por IA → Indicador de Risco Cidadão → dashboard e evidências.
"""
from __future__ import annotations

import argparse
import json
import logging
import pathlib
import urllib.request
from datetime import datetime

from . import dashboard, risco
from .auditoria import Auditoria, verificar_integridade
from .llm import traduzir
from .pii import MotorPII, resumo_por_categoria
from .taint import AnalisadorEstatico, MonitorTaint, VazamentoBloqueado, contaminar, contexto_origem

RAIZ = pathlib.Path(__file__).resolve().parent.parent


def coletar_api(api: str | None) -> list[dict]:
    if not api:
        return []
    try:
        with urllib.request.urlopen(f"{api.rstrip('/')}/api/ocorrencias?tamanho=100", timeout=5) as r:
            itens = json.loads(r.read())["itens"]
        return [{"id": f"API-{o['id']}", "bairro": o["bairro"], "descricao": o["descricao"], "contato": o.get("apelido") or ""}
                for o in itens]
    except Exception as e:  # API fora do ar não impede a auditoria
        logging.warning("API indisponível (%s); seguindo só com relatos de teste", e)
        return []


def executar_pipeline(relatos: list[dict], monitor: MonitorTaint) -> None:
    """Pipeline do protótipo com sinks instrumentados (mesmos destinos do pipeline real)."""
    saidas: dict[str, list] = {"log": [], "feed": [], "llm": [], "terceiro": [], "banco": []}

    @monitor.sink("log_aplicacao")
    def gravar_log(msg): saidas["log"].append(msg)

    @monitor.sink("feed_publico_app")
    def publicar(d): saidas["feed"].append(d)

    @monitor.sink("prompt_llm_terceiro")
    def enviar_llm(t): saidas["llm"].append(t)

    @monitor.sink("analytics_externo")
    def analytics(d): saidas["terceiro"].append(d)

    @monitor.sink("banco_cifrado", seguro=True)
    def salvar_banco(d): saidas["banco"].append(d)

    for bruto in relatos:
      with contexto_origem(f"relato:{bruto['id']}"):
        relato = contaminar(bruto, f"relato:{bruto['id']}")       # FONTE
        salvar_banco(relato)
        for etapa in (lambda: gravar_log(f"Relato recebido: {relato['descricao']} contato={relato['contato']}"),
                      lambda: publicar({"bairro": relato["bairro"], "texto": relato["descricao"].upper()}),
                      lambda: enviar_llm("Classifique a gravidade: " + relato["descricao"]),
                      lambda: analytics(relato)):
            try:
                etapa()
            except VazamentoBloqueado:
                pass  # registrado na auditoria; o pipeline segue sem vazar


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--api", default="http://localhost:5080")
    ap.add_argument("--relatos", type=pathlib.Path, default=RAIZ / "dados" / "relatos_teste.json")
    ap.add_argument("--codigo", type=pathlib.Path, default=RAIZ / "prototipo")
    ap.add_argument("--saida", type=pathlib.Path, default=RAIZ / "saida")
    ap.add_argument("--sem-llm", action="store_true")
    a = ap.parse_args()
    a.saida.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

    aud = Auditoria(a.saida / "auditoria.jsonl")
    relatos = json.loads(a.relatos.read_text(encoding="utf-8")) + coletar_api(a.api)
    aud.registrar("inicio", {"registros": len(relatos), "api": a.api})

    # 1) Parsing de PII
    motor = MotorPII()
    achados = [ac for r in relatos for ac in motor.analisar(r, f"relato:{r['id']}")]
    for ac in achados:
        aud.registrar("pii_detectada", ac.to_dict(), nivel="MEDIO")

    # 2) Taint dinâmico: v1 (observa: mostra o que vazaria) × v2 (bloqueia)
    v1 = MonitorTaint(Auditoria(), modo="observar")
    executar_pipeline(relatos, v1)
    v2 = MonitorTaint(aud, modo="bloquear")
    executar_pipeline(relatos, v2)

    # 3) Taint estático no código-fonte do protótipo
    estat = AnalisadorEstatico().analisar_caminho(a.codigo)
    for f in estat:
        aud.registrar("taint_estatico", f.to_dict(), nivel="ALTO")

    # 4) Indicador de Risco Cidadão
    irc_antes = risco.calcular(achados, v1.eventos, estat)
    vuln_v2 = [f for f in estat if "vulneravel" not in f.arquivo]
    irc_depois = risco.calcular([], v2.eventos, vuln_v2)

    # 5) Tradução por IA (só dados mascarados vão ao modelo)
    falhas = []
    for i, cat in enumerate(sorted({ac.categoria.value for ac in achados})):
        exemplo = next(ac for ac in achados if ac.categoria.value == cat)
        falhas.append({"id": f"F{i + 1}", "categoria": cat, "regra": exemplo.regra, "evidencia": exemplo.mascarado,
                       "ocorrencias": sum(1 for x in achados if x.categoria.value == cat)})
    falhas.append({"id": f"F{len(falhas) + 1}", "categoria": "fluxo", "regra": "TAINT",
                   "evidencia": f"{sum(1 for e in v2.eventos if e.decisao == 'bloqueado')} envios bloqueados"})
    trad = traduzir(falhas, usar_llm=not a.sem_llm)
    aud.registrar("traducao_llm", {"motor": trad.motor, "alertas": len(trad.alertas)})

    dados = {
        "gerado_em": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "fontes": f"{len(relatos)} relatos ({'API AquaGuard + ' if a.api else ''}conjunto de teste sintético)",
        "registros": len(relatos), "total_pii": len(achados), "pii_por_categoria": resumo_por_categoria(achados),
        "bloqueados": sum(1 for e in v2.eventos if e.decisao == "bloqueado"),
        "vazariam": sum(1 for e in v1.eventos if e.decisao == "vazou"),
        "irc_antes": irc_antes.to_dict(), "irc_depois": irc_depois.to_dict(),
        "eventos_protegido": [e.to_dict() for e in v2.eventos], "fluxos_estaticos": [f.to_dict() for f in estat],
        "alertas_cidadao": trad.alertas, "motor_llm": trad.motor,
    }
    aud.registrar("fim", {"irc_antes": irc_antes.valor, "irc_depois": irc_depois.valor})

    (a.saida / "dashboard.html").write_text(dashboard.gerar(dados), encoding="utf-8")
    (a.saida / "pii_achados.json").write_text(json.dumps([x.to_dict() for x in achados], ensure_ascii=False, indent=2), encoding="utf-8")
    (a.saida / "taint_dinamico.json").write_text(json.dumps({"v1_sem_protecao": [e.to_dict() for e in v1.eventos],
        "v2_protegido": [e.to_dict() for e in v2.eventos]}, ensure_ascii=False, indent=2), encoding="utf-8")
    (a.saida / "taint_estatico.json").write_text(json.dumps([f.to_dict() for f in estat], ensure_ascii=False, indent=2), encoding="utf-8")
    (a.saida / "risco_cidadao.json").write_text(json.dumps({"antes": irc_antes.to_dict(), "depois": irc_depois.to_dict()},
                                                           ensure_ascii=False, indent=2), encoding="utf-8")
    (a.saida / "alertas_cidadao.json").write_text(json.dumps({"motor": trad.motor, "alertas": trad.alertas},
                                                             ensure_ascii=False, indent=2), encoding="utf-8")
    ok, n = verificar_integridade(a.saida / "auditoria.jsonl")

    print(f"Registros: {len(relatos)} | PII detectadas: {len(achados)} | por categoria: {dados['pii_por_categoria']}")
    print(f"Taint v1 (sem proteção): {dados['vazariam']} vazamentos | v2: {dados['bloqueados']} bloqueados")
    print(f"Taint estático: {len(estat)} fluxos inseguros -> " + ", ".join(f"{pathlib.Path(f.arquivo).name}:{f.linha}" for f in estat))
    print(f"IRC antes: {irc_antes.valor:.1f} ({irc_antes.faixa}) | depois: {irc_depois.valor:.1f} ({irc_depois.faixa})")
    print(f"Motor de tradução: {trad.motor} | Auditoria íntegra: {ok} ({n} registros)")
    print(f"Dashboard: {a.saida / 'dashboard.html'}")


if __name__ == "__main__":
    main()
