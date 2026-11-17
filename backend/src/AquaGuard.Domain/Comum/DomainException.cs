namespace AquaGuard.Domain.Comum;

/// <summary>Violação de uma regra de negócio do domínio.</summary>
public class DomainException : Exception
{
    public DomainException(string mensagem) : base(mensagem) { }
}

/// <summary>Recurso solicitado não existe.</summary>
public sealed class NaoEncontradoException : DomainException
{
    public NaoEncontradoException(string recurso, object id)
        : base($"{recurso} '{id}' não encontrado(a).") { }
}
