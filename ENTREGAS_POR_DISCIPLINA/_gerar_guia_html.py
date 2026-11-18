"""Junta todos os PASSO_A_PASSO.md num único HTML fácil de ler (GUIA_PARA_TERMINAR_O_PROJETO.html).

Uso (só se alterar algum guia):  pip install markdown  &&  python _gerar_guia_html.py
"""
import html
import pathlib
import re

import markdown

AQUI = pathlib.Path(__file__).resolve().parent
SAIDA = AQUI.parent / "GUIA_PARA_TERMINAR_O_PROJETO.html"

SECOES = [
    ("inicio", "Comece aqui", "00_COMECE_AQUI.md"),
    ("explicacao", "O projeto explicado", "EXPLICACAO_SIMPLES.md"),
    ("preparar", "00 · Preparar o computador", "00_PREPARAR_COMPUTADOR/PASSO_A_PASSO.md"),
    ("soa", "01 · SOA e Web Services", "01_SOA_e_Web_Services/PASSO_A_PASSO.md"),
    ("csharp", "02 · C# Software Development", "02_CSharp_Software_Development/PASSO_A_PASSO.md"),
    ("mobile", "03 · Mobile Development & IoT", "03_Mobile_Development_e_IoT/PASSO_A_PASSO.md"),
    ("ml", "04 · IA & Machine Learning", "04_Inteligencia_Artificial_e_Machine_Learning/PASSO_A_PASSO.md"),
    ("cyber", "05 · Cybersecurity", "05_Cybersecurity/PASSO_A_PASSO.md"),
    ("os", "06 · Operating Systems", "06_Operating_Systems/PASSO_A_PASSO.md"),
    ("iot", "07 · Physical Computing (Wokwi)", "07_Physical_Computing_IoT_e_IoB/PASSO_A_PASSO.md"),
    ("testing", "08 · Testing + Pitch", "08_Testing_Compliance_e_QA/PASSO_A_PASSO.md"),
]


LISTA = re.compile(r"^\s*(?:[-*] |\d+\. )")


def separar_listas(texto: str) -> str:
    """O Python-Markdown só reconhece listas com linha em branco antes; insere quando falta."""
    saida, anterior = [], ""
    dentro_codigo = False
    for linha in texto.splitlines():
        if linha.startswith("```"):
            dentro_codigo = not dentro_codigo
        if (not dentro_codigo and LISTA.match(linha) and anterior.strip()
                and not LISTA.match(anterior) and not anterior.startswith((" ", "\t", "|"))):
            saida.append("")
        # tabelas também precisam de linha em branco antes
        elif (not dentro_codigo and linha.startswith("|") and anterior.strip()
                and not anterior.startswith("|")):
            saida.append("")
        saida.append(linha)
        anterior = linha
    return "\n".join(saida)


def converter(texto: str) -> str:
    texto = separar_listas(texto)
    # checklists "- [ ]" / "- [x]" viram caixinhas clicáveis
    texto = re.sub(r"^- \[ \] ", "- <input type='checkbox'> ", texto, flags=re.M)
    texto = re.sub(r"^- \[x\] ", "- <input type='checkbox' checked> ", texto, flags=re.M)
    corpo = markdown.markdown(texto, extensions=["tables", "fenced_code", "sane_lists"])
    # links de arquivos .md locais não funcionam no navegador: mostra só o nome
    corpo = re.sub(r'<a href="(?!https?://)[^"]*">(.*?)</a>', r"<b>\1</b>", corpo)
    # links da web abrem em nova aba
    corpo = corpo.replace('<a href="http', '<a target="_blank" rel="noopener" href="http')
    # blocos de texto para o Teams ganham botão "Copiar"
    corpo = corpo.replace("<pre><code>", "<pre><button class='copiar' onclick='copiar(this)'>Copiar</button><code>")
    return corpo


