import type { Alerta, Leitura, Painel, Sensor } from './types';

/**
 * Dados de DEMONSTRAÇÃO usados apenas quando a API não está acessível e não há cache.
 * O app sinaliza claramente ao usuário quando está mostrando estes dados.
 */
const agora = new Date().toISOString();

export const SENSORES_DEMO: Sensor[] = [
  { id: 1, codigo: 'AQG-001', nome: 'Córrego Três Pontes - R. Erva do Brejo', bairro: 'Jardim Pantanal', latitude: -23.4972, longitude: -46.4296, nivelAlertaCm: 80, nivelCriticoCm: 120, ativo: true, ultimoNivelCm: 92, ultimoRisco: 'Alerta', ultimaLeituraUtc: agora },
  { id: 2, codigo: 'AQG-002', nome: 'Várzea do Tietê - acesso', bairro: 'Jardim Pantanal', latitude: -23.493, longitude: -46.438, nivelAlertaCm: 70, nivelCriticoCm: 110, ativo: true, ultimoNivelCm: 40, ultimoRisco: 'Normal', ultimaLeituraUtc: agora },
  { id: 3, codigo: 'AQG-003', nome: 'Córrego Aricanduva', bairro: 'Aricanduva', latitude: -23.5672, longitude: -46.5094, nivelAlertaCm: 90, nivelCriticoCm: 140, ativo: true, ultimoNivelCm: 30, ultimoRisco: 'Normal', ultimaLeituraUtc: agora },
  { id: 4, codigo: 'AQG-004', nome: 'Córrego Ipiranga - Av. Ricardo Jafet', bairro: 'Ipiranga', latitude: -23.596, longitude: -46.6074, nivelAlertaCm: 100, nivelCriticoCm: 150, ativo: true, ultimoNivelCm: 65, ultimoRisco: 'Atencao', ultimaLeituraUtc: agora },
  { id: 5, codigo: 'AQG-005', nome: 'Galeria Pacaembu', bairro: 'Pacaembu', latitude: -23.5475, longitude: -46.665, nivelAlertaCm: 60, nivelCriticoCm: 100, ativo: true, ultimoNivelCm: 10, ultimoRisco: 'Normal', ultimaLeituraUtc: agora },
];

export const ALERTAS_DEMO: Alerta[] = [
  { id: 1, bairro: 'Jardim Pantanal', nivel: 'Alerta', mensagem: 'ALERTA em Jardim Pantanal: córrego perto de transbordar. Evite a região e proteja seus pertences.', ativo: true, criadoEmUtc: agora },
];

export const PAINEL_DEMO: Painel = {
  geradoEmUtc: agora,
  totalSensoresAtivos: 5,
  totalOcorrenciasAbertas: 2,
  totalAlertasAtivos: 1,
  riscoGeral: 'Alerta',
  bairros: [
    { bairro: 'Jardim Pantanal', sensores: 2, riscoAtual: 'Alerta', maiorNivelCm: 92, ocorrenciasAbertas: 1, alertasAtivos: 1 },
    { bairro: 'Ipiranga', sensores: 1, riscoAtual: 'Atencao', maiorNivelCm: 65, ocorrenciasAbertas: 0, alertasAtivos: 0 },
    { bairro: 'Aricanduva', sensores: 1, riscoAtual: 'Normal', maiorNivelCm: 30, ocorrenciasAbertas: 1, alertasAtivos: 0 },
    { bairro: 'Pacaembu', sensores: 1, riscoAtual: 'Normal', maiorNivelCm: 10, ocorrenciasAbertas: 0, alertasAtivos: 0 },
  ],
};

export function leiturasDemo(sensorId: number): Leitura[] {
  const base = SENSORES_DEMO.find((s) => s.id === sensorId)?.ultimoNivelCm ?? 20;
  return Array.from({ length: 12 }, (_, i) => {
    const nivel = Math.max(0, Math.round(base - (11 - i) * (base / 14)));
    return {
      id: i + 1,
      sensorId,
      nivelAguaCm: nivel,
      chuvaMmH: Math.round(nivel / 4),
      dataHoraUtc: new Date(Date.now() - (11 - i) * 10 * 60_000).toISOString(),
      risco: 'Normal' as const,
    };
  }).reverse();
}

