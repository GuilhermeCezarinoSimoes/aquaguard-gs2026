using System.Security.Cryptography;
using System.Text;
using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Mvc.Filters;
using Microsoft.OpenApi.Models;
using Swashbuckle.AspNetCore.SwaggerGen;

namespace AquaGuard.Api.Infra;

/// <summary>Marca endpoints que exigem a chave do dispositivo IoT.</summary>
[AttributeUsage(AttributeTargets.Method)]
public sealed class RequerChaveDispositivoAttribute : TypeFilterAttribute
{
    public RequerChaveDispositivoAttribute() : base(typeof(ChaveDispositivoFilter)) { }
}

/// <summary>
/// Valida o cabeçalho X-Device-Key (comparação em tempo constante).
/// Se AquaGuard:DeviceKey não estiver configurada, a validação é desabilitada (modo demo).
/// </summary>
public sealed class ChaveDispositivoFilter : IAsyncActionFilter
{
    public const string Header = "X-Device-Key";
    private readonly string? _chave;

    public ChaveDispositivoFilter(IConfiguration config) => _chave = config["AquaGuard:DeviceKey"];

    public Task OnActionExecutionAsync(ActionExecutingContext ctx, ActionExecutionDelegate next)
    {
        if (string.IsNullOrEmpty(_chave)) return next();

        var recebida = ctx.HttpContext.Request.Headers[Header].ToString();
        var ok = CryptographicOperations.FixedTimeEquals(Encoding.UTF8.GetBytes(recebida), Encoding.UTF8.GetBytes(_chave));
        if (!ok)
        {
            ctx.Result = new UnauthorizedObjectResult(new ProblemDetails
            {
                Status = 401, Title = "Dispositivo não autorizado", Detail = $"Cabeçalho {Header} ausente ou inválido."
            });
            return Task.CompletedTask;
        }
        return next();
    }
}

public sealed class ChaveDispositivoSwaggerFilter : IOperationFilter
{
    public void Apply(OpenApiOperation op, OperationFilterContext ctx)
    {
        var requer = ctx.MethodInfo.GetCustomAttributes(true).OfType<RequerChaveDispositivoAttribute>().Any();
        if (!requer) return;
        op.Security.Add(new OpenApiSecurityRequirement
        {
            [new OpenApiSecurityScheme { Reference = new OpenApiReference { Type = ReferenceType.SecurityScheme, Id = "DeviceKey" } }]
                = Array.Empty<string>()
        });
    }
}
