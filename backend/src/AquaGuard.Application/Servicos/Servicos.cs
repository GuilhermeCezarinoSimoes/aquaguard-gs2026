using AquaGuard.Application.Dtos;
using AquaGuard.Domain.Comum;
using AquaGuard.Domain.Entidades;
using AquaGuard.Domain.Enums;
using AquaGuard.Domain.Interfaces;
using AquaGuard.Domain.Risco;
using AquaGuard.Domain.ValueObjects;
using Microsoft.Extensions.Logging;

namespace AquaGuard.Application.Servicos;

// ======================= Contratos =======================

public interface ISensorServico
{
    Task<IReadOnlyList<SensorResponse>> ListarAsync(string? bairro, bool? ativo, CancellationToken ct = default);
    Task<SensorResponse> ObterAsync(int id, CancellationToken ct = default);
    Task<SensorResponse> CriarAsync(CriarSensorRequest req, CancellationToken ct = default);
    Task<SensorResponse> AtualizarLimitesAsync(int id, AtualizarLimitesRequest req, CancellationToken ct = default);
    Task DesativarAsync(int id, CancellationToken ct = default);
}

public interface ILeituraServico
{
    Task<RegistrarLeituraResponse> RegistrarAsync(RegistrarLeituraRequest req, CancellationToken ct = default);
    Task<IReadOnlyList<LeituraResponse>> HistoricoAsync(int sensorId, int horas, int limite, CancellationToken ct = default);
}

public interface IOcorrenciaServico
{
    Task<OcorrenciaResponse> CriarAsync(CriarOcorrenciaRequest req, CancellationToken ct = default);
    Task<OcorrenciaResponse> ObterAsync(int id, CancellationToken ct = default);
    Task<PaginaResponse<OcorrenciaResponse>> ListarAsync(string? bairro, StatusOcorrencia? status, int pagina, int tamanho, CancellationToken ct = default);
    Task<OcorrenciaResponse> AlterarStatusAsync(int id, AcaoOcorrencia acao, CancellationToken ct = default);
}

public interface IAlertaServico
{
    Task<IReadOnlyList<AlertaResponse>> ListarAsync(bool somenteAtivos, string? bairro, CancellationToken ct = default);
    Task<AlertaResponse> EncerrarAsync(int id, CancellationToken ct = default);
}

/// <summary>Consultas agregadas de leitura (implementadas com LINQ na infraestrutura).</summary>
public interface IPainelConsultas
{
    Task<PainelResponse> ObterPainelAsync(CancellationToken ct = default);
}

// ======================= Implementações =======================

public sealed class SensorServico : ISensorServico
{
    private readonly ISensorRepositorio _sensores;
    private readonly ILeituraRepositorio _leituras;
    private readonly IUnidadeDeTrabalho _uow;

    public SensorServico(ISensorRepositorio sensores, ILeituraRepositorio leituras, IUnidadeDeTrabalho uow)
    {
        _sensores = sensores;
        _leituras = leituras;
        _uow = uow;
    }

    public async Task<IReadOnlyList<SensorResponse>> ListarAsync(string? bairro, bool? ativo, CancellationToken ct = default)
    {
        var sensores = await _sensores.ListarAsync(bairro, ativo, ct);
        var resposta = new List<SensorResponse>(sensores.Count);
        foreach (var s in sensores)
            resposta.Add(SensorResponse.De(s, await _leituras.ObterUltimaAsync(s.Id, ct)));
        return resposta;
    }

    public async Task<SensorResponse> ObterAsync(int id, CancellationToken ct = default)
    {
        var s = await _sensores.ObterPorIdAsync(id, ct) ?? throw new NaoEncontradoException("Sensor", id);
        return SensorResponse.De(s, await _leituras.ObterUltimaAsync(s.Id, ct));
    }

    public async Task<SensorResponse> CriarAsync(CriarSensorRequest req, CancellationToken ct = default)
    {
        if (await _sensores.CodigoExisteAsync(req.Codigo.Trim().ToUpperInvariant(), ct))
            throw new DomainException($"Já existe um sensor com o código {req.Codigo}.");
        var sensor = new Sensor(req.Codigo, req.Nome, req.Bairro, new Coordenada(req.Latitude, req.Longitude),
            req.NivelAlertaCm, req.NivelCriticoCm);
        await _sensores.AdicionarAsync(sensor, ct);
        await _uow.SalvarAsync(ct);
        return SensorResponse.De(sensor);
    }

    public async Task<SensorResponse> AtualizarLimitesAsync(int id, AtualizarLimitesRequest req, CancellationToken ct = default)
    {
        var s = await _sensores.ObterPorIdAsync(id, ct) ?? throw new NaoEncontradoException("Sensor", id);
        s.DefinirLimites(req.NivelAlertaCm, req.NivelCriticoCm);
        await _uow.SalvarAsync(ct);
        return SensorResponse.De(s);
    }

    public async Task DesativarAsync(int id, CancellationToken ct = default)
    {
        var s = await _sensores.ObterPorIdAsync(id, ct) ?? throw new NaoEncontradoException("Sensor", id);
        s.Desativar();
        await _uow.SalvarAsync(ct);
    }
}

public sealed class LeituraServico : ILeituraServico
{
    private readonly ISensorRepositorio _sensores;
    private readonly ILeituraRepositorio _leituras;
    private readonly IAlertaRepositorio _alertas;
    private readonly ICalculadoraRisco _calculadora;
    private readonly IUnidadeDeTrabalho _uow;
    private readonly ILogger<LeituraServico> _log;

