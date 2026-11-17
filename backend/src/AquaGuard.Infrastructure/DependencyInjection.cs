using AquaGuard.Application.Servicos;
using AquaGuard.Domain.Interfaces;
using AquaGuard.Infrastructure.Consultas;
using AquaGuard.Infrastructure.Dados;
using AquaGuard.Infrastructure.Repositorios;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;

namespace AquaGuard.Infrastructure;

public static class DependencyInjection
{
    public static IServiceCollection AddAquaGuardInfrastructure(this IServiceCollection services, IConfiguration config)
    {
        var conn = config.GetConnectionString("AquaGuard") ?? "Data Source=aquaguard.db";
        services.AddDbContext<AquaGuardDbContext>(o => o.UseSqlite(conn));

        services.AddScoped<IUnidadeDeTrabalho>(sp => sp.GetRequiredService<AquaGuardDbContext>());
        services.AddScoped<ISensorRepositorio, SensorRepositorio>();
        services.AddScoped<ILeituraRepositorio, LeituraRepositorio>();
        services.AddScoped<IOcorrenciaRepositorio, OcorrenciaRepositorio>();
        services.AddScoped<IAlertaRepositorio, AlertaRepositorio>();
        services.AddScoped<IPainelConsultas, PainelConsultas>();
        return services;
    }
}
