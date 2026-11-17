"""Indicador de Risco Cidadão (IRC), de 0 a 100.

IRC = 100 × (1 − e^(−S/K)), onde S soma, para cada exposição:
      peso da categoria do dado (4 contato … 10 credencial)
    × fator de exposição do destino (vazou = 1,0 · em repouso sem proteção = 0,5 · bloqueado = 0,1)
    × alcance (relato público = 1,5 · interno = 1,0)
K = 120 calibra a curva para o volume de um bairro (≈ 12 credenciais vazadas → IRC ≈ 63;
um único CPF exposto em relato público → IRC ≈ 4). Saturação só com exposição massiva.

Faixas: 0–24 Baixo · 25–49 Moderado · 50–74 Alto · 75–100 Crítico.
Os componentes ficam no resultado para a explicação ser auditável.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any

from .pii import PESO_CATEGORIA, Achado, Categoria
from .taint import EventoFluxo, FluxoEstatico

K = 120.0
FATOR = {"vazou": 1.0, "em_repouso": 0.5, "bloqueado": 0.1, "sanitizado": 0.05}


def faixa(irc: float) -> str:
    return "Crítico" if irc >= 75 else "Alto" if irc >= 50 else "Moderado" if irc >= 25 else "Baixo"


REGRA_CATEGORIA = {
    "CPF": Categoria.IDENTIFICADOR, "CNPJ": Categoria.IDENTIFICADOR, "RG": Categoria.IDENTIFICADOR,
    "EMAIL": Categoria.CONTATO, "TELEFONE": Categoria.CONTATO, "CEP": Categoria.LOCALIZACAO,
    "ENDERECO_RESIDENCIAL": Categoria.LOCALIZACAO, "SENHA": Categoria.CREDENCIAL, "TOKEN_API": Categoria.CREDENCIAL,
    "CARTAO_CREDITO": Categoria.FINANCEIRO, "CID10": Categoria.SAUDE, "SAUDE_CONTEXTO": Categoria.SAUDE,
}


@dataclass
class IndicadorRisco:
    valor: float
    faixa: str
    soma: float
    componentes: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {"valor": round(self.valor, 1), "faixa": self.faixa, "soma": round(self.soma, 2),
                "componentes": self.componentes}


def calcular(achados_em_repouso: list[Achado], eventos: list[EventoFluxo], fluxos_estaticos: list[FluxoEstatico],
             publico: bool = True) -> IndicadorRisco:
    comp: list[dict[str, Any]] = []
    alcance = 1.5 if publico else 1.0
    for a in achados_em_repouso:
        comp.append({"tipo": "dado_em_repouso", "item": a.regra, "peso": a.peso, "fator": FATOR["em_repouso"],
                     "alcance": alcance, "pontos": a.peso * FATOR["em_repouso"] * alcance})
    for ev in eventos:
        if not ev.rotulos:
            continue
        peso = max(PESO_CATEGORIA[REGRA_CATEGORIA.get(r, Categoria.IDENTIFICADOR)] for r in ev.rotulos)
        f = FATOR.get(ev.decisao, 0.0)
        comp.append({"tipo": f"fluxo_{ev.decisao}", "item": ev.sink, "peso": peso, "fator": f, "alcance": 1.0,
                     "pontos": peso * f})
    for fl in fluxos_estaticos:  # vulnerabilidade no código = potencial de vazamento
        comp.append({"tipo": "codigo_vulneravel", "item": f"{fl.arquivo}:{fl.linha}", "peso": 6, "fator": 0.5,
                     "alcance": 1.0, "pontos": 3.0})
    s = sum(c["pontos"] for c in comp)
    v = 100 * (1 - math.exp(-s / K))
    return IndicadorRisco(v, faixa(v), s, comp)
