using AquaGuard.Domain.Comum;
using AquaGuard.Domain.Entidades;
using AquaGuard.Domain.Enums;
using AquaGuard.Domain.Risco;
using AquaGuard.Domain.ValueObjects;

namespace AquaGuard.Tests.Dominio;

public class SensorTests
{
    private static Sensor NovoSensor() =>
        new("aqg-100", "Ponto teste", "Centro", new Coordenada(-23.55, -46.63), 80, 120);

    [Fact]
    public void Construtor_NormalizaCodigo()
        => Assert.Equal("AQG-100", NovoSensor().Codigo);

    [Theory]
    [InlineData(0, 100)]
    [InlineData(100, 100)]
    [InlineData(120, 80)]
    public void DefinirLimites_Invalidos_LancaDomainException(double alerta, double critico)
        => Assert.Throws<DomainException>(() => NovoSensor().DefinirLimites(alerta, critico));

    [Fact]
    public void RegistrarLeitura_SensorInativo_LancaDomainException()
    {
        var s = NovoSensor();
        s.Desativar();
        Assert.Throws<DomainException>(() => s.RegistrarLeitura(10, 0));
    }

    [Theory]
    [InlineData(-1, 0)]
    [InlineData(10, -5)]
    [InlineData(1001, 0)]
    public void RegistrarLeitura_ValoresForaDaFaixa_LancaDomainException(double nivel, double chuva)
        => Assert.Throws<DomainException>(() => NovoSensor().RegistrarLeitura(nivel, chuva));

    [Fact]
    public void RegistrarLeitura_NoFuturo_LancaDomainException()
        => Assert.Throws<DomainException>(() => NovoSensor().RegistrarLeitura(10, 0, DateTime.UtcNow.AddHours(1)));

    [Fact]
    public void RegistrarLeitura_Valida_AdicionaNaColecao()
    {
        var s = NovoSensor();
        s.RegistrarLeitura(50, 5);
        Assert.Single(s.Leituras);
    }
}

public class CoordenadaTests
{
    [Theory]
    [InlineData(91, 0)]
    [InlineData(0, -181)]
    public void Invalida_LancaDomainException(double lat, double lon)
        => Assert.Throws<DomainException>(() => new Coordenada(lat, lon));

    [Fact]
    public void Distancia_SePaulista_ParaSe_Aprox3Km()
    {
        var paulista = new Coordenada(-23.5614, -46.6559);
        var se = new Coordenada(-23.5503, -46.6339);
        Assert.InRange(paulista.DistanciaKm(se), 2.0, 3.0);
    }
}

public class OcorrenciaTests
{
    private static Ocorrencia Nova() => new(TipoOcorrencia.RuaAlagada, "Rua alagada", "Centro",
        new Coordenada(-23.5, -46.6), 3);

    [Fact]
    public void FluxoCompleto_AbertaAnaliseResolvida()
    {
        var o = Nova();
        o.IniciarAnalise();
        o.Resolver();
        Assert.Equal(StatusOcorrencia.Resolvida, o.Status);
        Assert.NotNull(o.ResolvidaEmUtc);
        Assert.False(o.EstaAberta);
    }

    [Fact]
    public void ResolverDuasVezes_LancaDomainException()
    {
        var o = Nova();
        o.Resolver();
        Assert.Throws<DomainException>(() => o.Resolver());
    }

    [Fact]
    public void IniciarAnalise_ForaDeAberta_LancaDomainException()
    {
        var o = Nova();
        o.Descartar();
        Assert.Throws<DomainException>(() => o.IniciarAnalise());
    }

    [Theory]
    [InlineData("abc", 3)]
    [InlineData("Descrição válida", 0)]
    [InlineData("Descrição válida", 6)]
    public void DadosInvalidos_LancaDomainException(string descricao, int severidade)
        => Assert.Throws<DomainException>(() => new Ocorrencia(TipoOcorrencia.Outro, descricao, "Centro",
            new Coordenada(0, 0), severidade));

    [Fact]
    public void Apelido_EmBranco_ViraNulo()
        => Assert.Null(new Ocorrencia(TipoOcorrencia.Outro, "Descrição ok", "Centro", new Coordenada(0, 0), 1, "   ").Apelido);
}

public class AlertaTests
{
    [Fact]
    public void NivelNormal_NaoGeraAlerta()
        => Assert.Throws<DomainException>(() => new Alerta("Centro", NivelRisco.Normal, "msg"));

    [Fact]
    public void Escalar_NuncaReduzNivel()
    {
        var a = new Alerta("Centro", NivelRisco.Alerta, "msg");
        a.Escalar(NivelRisco.Atencao, "menor");
        Assert.Equal(NivelRisco.Alerta, a.Nivel);
        a.Escalar(NivelRisco.Critico, "maior");
        Assert.Equal(NivelRisco.Critico, a.Nivel);
        Assert.Equal("maior", a.Mensagem);
    }

    [Fact]
    public void Encerrar_DuasVezes_LancaDomainException()
    {
        var a = new Alerta("Centro", NivelRisco.Alerta, "msg");
        a.Encerrar();
        Assert.False(a.Ativo);
        Assert.Throws<DomainException>(() => a.Encerrar());
        Assert.Throws<DomainException>(() => a.Escalar(NivelRisco.Critico, "x"));
    }
}

public class CalculadoraRiscoTests
{
    private static readonly Sensor S = new("AQG-1", "Teste", "Centro", new Coordenada(0, 0), 100, 150);

    private static readonly CalculadoraRisco Calc = new(new IRegraRisco[]
        { new RegraNivelAgua(), new RegraIntensidadeChuva(), new RegraCombinada() });

    [Theory]
    [InlineData(10, 0, NivelRisco.Normal)]
    [InlineData(60, 0, NivelRisco.Atencao)]   // 60% do nível de alerta
    [InlineData(100, 0, NivelRisco.Alerta)]
    [InlineData(150, 0, NivelRisco.Critico)]
    [InlineData(0, 12, NivelRisco.Atencao)]   // chuva moderada
    [InlineData(0, 30, NivelRisco.Alerta)]    // chuva forte
    [InlineData(0, 60, NivelRisco.Critico)]   // chuva muito forte
    [InlineData(70, 30, NivelRisco.Alerta)]   // combinada
    [InlineData(110, 30, NivelRisco.Critico)] // combinada com água acima do alerta
    public void Calcular_RetornaPiorCaso(double nivel, double chuva, NivelRisco esperado)
        => Assert.Equal(esperado, Calc.Calcular(S, nivel, chuva));

    [Fact]
    public void SemRegras_LancaArgumentException()
        => Assert.Throws<ArgumentException>(() => new CalculadoraRisco(Array.Empty<IRegraRisco>()));
}
