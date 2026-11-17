namespace AquaGuard.Domain.Enums;

/// <summary>Nível de risco de alagamento (ordem crescente de gravidade).</summary>
public enum NivelRisco
{
    Normal = 0,
    Atencao = 1,
    Alerta = 2,
    Critico = 3
}

/// <summary>Tipo de ocorrência relatada pelo cidadão.</summary>
public enum TipoOcorrencia
{
    RuaAlagada = 1,
    BueiroEntupido = 2,
    CorregoTransbordando = 3,
    ImovelAtingido = 4,
    Outro = 99
}

/// <summary>Ciclo de vida de uma ocorrência.</summary>
public enum StatusOcorrencia
{
    Aberta = 1,
    EmAnalise = 2,
    Resolvida = 3,
    Descartada = 4
}
