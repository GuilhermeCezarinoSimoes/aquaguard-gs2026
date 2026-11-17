"""Taint Analysis do AquaGuard — rastreia dados pessoais desde a ENTRADA (fonte)
até as SAÍDAS (sinks) e BLOQUEIA vazamentos em saídas inseguras.

Duas abordagens complementares:

1. DINÂMICA (em execução): `Contaminado` é uma `str` que carrega rótulos de taint.
   A contaminação se propaga em concatenação, format, f-strings, slicing, upper(),
   replace(), join… Todo sink protegido verifica o taint antes de escrever.
   Somente o sanitizador (`sanitizar`) remove o taint (mascarando o conteúdo).

2. ESTÁTICA (no código-fonte): `AnalisadorEstatico` percorre a AST de módulos Python,
   marca variáveis que recebem dados de fontes (request.json, input(), payload…),
   propaga por atribuições e chamadas e reporta fluxos fonte → sink sem sanitização.
"""
from __future__ import annotations

import ast
import json
import pathlib
from dataclasses import dataclass, field
from typing import Any, Callable, Iterable

from .auditoria import Auditoria
from .pii import Achado, MotorPII

_motor = MotorPII()


# ============================================================ DINÂMICA
class Contaminado(str):
    """String com rótulos de taint (ex.: {'CPF', 'SAUDE_CONTEXTO'}) e origem."""

    rotulos: frozenset[str]
    origem: str

    def __new__(cls, valor: str, rotulos: Iterable[str], origem: str = "?"):
        obj = super().__new__(cls, valor)
        obj.rotulos = frozenset(rotulos)
        obj.origem = origem
        return obj

    # --- propagação -------------------------------------------------
    def _mesclar(self, outro: Any, resultado: str) -> "Contaminado":
        rot = set(self.rotulos) | set(getattr(outro, "rotulos", ()))
        return Contaminado(resultado, rot, self.origem)

    def __add__(self, outro):  # type: ignore[override]
        return self._mesclar(outro, str.__add__(self, outro))

    def __radd__(self, outro):
        return self._mesclar(outro, str.__add__(str(outro), self))

    def __mod__(self, args):  # type: ignore[override]
        return self._mesclar(args, str.__mod__(self, args))

    def __format__(self, spec):
        # f-strings chamam __format__; devolvemos Contaminado para que o
        # str.join interno do f-string seja detectado por `contaminado_em`.
        return Contaminado(str.__format__(str(self), spec), self.rotulos, self.origem)

    def __getitem__(self, k):  # type: ignore[override]
        return Contaminado(str.__getitem__(self, k), self.rotulos, self.origem)

    def format(self, *a, **kw):  # type: ignore[override]
        res = str.format(self, *a, **kw)
        rot = set(self.rotulos)
        for x in list(a) + list(kw.values()):
            rot |= set(getattr(x, "rotulos", ()))
        return Contaminado(res, rot, self.origem)

    for _m in ("upper", "lower", "strip", "lstrip", "rstrip", "title", "capitalize", "replace", "casefold"):
        exec(f"def {_m}(self, *a, **k):\n    return Contaminado(str.{_m}(self, *a, **k), self.rotulos, self.origem)")
    del _m


def contaminar(valor: Any, origem: str) -> Any:
    """FONTE: marca como contaminado todo texto que contenha PII (recursivo em JSON)."""
    if isinstance(valor, dict):
        return {k: contaminar(v, f"{origem}.{k}") for k, v in valor.items()}
    if isinstance(valor, list):
        return [contaminar(v, f"{origem}[{i}]") for i, v in enumerate(valor)]
    if isinstance(valor, str):
        achados = _motor.analisar_texto(valor)
        return Contaminado(valor, {a.regra for a in achados}, origem) if achados else valor
    return valor


def contaminado_em(valor: Any) -> set[str]:
    """Rótulos de taint presentes em qualquer parte do valor. Rechecagem por conteúdo
    garante detecção mesmo quando a propagação se perde (ex.: f-string → str comum)."""
    if isinstance(valor, Contaminado):
        return set(valor.rotulos) or {"PII"}
    if isinstance(valor, dict):
        r: set[str] = set()
        for k, v in valor.items():
            r |= contaminado_em(v)
        return r
    if isinstance(valor, (list, tuple)):
        r = set()
        for v in valor:
            r |= contaminado_em(v)
        return r
    if isinstance(valor, str):
        return {a.regra for a in _motor.analisar_texto(valor)}
    return set()


def sanitizar(valor: Any) -> Any:
    """SANITIZADOR: mascara PII e devolve dado limpo (sem taint)."""
    if isinstance(valor, dict):
        return {k: sanitizar(v) for k, v in _motor.mascarar(dict(valor)).items()}
    if isinstance(valor, list):
        return [sanitizar(v) for v in valor]
    if isinstance(valor, str):
        return str(_motor.mascarar_texto(str(valor)))
    return valor