    public LeituraServico(ISensorRepositorio sensores, ILeituraRepositorio leituras, IAlertaRepositorio alertas,
        ICalculadoraRisco calculadora, IUnidadeDeTrabalho uow, ILogger<LeituraServico> log)
    {
        _sensores = sensores;
        _leituras = leituras;
        _alertas = alertas;
        _calculadora = calculadora;
        _uow = uow;
        _log = log;
    }

    public async Task<RegistrarLeituraResponse> RegistrarAsync(RegistrarLeituraRequest req, CancellationToken ct = default)
    {
        var codigo = req.CodigoSensor.Trim().ToUpperInvariant();
        var sensor = await _sensores.ObterPorCodigoAsync(codigo, ct)
                     ?? throw new NaoEncontradoException("Sensor", codigo);

        var leitura = sensor.RegistrarLeitura(req.NivelAguaCm, req.ChuvaMmH, req.DataHoraUtc);
        var risco = _calculadora.Calcular(sensor, req.NivelAguaCm, req.ChuvaMmH);
        leitura.AplicarRisco(risco);
        await _leituras.AdicionarAsync(leitura, ct);

        Alerta? alerta = null;
        if (risco >= NivelRisco.Atencao)
        {
            alerta = await _alertas.ObterAtivoPorBairroAsync(sensor.Bairro, ct);
            var mensagem = MensagensRisco.Para(risco, sensor.Bairro);
            if (alerta is null)
            {
                alerta = new Alerta(sensor.Bairro, risco, mensagem, sensor.Id);
                await _alertas.AdicionarAsync(alerta, ct);
                _log.LogWarning("Novo alerta {Nivel} em {Bairro} (sensor {Codigo})", risco, sensor.Bairro, sensor.Codigo);
            }
            else
            {
                alerta.Escalar(risco, mensagem);
            }
        }

        await _uow.SalvarAsync(ct);
        return new RegistrarLeituraResponse(LeituraResponse.De(leitura), alerta is null ? null : AlertaResponse.De(alerta));
    }

    public async Task<IReadOnlyList<LeituraResponse>> HistoricoAsync(int sensorId, int horas, int limite, CancellationToken ct = default)
    {
        _ = await _sensores.ObterPorIdAsync(sensorId, ct) ?? throw new NaoEncontradoException("Sensor", sensorId);
        horas = Math.Clamp(horas, 1, 24 * 30);
        limite = Math.Clamp(limite, 1, 1000);
        var leituras = await _leituras.ListarPorSensorAsync(sensorId, DateTime.UtcNow.AddHours(-horas), limite, ct);
        return leituras.Select(LeituraResponse.De).ToList();
    }
}

public sealed class OcorrenciaServico : IOcorrenciaServico
{
    private readonly IOcorrenciaRepositorio _repo;
    private readonly IUnidadeDeTrabalho _uow;

    public OcorrenciaServico(IOcorrenciaRepositorio repo, IUnidadeDeTrabalho uow)
    {
        _repo = repo;
        _uow = uow;
    }

    public async Task<OcorrenciaResponse> CriarAsync(CriarOcorrenciaRequest req, CancellationToken ct = default)
    {
        var o = new Ocorrencia(req.Tipo, req.Descricao, req.Bairro, new Coordenada(req.Latitude, req.Longitude),
            req.Severidade, req.Apelido);
        await _repo.AdicionarAsync(o, ct);
        await _uow.SalvarAsync(ct);
        return OcorrenciaResponse.De(o);
    }

    public async Task<OcorrenciaResponse> ObterAsync(int id, CancellationToken ct = default)
        => OcorrenciaResponse.De(await _repo.ObterPorIdAsync(id, ct) ?? throw new NaoEncontradoException("Ocorrência", id));

    public async Task<PaginaResponse<OcorrenciaResponse>> ListarAsync(string? bairro, StatusOcorrencia? status,
        int pagina, int tamanho, CancellationToken ct = default)
    {
        pagina = Math.Max(1, pagina);
        tamanho = Math.Clamp(tamanho, 1, 100);
        var (itens, total) = await _repo.ListarAsync(bairro, status, pagina, tamanho, ct);
        return new PaginaResponse<OcorrenciaResponse>(itens.Select(OcorrenciaResponse.De).ToList(), pagina, tamanho, total);
    }

    public async Task<OcorrenciaResponse> AlterarStatusAsync(int id, AcaoOcorrencia acao, CancellationToken ct = default)
    {
        var o = await _repo.ObterPorIdAsync(id, ct) ?? throw new NaoEncontradoException("Ocorrência", id);
        switch (acao)
        {
            case AcaoOcorrencia.IniciarAnalise: o.IniciarAnalise(); break;
            case AcaoOcorrencia.Resolver: o.Resolver(); break;
            case AcaoOcorrencia.Descartar: o.Descartar(); break;
            default: throw new DomainException("Ação inválida.");
        }
        await _uow.SalvarAsync(ct);
        return OcorrenciaResponse.De(o);
    }
}

public sealed class AlertaServico : IAlertaServico
{
    private readonly IAlertaRepositorio _repo;
    private readonly IUnidadeDeTrabalho _uow;

    public AlertaServico(IAlertaRepositorio repo, IUnidadeDeTrabalho uow)
    {
        _repo = repo;
        _uow = uow;
    }

    public async Task<IReadOnlyList<AlertaResponse>> ListarAsync(bool somenteAtivos, string? bairro, CancellationToken ct = default)
        => (await _repo.ListarAsync(somenteAtivos, bairro, ct)).Select(AlertaResponse.De).ToList();

    public async Task<AlertaResponse> EncerrarAsync(int id, CancellationToken ct = default)
    {
        var a = await _repo.ObterPorIdAsync(id, ct) ?? throw new NaoEncontradoException("Alerta", id);
        a.Encerrar();
        await _uow.SalvarAsync(ct);
        return AlertaResponse.De(a);
    }
}
