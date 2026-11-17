"""Pipeline de relatos — VERSÃO 1 (VULNERÁVEL, mantida só para a auditoria).

Reproduz como o protótipo inicial tratava um relato de alagamento enviado pelo cidadão.
O analisador estático deve apontar cada linha marcada com  # VULN.
"""
import json
import logging

import requests

log = logging.getLogger("aquaguard")


def receber_relato(corpo_http: str) -> dict:
    return json.loads(corpo_http)


def processar(corpo_http: str) -> None:
    relato = receber_relato(corpo_http)
    descricao = relato["descricao"]
    contato = relato.get("contato", "")

    log.info("Novo relato recebido: %s", relato)                     # VULN: payload completo no log
    print(f"[debug] contato do cidadão: {contato}")                  # VULN: PII no console

    texto_publico = descricao.upper()
    responder_publico({"bairro": relato["bairro"], "texto": texto_publico})  # VULN: feed público sem máscara

    resumo = "Relato: " + descricao
    enviar_llm(resumo)                                                # VULN: dado pessoal para LLM de terceiro
    requests.post("https://analytics.exemplo.com/eventos", json=relato, timeout=5)  # VULN: terceiro


def responder_publico(dados: dict) -> None: ...
def enviar_llm(texto: str) -> None: ...
