using AquaGuard.Domain.Comum;
using AquaGuard.Domain.Entidades;
using AquaGuard.Domain.Enums;
using AquaGuard.Domain.Interfaces;
using AquaGuard.Infrastructure.Dados;
using Microsoft.EntityFrameworkCore;

namespace AquaGuard.Infrastructure.Repositorios;

/// <summary>Implementação genérica com EF Core (herdada pelos repositórios específicos).</summary>
public abstract class RepositorioBase<T> : IRepositorio<T> where T : EntidadeBase
{
    protected readonly AquaGuardDbContext Db;
    protected DbSet<T> Set => Db.Set<T>();

    protected RepositorioBase(AquaGuardDbContext db) => Db = db;

    public virtual Task<T?> ObterPorIdAsync(int id, CancellationToken ct = default)
        => Set.FirstOrDefaultAsync(e => e.Id == id, ct);

    public async Task AdicionarAsync(T entidade, CancellationToken ct = default)
        => await Set.AddAsync(entidade, ct);

    public void Remover(T entidade) => Set.Remove(entidade);
}

public sealed class SensorRepositorio : RepositorioBase<Sensor>, ISensorRepositorio
{
    public SensorRepositorio(AquaGuardDbContext db) : base(db) { }

    public Task<Sensor?> ObterPorCodigoAsync(string codigo, CancellationToken ct = default)
        => Set.FirstOrDefaultAsync(s => s.Codigo == codigo, ct);

    public Task<bool> CodigoExisteAsync(string codigo, CancellationToken ct = default)
        => Set.AnyAsync(s => s.Codigo == codigo, ct);

    public async Task<IReadOnlyList<Sensor>> ListarAsync(string? bairro, bool? ativo, CancellationToken ct = default)
    {
        IQueryable<Sensor> q = Set.AsNoTracking();
        if (!string.IsNullOrWhiteSpace(bairro)) q = q.Where(s => s.Bairro == bairro);
        if (ativo.HasValue) q = q.Where(s => s.Ativo == ativo.Value);
        return await q.OrderBy(s => s.Bairro).ThenBy(s => s.Codigo).ToListAsync(ct);
    }
}

public sealed class LeituraRepositorio : RepositorioBase<LeituraSensor>, ILeituraRepositorio
{
    public LeituraRepositorio(AquaGuardDbContext db) : base(db) { }

    public async Task<IReadOnlyList<LeituraSensor>> ListarPorSensorAsync(int sensorId, DateTime? desdeUtc, int limite,
        CancellationToken ct = default)
    {
        var q = Set.AsNoTracking().Where(l => l.SensorId == sensorId);
        if (desdeUtc.HasValue) q = q.Where(l => l.DataHoraUtc >= desdeUtc.Value);
        return await q.OrderByDescending(l => l.DataHoraUtc).Take(limite).ToListAsync(ct);
    }

    public Task<LeituraSensor?> ObterUltimaAsync(int sensorId, CancellationToken ct = default)
        => Set.AsNoTracking().Where(l => l.SensorId == sensorId)
              .OrderByDescending(l => l.DataHoraUtc).FirstOrDefaultAsync(ct);
}

public sealed class OcorrenciaRepositorio : RepositorioBase<Ocorrencia>, IOcorrenciaRepositorio
{
    public OcorrenciaRepositorio(AquaGuardDbContext db) : base(db) { }

    public async Task<(IReadOnlyList<Ocorrencia> Itens, int Total)> ListarAsync(string? bairro, StatusOcorrencia? status,
        int pagina, int tamanhoPagina, CancellationToken ct = default)
    {
        var q = Set.AsNoTracking().AsQueryable();
        if (!string.IsNullOrWhiteSpace(bairro)) q = q.Where(o => o.Bairro == bairro);
        if (status.HasValue) q = q.Where(o => o.Status == status.Value);

        var total = await q.CountAsync(ct);
        var itens = await q.OrderByDescending(o => o.Severidade).ThenByDescending(o => o.CriadoEmUtc)
                           .Skip((pagina - 1) * tamanhoPagina).Take(tamanhoPagina).ToListAsync(ct);
        return (itens, total);
    }
}

public sealed class AlertaRepositorio : RepositorioBase<Alerta>, IAlertaRepositorio
{
    public AlertaRepositorio(AquaGuardDbContext db) : base(db) { }

    public Task<Alerta?> ObterAtivoPorBairroAsync(string bairro, CancellationToken ct = default)
        => Set.Where(a => a.Bairro == bairro && a.Ativo).OrderByDescending(a => a.CriadoEmUtc).FirstOrDefaultAsync(ct);

    public async Task<IReadOnlyList<Alerta>> ListarAsync(bool somenteAtivos, string? bairro, CancellationToken ct = default)
    {
        var q = Set.AsNoTracking().AsQueryable();
        if (somenteAtivos) q = q.Where(a => a.Ativo);
        if (!string.IsNullOrWhiteSpace(bairro)) q = q.Where(a => a.Bairro == bairro);
        return await q.OrderByDescending(a => a.Nivel).ThenByDescending(a => a.CriadoEmUtc).ToListAsync(ct);
    }
}
