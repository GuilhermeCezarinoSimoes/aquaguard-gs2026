"""Motor de parsing de PII (dados pessoais) do AquaGuard.

Detecta dados pessoais e sensíveis (LGPD art. 5º, I e II) em textos livres e em
estruturas JSON aninhadas (relatos de cidadãos, logs, payloads de API e IoT).

Robustez:
  * normalização (acentos, caixa, espaços/pontuação inseridos para burlar: "1 2 3 . 4 5 6 ...")
  * validação matemática para reduzir falsos positivos (dígitos do CPF/CNPJ, Luhn de cartões)
  * detecção por CONTEÚDO e por NOME DO CAMPO (ex.: {"senha": "..."}; {"cpf": "..."})
  * contexto: termos de saúde só contam como dado sensível quando ligados a uma pessoa
  * nunca devolve o valor bruto: só a versão mascarada + hash (para auditoria)
"""
from __future__ import annotations

import hashlib
import re
import unicodedata
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Iterable


class Categoria(str, Enum):
    IDENTIFICADOR = "identificador"      # CPF, RG, CNPJ, CNH
    CONTATO = "contato"                  # e-mail, telefone
    LOCALIZACAO = "localizacao"          # endereço exato, CEP, GPS de residência
    FINANCEIRO = "financeiro"            # cartão, conta
    CREDENCIAL = "credencial"            # senha, token, chave de API
    SAUDE = "saude"                      # dado sensível (LGPD art. 5º, II)


# Peso de sensibilidade por categoria (usado no Indicador de Risco Cidadão).
PESO_CATEGORIA: dict[Categoria, int] = {
    Categoria.CONTATO: 4,
    Categoria.LOCALIZACAO: 4,
    Categoria.IDENTIFICADOR: 7,
    Categoria.FINANCEIRO: 8,
    Categoria.SAUDE: 9,
    Categoria.CREDENCIAL: 10,
}


# ----------------------------------------------------------------- validadores
def _digitos(s: str) -> str:
    return re.sub(r"\D", "", s)


def cpf_valido(valor: str) -> bool:
    d = _digitos(valor)
    if len(d) != 11 or d == d[0] * 11:
        return False
    for n in (9, 10):
        soma = sum(int(d[i]) * (n + 1 - i) for i in range(n))
        dv = (soma * 10) % 11 % 10
        if dv != int(d[n]):
            return False
    return True


def cnpj_valido(valor: str) -> bool:
    d = _digitos(valor)
    if len(d) != 14 or d == d[0] * 14:
        return False
    for n, pesos in ((12, [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]), (13, [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2])):
        r = sum(int(d[i]) * pesos[i] for i in range(n)) % 11
        if (0 if r < 2 else 11 - r) != int(d[n]):
            return False
    return True


def luhn_valido(valor: str) -> bool:
    d = _digitos(valor)
    if not 13 <= len(d) <= 19:
        return False
    total = 0
    for i, ch in enumerate(reversed(d)):
        n = int(ch)
        if i % 2 == 1:
            n *= 2
            if n > 9:
                n -= 9
        total += n
    return total % 10 == 0


def telefone_valido(valor: str) -> bool:
    d = _digitos(valor)
    if d.startswith("55") and len(d) in (12, 13):
        d = d[2:]
    return len(d) in (10, 11) and 11 <= int(d[:2]) <= 99 and (len(d) == 10 or d[2] == "9")


# ----------------------------------------------------------------- regras
@dataclass(frozen=True)
class RegraPII:
    nome: str
    categoria: Categoria
    padrao: re.Pattern[str]
    validador: Callable[[str], bool] | None = None
    descricao: str = ""
    base_legal: str = "LGPD art. 5º, I"


SEP = r"[\s.\-/]*"  # separadores usados para "disfarçar" números

