# AquaGuard · Backend C# (.NET 8) — C# Software Development + SOA e Web Services

**Integrantes:** Guilherme Cezarino Simoes (RM 557724) · Fabrini Soares (RM 557813) · João Both (RM 558690)

API REST que recebe as leituras dos sensores IoT (ESP32), calcula o risco de alagamento, emite alertas por bairro,
registra relatos dos cidadãos e alimenta o app mobile e o painel web. Backend **compartilhado** pelas disciplinas
de C# e SOA.

## Arquitetura (camadas)
```
AquaGuard.Api ──► AquaGuard.Application ──► AquaGuard.Domain
      │                     ▲                      ▲
      └──► AquaGuard.Infrastructure (EF Core + SQLite, repositórios, consultas LINQ)
tests/AquaGuard.Tests (xUnit: unidade de domínio + integração HTTP com WebApplicationFactory)
```
| Projeto | Conteúdo |
|---|---|
| `Domain` | Entidades ricas com encapsulamento (`Sensor`, `LeituraSensor`, `Ocorrencia`, `Alerta`), classe base abstrata `EntidadeBase`, Value Object `Coordenada` (record struct + Haversine), enums, exceções de domínio, **regras de risco polimórficas** (`IRegraRisco` → `RegraPorLimites` (Template Method) → `RegraNivelAgua`, `RegraIntensidadeChuva`; `RegraCombinada`) e `CalculadoraRisco` (Strategy), interfaces de repositório e Unit of Work |
| `Application` | DTOs `record` com DataAnnotations, serviços (`ISensorServico`, `ILeituraServico`, `IOcorrenciaServico`, `IAlertaServico`), registro de DI |
| `Infrastructure` | `AquaGuardDbContext` (Fluent API, índices, conversões), repositório genérico `RepositorioBase<T>` + específicos, `PainelConsultas` (LINQ: subconsulta, `GroupBy`, `Union`, projeções), **migrações**, seed |
| `Api` | Controllers REST, **Swagger/OpenAPI** com comentários XML, `ProblemDetails` (RFC 7807) via `IExceptionHandler`, autenticação de dispositivo por `X-Device-Key` (comparação em tempo constante), health check, CORS, painel web estático (`wwwroot/index.html`) |

## Mapa dos critérios
| C# (10 pts) | Onde |
|---|---|
| POO (3,0) | Herança (`EntidadeBase`, `RegraPorLimites`, `RepositorioBase<T>`), polimorfismo (`IRegraRisco`), encapsulamento (setters privados, coleções somente leitura, métodos de negócio `RegistrarLeitura`, `Escalar`, `Resolver`), abstração (interfaces), Value Object |
| Web API (2,5) | 5 controllers, 14 endpoints, verbos e status corretos (200/201/204/400/401/404/422), `CreatedAtAction`, paginação, filtros |
| EF Core + LINQ (1,5) | DbContext, Fluent API, migração `InicialAquaGuard`, consultas LINQ em repositórios e `PainelConsultas` |
| Async/Await (1,0) | Toda a pilha assíncrona com `CancellationToken` (controllers → serviços → repositórios → EF) |
| Qualidade (2,0) | Camadas, DI, nomes claros, tratamento global de erros, validação, segurança, **47 testes** |

| SOA (10 pts) | Onde |
|---|---|
| Estruturação do domínio (3,0) | `AquaGuard.Domain` (acima) |
| Conexão com banco (3,0) | EF Core + SQLite (`ConnectionStrings:AquaGuard`), repositórios + Unit of Work, health check do banco |
| Migrações (1,5) | `src/AquaGuard.Infrastructure/Dados/Migrations/` · aplicadas automaticamente no startup (`MigrateAsync`) |
| Documentação automática (1,5) | Swagger UI em `/swagger` · OpenAPI exportado em `docs/openapi.json` |
| Testes automatizados (1,0) | `tests/AquaGuard.Tests` — 47 testes (unidade + integração) |

## Endpoints
| Método | Rota | Descrição |
|---|---|---|
| GET | `/api/sensores?bairro=&ativo=` | Lista sensores com última leitura e risco |
| GET | `/api/sensores/{id}` | Detalhe |
| POST | `/api/sensores` | Cadastra sensor |
| PUT | `/api/sensores/{id}/limites` | Recalibra limites |
| DELETE | `/api/sensores/{id}` | Desativa (mantém histórico) |
| GET | `/api/sensores/{id}/leituras?horas=&limite=` | Histórico |
| POST | `/api/leituras` | **Ingestão IoT** (ESP32) → risco + alerta · exige `X-Device-Key` se configurada |
| GET | `/api/ocorrencias?bairro=&status=&pagina=&tamanho=` | Relatos (paginado) |
| GET | `/api/ocorrencias/{id}` | Detalhe |
| POST | `/api/ocorrencias` | Novo relato do cidadão |
| PATCH | `/api/ocorrencias/{id}/status` | IniciarAnalise / Resolver / Descartar |
| GET | `/api/alertas?bairro=&somenteAtivos=` | Alertas |
| POST | `/api/alertas/{id}/encerrar` | Encerra alerta |
| GET | `/api/painel` | Consolidado por bairro |
| GET | `/health` | Saúde (inclui banco) |

## Executar
Pré-requisito: [.NET 8 SDK](https://dotnet.microsoft.com/download/dotnet/8.0).
```bash
cd backend
dotnet restore
dotnet test                                   # 47 testes
dotnet run --project src/AquaGuard.Api --launch-profile http
# Painel: http://localhost:5080  ·  Swagger: http://localhost:5080/swagger
```
O banco SQLite `aquaguard.db` é criado e migrado automaticamente, com 5 sensores de demonstração em pontos reais de
alagamento de São Paulo (os dispositivos são simulados). Migrações manuais:
```bash
dotnet tool restore
dotnet ef migrations add NomeDaMigracao -p src/AquaGuard.Infrastructure -s src/AquaGuard.Api -o Dados/Migrations
dotnet ef database update -p src/AquaGuard.Infrastructure -s src/AquaGuard.Api
```
Chave dos dispositivos IoT: `AquaGuard__DeviceKey=<segredo>` (variável de ambiente). Vazia = modo demonstração.

## Evidências (`../evidencias/backend/`)
- `01_painel_web_alerta_critico.jpg` — painel web consumindo a API após leitura crítica
- `02_swagger_endpoints.jpg` — Swagger UI
- `03_dotnet_test_saida.txt` + `resultado_testes.trx` — 47 testes aprovados
- `04_integracao_payload_esp32.txt` — sequência de leituras de enchente enviada com o mesmo JSON do ESP32
