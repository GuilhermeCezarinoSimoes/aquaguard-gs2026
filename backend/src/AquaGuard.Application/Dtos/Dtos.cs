using System.ComponentModel.DataAnnotations;
using AquaGuard.Domain.Entidades;
using AquaGuard.Domain.Enums;

namespace AquaGuard.Application.Dtos;

// ---------- Sensores ----------

public sealed record CriarSensorRequest(
    [Required, StringLength(20, MinimumLength = 3)] string Codigo,
    [Required, StringLength(120, MinimumLength = 3)] string Nome,
    [Required, StringLength(80, MinimumLength = 2)] string Bairro,
    [Range(-90, 90)] double Latitude,
    [Range(-180, 180)] double Longitude,
    [Range(1, 1000)] double NivelAlertaCm,
    [Range(1, 1000)] double NivelCriticoCm);

public sealed record AtualizarLimitesRequest(
    [Range(1, 1000)] double NivelAlertaCm,
    [Range(1, 1000)] double NivelCriticoCm);

public sealed record SensorResponse(
    int Id, string Codigo, string Nome, string Bairro, double Latitude, double Longitude,
    double NivelAlertaCm, double NivelCriticoCm, bool Ativo,
    double? UltimoNivelCm, NivelRisco? UltimoRisco, DateTime? UltimaLeituraUtc)
{
    public static SensorResponse De(Sensor s, LeituraSensor? ultima = null) => new(
        s.Id, s.Codigo, s.Nome, s.Bairro, s.Latitude, s.Longitude, s.NivelAlertaCm, s.NivelCriticoCm,
        s.Ativo, ultima?.NivelAguaCm, ultima?.Risco, ultima?.DataHoraUtc);
}

// ---------- Leituras (IoT) ----------

/// <summary>Payload enviado pelo ESP32.</summary>
public sealed record RegistrarLeituraRequest(
    [Required, StringLength(20, MinimumLength = 3)] string CodigoSensor,
    [Range(0, 1000)] double NivelAguaCm,
    [Range(0, 500)] double ChuvaMmH,
    DateTime? DataHoraUtc);

public sealed record LeituraResponse(int Id, int SensorId, double NivelAguaCm, double ChuvaMmH,
    DateTime DataHoraUtc, NivelRisco Risco, string RiscoDescricao)
{
    public static LeituraResponse De(LeituraSensor l) =>
        new(l.Id, l.SensorId, l.NivelAguaCm, l.ChuvaMmH, l.DataHoraUtc, l.Risco, l.Risco.ToString());
}

/// <summary>Resposta para o dispositivo: o ESP32 usa "Risco" para acionar LED/buzzer.</summary>
public sealed record RegistrarLeituraResponse(LeituraResponse Leitura, AlertaResponse? AlertaGerado);

// ---------- Ocorrências ----------

public sealed record CriarOcorrenciaRequest(
    [Required] TipoOcorrencia Tipo,
    [Required, StringLength(500, MinimumLength = 5)] string Descricao,
    [Required, StringLength(80, MinimumLength = 2)] string Bairro,
    [Range(-90, 90)] double Latitude,
    [Range(-180, 180)] double Longitude,
    [Range(1, 5)] int Severidade,
    [StringLength(40)] string? Apelido);

public enum AcaoOcorrencia { IniciarAnalise = 1, Resolver = 2, Descartar = 3 }

public sealed record AlterarStatusOcorrenciaRequest([Required] AcaoOcorrencia Acao);

public sealed record OcorrenciaResponse(int Id, TipoOcorrencia Tipo, string Descricao, string Bairro,
    double Latitude, double Longitude, int Severidade, string? Apelido, StatusOcorrencia Status,
    DateTime CriadoEmUtc, DateTime? ResolvidaEmUtc)
{
    public static OcorrenciaResponse De(Ocorrencia o) => new(o.Id, o.Tipo, o.Descricao, o.Bairro,
        o.Latitude, o.Longitude, o.Severidade, o.Apelido, o.Status, o.CriadoEmUtc, o.ResolvidaEmUtc);
}

public sealed record PaginaResponse<T>(IReadOnlyList<T> Itens, int Pagina, int TamanhoPagina, int Total)
{
    public int TotalPaginas => TamanhoPagina == 0 ? 0 : (int)Math.Ceiling(Total / (double)TamanhoPagina);
}

// ---------- Alertas ----------

public sealed record AlertaResponse(int Id, string Bairro, NivelRisco Nivel, string NivelDescricao,
    string Mensagem, bool Ativo, int? SensorId, DateTime CriadoEmUtc, DateTime? EncerradoEmUtc)
{
    public static AlertaResponse De(Alerta a) => new(a.Id, a.Bairro, a.Nivel, a.Nivel.ToString(),
        a.Mensagem, a.Ativo, a.SensorId, a.CriadoEmUtc, a.EncerradoEmUtc);
}

// ---------- Painel ----------

public sealed record ResumoBairroResponse(string Bairro, int Sensores, NivelRisco RiscoAtual,
    string RiscoDescricao, double? MaiorNivelCm, int OcorrenciasAbertas, int AlertasAtivos);

public sealed record PainelResponse(DateTime GeradoEmUtc, int TotalSensoresAtivos, int TotalOcorrenciasAbertas,
    int TotalAlertasAtivos, NivelRisco RiscoGeral, IReadOnlyList<ResumoBairroResponse> Bairros);
