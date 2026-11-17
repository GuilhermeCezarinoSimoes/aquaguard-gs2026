using AquaGuard.Domain.Comum;
using AquaGuard.Domain.Enums;
using AquaGuard.Domain.ValueObjects;

namespace AquaGuard.Domain.Entidades;

/// <summary>
/// Relato colaborativo feito pelo cidadão no app (ex.: "rua alagada na esquina X").
/// Não armazena dados pessoais: apenas um apelido opcional.
/// </summary>
public class Ocorrencia : EntidadeBase
{
    public TipoOcorrencia Tipo { get; private set; }
    public string Descricao { get; private set; } = string.Empty;
    public string Bairro { get; private set; } = string.Empty;
    public double Latitude { get; private set; }
    public double Longitude { get; private set; }

    /// <summary>Severidade informada pelo cidadão (1 = leve … 5 = grave).</summary>
    public int Severidade { get; private set; }

    public string? Apelido { get; private set; }
    public StatusOcorrencia Status { get; private set; } = StatusOcorrencia.Aberta;
    public DateTime? ResolvidaEmUtc { get; private set; }

    protected Ocorrencia() { } // EF Core

    public Ocorrencia(TipoOcorrencia tipo, string descricao, string bairro, Coordenada local,
                      int severidade, string? apelido = null)
    {
        if (!Enum.IsDefined(tipo)) throw new DomainException("Tipo de ocorrência inválido.");
        if (string.IsNullOrWhiteSpace(descricao) || descricao.Trim().Length < 5)
            throw new DomainException("Descreva a ocorrência com pelo menos 5 caracteres.");
        if (descricao.Length > 500) throw new DomainException("Descrição deve ter no máximo 500 caracteres.");
        if (string.IsNullOrWhiteSpace(bairro)) throw new DomainException("Bairro é obrigatório.");
        if (severidade is < 1 or > 5) throw new DomainException("Severidade deve estar entre 1 e 5.");

        Tipo = tipo;
        Descricao = descricao.Trim();
        Bairro = bairro.Trim();
        Latitude = local.Latitude;
        Longitude = local.Longitude;
        Severidade = severidade;
        Apelido = string.IsNullOrWhiteSpace(apelido) ? null : apelido.Trim();
    }

    /// <summary>Máquina de estados: Aberta → EmAnalise → Resolvida | Descartada.</summary>
    public void IniciarAnalise()
    {
        if (Status != StatusOcorrencia.Aberta)
            throw new DomainException("Somente ocorrências abertas podem entrar em análise.");
        Status = StatusOcorrencia.EmAnalise;
        MarcarAtualizado();
    }

    public void Resolver()
    {
        if (Status is StatusOcorrencia.Resolvida or StatusOcorrencia.Descartada)
            throw new DomainException("Ocorrência já foi encerrada.");
        Status = StatusOcorrencia.Resolvida;
        ResolvidaEmUtc = DateTime.UtcNow;
        MarcarAtualizado();
    }

    public void Descartar()
    {
        if (Status is StatusOcorrencia.Resolvida or StatusOcorrencia.Descartada)
            throw new DomainException("Ocorrência já foi encerrada.");
        Status = StatusOcorrencia.Descartada;
        MarcarAtualizado();
    }

    public bool EstaAberta => Status is StatusOcorrencia.Aberta or StatusOcorrencia.EmAnalise;
}
