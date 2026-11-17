using AquaGuard.Domain.Comum;
using AquaGuard.Domain.Entidades;
using AquaGuard.Domain.Enums;

namespace AquaGuard.Domain.Interfaces;

/// <summary>Repositório genérico assíncrono.</summary>
public interface IRepositorio<T> where T : EntidadeBase
{
    Task<T?> ObterPorIdAsync(int id, CancellationToken ct = default);
    Task AdicionarAsync(T entidade, CancellationToken ct = default);
    void Remover(T entidade);
}

public interface ISensorRepositorio : IRepositorio<Sensor>
{
    Task<Sensor?> ObterPorCodigoAsync(string codigo, CancellationToken ct = default);
    Task<IReadOnlyList<Sensor>> ListarAsync(string? bairro, bool? ativo, CancellationToken ct = default);
    Task<bool> CodigoExisteAsync(string codigo, CancellationToken ct = default);
}

public interface ILeituraRepositorio : IRepositorio<LeituraSensor>
{
    Task<IReadOnlyList<LeituraSensor>> ListarPorSensorAsync(int sensorId, DateTime? desdeUtc, int limite, CancellationToken ct = default);
    Task<LeituraSensor?> ObterUltimaAsync(int sensorId, CancellationToken ct = default);
}

public interface IOcorrenciaRepositorio : IRepositorio<Ocorrencia>
{
    Task<(IReadOnlyList<Ocorrencia> Itens, int Total)> ListarAsync(string? bairro, StatusOcorrencia? status,
        int pagina, int tamanhoPagina, CancellationToken ct = default);
}

public interface IAlertaRepositorio : IRepositorio<Alerta>
{
    Task<Alerta?> ObterAtivoPorBairroAsync(string bairro, CancellationToken ct = default);
    Task<IReadOnlyList<Alerta>> ListarAsync(bool somenteAtivos, string? bairro, CancellationToken ct = default);
}

/// <summary>Unit of Work: confirma todas as alterações em uma única transação.</summary>
public interface IUnidadeDeTrabalho
{
    Task<int> SalvarAsync(CancellationToken ct = default);
}
