using AquaGuard.Api.Infra;
using AquaGuard.Application.Dtos;
using AquaGuard.Application.Servicos;
using AquaGuard.Domain.Enums;
using Microsoft.AspNetCore.Mvc;

namespace AquaGuard.Api.Controllers;

/// <summary>Sensores IoT instalados em pontos de alagamento.</summary>
[ApiController]
[Route("api/sensores")]
[Produces("application/json")]
public sealed class SensoresController : ControllerBase
{
    private readonly ISensorServico _servico;
    private readonly ILeituraServico _leituras;

    public SensoresController(ISensorServico servico, ILeituraServico leituras)
    {
        _servico = servico;
        _leituras = leituras;
    }

    /// <summary>Lista sensores com a última leitura e o risco atual.</summary>
    /// <param name="bairro">Filtra por bairro (opcional).</param>
    /// <param name="ativo">Filtra por situação (opcional).</param>
    [HttpGet]
    [ProducesResponseType(typeof(IReadOnlyList<SensorResponse>), StatusCodes.Status200OK)]
    public async Task<IActionResult> Listar([FromQuery] string? bairro, [FromQuery] bool? ativo, CancellationToken ct)
        => Ok(await _servico.ListarAsync(bairro, ativo, ct));

    /// <summary>Obtém um sensor pelo id.</summary>
    [HttpGet("{id:int}")]
    [ProducesResponseType(typeof(SensorResponse), StatusCodes.Status200OK)]
    [ProducesResponseType(StatusCodes.Status404NotFound)]
    public async Task<IActionResult> Obter(int id, CancellationToken ct) => Ok(await _servico.ObterAsync(id, ct));

    /// <summary>Cadastra um novo sensor.</summary>
    [HttpPost]
    [ProducesResponseType(typeof(SensorResponse), StatusCodes.Status201Created)]
    [ProducesResponseType(StatusCodes.Status400BadRequest)]
    [ProducesResponseType(StatusCodes.Status422UnprocessableEntity)]
    public async Task<IActionResult> Criar([FromBody] CriarSensorRequest req, CancellationToken ct)
    {
        var criado = await _servico.CriarAsync(req, ct);
        return CreatedAtAction(nameof(Obter), new { id = criado.Id }, criado);
    }

    /// <summary>Recalibra os limites de alerta/crítico do ponto.</summary>
    [HttpPut("{id:int}/limites")]
    [ProducesResponseType(typeof(SensorResponse), StatusCodes.Status200OK)]
    [ProducesResponseType(StatusCodes.Status404NotFound)]
    [ProducesResponseType(StatusCodes.Status422UnprocessableEntity)]
    public async Task<IActionResult> AtualizarLimites(int id, [FromBody] AtualizarLimitesRequest req, CancellationToken ct)
        => Ok(await _servico.AtualizarLimitesAsync(id, req, ct));

    /// <summary>Desativa um sensor (manutenção). Não apaga o histórico.</summary>
    [HttpDelete("{id:int}")]
    [ProducesResponseType(StatusCodes.Status204NoContent)]
    [ProducesResponseType(StatusCodes.Status404NotFound)]
    public async Task<IActionResult> Desativar(int id, CancellationToken ct)
    {
        await _servico.DesativarAsync(id, ct);
        return NoContent();
    }

    /// <summary>Histórico de leituras de um sensor.</summary>
    /// <param name="id">Id do sensor.</param>
    /// <param name="horas">Janela em horas (1–720). Padrão 24.</param>
    /// <param name="limite">Máximo de registros (1–1000). Padrão 200.</param>
    [HttpGet("{id:int}/leituras")]
    [ProducesResponseType(typeof(IReadOnlyList<LeituraResponse>), StatusCodes.Status200OK)]
    [ProducesResponseType(StatusCodes.Status404NotFound)]
    public async Task<IActionResult> Historico(int id, CancellationToken ct, [FromQuery] int horas = 24, [FromQuery] int limite = 200)
        => Ok(await _leituras.HistoricoAsync(id, horas, limite, ct));
}

/// <summary>Ingestão de leituras enviadas pelo ESP32.</summary>
[ApiController]
[Route("api/leituras")]
[Produces("application/json")]
public sealed class LeiturasController : ControllerBase
{
    private readonly ILeituraServico _servico;

    public LeiturasController(ILeituraServico servico) => _servico = servico;

    /// <summary>Registra uma leitura, calcula o risco e, se necessário, emite/escala o alerta do bairro.</summary>
    /// <remarks>
    /// Exemplo de payload do ESP32:
    ///
    ///     { "codigoSensor": "AQG-001", "nivelAguaCm": 95.5, "chuvaMmH": 32 }
    /// </remarks>
    [HttpPost]
    [RequerChaveDispositivo]
    [ProducesResponseType(typeof(RegistrarLeituraResponse), StatusCodes.Status201Created)]
    [ProducesResponseType(StatusCodes.Status400BadRequest)]
    [ProducesResponseType(StatusCodes.Status401Unauthorized)]
    [ProducesResponseType(StatusCodes.Status404NotFound)]
    [ProducesResponseType(StatusCodes.Status422UnprocessableEntity)]
    public async Task<IActionResult> Registrar([FromBody] RegistrarLeituraRequest req, CancellationToken ct)
    {
        var r = await _servico.RegistrarAsync(req, ct);
        return StatusCode(StatusCodes.Status201Created, r);
    }
}

