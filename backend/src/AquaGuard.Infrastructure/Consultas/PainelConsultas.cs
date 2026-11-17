using AquaGuard.Application.Dtos;
using AquaGuard.Application.Servicos;
using AquaGuard.Domain.Enums;
using AquaGuard.Infrastructure.Dados;
using Microsoft.EntityFrameworkCore;

namespace AquaGuard.Infrastructure.Consultas;

/// <summary>Consultas de leitura do painel, escritas com LINQ (GroupBy, Join, projeções).</summary>
public sealed class PainelConsultas : IPainelConsultas
{
    private readonly AquaGuardDbContext _db;

    public PainelConsultas(AquaGuardDbContext db) => _db = db;

    public async Task<PainelResponse> ObterPainelAsync(CancellationToken ct = default)
    {
        // Última leitura de cada sensor ativo (subconsulta traduzida para SQL pelo EF Core).
        var ultimas = await _db.Sensores.AsNoTracking()
            .Where(s => s.Ativo)
            .Select(s => new
            {
                s.Bairro,
                Ultima = _db.Leituras.Where(l => l.SensorId == s.Id)
                                     .OrderByDescending(l => l.DataHoraUtc)
                                     .Select(l => new { l.NivelAguaCm, l.Risco })
                                     .FirstOrDefault()
            })
            .ToListAsync(ct);

        var ocorrenciasPorBairro = await _db.Ocorrencias.AsNoTracking()
            .Where(o => o.Status == StatusOcorrencia.Aberta || o.Status == StatusOcorrencia.EmAnalise)
            .GroupBy(o => o.Bairro)
            .Select(g => new { Bairro = g.Key, Qtd = g.Count() })
            .ToDictionaryAsync(x => x.Bairro, x => x.Qtd, ct);

        var alertasPorBairro = await _db.Alertas.AsNoTracking()
            .Where(a => a.Ativo)
            .GroupBy(a => a.Bairro)
            .Select(g => new { Bairro = g.Key, Qtd = g.Count() })
            .ToDictionaryAsync(x => x.Bairro, x => x.Qtd, ct);

        var bairros = ultimas.Select(u => u.Bairro)
            .Union(ocorrenciasPorBairro.Keys)
            .Union(alertasPorBairro.Keys)
            .Distinct()
            .Select(bairro =>
            {
                var doBairro = ultimas.Where(u => u.Bairro == bairro).ToList();
                var risco = doBairro.Where(u => u.Ultima != null)
                                    .Select(u => u.Ultima!.Risco)
                                    .DefaultIfEmpty(NivelRisco.Normal)
                                    .Max();
                var maiorNivel = doBairro.Where(u => u.Ultima != null)
                                         .Select(u => (double?)u.Ultima!.NivelAguaCm)
                                         .Max();
                return new ResumoBairroResponse(bairro, doBairro.Count, risco, risco.ToString(), maiorNivel,
                    ocorrenciasPorBairro.GetValueOrDefault(bairro), alertasPorBairro.GetValueOrDefault(bairro));
            })
            .OrderByDescending(b => b.RiscoAtual)
            .ThenByDescending(b => b.OcorrenciasAbertas)
            .ThenBy(b => b.Bairro)
            .ToList();

        return new PainelResponse(
            DateTime.UtcNow,
            ultimas.Count,
            ocorrenciasPorBairro.Values.Sum(),
            alertasPorBairro.Values.Sum(),
            bairros.Select(b => b.RiscoAtual).DefaultIfEmpty(NivelRisco.Normal).Max(),
            bairros);
    }
}
