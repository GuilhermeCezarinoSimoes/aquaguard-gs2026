using AquaGuard.Domain.Entidades;
using AquaGuard.Domain.Interfaces;
using Microsoft.EntityFrameworkCore;

namespace AquaGuard.Infrastructure.Dados;

public class AquaGuardDbContext : DbContext, IUnidadeDeTrabalho
{
    public AquaGuardDbContext(DbContextOptions<AquaGuardDbContext> options) : base(options) { }

    public DbSet<Sensor> Sensores => Set<Sensor>();
    public DbSet<LeituraSensor> Leituras => Set<LeituraSensor>();
    public DbSet<Ocorrencia> Ocorrencias => Set<Ocorrencia>();
    public DbSet<Alerta> Alertas => Set<Alerta>();

    public Task<int> SalvarAsync(CancellationToken ct = default) => SaveChangesAsync(ct);

    protected override void OnModelCreating(ModelBuilder mb)
    {
        mb.Entity<Sensor>(e =>
        {
            e.ToTable("Sensores");
            e.HasKey(x => x.Id);
            e.Property(x => x.Codigo).HasMaxLength(20).IsRequired();
            e.HasIndex(x => x.Codigo).IsUnique();
            e.Property(x => x.Nome).HasMaxLength(120).IsRequired();
            e.Property(x => x.Bairro).HasMaxLength(80).IsRequired();
            e.HasIndex(x => x.Bairro);
            e.Ignore(x => x.Local);
            e.HasMany(x => x.Leituras).WithOne(l => l.Sensor!).HasForeignKey(l => l.SensorId)
             .OnDelete(DeleteBehavior.Cascade);
            e.Navigation(x => x.Leituras).UsePropertyAccessMode(PropertyAccessMode.Field);
        });

        mb.Entity<LeituraSensor>(e =>
        {
            e.ToTable("Leituras");
            e.HasKey(x => x.Id);
            e.Property(x => x.Risco).HasConversion<int>();
            e.HasIndex(x => new { x.SensorId, x.DataHoraUtc });
        });

        mb.Entity<Ocorrencia>(e =>
        {
            e.ToTable("Ocorrencias");
            e.HasKey(x => x.Id);
            e.Property(x => x.Descricao).HasMaxLength(500).IsRequired();
            e.Property(x => x.Bairro).HasMaxLength(80).IsRequired();
            e.Property(x => x.Apelido).HasMaxLength(40);
            e.Property(x => x.Tipo).HasConversion<int>();
            e.Property(x => x.Status).HasConversion<int>();
            e.Ignore(x => x.EstaAberta);
            e.HasIndex(x => new { x.Bairro, x.Status });
        });

        mb.Entity<Alerta>(e =>
        {
            e.ToTable("Alertas");
            e.HasKey(x => x.Id);
            e.Property(x => x.Bairro).HasMaxLength(80).IsRequired();
            e.Property(x => x.Mensagem).HasMaxLength(300).IsRequired();
            e.Property(x => x.Nivel).HasConversion<int>();
            e.HasOne(x => x.Sensor).WithMany().HasForeignKey(x => x.SensorId).OnDelete(DeleteBehavior.SetNull);
            e.HasIndex(x => new { x.Bairro, x.Ativo });
        });
    }
}
