# 01 — Arquitetura Orientada a Serviços (SOA) e Web Services

## O que o professor pede
Um **servidor (backend)** do projeto com: organização do "domínio" (as regras do negócio), **banco de dados**,
**migrações** (o histórico de criação das tabelas), **documentação automática** dos endereços da API (Swagger) e
**testes automáticos**. Entrega: **link do GitHub**.

| Critério | Pontos | Onde está | Pronto? |
|---|---|---|---|
| Estruturação do domínio | 3,0 | `backend\src\AquaGuard.Domain` | ✅ |
| Conexão com banco de dados | 3,0 | `backend\src\AquaGuard.Infrastructure` (EF Core + SQLite) | ✅ |
| Migrações | 1,5 | `backend\src\AquaGuard.Infrastructure\Dados\Migrations` | ✅ |
| Documentação automática | 1,5 | Swagger em `http://localhost:5080/swagger` | ✅ |
| Testes automatizados | 1,0 | `backend\tests` — 47 testes, todos passando | ✅ |

Evidências já prontas em `evidencias\backend\` (print do Swagger, print do painel, resultado dos 47 testes).
Explicação técnica completa: `backend\README.md`.

## O que VOCÊ precisa fazer
1. O projeto **já está no GitHub**: https://github.com/GuilhermeCezarinoSimoes/aquaguard-gs2026 (abra e veja a pasta `backend`).
2. Enviar no Teams o texto abaixo (só **uma** pessoa do grupo).

### (Opcional, 5 min) Ver funcionando com seus olhos
1. Dois cliques em `00_PREPARAR_COMPUTADOR\B_LIGAR_SERVIDOR_API.bat`.
2. No navegador, na página **Swagger**, clique em **GET /api/sensores** ▸ **Try it out** ▸ **Execute**.
   Aparecem os 5 sensores. Isso é a API respondendo.
3. Para rodar os testes: abra o **cmd** ▸ digite `cd ` (com espaço), arraste a pasta `backend` para a janela, Enter ▸
   digite `dotnet test` ▸ Enter. Deve terminar com **"Aprovado! … Aprovado: 47"** (ou "Passed: 47").

## O que enviar no Teams (copie e cole — já está com o link certo)
```
Global Solution 2026.2 – CitizenTech – AquaGuard
Integrantes: Guilherme Cezarino Simoes e Fabrini Soares
Repositório: https://github.com/GuilhermeCezarinoSimoes/aquaguard-gs2026
Backend (SOA): pasta /backend – README em /backend/README.md
Documentação dos endpoints: Swagger (/swagger) e backend/docs/openapi.json
Evidências: /evidencias/backend
```

## Deu erro?
Veja a tabela "Deu erro?" em `00_PREPARAR_COMPUTADOR\PASSO_A_PASSO.md`.
