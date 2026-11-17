using System.Reflection;
using System.Text.Json.Serialization;
using AquaGuard.Api.Infra;
using AquaGuard.Application;
using AquaGuard.Infrastructure;
using AquaGuard.Infrastructure.Dados;
using Microsoft.EntityFrameworkCore;
using Microsoft.OpenApi.Models;

var builder = WebApplication.CreateBuilder(args);

builder.Services
    .AddControllers()
    .AddJsonOptions(o => o.JsonSerializerOptions.Converters.Add(new JsonStringEnumConverter()));

builder.Services.AddAquaGuardApplication();
builder.Services.AddAquaGuardInfrastructure(builder.Configuration);

builder.Services.AddProblemDetails();
builder.Services.AddExceptionHandler<TratadorExcecoes>();
builder.Services.AddHealthChecks().AddDbContextCheck<AquaGuardDbContext>("database");

builder.Services.AddCors(o => o.AddDefaultPolicy(p => p.AllowAnyOrigin().AllowAnyHeader().AllowAnyMethod()));

builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen(c =>
{
    c.SwaggerDoc("v1", new OpenApiInfo
    {
        Title = "AquaGuard API",
        Version = "v1",
        Description = "CitizenTech de prevenção de alagamentos: sensores IoT (ESP32), leituras, " +
                      "alertas por bairro e ocorrências relatadas pelos cidadãos. FIAP Global Solution 2026.2.",
        Contact = new OpenApiContact { Name = "Guilherme Cezarino Simoes e Fabrini Soares" }
    });
    var xml = Path.Combine(AppContext.BaseDirectory, $"{Assembly.GetExecutingAssembly().GetName().Name}.xml");
    c.IncludeXmlComments(xml);
    c.AddSecurityDefinition("DeviceKey", new OpenApiSecurityScheme
    {
        Name = ChaveDispositivoFilter.Header,
        In = ParameterLocation.Header,
        Type = SecuritySchemeType.ApiKey,
        Description = "Chave dos dispositivos IoT (POST /api/leituras)."
    });
    c.OperationFilter<ChaveDispositivoSwaggerFilter>();
});

var app = builder.Build();

// Cria/atualiza o banco aplicando as migrações versionadas e carrega dados de demonstração.
using (var scope = app.Services.CreateScope())
{
    var db = scope.ServiceProvider.GetRequiredService<AquaGuardDbContext>();
    if (db.Database.IsRelational()) await db.Database.MigrateAsync();
    else await db.Database.EnsureCreatedAsync();
    if (app.Configuration.GetValue("AquaGuard:Seed", true)) await SeedDados.AplicarAsync(db);
}

app.UseExceptionHandler();
app.UseStatusCodePages();
app.UseCors();

app.UseSwagger();
app.UseSwaggerUI(c =>
{
    c.SwaggerEndpoint("/swagger/v1/swagger.json", "AquaGuard API v1");
    c.DocumentTitle = "AquaGuard API";
});

app.UseDefaultFiles();
app.UseStaticFiles();

app.MapControllers();
app.MapHealthChecks("/health");

app.Run();

/// <summary>Exposto para testes de integração (WebApplicationFactory).</summary>
public partial class Program;