/// <summary>Relatos colaborativos de alagamento feitos pelos cidadãos.</summary>
[ApiController]
[Route("api/ocorrencias")]
[Produces("application/json")]
public sealed class OcorrenciasController : ControllerBase
{
    private readonly IOcorrenciaServico _servico;

    public OcorrenciasController(IOcorrenciaServico servico) => _servico = servico;

    /// <summary>Lista ocorrências (paginado, mais graves primeiro).</summary>
    [HttpGet]
    [ProducesResponseType(typeof(PaginaResponse<OcorrenciaResponse>), StatusCodes.Status200OK)]
    public async Task<IActionResult> Listar([FromQuery] string? bairro, [FromQuery] StatusOcorrencia? status,
        CancellationToken ct, [FromQuery] int pagina = 1, [FromQuery] int tamanho = 20)
        => Ok(await _servico.ListarAsync(bairro, status, pagina, tamanho, ct));

    /// <summary>Obtém uma ocorrência.</summary>
    [HttpGet("{id:int}")]
    [ProducesResponseType(typeof(OcorrenciaResponse), StatusCodes.Status200OK)]
    [ProducesResponseType(StatusCodes.Status404NotFound)]
    public async Task<IActionResult> Obter(int id, CancellationToken ct) => Ok(await _servico.ObterAsync(id, ct));

    /// <summary>Registra uma nova ocorrência (sem dados pessoais).</summary>
    [HttpPost]
    [ProducesResponseType(typeof(OcorrenciaResponse), StatusCodes.Status201Created)]
    [ProducesResponseType(StatusCodes.Status400BadRequest)]
    [ProducesResponseType(StatusCodes.Status422UnprocessableEntity)]
    public async Task<IActionResult> Criar([FromBody] CriarOcorrenciaRequest req, CancellationToken ct)
    {
        var criada = await _servico.CriarAsync(req, ct);
        return CreatedAtAction(nameof(Obter), new { id = criada.Id }, criada);
    }

    /// <summary>Avança o status: IniciarAnalise, Resolver ou Descartar.</summary>
    [HttpPatch("{id:int}/status")]
    [ProducesResponseType(typeof(OcorrenciaResponse), StatusCodes.Status200OK)]
    [ProducesResponseType(StatusCodes.Status404NotFound)]
    [ProducesResponseType(StatusCodes.Status422UnprocessableEntity)]
    public async Task<IActionResult> AlterarStatus(int id, [FromBody] AlterarStatusOcorrenciaRequest req, CancellationToken ct)
        => Ok(await _servico.AlterarStatusAsync(id, req.Acao, ct));
}

/// <summary>Alertas emitidos por bairro.</summary>
[ApiController]
[Route("api/alertas")]
[Produces("application/json")]
public sealed class AlertasController : ControllerBase
{
    private readonly IAlertaServico _servico;

    public AlertasController(IAlertaServico servico) => _servico = servico;

    /// <summary>Lista alertas (por padrão, só os ativos).</summary>
    [HttpGet]
    [ProducesResponseType(typeof(IReadOnlyList<AlertaResponse>), StatusCodes.Status200OK)]
    public async Task<IActionResult> Listar([FromQuery] string? bairro, CancellationToken ct, [FromQuery] bool somenteAtivos = true)
        => Ok(await _servico.ListarAsync(somenteAtivos, bairro, ct));

    /// <summary>Encerra um alerta (situação normalizada).</summary>
    [HttpPost("{id:int}/encerrar")]
    [ProducesResponseType(typeof(AlertaResponse), StatusCodes.Status200OK)]
    [ProducesResponseType(StatusCodes.Status404NotFound)]
    [ProducesResponseType(StatusCodes.Status422UnprocessableEntity)]
    public async Task<IActionResult> Encerrar(int id, CancellationToken ct) => Ok(await _servico.EncerrarAsync(id, ct));
}

/// <summary>Visão consolidada por bairro (painel do app e da Defesa Civil).</summary>
[ApiController]
[Route("api/painel")]
[Produces("application/json")]
public sealed class PainelController : ControllerBase
{
    private readonly IPainelConsultas _consultas;

    public PainelController(IPainelConsultas consultas) => _consultas = consultas;

    /// <summary>Resumo de risco, alertas e ocorrências por bairro.</summary>
    [HttpGet]
    [ProducesResponseType(typeof(PainelResponse), StatusCodes.Status200OK)]
    public async Task<IActionResult> Obter(CancellationToken ct) => Ok(await _consultas.ObterPainelAsync(ct));
}
