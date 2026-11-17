namespace AquaGuard.Domain.Comum;

/// <summary>
/// Classe base abstrata de todas as entidades persistidas.
/// Centraliza identidade e auditoria (encapsulamento + herança).
/// </summary>
public abstract class EntidadeBase
{
    public int Id { get; protected set; }

    public DateTime CriadoEmUtc { get; protected set; } = DateTime.UtcNow;

    public DateTime? AtualizadoEmUtc { get; protected set; }

    protected void MarcarAtualizado() => AtualizadoEmUtc = DateTime.UtcNow;
}
