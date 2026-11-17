using AquaGuard.Domain.Comum;
using Microsoft.AspNetCore.Diagnostics;
using Microsoft.AspNetCore.Mvc;

namespace AquaGuard.Api.Infra;

/// <summary>Converte exceções de domínio em respostas RFC 7807 (ProblemDetails).</summary>
public sealed class TratadorExcecoes : IExceptionHandler
{
    private readonly ILogger<TratadorExcecoes> _log;

    public TratadorExcecoes(ILogger<TratadorExcecoes> log) => _log = log;

    public async ValueTask<bool> TryHandleAsync(HttpContext ctx, Exception ex, CancellationToken ct)
    {
        var (status, titulo) = ex switch
        {
            NaoEncontradoException => (StatusCodes.Status404NotFound, "Recurso não encontrado"),
            DomainException => (StatusCodes.Status422UnprocessableEntity, "Regra de negócio violada"),
            _ => (StatusCodes.Status500InternalServerError, "Erro interno")
        };

        if (status == 500) _log.LogError(ex, "Erro não tratado");
        else _log.LogInformation("Requisição rejeitada: {Mensagem}", ex.Message);

        var problem = new ProblemDetails
        {
            Status = status,
            Title = titulo,
            // Nunca expor stack trace / detalhes internos em erro 500.
            Detail = status == 500 ? "Ocorreu um erro inesperado." : ex.Message,
            Instance = ctx.Request.Path
        };
        ctx.Response.StatusCode = status;
        await ctx.Response.WriteAsJsonAsync(problem, ct);
        return true;
    }
}