REGRAS: list[RegraPII] = [
    RegraPII("CPF", Categoria.IDENTIFICADOR,
             re.compile(rf"(?<!\d)\d{SEP}\d{SEP}\d{SEP}\d{SEP}\d{SEP}\d{SEP}\d{SEP}\d{SEP}\d{SEP}\d{SEP}\d(?!\d)"),
             cpf_valido, "CPF com dígitos verificadores válidos"),
    RegraPII("CNPJ", Categoria.IDENTIFICADOR,
             re.compile(r"(?<!\d)\d{2}\.?\d{3}\.?\d{3}/?\d{4}-?\d{2}(?!\d)"), cnpj_valido, "CNPJ válido"),
    RegraPII("RG", Categoria.IDENTIFICADOR,
             re.compile(r"(?i)\b(?:rg|identidade)\s*(?:n[ºo°.]?\s*)?[:\-]?\s*(\d{1,2}\.?\d{3}\.?\d{3}-?[\dxX])\b"),
             None, "RG precedido da palavra RG/identidade"),
    RegraPII("CARTAO_CREDITO", Categoria.FINANCEIRO,
             re.compile(r"(?<!\d)(?:\d[ \-]?){13,19}(?!\d)"), luhn_valido, "Número de cartão (Luhn)"),
    RegraPII("EMAIL", Categoria.CONTATO,
             re.compile(r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}"), None, "Endereço de e-mail"),
    RegraPII("TELEFONE", Categoria.CONTATO,
             re.compile(r"(?<!\d)(?:\+?55\s?)?\(?\d{2}\)?\s?9?\s?\d{4}[\s\-]?\d{4}(?!\d)"), telefone_valido,
             "Telefone fixo/celular BR"),
    RegraPII("CEP", Categoria.LOCALIZACAO,
             re.compile(r"(?i)\bcep\s*[:\-]?\s*\d{5}-?\d{3}\b"), None, "CEP (com a palavra CEP)"),
    RegraPII("ENDERECO_RESIDENCIAL", Categoria.LOCALIZACAO,
             re.compile(r"(?i)\b(?:moro|resido|minha casa|meu endere[cç]o)\b[^.\n]{0,40}?\b(?:rua|r\.|av\.?|avenida|travessa)\s+[^,.\n]{2,40},?\s*(?:n[ºo°.]?\s*)?\d{1,5}"),
             None, "Endereço exato associado à pessoa"),
    RegraPII("SENHA", Categoria.CREDENCIAL,
             re.compile(r"(?i)\b(?:senha|password|passwd|pwd)\b\s*(?:é|eh|=|:)\s*\S{4,}"), None, "Senha em texto claro"),
    RegraPII("TOKEN_API", Categoria.CREDENCIAL,
             re.compile(r"\b(?:sk-[A-Za-z0-9_\-]{16,}|gh[pousr]_[A-Za-z0-9]{20,}|AKIA[0-9A-Z]{16}|eyJ[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{5,})\b"),
             None, "Chave de API / JWT"),
    RegraPII("CID10", Categoria.SAUDE,
             re.compile(r"(?i)\bCID[\s\-:]*([A-TV-Z]\d{2}(?:\.\d)?)\b"), None, "Código de doença CID-10",
             "LGPD art. 5º, II (dado sensível)"),
]

# Termos de saúde: contam como dado SENSÍVEL quando há um vínculo pessoal próximo
# ("tenho asma", "minha mãe é cadeirante", "sou diabético").
TERMOS_SAUDE = [
    "asma", "bronquite", "diabete", "diabetica", "diabetico", "hipertens", "cancer", "hiv", "aids", "gravida",
    "gestante", "cadeirante", "deficiencia", "deficiente", "autis", "epilep", "depress", "dialise", "insulina",
    "oxigenio", "leptospirose", "dengue", "covid", "tuberculose", "acamad", "marcapasso", "quimioterapia",
]
VINCULO_PESSOAL = r"(?:tenho|tem|sou|estou|esta|minha|meu|minhas|meus|filh[oa]|mae|pai|avo|esposa|marido|vizinh[oa])"
REGEX_SAUDE = re.compile(rf"\b{VINCULO_PESSOAL}\b[\w\s,]{{0,30}}?\b({'|'.join(TERMOS_SAUDE)})\w*")

# Nomes de campos que, por si só, indicam PII (detecção por chave em JSON).
CAMPOS_SENSIVEIS: dict[str, Categoria] = {
    "cpf": Categoria.IDENTIFICADOR, "rg": Categoria.IDENTIFICADOR, "cnpj": Categoria.IDENTIFICADOR,
    "email": Categoria.CONTATO, "e_mail": Categoria.CONTATO, "telefone": Categoria.CONTATO, "celular": Categoria.CONTATO,
    "phone": Categoria.CONTATO, "senha": Categoria.CREDENCIAL, "password": Categoria.CREDENCIAL,
    "token": Categoria.CREDENCIAL, "api_key": Categoria.CREDENCIAL, "apikey": Categoria.CREDENCIAL,
    "device_key": Categoria.CREDENCIAL, "x_device_key": Categoria.CREDENCIAL, "cartao": Categoria.FINANCEIRO,
    "diagnostico": Categoria.SAUDE, "doenca": Categoria.SAUDE, "condicao_saude": Categoria.SAUDE,
    "endereco": Categoria.LOCALIZACAO, "cep": Categoria.LOCALIZACAO,
}


# ----------------------------------------------------------------- resultado
@dataclass
class Achado:
    regra: str
    categoria: Categoria
    caminho: str            # onde foi encontrado (ex.: "relatos[3].descricao")
    mascarado: str          # nunca o valor bruto
    hash_valor: str         # sha256 truncado (correlação em auditoria sem expor o dado)
    inicio: int = -1
    fim: int = -1
    base_legal: str = "LGPD art. 5º, I"

    @property
    def peso(self) -> int:
        return PESO_CATEGORIA[self.categoria]

    def to_dict(self) -> dict[str, Any]:
        return {"regra": self.regra, "categoria": self.categoria.value, "caminho": self.caminho,
                "mascarado": self.mascarado, "hash": self.hash_valor, "peso": self.peso, "base_legal": self.base_legal}


def normalizar(texto: str) -> str:
    sem_acento = unicodedata.normalize("NFKD", texto)
    return "".join(c for c in sem_acento if not unicodedata.combining(c)).lower()


def hash_curto(valor: str) -> str:
    return hashlib.sha256(valor.encode("utf-8")).hexdigest()[:12]


def mascarar_valor(valor: str, regra: str) -> str:
    v = valor.strip()
    if regra == "EMAIL" and "@" in v:
        usuario, dominio = v.split("@", 1)
        return f"{usuario[:1]}***@{dominio}"
    if regra in {"SENHA", "TOKEN_API"}:
        return "[CREDENCIAL REMOVIDA]"
    if regra == "SAUDE_CONTEXTO" or regra == "CID10":
        return "[DADO DE SAÚDE REMOVIDO]"
    d = _digitos(v)
    if len(d) >= 6:
        return f"***{d[-2:]}" if regra != "CPF" else f"***.***.***-{d[-2:]}"
    return "*" * min(len(v), 8)


@dataclass
class MotorPII:
    regras: list[RegraPII] = field(default_factory=lambda: list(REGRAS))

    def analisar_texto(self, texto: str, caminho: str = "$") -> list[Achado]:
        if not texto:
            return []
        achados: list[Achado] = []
        ocupado: list[tuple[int, int]] = []

        def livre(i: int, f: int) -> bool:
            return all(f <= a or i >= b for a, b in ocupado)

        for regra in self.regras:
            for m in regra.padrao.finditer(texto):
                valor = m.group(0)
                if regra.validador and not regra.validador(valor):
                    continue
                if not livre(m.start(), m.end()):
                    continue  # evita contar o mesmo trecho como CPF e telefone, por ex.
                ocupado.append((m.start(), m.end()))
                achados.append(Achado(regra.nome, regra.categoria, caminho, mascarar_valor(valor, regra.nome),
                                      hash_curto(_digitos(valor) or valor), m.start(), m.end(), regra.base_legal))

        norm = normalizar(texto)  # mesmo comprimento para textos latinos usuais
        for m in REGEX_SAUDE.finditer(norm):
            if livre(m.start(), m.end()):
                ocupado.append((m.start(), m.end()))
                achados.append(Achado("SAUDE_CONTEXTO", Categoria.SAUDE, caminho, "[DADO DE SAÚDE REMOVIDO]",
                                      hash_curto(m.group(0)), m.start(), m.end(), "LGPD art. 5º, II (dado sensível)"))
        return sorted(achados, key=lambda a: a.inicio)

    def analisar(self, dado: Any, caminho: str = "$") -> list[Achado]:
        """Percorre recursivamente dict/list/str (payloads JSON)."""
        achados: list[Achado] = []
        if isinstance(dado, dict):
            for chave, valor in dado.items():
                sub = f"{caminho}.{chave}"
                chave_norm = re.sub(r"[^a-z0-9]", "_", normalizar(str(chave)))
                cat = CAMPOS_SENSIVEIS.get(chave_norm)
                conteudo = self.analisar(valor, sub)
                if cat and valor not in (None, "", []) and not conteudo:
                    v = str(valor)
                    achados.append(Achado(f"CAMPO_{chave_norm.upper()}", cat, sub, mascarar_valor(v, "SENHA" if cat == Categoria.CREDENCIAL else chave_norm.upper()),
                                          hash_curto(v)))
                achados.extend(conteudo)
        elif isinstance(dado, (list, tuple)):
            for i, item in enumerate(dado):
                achados.extend(self.analisar(item, f"{caminho}[{i}]"))
        elif isinstance(dado, str):
            achados.extend(self.analisar_texto(dado, caminho))
        return achados

    def mascarar_texto(self, texto: str) -> str:
        """Sanitizador: substitui cada PII pela versão mascarada."""
        partes, pos = [], 0
        for a in self.analisar_texto(texto):
            partes.append(texto[pos:a.inicio])
            partes.append(a.mascarado)
            pos = a.fim
        partes.append(texto[pos:])
        return "".join(partes)

    def mascarar(self, dado: Any) -> Any:
        if isinstance(dado, dict):
            out = {}
            for k, v in dado.items():
                cat = CAMPOS_SENSIVEIS.get(re.sub(r"[^a-z0-9]", "_", normalizar(str(k))))
                out[k] = ("[REMOVIDO]" if cat and v not in (None, "") and not isinstance(v, (dict, list)) and not self.analisar(v)
                          else self.mascarar(v))
            return out
        if isinstance(dado, list):
            return [self.mascarar(x) for x in dado]
        if isinstance(dado, str):
            return self.mascarar_texto(dado)
        return dado


def resumo_por_categoria(achados: Iterable[Achado]) -> dict[str, int]:
    r: dict[str, int] = {c.value: 0 for c in Categoria}
    for a in achados:
        r[a.categoria.value] += 1
    return r
