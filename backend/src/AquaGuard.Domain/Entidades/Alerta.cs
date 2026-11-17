using AquaGuard.Domain.Comum;
using AquaGuard.Domain.Enums;

namespace AquaGuard.Domain.Entidades;

/// <summary>Alerta emitido à população de um bairro quando o risco sobe.</summary>
public class Alerta : EntidadeBase
{
    public int? SensorId { get; private set; }
    public Sensor? Sensor { get; private set; }
    public string Bairro { get; private set; } = string.Empty;
    public NivelRisco Nivel { get; private set; }
    public string Mensagem { get; private set; } = string.Empty;
    public bool Ativo { get; private set; } = true;
    public DateTime? EncerradoEmUtc { get; private set; }

    protected Alerta() { } // EF Core

    public Alerta(string bairro, NivelRisco nivel, string mensagem, int? sensorId = null)
    {
        if (string.IsNullOrWhiteSpace(bairro)) throw new DomainException("Bairro é obrigatório.");
        if (nivel < NivelRisco.Atencao) throw new DomainException("Alertas só são emitidos a partir do nível Atenção.");
        if (string.IsNullOrWhiteSpace(mensagem)) throw new DomainException("Mensagem é obrigatória.");
        Bairro = bairro.Trim();
        Nivel = nivel;
        Mensagem = mensagem.Trim();
        SensorId = sensorId;
    }

    /// <summary>Eleva o nível de um alerta ativo (nunca reduz: segurança primeiro).</summary>
    public void Escalar(NivelRisco novoNivel, string mensagem)
    {
        if (!Ativo) throw new DomainException("Não é possível escalar um alerta encerrado.");
        if (novoNivel <= Nivel) return;
        Nivel = novoNivel;
        Mensagem = mensagem;
        MarcarAtualizado();
    }

    public void Encerrar()
    {
        if (!Ativo) throw new DomainException("Alerta já encerrado.");
        Ativo = false;
        EncerradoEmUtc = DateTime.UtcNow;
        MarcarAtualizado();
    }
}
