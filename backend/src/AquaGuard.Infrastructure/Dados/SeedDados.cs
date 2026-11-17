using AquaGuard.Domain.Entidades;
using AquaGuard.Domain.Enums;
using AquaGuard.Domain.ValueObjects;
using Microsoft.EntityFrameworkCore;

namespace AquaGuard.Infrastructure.Dados;

/// <summary>
/// Dados iniciais de DEMONSTRAÇÃO (protótipo). Os pontos ficam em locais reais de
/// São Paulo historicamente afetados por alagamentos; os dispositivos são simulados (Wokwi).
/// Nenhum dado pessoal é armazenado.
/// </summary>
public static class SeedDados
{
    public static async Task AplicarAsync(AquaGuardDbContext db, CancellationToken ct = default)
    {
        if (await db.Sensores.AnyAsync(ct)) return;

        var sensores = new[]
        {
            new Sensor("AQG-001", "Córrego Três Pontes - R. Erva do Brejo", "Jardim Pantanal",
                new Coordenada(-23.4972, -46.4296), 80, 120),
            new Sensor("AQG-002", "Várzea do Tietê - Av. Pres. Washington Luís (acesso)", "Jardim Pantanal",
                new Coordenada(-23.4930, -46.4380), 70, 110),
            new Sensor("AQG-003", "Córrego Aricanduva - Av. Aricanduva", "Aricanduva",
                new Coordenada(-23.5672, -46.5094), 90, 140),
            new Sensor("AQG-004", "Córrego Ipiranga - Av. Ricardo Jafet", "Ipiranga",
                new Coordenada(-23.5960, -46.6074), 100, 150),
            new Sensor("AQG-005", "Galeria Pacaembu - Praça Charles Miller", "Pacaembu",
                new Coordenada(-23.5475, -46.6650), 60, 100),
        };
        db.Sensores.AddRange(sensores);
        await db.SaveChangesAsync(ct);

        db.Ocorrencias.AddRange(
            new Ocorrencia(TipoOcorrencia.BueiroEntupido, "Boca de lobo entupida com lixo na esquina da escola",
                "Jardim Pantanal", new Coordenada(-23.4965, -46.4301), 3, "Morador JP"),
            new Ocorrencia(TipoOcorrencia.RuaAlagada, "Rua alagada após chuva da tarde, carros não passam",
                "Aricanduva", new Coordenada(-23.5680, -46.5100), 4));
        await db.SaveChangesAsync(ct);
    }
}
