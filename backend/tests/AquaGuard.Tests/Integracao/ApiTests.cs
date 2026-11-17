using System.Net;
using System.Net.Http.Json;
using System.Text.Json;
using System.Text.Json.Serialization;
using AquaGuard.Application.Dtos;
using AquaGuard.Domain.Enums;
using AquaGuard.Infrastructure.Dados;
using Microsoft.AspNetCore.Hosting;
using Microsoft.AspNetCore.Mvc.Testing;
using Microsoft.Data.Sqlite;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.DependencyInjection.Extensions;

namespace AquaGuard.Tests.Integracao;

/// <summary>Sobe a API real com um SQLite em memória isolado por fábrica.</summary>
public sealed class AquaGuardFactory : WebApplicationFactory<Program>
{
    private readonly SqliteConnection _conexao = new("DataSource=:memory:");
    public string? DeviceKey { get; init; }

    protected override void ConfigureWebHost(IWebHostBuilder builder)
    {
        _conexao.Open();
        builder.UseEnvironment("Testing");
        builder.UseSetting("AquaGuard:DeviceKey", DeviceKey ?? "");
        builder.ConfigureServices(services =>
        {
            services.RemoveAll<DbContextOptions<AquaGuardDbContext>>();
            services.AddDbContext<AquaGuardDbContext>(o => o.UseSqlite(_conexao));
        });
    }

    protected override void Dispose(bool disposing)
    {
        base.Dispose(disposing);
        _conexao.Dispose();
    }
}

public class ApiTests : IClassFixture<AquaGuardFactory>
{
    private static readonly JsonSerializerOptions Json = new(JsonSerializerDefaults.Web)
    { Converters = { new JsonStringEnumConverter() } };

    private readonly HttpClient _http;

    public ApiTests(AquaGuardFactory f) => _http = f.CreateClient();

    [Fact]
    public async Task Health_Retorna200()
        => Assert.Equal(HttpStatusCode.OK, (await _http.GetAsync("/health")).StatusCode);

    [Fact]
    public async Task Swagger_DocumentoDisponivel()
    {
        var r = await _http.GetAsync("/swagger/v1/swagger.json");
        Assert.Equal(HttpStatusCode.OK, r.StatusCode);
        Assert.Contains("/api/leituras", await r.Content.ReadAsStringAsync());
    }

    [Fact]
    public async Task Sensores_Seed_RetornaCincoPontos()
    {
        var lista = await _http.GetFromJsonAsync<List<SensorResponse>>("/api/sensores", Json);
        Assert.NotNull(lista);
        Assert.True(lista!.Count >= 5);
    }

    [Fact]
    public async Task Sensor_Inexistente_Retorna404ProblemDetails()
    {
        var r = await _http.GetAsync("/api/sensores/9999");
        Assert.Equal(HttpStatusCode.NotFound, r.StatusCode);
        Assert.Contains("não encontrado", await r.Content.ReadAsStringAsync());
    }

    [Fact]
    public async Task CriarSensor_CodigoDuplicado_Retorna422()
    {
        var req = new CriarSensorRequest("AQG-001", "Duplicado", "Centro", -23.5, -46.6, 50, 80);
        var r = await _http.PostAsJsonAsync("/api/sensores", req, Json);
        Assert.Equal(HttpStatusCode.UnprocessableEntity, r.StatusCode);
    }

    [Fact]
    public async Task CriarSensor_PayloadInvalido_Retorna400()
    {
        var req = new CriarSensorRequest("X", "", "", 200, 0, -1, 0);
        var r = await _http.PostAsJsonAsync("/api/sensores", req, Json);
        Assert.Equal(HttpStatusCode.BadRequest, r.StatusCode);
    }

    [Fact]
    public async Task Leitura_Critica_GeraAlertaNoBairro_EApareceNoPainel()
    {
        var r = await _http.PostAsJsonAsync("/api/leituras",
            new RegistrarLeituraRequest("AQG-004", 160, 55, null), Json);
        Assert.Equal(HttpStatusCode.Created, r.StatusCode);

        var corpo = await r.Content.ReadFromJsonAsync<RegistrarLeituraResponse>(Json);
        Assert.Equal(NivelRisco.Critico, corpo!.Leitura.Risco);
        Assert.NotNull(corpo.AlertaGerado);
        Assert.Equal("Ipiranga", corpo.AlertaGerado!.Bairro);

        var alertas = await _http.GetFromJsonAsync<List<AlertaResponse>>("/api/alertas?bairro=Ipiranga", Json);
        Assert.Contains(alertas!, a => a.Nivel == NivelRisco.Critico && a.Ativo);

        var painel = await _http.GetFromJsonAsync<PainelResponse>("/api/painel", Json);
        Assert.Equal(NivelRisco.Critico, painel!.RiscoGeral);
        Assert.Equal("Ipiranga", painel.Bairros[0].Bairro);
    }