_ORIGEM_ATUAL: list[str] = []


def _origem_de(valor: Any) -> str | None:
    """Origem da primeira parte contaminada (recursivo); se a propagação se perdeu, usa o contexto atual."""
    if isinstance(valor, Contaminado):
        return valor.origem
    if isinstance(valor, dict):
        valor = list(valor.values())
    if isinstance(valor, (list, tuple)):
        for v in valor:
            o = _origem_de(v)
            if o:
                return o
        return None
    return _ORIGEM_ATUAL[-1] if _ORIGEM_ATUAL and contaminado_em(valor) else None


class contexto_origem:
    """Context manager: identifica a requisição em processamento (ex.: id do relato)."""

    def __init__(self, origem: str):
        self.origem = origem

    def __enter__(self):
        _ORIGEM_ATUAL.append(self.origem)
        return self

    def __exit__(self, *exc):
        _ORIGEM_ATUAL.pop()


class VazamentoBloqueado(Exception):
    def __init__(self, sink: str, rotulos: set[str]):
        super().__init__(f"Fluxo contaminado {sorted(rotulos)} bloqueado no sink '{sink}'")
        self.sink = sink
        self.rotulos = rotulos


@dataclass
class EventoFluxo:
    sink: str
    seguro: bool
    rotulos: list[str]
    decisao: str        # "permitido" | "bloqueado" | "sanitizado"
    origem: str

    def to_dict(self) -> dict[str, Any]:
        return self.__dict__.copy()


@dataclass
class MonitorTaint:
    """Registra sinks e aplica a política: dado contaminado nunca chega a sink inseguro."""

    auditoria: Auditoria
    modo: str = "bloquear"   # "bloquear" | "sanitizar" | "observar" (apenas registra: usado para demonstrar o risco)
    eventos: list[EventoFluxo] = field(default_factory=list)

    def sink(self, nome: str, seguro: bool = False) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        """Decorator. `seguro=True` = saída com controle de acesso e criptografia (ex.: banco cifrado)."""
        def deco(fn: Callable[..., Any]) -> Callable[..., Any]:
            def wrapper(*args: Any, **kwargs: Any) -> Any:
                rot = set()
                origem = "?"
                for x in list(args) + list(kwargs.values()):
                    rot |= contaminado_em(x)
                    origem = _origem_de(x) or origem
                if not rot or seguro:
                    self._registrar(nome, seguro, rot, "permitido", origem)
                    return fn(*args, **kwargs)
                if self.modo == "bloquear":
                    self._registrar(nome, seguro, rot, "bloqueado", origem)
                    raise VazamentoBloqueado(nome, rot)
                if self.modo == "sanitizar":
                    self._registrar(nome, seguro, rot, "sanitizado", origem)
                    return fn(*[sanitizar(a) for a in args], **{k: sanitizar(v) for k, v in kwargs.items()})
                self._registrar(nome, seguro, rot, "vazou", origem)
                return fn(*args, **kwargs)
            wrapper.__name__ = fn.__name__
            return wrapper
        return deco

    def _registrar(self, sink: str, seguro: bool, rot: set[str], decisao: str, origem: str) -> None:
        ev = EventoFluxo(sink, seguro, sorted(rot), decisao, origem)
        self.eventos.append(ev)
        if rot:
            self.auditoria.registrar("taint_fluxo", ev.to_dict(),
                                     nivel="CRITICO" if decisao == "vazou" else "ALTO" if decisao == "bloqueado" else "INFO")


# ============================================================ ESTÁTICA
FONTES_PADRAO = {"input", "request.json", "request.get_json", "request.form", "request.args", "receber_relato",
                 "ler_payload", "json.loads", "payload_http"}
SINKS_INSEGUROS = {
    "print": "console", "logging.info": "log", "logging.warning": "log", "logging.error": "log", "logging.debug": "log",
    "log.info": "log", "log.warning": "log", "log.error": "log", "logger.info": "log", "logger.warning": "log",
    "logger.error": "log", "requests.post": "http_externo", "requests.get": "http_externo", "publicar_mqtt": "mqtt_publico",
    "responder_publico": "resposta_publica_api", "enviar_llm": "llm_terceiro", "salvar_csv": "arquivo_texto",
    "write": "arquivo_texto",
}
SANITIZADORES_PADRAO = {"sanitizar", "mascarar", "mascarar_texto", "anonimizar", "hash_curto"}


def _nome_chamada(no: ast.AST) -> str:
    if isinstance(no, ast.Name):
        return no.id
    if isinstance(no, ast.Attribute):
        base = _nome_chamada(no.value)
        return f"{base}.{no.attr}" if base else no.attr
    if isinstance(no, ast.Call):
        return _nome_chamada(no.func)
    if isinstance(no, ast.Subscript):
        return _nome_chamada(no.value)
    return ""


