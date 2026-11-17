"""Reproduz, no computador, o MESMO payload que o ESP32 envia (POST /api/leituras).

Uso apenas para demonstrar a integração ponta a ponta quando a API está em localhost
(o simulador Wokwi web não alcança o localhost da máquina). Não substitui o circuito.

    python iot/simulador_payload.py --api http://localhost:5080 --sensor AQG-001 --cenario enchente
"""
from __future__ import annotations

import argparse
import json
import time
import urllib.error
import urllib.request

CENARIOS = {
    # (nível da água cm, chuva mm/h) a cada passo
    "normal": [(15, 0), (16, 1), (15, 0)],
    "enchente": [(20, 5), (35, 12), (55, 22), (75, 30), (95, 38), (125, 55), (110, 20), (70, 5), (40, 0)],
}


def enviar(api: str, sensor: str, nivel: float, chuva: float, chave: str | None) -> dict:
    corpo = json.dumps({"codigoSensor": sensor, "nivelAguaCm": nivel, "chuvaMmH": chuva}).encode()
    req = urllib.request.Request(f"{api.rstrip('/')}/api/leituras", data=corpo, method="POST",
                                 headers={"Content-Type": "application/json", **({"X-Device-Key": chave} if chave else {})})
    with urllib.request.urlopen(req, timeout=5) as r:
        return json.loads(r.read())


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--api", default="http://localhost:5080")
    ap.add_argument("--sensor", default="AQG-001")
    ap.add_argument("--cenario", choices=CENARIOS, default="enchente")
    ap.add_argument("--intervalo", type=float, default=2.0)
    ap.add_argument("--chave", default=None)
    a = ap.parse_args()
    for nivel, chuva in CENARIOS[a.cenario]:
        try:
            r = enviar(a.api, a.sensor, nivel, chuva, a.chave)
            alerta = r.get("alertaGerado") or {}
            print(f"nivel={nivel:>5.1f}cm chuva={chuva:>4.1f}mm/h -> risco={r['leitura']['risco']:<8} "
                  f"alerta_bairro={alerta.get('nivel', '-')}")
        except urllib.error.HTTPError as e:
            print(f"HTTP {e.code}: {e.read().decode()[:200]}")
        except urllib.error.URLError as e:
            print(f"API indisponível: {e.reason}")
            break
        time.sleep(a.intervalo)


if __name__ == "__main__":
    main()
