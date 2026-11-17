using AquaGuard.Domain.Comum;
using AquaGuard.Domain.ValueObjects;

namespace AquaGuard.Domain.Entidades;

/// <summary>
/// Estação IoT (ESP32 + sensor ultrassônico) instalada em um ponto de alagamento:
/// córrego, galeria ou boca de lobo.
/// </summary>
public class Sensor : EntidadeBase
{
    private readonly List<LeituraSensor> _leituras = new();

    /// <summary>Código único do dispositivo (ex.: AQG-001), enviado pelo ESP32.</summary>
    public string Codigo { get; private set; } = string.Empty;
    public string Nome { get; private set; } = string.Empty;
    public string Bairro { get; private set; } = string.Empty;
    public double Latitude { get; private set; }
    public double Longitude { get; private set; }

    /// <summary>Nível (cm) a partir do qual o ponto entra em "Alerta".</summary>
    public double NivelAlertaCm { get; private set; }

    /// <summary>Nível (cm) a partir do qual o ponto é "Crítico" (água na via).</summary>
    public double NivelCriticoCm { get; private set; }

    public bool Ativo { get; private set; } = true;

    public IReadOnlyCollection<LeituraSensor> Leituras => _leituras.AsReadOnly();

    protected Sensor() { } // EF Core

    public Sensor(string codigo, string nome, string bairro, Coordenada local,
                  double nivelAlertaCm, double nivelCriticoCm)
    {
        if (string.IsNullOrWhiteSpace(codigo)) throw new DomainException("Código do sensor é obrigatório.");
        if (string.IsNullOrWhiteSpace(nome)) throw new DomainException("Nome do sensor é obrigatório.");
        if (string.IsNullOrWhiteSpace(bairro)) throw new DomainException("Bairro é obrigatório.");
        DefinirLimites(nivelAlertaCm, nivelCriticoCm);

        Codigo = codigo.Trim().ToUpperInvariant();
        Nome = nome.Trim();
        Bairro = bairro.Trim();
        Latitude = local.Latitude;
        Longitude = local.Longitude;
    }

    public Coordenada Local => new(Latitude, Longitude);

    public void DefinirLimites(double nivelAlertaCm, double nivelCriticoCm)
    {
        if (nivelAlertaCm <= 0) throw new DomainException("Nível de alerta deve ser positivo.");
        if (nivelCriticoCm <= nivelAlertaCm)
            throw new DomainException("Nível crítico deve ser maior que o nível de alerta.");
        NivelAlertaCm = nivelAlertaCm;
        NivelCriticoCm = nivelCriticoCm;
        MarcarAtualizado();
    }

    public void Desativar() { Ativo = false; MarcarAtualizado(); }

    public void Ativar() { Ativo = true; MarcarAtualizado(); }

    /// <summary>Registra uma nova leitura; sensores inativos não aceitam dados.</summary>
    public LeituraSensor RegistrarLeitura(double nivelAguaCm, double chuvaMmH, DateTime? dataHoraUtc = null)
    {
        if (!Ativo) throw new DomainException($"Sensor {Codigo} está inativo.");
        var leitura = new LeituraSensor(this, nivelAguaCm, chuvaMmH, dataHoraUtc ?? DateTime.UtcNow);
        _leituras.Add(leitura);
        return leitura;
    }
}
