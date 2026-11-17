using AquaGuard.Application.Servicos;
using AquaGuard.Domain.Risco;
using Microsoft.Extensions.DependencyInjection;

namespace AquaGuard.Application;

public static class DependencyInjection
{
    /// <summary>Registra regras de risco (Strategy) e serviços de aplicação.</summary>
    public static IServiceCollection AddAquaGuardApplication(this IServiceCollection services)
    {
        services.AddSingleton<IRegraRisco, RegraNivelAgua>();
        services.AddSingleton<IRegraRisco, RegraIntensidadeChuva>();
        services.AddSingleton<IRegraRisco, RegraCombinada>();
        services.AddSingleton<ICalculadoraRisco, CalculadoraRisco>();

        services.AddScoped<ISensorServico, SensorServico>();
        services.AddScoped<ILeituraServico, LeituraServico>();
        services.AddScoped<IOcorrenciaServico, OcorrenciaServico>();
        services.AddScoped<IAlertaServico, AlertaServico>();
        return services;
    }
}
