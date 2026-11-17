"""Trilha de auditoria (JSON Lines) com encadeamento de hashes.

Cada linha contém o hash da anterior: qualquer alteração/remoção posterior é detectada
por `verificar_integridade` (evidência confiável para a auditoria do protótipo).
Nunca grava dados pessoais brutos — apenas valores mascarados e hashes.
"""
from __future__ import annotations

import hashlib
import json
import pathlib
from datetime import datetime, timezone
from typing import Any


class Auditoria:
    def __init__(self, arquivo: pathlib.Path | None = None):
        self.arquivo = arquivo
        self.registros: list[dict[str, Any]] = []
        self._ultimo_hash = "0" * 64
        if arquivo:
            arquivo.parent.mkdir(parents=True, exist_ok=True)
            arquivo.write_text("", encoding="utf-8")

    def registrar(self, evento: str, dados: dict[str, Any], nivel: str = "INFO") -> dict[str, Any]:
        reg = {"ts": datetime.now(timezone.utc).isoformat(timespec="seconds"), "evento": evento, "nivel": nivel,
               "dados": dados, "hash_anterior": self._ultimo_hash}
        reg["hash"] = hashlib.sha256(json.dumps(reg, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
        self._ultimo_hash = reg["hash"]
        self.registros.append(reg)
        if self.arquivo:
            with self.arquivo.open("a", encoding="utf-8") as fh:
                fh.write(json.dumps(reg, ensure_ascii=False) + "\n")
        return reg


def verificar_integridade(arquivo: pathlib.Path) -> tuple[bool, int]:
    anterior = "0" * 64
    linhas = [l for l in arquivo.read_text(encoding="utf-8").splitlines() if l.strip()]
    for i, linha in enumerate(linhas, 1):
        reg = json.loads(linha)
        h = reg.pop("hash")
        if reg["hash_anterior"] != anterior:
            return False, i
        if hashlib.sha256(json.dumps(reg, sort_keys=True, ensure_ascii=False).encode()).hexdigest() != h:
            return False, i
        anterior = h
    return True, len(linhas)