partes, menu = [], []
for ancora, titulo, arquivo in SECOES:
    conteudo = (AQUI / arquivo).read_text(encoding="utf-8")
    pasta = "ENTREGAS_POR_DISCIPLINA" + ("\\" + arquivo.split("/")[0] if "/" in arquivo else "")
    menu.append(f'<a href="#{ancora}">{html.escape(titulo)}</a>')
    partes.append(f'<section id="{ancora}"><div class="pasta">📁 Pasta: {html.escape(pasta)}</div>'
                  f"{converter(conteudo)}<p class='topo'><a href='#inicio'>↑ voltar ao início</a></p></section>")

SAIDA.write_text(f"""<!doctype html>
<html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>AquaGuard · Guia para terminar o projeto</title>
<style>
:root{{--bg:#f6f7f9;--card:#fff;--txt:#14171f;--muted:#5b6576;--line:#e1e5eb;--brand:#0a6cb0;--soft:#e8f2fb}}
*{{box-sizing:border-box}} html{{scroll-behavior:smooth}}
body{{margin:0;font:17px/1.6 "Segoe UI",system-ui,sans-serif;background:var(--bg);color:var(--txt)}}
nav{{position:fixed;top:0;left:0;bottom:0;width:270px;overflow:auto;background:#0f2235;padding:20px 12px}}
nav h1{{color:#fff;font-size:18px;margin:0 8px 14px}} nav a{{display:block;color:#cfe3f5;text-decoration:none;padding:7px 10px;border-radius:8px;font-size:15px}}
nav a:hover{{background:#1d3a57;color:#fff}} nav .prazo{{color:#ffcf66;font-size:13px;margin:16px 10px}}
main{{margin-left:270px;padding:24px 32px 80px;max-width:1100px}}
section{{background:var(--card);border:1px solid var(--line);border-radius:16px;padding:8px 28px 18px;margin:0 0 28px}}
h1{{font-size:28px}} h2{{font-size:22px;border-bottom:2px solid var(--soft);padding-bottom:4px;margin-top:28px}} h3{{font-size:19px}}
table{{border-collapse:collapse;width:100%;margin:12px 0;font-size:15px;display:block;overflow-x:auto}}
th,td{{border:1px solid var(--line);padding:7px 9px;text-align:left;vertical-align:top}} th{{background:var(--soft)}}
code{{background:#eef1f5;padding:1px 5px;border-radius:5px;font-size:15px}}
pre{{position:relative;background:#0f2235;color:#e9f2fb;padding:16px;border-radius:10px;overflow:auto}} pre code{{background:none;color:inherit;padding:0}}
.copiar{{position:absolute;top:8px;right:8px;background:#ffcf66;border:0;border-radius:6px;padding:4px 12px;font-weight:700;cursor:pointer}}
blockquote{{margin:12px 0;padding:10px 16px;background:#fff7e0;border-left:5px solid #e0a800;border-radius:8px}}
.pasta{{display:inline-block;margin-top:16px;background:var(--soft);color:var(--brand);font-weight:600;padding:4px 12px;border-radius:999px;font-size:14px}}
.topo{{text-align:right;font-size:14px}} input[type=checkbox]{{transform:scale(1.3);margin-right:6px}}
@media (max-width:800px){{nav{{position:static;width:auto}} main{{margin:0;padding:12px}} section{{padding:6px 14px}}}}
</style></head><body>
<nav><h1>AquaGuard<br><small style="font-weight:400;color:#9fc3e3">Guia para terminar a GS</small></h1>
{''.join(menu)}<div class="prazo">⏰ Prazo: 19/11/2026 às 23h55</div></nav>
<main>{''.join(partes)}</main>
<script>
function copiar(b){{const t=b.nextElementSibling.innerText;navigator.clipboard.writeText(t).then(()=>{{b.textContent='Copiado!';setTimeout(()=>b.textContent='Copiar',1500)}})}}
</script></body></html>""", encoding="utf-8")
print("Gerado:", SAIDA)
