"""Tradução de falhas técnicas em alertas claros para o cidadão (remediação com IA).

- Com ANTHROPIC_API_KEY (ou perfil `ant auth login`) e o pacote `anthropic`, usa o Claude.
- Sem credencial/rede, usa um tradutor OFFLINE baseado em modelos de texto
  (o relatório informa qual motor foi usado — nunca fingimos ter chamado a IA).

Segurança do próprio LLM (o prompt é um SINK):
  * só enviamos ao modelo achados JÁ MASCARADOS (sanitizar) — nenhum dado pessoal sai do sistema;
  * a saída do modelo é tratada como texto não confiável e passa de novo pelo motor de PII.
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any

from .pii import MotorPII
from .taint import contaminado_em, sanitizar

MODELO = os.environ.get("AQUAGUARD_LLM_MODEL", "claude-opus-5-5")

SISTEMA = (
    "Você é o assistente de segurança do AquaGuard, app de alerta de alagamentos em São Paulo. "
    "Recebe falhas técnicas de privacidade (já anonimizadas) e escreve, em português simples, para um morador "
    "sem conhecimento técnico: 1) o risco real para ele em uma frase; 2) o que o AquaGuard fez/vai fazer; "
    "3) uma orientação prática. Máximo de 60 palavras por item, sem jargão e sem alarmismo. "
    "Responda SOMENTE com JSON: lista de objetos {\"id\", \"titulo\", \"risco_para_voce\", \"o_que_fizemos\", \"o_que_voce_pode_fazer\"}."
)

MODELOS_OFFLINE: dict[str, dict[str, str]] = {
    "credencial": {"titulo": "Senha ou chave exposta",
                   "risco": "Alguém poderia entrar em uma conta ou enviar dados falsos se passando por um sensor.",
                   "acao": "Bloqueamos a gravação e a credencial deve ser trocada imediatamente.",
                   "dica": "Nunca escreva senhas em relatos ou mensagens. Se escreveu, troque a senha."},
    "saude": {"titulo": "Informação de saúde no relato",
              "risco": "Dados de saúde são sensíveis: expostos, podem gerar discriminação ou golpes.",
              "acao": "Removemos a informação antes de publicar o relato e de gravar logs.",
              "dica": "Para pedir ajuda prioritária (ex.: pessoa acamada), ligue 199 (Defesa Civil)."},
    "identificador": {"titulo": "Documento pessoal (CPF/RG) no relato",
                      "risco": "Com seu CPF, golpistas podem tentar abrir contas ou fazer compras em seu nome.",
                      "acao": "Mascaramos o número; ele não aparece para outros moradores.",
                      "dica": "O AquaGuard nunca pede CPF. Desconfie de quem pedir em nome do app."},
    "contato": {"titulo": "Telefone ou e-mail exposto",
                "risco": "Seu contato público pode receber golpes de falso resgate durante enchentes.",
                "acao": "Ocultamos o contato no relato público.",
                "dica": "Não divulgue seu telefone; a Defesa Civil oficial liga do 199."},
    "localizacao": {"titulo": "Endereço exato da sua casa",
                    "risco": "Com a casa vazia durante a enchente, o endereço exposto facilita furtos.",
                    "acao": "Publicamos só o bairro, nunca o número da casa.",
                    "dica": "Informe apenas a rua ou um ponto de referência."},
    "financeiro": {"titulo": "Dados de cartão expostos",
                   "risco": "O número do cartão pode ser usado em compras fraudulentas.",
                   "acao": "Bloqueamos e apagamos o dado.",
                   "dica": "Avise seu banco e peça um novo cartão."},
    "fluxo": {"titulo": "Dado pessoal indo para um lugar inseguro",
              "risco": "Uma parte do sistema tentou enviar seus dados para um log ou serviço externo.",
              "acao": "O AquaGuard bloqueou o envio automaticamente antes que vazasse.",
              "dica": "Nada a fazer: a proteção funcionou. A equipe corrigirá o código."},
}


@dataclass
class Traducao:
    motor: str          # "claude:<modelo>" ou "offline"
    alertas: list[dict[str, Any]]


def _offline(falhas: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out = []
    for f in falhas:
        m = MODELOS_OFFLINE.get(f.get("categoria", "fluxo"), MODELOS_OFFLINE["fluxo"])
        out.append({"id": f["id"], "titulo": m["titulo"], "risco_para_voce": m["risco"],
                    "o_que_fizemos": m["acao"], "o_que_voce_pode_fazer": m["dica"]})
    return out


def _claude(falhas: list[dict[str, Any]]) -> list[dict[str, Any]]:
    import anthropic  # importado só quando há credencial

    client = anthropic.Anthropic()
    pedido = dict(model=MODELO, max_tokens=4000, system=SISTEMA,
                  output_config={"effort": "low"},
                  messages=[{"role": "user", "content": "Falhas (anonimizadas):\n" + json.dumps(falhas, ensure_ascii=False)}])
    try:  # fallback do servidor em caso de recusa (beta); se a versão do SDK não suportar, chamada simples
        resp = client.beta.messages.create(betas=["server-side-fallback-2026-07-01"], fallbacks="default", **pedido)
    except TypeError:
        resp = client.messages.create(**pedido)
    if resp.stop_reason == "refusal":
        raise RuntimeError("modelo recusou")
    texto = "".join(b.text for b in resp.content if b.type == "text").strip()
    texto = texto[texto.find("["): texto.rfind("]") + 1]
    return json.loads(texto)


def traduzir(falhas_tecnicas: list[dict[str, Any]], usar_llm: bool = True) -> Traducao:
    # 1) SINK "llm_terceiro": nada contaminado sai daqui.
    falhas = sanitizar(falhas_tecnicas)
    assert not any(contaminado_em(f.get("evidencia", "")) for f in falhas), "PII no prompt do LLM"

    credencial = os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("ANTHROPIC_AUTH_TOKEN")
    if usar_llm and credencial:
        try:
            alertas = _claude(falhas)
            motor = f"claude:{MODELO}"
        except Exception as e:  # rede, cota, formato — cai para o modo offline
            alertas, motor = _offline(falhas), f"offline (falha no LLM: {type(e).__name__})"
    else:
        alertas, motor = _offline(falhas), "offline (sem credencial de LLM)"

    # 2) Saída do LLM é não confiável: remascara qualquer PII que o modelo possa ter gerado.
    motor_pii = MotorPII()
    alertas = [motor_pii.mascarar(a) for a in alertas]
    return Traducao(motor, alertas)
