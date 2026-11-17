"""Gera o Dashboard Executivo (HTML estático, sem dependências) com o Indicador de Risco Cidadão."""
from __future__ import annotations

import html
import json
from typing import Any


def _cor(faixa: str) -> str:
    return {"Baixo": "#1B7F3B", "Moderado": "#8A5A00", "Alto": "#B54708", "Crítico": "#B42318"}[faixa]


def gerar(dados: dict[str, Any]) -> str:
    e = lambda s: html.escape(str(s))  # noqa: E731
    antes, depois = dados["irc_antes"], dados["irc_depois"]
    cats = dados["pii_por_categoria"]
    max_cat = max(cats.values()) or 1
    barras = "".join(
        f"<div class='bar'><span>{e(k)}</span><div class='track'><div class='fill' style='width:{v / max_cat * 100:.0f}%'></div></div><b>{v}</b></div>"
        for k, v in sorted(cats.items(), key=lambda x: -x[1]))
    fluxos = "".join(
        f"<tr><td>{e(f['sink'])}</td><td>{e(', '.join(f['rotulos']))}</td><td><span class='tag {e(f['decisao'])}'>{e(f['decisao'])}</span></td><td>{e(f['origem'])}</td></tr>"
        for f in dados["eventos_protegido"] if f["rotulos"])
    estaticos = "".join(
        f"<tr><td>{e(f['arquivo'])}:{f['linha']}</td><td>{e(f['tipo_sink'])}</td><td><code>{e(f['trecho'][:90])}</code></td></tr>"
        for f in dados["fluxos_estaticos"])
    alertas = "".join(
        f"<div class='alerta'><h4>{e(a.get('titulo'))}</h4><p><b>Risco para você:</b> {e(a.get('risco_para_voce'))}</p>"
        f"<p><b>O que fizemos:</b> {e(a.get('o_que_fizemos'))}</p><p><b>O que você pode fazer:</b> {e(a.get('o_que_voce_pode_fazer'))}</p></div>"
        for a in dados["alertas_cidadao"][:6])

    def gauge(irc: dict[str, Any], rotulo: str) -> str:
        v = irc["valor"]
        return (f"<div class='card gauge'><div class='l'>{e(rotulo)}</div>"
                f"<svg viewBox='0 0 120 70' role='img' aria-label='{e(rotulo)}: {v:.0f} de 100, {e(irc['faixa'])}'>"
                f"<path d='M10 60 A50 50 0 0 1 110 60' fill='none' stroke='var(--line)' stroke-width='12' stroke-linecap='round'/>"
                f"<path d='M10 60 A50 50 0 0 1 110 60' fill='none' stroke='{_cor(irc['faixa'])}' stroke-width='12' stroke-linecap='round' "
                f"stroke-dasharray='{157 * v / 100:.1f} 200'/></svg>"
                f"<div class='v'>{v:.0f}<small>/100</small></div><div class='pill' style='background:{_cor(irc['faixa'])}'>{e(irc['faixa'])}</div></div>")

    return f"""<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>AquaGuard · Risco Cidadão</title><style>
:root{{--bg:#f5f7fa;--card:#fff;--txt:#0f172a;--muted:#64748b;--line:#e2e8f0}}
@media (prefers-color-scheme:dark){{:root{{--bg:#0b1220;--card:#111a2e;--txt:#e5e7eb;--muted:#94a3b8;--line:#1e293b}}}}
*{{box-sizing:border-box}}body{{margin:0;font:15px/1.5 system-ui,-apple-system,Segoe UI,Roboto,sans-serif;background:var(--bg);color:var(--txt)}}
main{{max-width:1150px;margin:auto;padding:24px 16px 48px;display:grid;gap:16px}}h1{{margin:0;font-size:26px}}h2{{font-size:18px;margin:0 0 10px}}
.sub{{color:var(--muted);font-size:13px}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:12px}}
.card{{background:var(--card);border:1px solid var(--line);border-radius:16px;padding:16px}}
.gauge{{text-align:center}}.gauge svg{{width:180px;max-width:100%}}.gauge .v{{font-size:40px;font-weight:800;margin-top:-28px}}.gauge small{{font-size:14px;color:var(--muted)}}
.l{{color:var(--muted);font-size:12px;text-transform:uppercase;letter-spacing:.06em}}.kpi{{font-size:30px;font-weight:700}}
.pill,.tag{{display:inline-block;color:#fff;border-radius:999px;padding:2px 12px;font-weight:700;font-size:13px}}
.tag.bloqueado{{background:#1B7F3B}}.tag.vazou{{background:#B42318}}.tag.sanitizado{{background:#0A6CB0}}.tag.permitido{{background:#64748b}}
.bar{{display:grid;grid-template-columns:110px 1fr 30px;gap:8px;align-items:center;margin:6px 0}}.track{{background:var(--line);border-radius:6px;height:10px}}
.fill{{background:#0A6CB0;height:10px;border-radius:6px}}table{{width:100%;border-collapse:collapse;font-size:13px}}th,td{{text-align:left;padding:7px 6px;border-bottom:1px solid var(--line);vertical-align:top}}
th{{color:var(--muted)}}code{{font-size:12px;word-break:break-all}}.scroll{{overflow-x:auto}}
.alerta{{border-left:5px solid #B54708;background:var(--bg);border-radius:10px;padding:10px 14px;margin:8px 0}}.alerta h4{{margin:0 0 4px}}.alerta p{{margin:2px 0}}
</style></head><body><main>
<header><h1>AquaGuard · Dashboard Executivo de Privacidade</h1>
<div class="sub">Indicador de Risco Cidadão (IRC) · gerado em {e(dados['gerado_em'])} · fontes: {e(dados['fontes'])} · motor de IA: {e(dados['motor_llm'])}</div></header>
<section class="grid">{gauge(antes, "IRC sem proteção (v1)")}{gauge(depois, "IRC com Taint Analysis (v2)")}
<div class="card"><div class="l">Registros analisados</div><div class="kpi">{dados['registros']}</div><div class="sub">relatos de cidadãos e payloads</div>
<div class="l" style="margin-top:12px">Dados pessoais detectados</div><div class="kpi">{dados['total_pii']}</div></div>
<div class="card"><div class="l">Vazamentos bloqueados</div><div class="kpi">{dados['bloqueados']}</div>
<div class="l" style="margin-top:12px">Vazamentos que passariam na v1</div><div class="kpi">{dados['vazariam']}</div>
<div class="l" style="margin-top:12px">Falhas no código (estático)</div><div class="kpi">{len(dados['fluxos_estaticos'])}</div></div></section>
<section class="grid"><div class="card"><h2>PII por categoria</h2>{barras}</div>
<div class="card"><h2>Redução de risco</h2><p>O IRC caiu de <b>{antes['valor']:.0f}</b> ({e(antes['faixa'])}) para <b>{depois['valor']:.0f}</b> ({e(depois['faixa'])}),
uma redução de <b>{antes['valor'] - depois['valor']:.0f} pontos</b>, porque os fluxos com dados pessoais passaram a ser bloqueados antes de chegar a logs, feed público, LLM e serviços externos.</p>
<p class="sub">IRC = 100·(1−e^(−S/120)); S = Σ peso da categoria × fator de exposição × alcance. Detalhe em risco_cidadao.json.</p></div></section>
<section class="card"><h2>Alertas para o cidadão</h2><p class='sub'>Tradução das falhas técnicas · motor: {e(dados['motor_llm'])}</p>{alertas}</section>
<section class="card"><h2>Taint Analysis em execução (v2 protegida)</h2><div class="scroll"><table><thead><tr><th>Sink</th><th>Dados</th><th>Decisão</th><th>Origem</th></tr></thead><tbody>{fluxos}</tbody></table></div></section>
<section class="card"><h2>Taint Analysis estático (código-fonte)</h2><div class="scroll"><table><thead><tr><th>Local</th><th>Sink</th><th>Trecho</th></tr></thead><tbody>{estaticos or '<tr><td colspan=3>Nenhum fluxo inseguro.</td></tr>'}</tbody></table></div></section>
<script type="application/json" id="dados">{html.escape(json.dumps({k: dados[k] for k in ('irc_antes', 'irc_depois', 'pii_por_categoria')}, ensure_ascii=False))}</script>
</main></body></html>"""