@dataclass
class FluxoEstatico:
    arquivo: str
    linha: int
    sink: str
    tipo_sink: str
    variaveis: list[str]
    trecho: str

    def to_dict(self) -> dict[str, Any]:
        return self.__dict__.copy()


class _Visitante(ast.NodeVisitor):
    def __init__(self, arquivo: str, fonte: str, fontes: set[str], sanitizadores: set[str]):
        self.arquivo, self.linhas = arquivo, fonte.splitlines()
        self.fontes, self.sanit = fontes, sanitizadores
        self.contaminadas: set[str] = set()
        self.fluxos: list[FluxoEstatico] = []
        self.parametros_fonte: set[str] = set()

    # Funções cujo parâmetro se chama payload/relato/dados_cidadao também são fontes.
    def visit_FunctionDef(self, no: ast.FunctionDef) -> None:
        anteriores = set(self.contaminadas)
        for arg in no.args.args:
            if arg.arg in {"payload", "relato", "dados_cidadao", "req", "corpo"}:
                self.contaminadas.add(arg.arg)
        self.generic_visit(no)
        self.contaminadas = anteriores

    def _expr_contaminada(self, no: ast.AST | None) -> bool:
        if no is None:
            return False
        if isinstance(no, ast.Call):
            nome = _nome_chamada(no.func)
            if nome.split(".")[-1] in self.sanit or nome in self.sanit:
                return False
            if nome in self.fontes or nome.split(".")[-1] in {f.split(".")[-1] for f in self.fontes if "." not in f}:
                return True
            return any(self._expr_contaminada(a) for a in list(no.args) + [k.value for k in no.keywords]) or \
                self._expr_contaminada(no.func)
        if isinstance(no, ast.Name):
            return no.id in self.contaminadas
        if isinstance(no, ast.Attribute):
            return _nome_chamada(no) in self.fontes or self._expr_contaminada(no.value)
        return any(self._expr_contaminada(f) for f in ast.iter_child_nodes(no))

    def _alvos(self, alvo: ast.AST) -> list[str]:
        if isinstance(alvo, ast.Name):
            return [alvo.id]
        if isinstance(alvo, (ast.Tuple, ast.List)):
            return [n for e in alvo.elts for n in self._alvos(e)]
        if isinstance(alvo, (ast.Subscript, ast.Attribute)):
            return [_nome_chamada(alvo)]
        return []

    def visit_Assign(self, no: ast.Assign) -> None:
        cont = self._expr_contaminada(no.value)
        for alvo in no.targets:
            for nome in self._alvos(alvo):
                (self.contaminadas.add if cont else self.contaminadas.discard)(nome)
        self.generic_visit(no)

    def visit_AugAssign(self, no: ast.AugAssign) -> None:
        if self._expr_contaminada(no.value):
            for nome in self._alvos(no.target):
                self.contaminadas.add(nome)
        self.generic_visit(no)

    def visit_Call(self, no: ast.Call) -> None:
        nome = _nome_chamada(no.func)
        chave = nome if nome in SINKS_INSEGUROS else nome.split(".")[-1] if nome.split(".")[-1] in SINKS_INSEGUROS else None
        if chave:
            args = list(no.args) + [k.value for k in no.keywords]
            if any(self._expr_contaminada(a) for a in args):
                vars_ = sorted({n.id for a in args for n in ast.walk(a) if isinstance(n, ast.Name) and n.id in self.contaminadas})
                trecho = self.linhas[no.lineno - 1].strip() if no.lineno - 1 < len(self.linhas) else ""
                self.fluxos.append(FluxoEstatico(self.arquivo, no.lineno, nome, SINKS_INSEGUROS[chave], vars_, trecho))
        self.generic_visit(no)


class AnalisadorEstatico:
    def __init__(self, fontes: set[str] | None = None, sanitizadores: set[str] | None = None):
        self.fontes = fontes or set(FONTES_PADRAO)
        self.sanit = sanitizadores or set(SANITIZADORES_PADRAO)

    def analisar_codigo(self, codigo: str, arquivo: str = "<memoria>") -> list[FluxoEstatico]:
        v = _Visitante(arquivo, codigo, self.fontes, self.sanit)
        v.visit(ast.parse(codigo, filename=arquivo))
        return v.fluxos

    def analisar_caminho(self, caminho: pathlib.Path) -> list[FluxoEstatico]:
        arquivos = [caminho] if caminho.is_file() else sorted(caminho.rglob("*.py"))
        fluxos: list[FluxoEstatico] = []
        base = caminho if caminho.is_dir() else caminho.parent
        for f in arquivos:  # caminho relativo: não expõe a estrutura de pastas da máquina
            rel = f"{base.name}/{f.relative_to(base).as_posix()}"
            fluxos.extend(self.analisar_codigo(f.read_text(encoding="utf-8"), rel))
        return fluxos


def para_json(achados: list[Achado]) -> str:
    return json.dumps([a.to_dict() for a in achados], ensure_ascii=False, indent=2)
