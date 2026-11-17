using AquaGuard.Domain.Comum;

namespace AquaGuard.Domain.ValueObjects;

/// <summary>
/// Value Object imutável que representa uma posição geográfica válida.
/// </summary>
public readonly record struct Coordenada
{
    public double Latitude { get; }
    public double Longitude { get; }

    public Coordenada(double latitude, double longitude)
    {
        if (latitude is < -90 or > 90)
            throw new DomainException("Latitude deve estar entre -90 e 90.");
        if (longitude is < -180 or > 180)
            throw new DomainException("Longitude deve estar entre -180 e 180.");
        Latitude = latitude;
        Longitude = longitude;
    }

    /// <summary>Distância aproximada em km (fórmula de Haversine).</summary>
    public double DistanciaKm(Coordenada outra)
    {
        const double raioTerraKm = 6371.0;
        static double Rad(double g) => g * Math.PI / 180.0;
        var dLat = Rad(outra.Latitude - Latitude);
        var dLon = Rad(outra.Longitude - Longitude);
        var a = Math.Sin(dLat / 2) * Math.Sin(dLat / 2) +
                Math.Cos(Rad(Latitude)) * Math.Cos(Rad(outra.Latitude)) *
                Math.Sin(dLon / 2) * Math.Sin(dLon / 2);
        return raioTerraKm * 2 * Math.Atan2(Math.Sqrt(a), Math.Sqrt(1 - a));
    }
}
