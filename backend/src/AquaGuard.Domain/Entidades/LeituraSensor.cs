using AquaGuard.Domain.Comum;
using AquaGuard.Domain.Enums;

namespace AquaGuard.Domain.Entidades;

/// <summary>Medição enviada por um sensor (nível da água + intensidade de chuva).</summary>
public class LeituraSensor : EntidadeBase
{
    public int SensorId { get; private set; }
    public Sensor? Sensor { get; private set; }

    /// <summary>Altura da lâmina d'água em centímetros.</summary>
    public double NivelAguaCm { get; private set; }

    /// <summary>Intensidade de chuva estimada em mm/h (pluviômetro).</summary>
    public double ChuvaMmH { get; private set; }

    public DateTime DataHoraUtc { get; private set; }

    /// <summary>Risco calculado no momento da ingestão.</summary>
    public NivelRisco Risco { get; private set; }

    protected LeituraSensor() { } // EF Core

    internal LeituraSensor(Sensor sensor, double nivelAguaCm, double chuvaMmH, DateTime dataHoraUtc)
    {
        if (nivelAguaCm is < 0 or > 1000) throw new DomainException("Nível da água fora da faixa (0–1000 cm).");
        if (chuvaMmH is < 0 or > 500) throw new DomainException("Chuva fora da faixa (0–500 mm/h).");
        if (dataHoraUtc > DateTime.UtcNow.AddMinutes(5))
            throw new DomainException("Data/hora da leitura não pode estar no futuro.");

        Sensor = sensor;
        SensorId = sensor.Id;
        NivelAguaCm = nivelAguaCm;
        ChuvaMmH = chuvaMmH;
        DataHoraUtc = dataHoraUtc;
    }

    public void AplicarRisco(NivelRisco risco) => Risco = risco;
}
