import { useColorScheme } from 'react-native';
import type { NivelRisco } from '../lib/types';

const claro = {
  fundo: '#F2F4F7',
  superficie: '#FFFFFF',
  texto: '#0B1220',
  textoSecundario: '#5B6576',
  borda: '#E3E7ED',
  marca: '#0A6CB0',
  marcaSuave: '#E3F0FA',
  /** Fundo de botões/elementos preenchidos com texto branco (contraste ≥ 4.5:1). */
  marcaForte: '#0A6CB0',
  sucesso: '#1B7F3B',
  perigo: '#C62828',
};

const escuro: typeof claro = {
  fundo: '#000000',
  superficie: '#14181F',
  texto: '#F2F4F7',
  textoSecundario: '#A3ACBA',
  borda: '#262C36',
  marca: '#4FA8E8',
  marcaSuave: '#0E2638',
  marcaForte: '#1864AB',
  sucesso: '#4CC172',
  perigo: '#FF6B6B',
};

/** Cores de risco com contraste AA para texto branco sobre o fundo (verificado ≥ 4.5:1). */
export const COR_RISCO: Record<NivelRisco, string> = {
  Normal: '#1B7F3B',
  Atencao: '#8A5A00',
  Alerta: '#B54708',
  Critico: '#B42318',
};

export const espaco = { xs: 4, sm: 8, md: 16, lg: 24, xl: 32 } as const;
export const raio = { sm: 10, md: 16, lg: 22, pill: 999 } as const;

export const tipografia = {
  tituloGrande: { fontSize: 32, fontWeight: '700' as const, letterSpacing: -0.5 },
  titulo: { fontSize: 22, fontWeight: '700' as const, letterSpacing: -0.3 },
  subtitulo: { fontSize: 17, fontWeight: '600' as const },
  corpo: { fontSize: 17, lineHeight: 24 },
  legenda: { fontSize: 14, lineHeight: 19 },
};

export type Cores = typeof claro;

export function useCores(): Cores {
  return useColorScheme() === 'dark' ? escuro : claro;
}
