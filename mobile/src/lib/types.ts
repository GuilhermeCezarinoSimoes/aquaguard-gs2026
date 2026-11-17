export type NivelRisco = 'Normal' | 'Atencao' | 'Alerta' | 'Critico';

export type TipoOcorrencia =
  | 'RuaAlagada'
  | 'BueiroEntupido'
  | 'CorregoTransbordando'
  | 'ImovelAtingido'
  | 'Outro';

export interface Sensor {
  id: number;
  codigo: string;
  nome: string;
  bairro: string;
  latitude: number;
  longitude: number;
  nivelAlertaCm: number;
  nivelCriticoCm: number;
  ativo: boolean;
  ultimoNivelCm: number | null;
  ultimoRisco: NivelRisco | null;
  ultimaLeituraUtc: string | null;
}

export interface Leitura {
  id: number;
  sensorId: number;
  nivelAguaCm: number;
  chuvaMmH: number;
  dataHoraUtc: string;
  risco: NivelRisco;
}

export interface Alerta {
  id: number;
  bairro: string;
  nivel: NivelRisco;
  mensagem: string;
  ativo: boolean;
  criadoEmUtc: string;
}

export interface ResumoBairro {
  bairro: string;
  sensores: number;
  riscoAtual: NivelRisco;
  maiorNivelCm: number | null;
  ocorrenciasAbertas: number;
  alertasAtivos: number;
}

export interface Painel {
  geradoEmUtc: string;
  totalSensoresAtivos: number;
  totalOcorrenciasAbertas: number;
  totalAlertasAtivos: number;
  riscoGeral: NivelRisco;
  bairros: ResumoBairro[];
}

export interface NovaOcorrencia {
  tipo: TipoOcorrencia;
  descricao: string;
  bairro: string;
  latitude: number;
  longitude: number;
  severidade: number;
  apelido?: string | null;
}

export type StatusSync = 'pendente' | 'enviado' | 'erro';

/** Relato salvo no banco local do aparelho (SQLite). */
export interface RelatoLocal extends NovaOcorrencia {
  idLocal: number;
  criadoEm: string;
  statusSync: StatusSync;
  idRemoto: number | null;
}

/** Origem dos dados exibidos: API ao vivo, cache local ou demonstração. */
export type OrigemDados = 'api' | 'cache' | 'demo';
