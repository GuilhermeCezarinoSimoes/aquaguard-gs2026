import type { NivelRisco, TipoOcorrencia } from './types';

/** Bairros atendidos no protótipo, com coordenada de referência (centro aproximado). */
export const BAIRROS: { nome: string; latitude: number; longitude: number }[] = [
  { nome: 'Jardim Pantanal', latitude: -23.4965, longitude: -46.4320 },
  { nome: 'Aricanduva', latitude: -23.5672, longitude: -46.5094 },
  { nome: 'Ipiranga', latitude: -23.5960, longitude: -46.6074 },
  { nome: 'Pacaembu', latitude: -23.5475, longitude: -46.6650 },
];

export const TIPOS_OCORRENCIA: { valor: TipoOcorrencia; rotulo: string; icone: string }[] = [
  { valor: 'RuaAlagada', rotulo: 'Rua alagada', icone: 'water' },
  { valor: 'BueiroEntupido', rotulo: 'Bueiro entupido', icone: 'trash' },
  { valor: 'CorregoTransbordando', rotulo: 'Córrego transbordando', icone: 'trending-up' },
  { valor: 'ImovelAtingido', rotulo: 'Casa atingida', icone: 'home' },
  { valor: 'Outro', rotulo: 'Outro', icone: 'ellipsis-horizontal' },
];

export const ROTULO_RISCO: Record<NivelRisco, string> = {
  Normal: 'Normal',
  Atencao: 'Atenção',
  Alerta: 'Alerta',
  Critico: 'Perigo',
};

export const ICONE_RISCO: Record<NivelRisco, string> = {
  Normal: 'checkmark-circle',
  Atencao: 'eye',
  Alerta: 'warning',
  Critico: 'alert-circle',
};

/** Orientações em linguagem simples para cada nível (baseadas nas recomendações da Defesa Civil). */
export const ORIENTACAO_RISCO: Record<NivelRisco, { titulo: string; dicas: string[] }> = {
  Normal: {
    titulo: 'Sem risco de alagamento agora',
    dicas: ['Mantenha bueiros e calçadas livres de lixo.', 'Salve o telefone da Defesa Civil: 199.'],
  },
  Atencao: {
    titulo: 'Chuva ou água subindo. Fique atento.',
    dicas: ['Evite deixar o carro em ruas baixas.', 'Deixe documentos e remédios em local alto.'],
  },
  Alerta: {
    titulo: 'O córrego está perto de transbordar.',
    dicas: ['Evite passar pela região.', 'Desligue aparelhos da tomada se a água se aproximar.', 'Avise vizinhos idosos.'],
  },
  Critico: {
    titulo: 'Água na rua. Proteja-se agora.',
    dicas: [
      'Não entre na água: ela pode esconder buracos e estar contaminada.',
      'Procure um lugar alto e seguro.',
      'Emergência: Defesa Civil 199 · Bombeiros 193.',
    ],
  },
};

export const ORDEM_RISCO: Record<NivelRisco, number> = { Normal: 0, Atencao: 1, Alerta: 2, Critico: 3 };
