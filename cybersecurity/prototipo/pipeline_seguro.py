"""Pipeline de relatos — VERSÃO 2 (CORRIGIDA).

Todo dado vindo do cidadão passa pelo sanitizador antes de qualquer saída.
O analisador estático deve reportar ZERO fluxos inseguros neste arquivo.
"""
import json
import logging

from aquaguard_sec.taint import sanitizar

log = logging.getLogger("aquaguard")


def receber_relato(corpo_http: str) -> dict:
    return json.loads(corpo_http)


def processar(corpo_http: str) -> None:
    relato = receber_relato(corpo_http)
    seguro = sanitizar(relato)

    log.info("Novo relato recebido no bairro %s", seguro["bairro"])
    responder_publico({"bairro": seguro["bairro"], "texto": seguro["descricao"]})
    enviar_llm("Relato: " + seguro["descricao"])


def responder_publico(dados: dict) -> None: ...
def enviar_llm(texto: str) -> None: ...
