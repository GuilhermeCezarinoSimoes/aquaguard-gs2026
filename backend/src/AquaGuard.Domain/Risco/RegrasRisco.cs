using AquaGuard.Domain.Entidades;
using AquaGuard.Domain.Enums;

namespace AquaGuard.Domain.Risco;

/// <summary>Contrato de uma regra de avaliação de risco (Strategy).</summary>
public interface IRegraRisco
{
    string Nome { get; }
    NivelRisco Avaliar(Sensor sensor, double nivelAguaCm, double chuvaMmH);
}

/// <summary>Regra base com a lógica comum de comparação por limites (Template Method).</summary>
public abstract class RegraPorLimites : IRegraRisco
{
    public abstract string Nome { get; }

    protected abstract double ObterValor(double nivelAguaCm, double chuvaMmH);
    protected abstract (double atencao, double alerta, double critico) ObterLimites(Sensor sensor);

    public NivelRisco Avaliar(Sensor sensor, double nivelAguaCm, double chuvaMmH)
    {
        var valor = ObterValor(nivelAguaCm, chuvaMmH);
        var (atencao, alerta, critico) = ObterLimites(sensor);
        if (valor >= critico) return NivelRisco.Critico;
        if (valor >= alerta) return NivelRisco.Alerta;
        if (valor >= atencao) return NivelRisco.Atencao;
        return NivelRisco.Normal;
    }
}

/// <summary>Risco pela altura da água em relação aos limites calibrados do ponto.</summary>
public sealed class RegraNivelAgua : RegraPorLimites
{
    public override string Nome => "NivelAgua";
    protected override double ObterValor(double nivelAguaCm, double chuvaMmH) => nivelAguaCm;
    protected override (double, double, double) ObterLimites(Sensor s)
        => (s.NivelAlertaCm * 0.6, s.NivelAlertaCm, s.NivelCriticoCm);
}

/// <summary>
/// Risco pela intensidade de chuva. Faixas adaptadas da classificação usada pela
/// Defesa Civil/CGE-SP: moderada ≥ 10 mm/h, forte ≥ 25 mm/h, muito forte ≥ 50 mm/h.
/// </summary>
public sealed class RegraIntensidadeChuva : RegraPorLimites
{
    public override string Nome => "IntensidadeChuva";
    protected override double ObterValor(double nivelAguaCm, double chuvaMmH) => chuvaMmH;
    protected override (double, double, double) ObterLimites(Sensor s) => (10, 25, 50);
}

/// <summary>Combinação: água já em atenção + chuva forte = sobe um nível (tendência de piora).</summary>
public sealed class RegraCombinada : IRegraRisco
{
    public string Nome => "Combinada";

    public NivelRisco Avaliar(Sensor sensor, double nivelAguaCm, double chuvaMmH)
    {
        var aguaSubindo = nivelAguaCm >= sensor.NivelAlertaCm * 0.6;
        var chuvaForte = chuvaMmH >= 25;
        if (aguaSubindo && chuvaForte)
            return nivelAguaCm >= sensor.NivelAlertaCm ? NivelRisco.Critico : NivelRisco.Alerta;
        return NivelRisco.Normal;
    }
}

public interface ICalculadoraRisco
{
    NivelRisco Calcular(Sensor sensor, double nivelAguaCm, double chuvaMmH);
}

/// <summary>Aplica todas as regras registradas e devolve o pior caso (abordagem conservadora).</summary>
public sealed class CalculadoraRisco : ICalculadoraRisco
{
    private readonly IReadOnlyList<IRegraRisco> _regras;

    public CalculadoraRisco(IEnumerable<IRegraRisco> regras)
    {
        _regras = regras.ToList();
        if (_regras.Count == 0) throw new ArgumentException("Ao menos uma regra de risco é necessária.");
    }

    public NivelRisco Calcular(Sensor sensor, double nivelAguaCm, double chuvaMmH)
        => _regras.Select(r => r.Avaliar(sensor, nivelAguaCm, chuvaMmH)).Max();
}

public static class MensagensRisco
{
    public static string Para(NivelRisco nivel, string bairro) => nivel switch
    {
        NivelRisco.Critico => $"PERIGO em {bairro}: água na via. Não atravesse ruas alagadas e procure local alto.",
        NivelRisco.Alerta => $"ALERTA em {bairro}: córrego perto de transbordar. Evite a região e proteja seus pertences.",
        NivelRisco.Atencao => $"ATENÇÃO em {bairro}: chuva ou nível de água subindo. Acompanhe o app.",
        _ => $"Situação normal em {bairro}."
    };
}
