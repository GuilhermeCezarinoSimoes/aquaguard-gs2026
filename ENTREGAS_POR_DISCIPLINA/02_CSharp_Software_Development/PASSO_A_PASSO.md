# 02 — C# Software Development

## O que o professor pede
Um projeto em **C#/.NET** com **Web API**, **Entity Framework Core** (banco de dados), README com instruções,
documentação dos endpoints (Swagger) e evidências. Entrega: **link do GitHub**.
É o **mesmo backend** da matéria de SOA (o edital permite um backend compartilhado).

| Critério | Pontos | O que significa (simples) | Onde está | Pronto? |
|---|---|---|---|---|
| POO | 3,0 | Programação orientada a objetos: classes, herança, interfaces | `backend\src\AquaGuard.Domain` (ex.: `Entidades\Sensor.cs`, `Risco\RegrasRisco.cs`) | ✅ |
| Web API | 2,5 | Os "endereços" que o app e o sensor usam | `backend\src\AquaGuard.Api\Controllers\Controllers.cs` (15 endpoints) | ✅ |
| EF Core + LINQ | 1,5 | Banco de dados e consultas | `backend\src\AquaGuard.Infrastructure` (ex.: `Consultas\PainelConsultas.cs`) | ✅ |
| Async/Await | 1,0 | Código que não "trava" esperando o banco | Todos os métodos `...Async` | ✅ |
| Qualidade do código | 2,0 | Organização, testes, tratamento de erros | 4 projetos separados + 47 testes | ✅ |

O mapa completo de "critério → arquivo" está em `backend\README.md`, seção **"Mapa dos critérios"**.

## O que VOCÊ precisa fazer
1. Publicar no GitHub (se ainda não fez) — `00_PREPARAR_COMPUTADOR\PASSO_A_PASSO.md`, Parte 3.
2. Enviar no Teams.

## O que enviar no Teams (copie e cole, trocando o link)
```
Global Solution 2026.2 – CitizenTech – AquaGuard
Integrantes: Guilherme Cezarino Simoes e Fabrini Soares
Repositório: https://github.com/SEU-USUARIO/aquaguard-gs2026
Projeto C# (.NET 8 Web API + EF Core): pasta /backend – instruções em /backend/README.md
Documentação: Swagger em /swagger · Evidências: /evidencias/backend (47 testes aprovados)
```
