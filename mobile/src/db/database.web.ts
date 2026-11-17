import type { NovaOcorrencia, RelatoLocal, StatusSync } from '../lib/types';

/**
 * Versão WEB do banco local (usada só ao abrir o app no navegador para demonstração).
 * Mesma interface de database.ts; persiste em localStorage porque o SQLite nativo
 * exige configurações extras (WASM + cabeçalhos COOP/COEP) no navegador.
 * No Android/iOS o app usa SQLite real (database.ts).
 */
const PREFIXO = 'aquaguard:';

function ler<T>(chave: string, padrao: T): T {
  try {
    const v = globalThis.localStorage?.getItem(PREFIXO + chave);
    return v ? (JSON.parse(v) as T) : padrao;
  } catch {
    return padrao;
  }
}

function gravar(chave: string, valor: unknown): void {
  try {
    globalThis.localStorage?.setItem(PREFIXO + chave, JSON.stringify(valor));
  } catch {
    /* armazenamento indisponível (modo privado) */
  }
}

export const banco = {
  async salvarRelato(o: NovaOcorrencia): Promise<number> {
    const relatos = ler<RelatoLocal[]>('relatos', []);
    const idLocal = relatos.reduce((m, r) => Math.max(m, r.idLocal), 0) + 1;
    relatos.push({ ...o, apelido: o.apelido ?? null, idLocal, criadoEm: new Date().toISOString(), statusSync: 'pendente', idRemoto: null });
    gravar('relatos', relatos);
    return idLocal;
  },
  async listarRelatos(): Promise<RelatoLocal[]> {
    return ler<RelatoLocal[]>('relatos', []).sort((a, b) => b.criadoEm.localeCompare(a.criadoEm));
  },
  async atualizarSync(idLocal: number, status: StatusSync, idRemoto: number | null = null): Promise<void> {
    gravar('relatos', ler<RelatoLocal[]>('relatos', []).map((r) =>
      r.idLocal === idLocal ? { ...r, statusSync: status, idRemoto: idRemoto ?? r.idRemoto } : r));
  },
  async excluirRelato(idLocal: number): Promise<void> {
    gravar('relatos', ler<RelatoLocal[]>('relatos', []).filter((r) => r.idLocal !== idLocal));
  },
  async obterPreferencia(chave: string): Promise<string | null> {
    return ler<Record<string, string>>('prefs', {})[chave] ?? null;
  },
  async salvarPreferencia(chave: string, valor: string): Promise<void> {
    gravar('prefs', { ...ler<Record<string, string>>('prefs', {}), [chave]: valor });
  },
  async salvarCache<T>(chave: string, dados: T): Promise<void> {
    gravar(`cache:${chave}`, { dados, atualizadoEm: new Date().toISOString() });
  },
  async lerCache<T>(chave: string): Promise<{ dados: T; atualizadoEm: string } | null> {
    return ler<{ dados: T; atualizadoEm: string } | null>(`cache:${chave}`, null);
  },
};