    [Fact]
    public async Task Leitura_Normal_NaoGeraAlerta()
    {
        var r = await _http.PostAsJsonAsync("/api/leituras",
            new RegistrarLeituraRequest("AQG-005", 5, 0, null), Json);
        var corpo = await r.Content.ReadFromJsonAsync<RegistrarLeituraResponse>(Json);
        Assert.Equal(NivelRisco.Normal, corpo!.Leitura.Risco);
        Assert.Null(corpo.AlertaGerado);
    }

    [Fact]
    public async Task Leitura_SensorDesconhecido_Retorna404()
    {
        var r = await _http.PostAsJsonAsync("/api/leituras", new RegistrarLeituraRequest("NAO-EXISTE", 10, 0, null), Json);
        Assert.Equal(HttpStatusCode.NotFound, r.StatusCode);
    }

    [Fact]
    public async Task Historico_RetornaLeiturasMaisRecentesPrimeiro()
    {
        await _http.PostAsJsonAsync("/api/leituras", new RegistrarLeituraRequest("AQG-003", 10, 0, DateTime.UtcNow.AddMinutes(-10)), Json);
        await _http.PostAsJsonAsync("/api/leituras", new RegistrarLeituraRequest("AQG-003", 20, 0, DateTime.UtcNow), Json);
        var sensores = await _http.GetFromJsonAsync<List<SensorResponse>>("/api/sensores", Json);
        var id = sensores!.First(s => s.Codigo == "AQG-003").Id;

        var hist = await _http.GetFromJsonAsync<List<LeituraResponse>>($"/api/sensores/{id}/leituras?horas=1", Json);
        Assert.True(hist!.Count >= 2);
        Assert.True(hist[0].DataHoraUtc >= hist[1].DataHoraUtc);
    }

    [Fact]
    public async Task Ocorrencia_CriarEResolver_FluxoCompleto()
    {
        var criar = new CriarOcorrenciaRequest(TipoOcorrencia.BueiroEntupido, "Bueiro entupido na praça",
            "Pacaembu", -23.54, -46.66, 2, null);
        var r = await _http.PostAsJsonAsync("/api/ocorrencias", criar, Json);
        Assert.Equal(HttpStatusCode.Created, r.StatusCode);
        var o = await r.Content.ReadFromJsonAsync<OcorrenciaResponse>(Json);

        var r2 = await _http.PatchAsJsonAsync($"/api/ocorrencias/{o!.Id}/status",
            new AlterarStatusOcorrenciaRequest(AcaoOcorrencia.Resolver), Json);
        var resolvida = await r2.Content.ReadFromJsonAsync<OcorrenciaResponse>(Json);
        Assert.Equal(StatusOcorrencia.Resolvida, resolvida!.Status);

        var r3 = await _http.PatchAsJsonAsync($"/api/ocorrencias/{o.Id}/status",
            new AlterarStatusOcorrenciaRequest(AcaoOcorrencia.Resolver), Json);
        Assert.Equal(HttpStatusCode.UnprocessableEntity, r3.StatusCode);
    }

    [Fact]
    public async Task Ocorrencias_ListagemPaginada()
    {
        var pagina = await _http.GetFromJsonAsync<PaginaResponse<OcorrenciaResponse>>("/api/ocorrencias?pagina=1&tamanho=1", Json);
        Assert.Single(pagina!.Itens);
        Assert.True(pagina.Total >= 2);
    }
}

public class ChaveDispositivoTests : IClassFixture<ChaveDispositivoTests.FactoryComChave>
{
    public sealed class FactoryComChave : WebApplicationFactory<Program>
    {
        private readonly SqliteConnection _c = new("DataSource=:memory:");
        protected override void ConfigureWebHost(IWebHostBuilder builder)
        {
            _c.Open();
            builder.UseSetting("AquaGuard:DeviceKey", "segredo-teste");
            builder.ConfigureServices(s =>
            {
                s.RemoveAll<DbContextOptions<AquaGuardDbContext>>();
                s.AddDbContext<AquaGuardDbContext>(o => o.UseSqlite(_c));
            });
        }
        protected override void Dispose(bool disposing) { base.Dispose(disposing); _c.Dispose(); }
    }

    private readonly FactoryComChave _f;
    public ChaveDispositivoTests(FactoryComChave f) => _f = f;

    [Fact]
    public async Task SemChave_Retorna401()
    {
        var http = _f.CreateClient();
        var r = await http.PostAsJsonAsync("/api/leituras", new RegistrarLeituraRequest("AQG-001", 10, 0, null));
        Assert.Equal(HttpStatusCode.Unauthorized, r.StatusCode);
    }

    [Fact]
    public async Task ComChaveCorreta_Retorna201()
    {
        var http = _f.CreateClient();
        http.DefaultRequestHeaders.Add("X-Device-Key", "segredo-teste");
        var r = await http.PostAsJsonAsync("/api/leituras", new RegistrarLeituraRequest("AQG-001", 10, 0, null));
        Assert.Equal(HttpStatusCode.Created, r.StatusCode);
    }
}
