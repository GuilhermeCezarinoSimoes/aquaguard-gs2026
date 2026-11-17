using System;
using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

namespace AquaGuard.Infrastructure.Dados.Migrations
{
    /// <inheritdoc />
    public partial class InicialAquaGuard : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.CreateTable(
                name: "Ocorrencias",
                columns: table => new
                {
                    Id = table.Column<int>(type: "INTEGER", nullable: false)
                        .Annotation("Sqlite:Autoincrement", true),
                    Tipo = table.Column<int>(type: "INTEGER", nullable: false),
                    Descricao = table.Column<string>(type: "TEXT", maxLength: 500, nullable: false),
                    Bairro = table.Column<string>(type: "TEXT", maxLength: 80, nullable: false),
                    Latitude = table.Column<double>(type: "REAL", nullable: false),
                    Longitude = table.Column<double>(type: "REAL", nullable: false),
                    Severidade = table.Column<int>(type: "INTEGER", nullable: false),
                    Apelido = table.Column<string>(type: "TEXT", maxLength: 40, nullable: true),
                    Status = table.Column<int>(type: "INTEGER", nullable: false),
                    ResolvidaEmUtc = table.Column<DateTime>(type: "TEXT", nullable: true),
                    CriadoEmUtc = table.Column<DateTime>(type: "TEXT", nullable: false),
                    AtualizadoEmUtc = table.Column<DateTime>(type: "TEXT", nullable: true)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_Ocorrencias", x => x.Id);
                });

            migrationBuilder.CreateTable(
                name: "Sensores",
                columns: table => new
                {
                    Id = table.Column<int>(type: "INTEGER", nullable: false)
                        .Annotation("Sqlite:Autoincrement", true),
                    Codigo = table.Column<string>(type: "TEXT", maxLength: 20, nullable: false),
                    Nome = table.Column<string>(type: "TEXT", maxLength: 120, nullable: false),
                    Bairro = table.Column<string>(type: "TEXT", maxLength: 80, nullable: false),
                    Latitude = table.Column<double>(type: "REAL", nullable: false),
                    Longitude = table.Column<double>(type: "REAL", nullable: false),
                    NivelAlertaCm = table.Column<double>(type: "REAL", nullable: false),
                    NivelCriticoCm = table.Column<double>(type: "REAL", nullable: false),
                    Ativo = table.Column<bool>(type: "INTEGER", nullable: false),
                    CriadoEmUtc = table.Column<DateTime>(type: "TEXT", nullable: false),
                    AtualizadoEmUtc = table.Column<DateTime>(type: "TEXT", nullable: true)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_Sensores", x => x.Id);
                });

            migrationBuilder.CreateTable(
                name: "Alertas",
                columns: table => new
                {
                    Id = table.Column<int>(type: "INTEGER", nullable: false)
                        .Annotation("Sqlite:Autoincrement", true),
                    SensorId = table.Column<int>(type: "INTEGER", nullable: true),
                    Bairro = table.Column<string>(type: "TEXT", maxLength: 80, nullable: false),
                    Nivel = table.Column<int>(type: "INTEGER", nullable: false),
                    Mensagem = table.Column<string>(type: "TEXT", maxLength: 300, nullable: false),
                    Ativo = table.Column<bool>(type: "INTEGER", nullable: false),
                    EncerradoEmUtc = table.Column<DateTime>(type: "TEXT", nullable: true),
                    CriadoEmUtc = table.Column<DateTime>(type: "TEXT", nullable: false),
                    AtualizadoEmUtc = table.Column<DateTime>(type: "TEXT", nullable: true)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_Alertas", x => x.Id);
                    table.ForeignKey(
                        name: "FK_Alertas_Sensores_SensorId",
                        column: x => x.SensorId,
                        principalTable: "Sensores",
                        principalColumn: "Id",
                        onDelete: ReferentialAction.SetNull);
                });

            migrationBuilder.CreateTable(
                name: "Leituras",
                columns: table => new
                {
                    Id = table.Column<int>(type: "INTEGER", nullable: false)
                        .Annotation("Sqlite:Autoincrement", true),
                    SensorId = table.Column<int>(type: "INTEGER", nullable: false),
                    NivelAguaCm = table.Column<double>(type: "REAL", nullable: false),
                    ChuvaMmH = table.Column<double>(type: "REAL", nullable: false),
                    DataHoraUtc = table.Column<DateTime>(type: "TEXT", nullable: false),
                    Risco = table.Column<int>(type: "INTEGER", nullable: false),
                    CriadoEmUtc = table.Column<DateTime>(type: "TEXT", nullable: false),
                    AtualizadoEmUtc = table.Column<DateTime>(type: "TEXT", nullable: true)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_Leituras", x => x.Id);
                    table.ForeignKey(
                        name: "FK_Leituras_Sensores_SensorId",
                        column: x => x.SensorId,
                        principalTable: "Sensores",
                        principalColumn: "Id",
                        onDelete: ReferentialAction.Cascade);
                });

            migrationBuilder.CreateIndex(
                name: "IX_Alertas_Bairro_Ativo",
                table: "Alertas",
                columns: new[] { "Bairro", "Ativo" });

            migrationBuilder.CreateIndex(
                name: "IX_Alertas_SensorId",
                table: "Alertas",
                column: "SensorId");

            migrationBuilder.CreateIndex(
                name: "IX_Leituras_SensorId_DataHoraUtc",
                table: "Leituras",
                columns: new[] { "SensorId", "DataHoraUtc" });

            migrationBuilder.CreateIndex(
                name: "IX_Ocorrencias_Bairro_Status",
                table: "Ocorrencias",
                columns: new[] { "Bairro", "Status" });

            migrationBuilder.CreateIndex(
                name: "IX_Sensores_Bairro",
                table: "Sensores",
                column: "Bairro");

            migrationBuilder.CreateIndex(
                name: "IX_Sensores_Codigo",
                table: "Sensores",
                column: "Codigo",
                unique: true);
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropTable(
                name: "Alertas");

            migrationBuilder.DropTable(
                name: "Leituras");

            migrationBuilder.DropTable(
                name: "Ocorrencias");

            migrationBuilder.DropTable(
                name: "Sensores");
        }
    }
}
