"""Baixa os dados históricos oficiais do INMET e extrai apenas a estação A701
(SÃO PAULO - MIRANTE), usada pelo AquaGuard.

Fonte: https://portal.inmet.gov.br/dadoshistoricos  (arquivos anuais .zip)

Uso:
    python dados/download_inmet.py --inicio 2015 --fim 2025 --cache <pasta_temporaria>

Os .zip (≈100 MB cada) ficam na pasta de cache; somente os CSVs da estação A701
(≈1,5 MB/ano) são copiados para dados/raw/.
"""
from __future__ import annotations

import argparse
import io
import pathlib
import urllib.request
import zipfile

URL = "https://portal.inmet.gov.br/uploads/dadoshistoricos/{ano}.zip"
ESTACAO = "A701"
RAW_DIR = pathlib.Path(__file__).resolve().parent / "raw"


def baixar(ano: int, cache: pathlib.Path) -> pathlib.Path:
    destino = cache / f"inmet_{ano}.zip"
    if destino.exists() and destino.stat().st_size > 1_000_000:
        return destino
    print(f"[download] {ano} ...", flush=True)
    req = urllib.request.Request(URL.format(ano=ano), headers={"User-Agent": "Mozilla/5.0 (educational)"})
    with urllib.request.urlopen(req, timeout=600) as resp, open(destino, "wb") as fh:
        while chunk := resp.read(1 << 20):
            fh.write(chunk)
    return destino


def extrair_estacao(zip_path: pathlib.Path, ano: int) -> pathlib.Path | None:
    with zipfile.ZipFile(zip_path) as zf:
        nomes = [n for n in zf.namelist() if f"_{ESTACAO}_" in n.upper()]
        if not nomes:
            print(f"[aviso] {ESTACAO} não encontrada em {ano}")
            return None
        RAW_DIR.mkdir(parents=True, exist_ok=True)
        saida = RAW_DIR / f"INMET_{ESTACAO}_SAO_PAULO_MIRANTE_{ano}.csv"
        with zf.open(nomes[0]) as src:
            saida.write_bytes(io.BytesIO(src.read()).getvalue())
        print(f"[ok] {nomes[0]} -> {saida.name}")
        return saida


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--inicio", type=int, default=2015)
    ap.add_argument("--fim", type=int, default=2025)
    ap.add_argument("--cache", type=pathlib.Path, default=pathlib.Path(".cache_inmet"))
    args = ap.parse_args()
    args.cache.mkdir(parents=True, exist_ok=True)
    for ano in range(args.inicio, args.fim + 1):
        z = baixar(ano, args.cache)
        extrair_estacao(z, ano)


if __name__ == "__main__":
    main()
